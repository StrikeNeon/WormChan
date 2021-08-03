import uvicorn
from datetime import timedelta
from typing import Optional
import json
from fastapi import (FastAPI, HTTPException,
                     Depends, status,
                     Response, WebSocket,
                     File, UploadFile,
                     Request)
from fastapi.responses import FileResponse, ORJSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from loguru import logger
# from WormChan import memeater, small_memeater

from minio_utils import (get_from_minio, save_to_minio,
                         list_unsaved_files, purge_all_files,
                         purge_unsaved_files, purge_saved_files, purge_pepes,
                         extract_saved_files, extract_pepes,
                         zip_saved_files, zip_pepes)

from user_utils import (user,
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

class user_model(BaseModel):
    username: str
    password: str
    email: str
    full_name: Optional[str] = None


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


@app.post("/get_saved/")
async def get_saved_archive(current_user:
                            user = Depends(get_current_active_user)):
    try:
        extract_saved_files(current_user.username)
    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="could not find saved file"
        )
    return Response(status_code=200)


@app.get("/send_saved/")
async def send_saved_archive(current_user:
                             user = Depends(get_current_active_user)):
    archive = zip_saved_files(current_user.username)
    output = get_from_minio(f"{current_user.username}_saved", archive)
    if output:
        return FileResponse(status_code=200,
                            path=archive, media_type="application/zip")
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="saved file could not be retrieved"
        )


@app.get("/purge_pepes/")
async def purge_user_pepes(current_user:
                           user = Depends(get_current_active_user)):
    purge_pepes(current_user.username)
    return Response(status_code=200)


@app.post("/get_pepes/")
async def get_pepe_archive(request: Request, zipfile: UploadFile = File(...), current_user:
                           user = Depends(get_current_active_user)):
    # get file from client
    print(zipfile.filename, zipfile.content_type)
    content = await zipfile.read(-1)
    print(len(content))
    save_to_minio(f"{current_user.username}_pepes",
                  zipfile.filename, content,
                  len(content))
    extract_pepes(current_user.username)
    return Response(status_code=200)


@app.get("/send_pepes/")
async def send_pepe_archive(current_user:
                            user = Depends(get_current_active_user)):
    archive = zip_pepes(current_user.username)
    logger.debug(f"{current_user.username} is getting pepes")
    if archive:
        return FileResponse(status_code=200,
                            path=f"./BASE/{current_user.username}_pepes/{archive}",
                            media_type="application/zip")
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="pepes could not be archived"
        )


@app.websocket("/eat_mems/")
async def eat_mems(websocket: WebSocket,
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
                                     current_user.username, "diff_hash")
    logger.debug("task enqued")
    result = eat_mem_task.AsyncResult(scrape_task.id)
    counter = 1
    while not result.ready():
        await async_sleep(counter)
        result = eat_mem_task.AsyncResult(scrape_task.id)
        logger.info(result.status)
        if counter <= 50:
            counter += 1
    state = result.status
    logger.info(state)
    await websocket.send_text(state)
    logger.debug("task status sent")
    return await websocket.close()


@app.get("/get_mem_names/", response_class=ORJSONResponse)
async def get_mem_names(current_user: user = Depends(get_current_user)):
    output = list_unsaved_files(current_user.username, verbose=True)
    return {"pics": output[f"{current_user.username}_main"]}


@app.post("/get_mem/")
async def get_mem(file_list: file_list, index: int = 0,
                  current_user: user = Depends(get_current_active_user)):
    try:
        output = get_from_minio(f"{current_user.username}_main",
                                file_list.files[index])
    except IndexError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="index greater than images list"
        )
    if output:
        if ".png" in file_list.files[index]:
            return Response(status_code=200,
                            content=output.read(), media_type="image/png")
        if ".jpg" in file_list.files[index]:
            return Response(status_code=200,
                            content=output.read(), media_type="image/jpg")
    raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="could not get file with this index"
        )


@app.get("/get_placeholder/")
async def get_placeholder():
    try:
        output = get_from_minio("static", "SORRY_NOTHING.jpg")
        return Response(status_code=200,
                        content=output.read(), media_type="image/jpg")
    except Exception as ex:
        logger.error(f"placeholder image retrieval failed with exception {ex}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="placeholder image could not be retrieved"
        )


@app.post("/token", response_class=ORJSONResponse)
async def login_for_access_token(form_data:
                                 OAuth2PasswordRequestForm = Depends()):
    logger.debug(f"token request recieved {form_data.username}")
    user = authenticate_user(form_data.username, form_data.password)
    logger.info(f"user {form_data.username} authenticated" if user else f"user {form_data.username} not authenticated")
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
    return {"access_token": access_token,
            "token_type": "bearer"}


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


@app.post("/users/create_user/", response_class=ORJSONResponse)
async def create_new_user(new_user: user_model):
    user_record = {"username": new_user.username,
                   "password": new_user.password,
                   "email": new_user.email,
                   "full_name": new_user.full_name if new_user.full_name else None}
    print(new_user.email, check_email(new_user.email))
    if not check_email(new_user.email):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="malformed email"
        )
    response = create_user(user_record)
    if response:
        return {"status": "success"}
    else:
        return {"status": "fail", "reason": "user exists"}


@app.get("/users/delete_me/")
async def delete_me(username: str, password: str,
                    current_user: user = Depends(get_current_active_user)):
    response = remove_user(username, password, current_user)
    if not response:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN
        )
    return Response(status_code=200)


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True, log_level="info")