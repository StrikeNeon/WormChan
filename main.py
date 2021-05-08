from datetime import timedelta
from typing import Optional
from fastapi import FastAPI, HTTPException, Depends, status, Response
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from loguru import logger
from WormChan import memeater, small_memeater

from minio_utils import (client, get_from_minio,
                         list_unsaved_files, purge_all_files,
                         purge_unsaved_files)

from user_utils import (user, token,
                        get_current_user, get_current_active_user,
                        create_access_token,
                        authenticate_user, create_user,
                        check_email, remove_user,
                        set_relevants)

from consts import glob_boards, ACCESS_TOKEN_EXPIRE_MINUTES
from workers import eat_mem_task
app = FastAPI()


class task(BaseModel):
    boards: list


class board(BaseModel):
    board: str


class file_list(BaseModel):
    files: list

# @app.get("/set_relevants/{task}")


@app.get("/full_purge/")
async def full_purge(current_user: user = Depends(get_current_active_user)):
    purge_all_files(current_user.username)
    return {"response": "all files purged"}


@app.get("/purge_unsaved/")
async def purge_unsaved(current_user: user = Depends(get_current_active_user)):
    purge_unsaved_files(current_user.username)
    return {"response": "unsaved files purged"}


@app.post("/eat_mem/")
async def eat_mem(board_task: board,
                  current_user: user = Depends(get_current_active_user)):
    small_eat_mem_task.delay(board_task.board, current_user.username)
    return {"response":
            f"board f'/{board}/', enqueued for user {current_user.username}"}


@app.post("/eat_mems/")
async def eat_memes(task: task, current_user:
                    user = Depends(get_current_active_user)):
    eat_mem_task.delay(task.boards, current_user.username)
    return {"response":
            f"boards {[f'/{board}/' for board in task.boards if board in glob_boards]},\
            enqueued for user {current_user.username}"}


@app.get("/get_mem_names/")
async def get_mem_names(current_user: user = Depends(get_current_user)):
    output = list_unsaved_files(current_user.username, verbose=True)
    return {"pics": output[f"{current_user.username}_main"]}


@app.post("/get_mem/")
async def get_mem(file_list: file_list, index: int = 0,
                  current_user: user = Depends(get_current_active_user)):
    try:
        output = get_from_minio(client, f"{current_user.username}_main", file_list.files[index])
    except IndexError:
        return Response(status_code=500)
    if output:
        if ".png" in file_list.files[index]:
            return Response(content=output.read(), media_type="image/png")
        if ".jpg" in file_list.files[index]:
            return Response(content=output.read(), media_type="image/jpg")
    return Response(status_code=404)



@app.get("/get_placeholder/")
async def get_placeholder():
    try:
        output = get_from_minio(client, "static", "SORRY_NOTHING.jpg")
    except Exception as ex:
        logger.error(f"placeholder image retrieval failed with exception {ex}")
    return Response(content=output.read(), media_type="image/jpg")


@app.post("/token", response_model=token)
async def login_for_access_token(form_data:
                                 OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
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
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/users/me/")
async def read_users_me(current_user: user = Depends(get_current_active_user)):
    return current_user


@app.post("/users/set_relevants/")
async def set_user_relevants(relevants: task,
                             current_user:
                             user = Depends(get_current_active_user)):
    print(current_user)
    set_relevants(current_user.username, relevants.boards)
    return current_user


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
        return {"response": f"user {username} has been successfully created"}
    else:
        return {"response": f"user {username} already exists"}


@app.get("/users/delete_me/")
async def delete_me(username: str, password: str,
                    current_user: user = Depends(get_current_active_user)):
    response = remove_user(username, password, current_user)
    if not response:
        return {"response": "there was an error deleting you"}
