from datetime import timedelta
from typing import Optional
import json
from fastapi import (FastAPI, HTTPException,
                     Depends, status,
                     Response, WebSocket,
                     File, UploadFile)
from fastapi.responses import FileResponse
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from loguru import logger
from celery.result import AsyncResult
# from WormChan import memeater, small_memeater

from minio_utils import (client, get_from_minio, save_to_minio,
                         list_unsaved_files, purge_all_files,
                         purge_unsaved_files, purge_saved_files, purge_pepes,
                         extract_saved_files, extract_pepes,
                         zip_saved_files, zip_pepes)

from user_utils import (user, token,
                        get_current_user, get_current_active_user,
                        create_access_token,
                        authenticate_user, create_user,
                        check_email, remove_user,
                        set_relevants, parse_user_query)

from consts import ACCESS_TOKEN_EXPIRE_MINUTES
from workers import eat_mem_task
from asyncio import sleep as async_sleep

app = FastAPI()


class task(BaseModel):
    boards: list


class file_list(BaseModel):
    files: list


# TODO move most iteratives to either beackgrounds or to celery workers


@app.get("/full_purge/")
async def full_purge(current_user:
                     user = Depends(get_current_active_user)):
    purge_all_files(current_user.username)
    return Response(status_code=200)


# TODO get from and send to methods
@app.get("/purge_unsaved/")
async def purge_unsaved(current_user:
                        user = Depends(get_current_active_user)):
    purge_unsaved_files(current_user.username)
    return Response(status_code=200)


@app.get("/purge_saved/")
async def purge_saved(current_user:
                      user = Depends(get_current_active_user)):
    purge_saved_files(current_user.username)
    return Response(status_code=200)


@app.get("/get_pepes/")
async def get_saved_archive(current_user:
                            user = Depends(get_current_active_user)):
    # get file from client
    extract_saved_files(current_user.username)
    return Response(status_code=200)


@app.get("/send_saved/")
async def send_saved_archive(current_user:
                             user = Depends(get_current_active_user)):
    archive = zip_saved_files(current_user.username)
    output = get_from_minio(client, f"{current_user.username}_saved", archive)
    if output:
        return FileResponse(status_code=200,
                            path=archive, media_type="application/zip")
    else:
        return Response(status_code=500)


@app.get("/purge_pepes/")
async def purge_user_pepes(current_user:
                           user = Depends(get_current_active_user)):
    purge_pepes(current_user.username)
    return Response(status_code=200)


@app.get("/get_pepes/")
async def get_pepe_archive(zipfile: UploadFile = File(...), current_user:
                           user = Depends(get_current_active_user)):
    # get file from client
    await zipfile.read()
    save_to_minio(client, f"{current_user.username}_pepes",
                  zipfile.name, zipfile.file,
                  len(zipfile.file))
    extract_pepes(current_user.username)
    return Response(status_code=200)


@app.get("/send_pepes/")
async def send_pepe_archive(current_user:
                            user = Depends(get_current_active_user)):
    archive = zip_pepes(current_user.username)
    output = get_from_minio(client, f"{current_user.username}_pepes", archive)
    if output:
        return FileResponse(status_code=200,
                            path=archive, media_type="application/zip")
    else:
        return Response(status_code=500)


@app.websocket("/ws/")
async def websocket_endpoint(websocket: WebSocket,
                             token: str):
    try:
        current_user = await parse_user_query(websocket, token)
    except HTTPException:
        return await websocket.close()
    logger.debug(current_user.username)
    await websocket.accept()
    logger.debug("current user accepted")
    await websocket.send_bytes(json.dumps({"response":
                                           {"user": current_user.username,
                                            "status": "connected"}}).encode("utf-8"))
    logger.debug("connection status sent")
    raw_msg = await websocket.receive_bytes()
    decoded_msg = json.loads(raw_msg.decode("utf-8"))
    logger.debug(decoded_msg)
    scrape_task = eat_mem_task.delay(decoded_msg["boards"],
                                     current_user.username)
    logger.debug("task enqued")
    result = eat_mem_task.AsyncResult(scrape_task.id)
    while not result.ready():
        await async_sleep(5)
        result = eat_mem_task.AsyncResult(scrape_task.id)
        logger.info(result.ready())
        state = result.status
        logger.info(state)
    state = result.status
    logger.info(state)
    await websocket.send_text(state)
    logger.debug("task status sent")
    return await websocket.close()


@app.post("/eat_mems/")
async def eat_memes(task: task, current_user:
                    user = Depends(get_current_active_user)):
    scrape_task = eat_mem_task.delay(task.boards, current_user.username)
    result = AsyncResult(scrape_task.id)
    state = result.state
    logger.info(state)
    return {"response":
            {"user": current_user.username,
             "status": "finished"}}


@app.get("/get_mem_names/")
async def get_mem_names(current_user: user = Depends(get_current_user)):
    output = list_unsaved_files(current_user.username, verbose=True)
    return Response(status_code=200,
                    content={"pics":
                             output[f"{current_user.username}_main"]})


@app.post("/get_mem/")
async def get_mem(file_list: file_list, index: int = 0,
                  current_user: user = Depends(get_current_active_user)):
    try:
        output = get_from_minio(client, f"{current_user.username}_main",
                                file_list.files[index])
    except IndexError:
        return Response(status_code=500)
    if output:
        if ".png" in file_list.files[index]:
            return Response(status_code=200,
                            content=output.read(), media_type="image/png")
        if ".jpg" in file_list.files[index]:
            return Response(status_code=200,
                            content=output.read(), media_type="image/jpg")
    return Response(status_code=404)


@app.get("/get_placeholder/")
async def get_placeholder():
    try:
        output = get_from_minio(client, "static", "SORRY_NOTHING.jpg")
        return Response(status_code=200,
                        content=output.read(), media_type="image/jpg")
    except Exception as ex:
        logger.error(f"placeholder image retrieval failed with exception {ex}")
        return Response(status_code=500)


@app.post("/token", response_model=token)
async def login_for_access_token(form_data:
                                 OAuth2PasswordRequestForm = Depends()):
    logger.debug(f"token request recieved {form_data.username}")
    user = authenticate_user(form_data.username, form_data.password)
    logger.info(f"user {form_data.username} authenticated")
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return Response(status_code=200,
                    content={"access_token": access_token,
                             "token_type": "bearer"})


@app.get("/users/me/")
async def read_users_me(current_user: user = Depends(get_current_active_user)):
    return current_user


@app.post("/users/set_relevants/")
async def set_user_relevants(relevants: task,
                             current_user:
                             user = Depends(get_current_active_user)):
    set_relevants(current_user.username, relevants.boards)
    logger.info(f"{current_user} relevants set to {relevants.boards}")
    return Response(status_code=200)


@app.post("/users/create_user/")
async def create_new_user(username: str, password: str,
                          email: str, full_name: Optional[str] = None):
    user_record = {"username": username,
                   "password": password,
                   "email": email,
                   "full_name": full_name if full_name else None}
    if not check_email(email):
        return {"response": "email is invalid"}
    response = create_user(user_record)
    if response:
        return Response(status_code=200)
    else:
        return Response(status_code=401)


@app.get("/users/delete_me/")
async def delete_me(username: str, password: str,
                    current_user: user = Depends(get_current_active_user)):
    response = remove_user(username, password, current_user)
    if not response:
        return Response(status_code=401)
    return Response(status_code=200)
