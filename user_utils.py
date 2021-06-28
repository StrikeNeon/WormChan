from pymongo import MongoClient
from datetime import datetime, timedelta
from pydantic import BaseModel
from typing import Optional
from fastapi import Depends, HTTPException, status, Query, WebSocket
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.exc import UnknownHashError
from passlib.context import CryptContext
from consts import ALGORITHM, SECRET_KEY
from loguru import logger
import re


client = MongoClient('127.0.0.1:27017')

db = client['pic_random']
collection = db['faces']

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class token(BaseModel):
    access_token: str
    token_type: str


class token_data(BaseModel):
    username: Optional[str] = None


class user(BaseModel):
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    relevants: Optional[list] = None
    disabled: Optional[bool] = False


class user_in_db(user):
    hashed_password: str


def get_user(username: str):
    response = collection.find_one({'username': username})
    if response:
        return user_in_db(**response)


async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        user_token = token_data(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(username=user_token.username)
    if user is None:
        raise credentials_exception
    return user


async def parse_user_query(websocket: WebSocket,
                           user_token: Optional[str] = Query(None)):
    logger.debug(user_token)
    if user_token is None:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
    try:
        current_user = await get_current_user(user_token)
    except AttributeError:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
    try:
        if get_current_active_user(current_user):
            return current_user
    except HTTPException:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)


async def get_current_active_user(current_user:
                                  user = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def authenticate_user(username: str, password: str):
    user = get_user(username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_password(plain_password: str, hashed_password: str):
    try:
        verification = pwd_context.verify(plain_password, hashed_password)
        return verification
    except UnknownHashError:
        raise HTTPException(status_code=403,
                            detail="password could not be identified")


def get_password_hash(password: str):
    return pwd_context.hash(password)


def create_user(user_dict: dict):
    response = collection.find_one({'username': user_dict["username"]})
    if response:
        return False
    user_record = {
        "username": user_dict["username"],
        "email": user_dict["email"],
        "hashed_password": get_password_hash(user_dict["password"]),
        "full_name": user_dict["full_name"] if
        user_dict.get("full_name") else None,
        "disabled": False}
    post_id = collection.insert_one(user_record).inserted_id
    logger.info(f"new user {user_record['username']}, \
                            email: {user_dict['email']}, \
                            saved in collection under id {post_id}")
    return True


def add_imhash_to_db(hash_str: str, filename: str, username: str, method: str, distant: bool):
    hash_collection = db['pic_hashes']
    hashes = hash_collection.find_one({"username": username})
    if not hashes:
        if distant:
            hash_collection.insert_one({"username": username, "avg_hash_db": [{filename: hash_str}]})
        else:
            hash_collection.insert_one({"username": username, f"{method}_db": [{filename: hash_str}]})
        return True
    #  this is where the search algo should be
    #  TODO similar hash search algo
    if distant:
        try:
            hash_list = hashes["avg_hash_db"]
        except KeyError:
            hash_collection.update_one({"username": username}, {"$set": {"avg_hash_db": [{filename: hash_str}]}})
            return True
        if hash_str not in hash_list:
            hash_list.append({filename: hash_str})
            hash_collection.update_one({"username": username}, {"$set": {"avg_hash_db": hash_list}})
            return True
        else:
            return
    try:
        hash_list = hashes[f"{method}_db"]
    except KeyError:
        hash_collection.update_one({"username": username}, {"$set": {f"{method}_db": [{filename: hash_str}]}})
        return True
    if hash_str not in hash_list:
        hash_list.append({filename: hash_str})
        hash_collection.update_one({"username": username}, {"$set": {f"{method}_db": hash_list}})
        return True
    else:
        return


def unban_user(username: str):
    collection.find_one_and_update({'username': username},
                                   {"$set": {'disabled': False}})
    logger.info(f"user {username} was unbanned")


def ban_user(username: str):
    collection.find_one_and_update({'username': username},
                                   {"$set": {'disabled': True}})
    logger.info(f"user {username} was banned")


def set_relevants(username: str, relevants: list):
    collection.find_one_and_update({'username': username},
                                   {"$set": {'relevants': relevants}})
    logger.info(f"user {username} relevants set")


def remove_user(username: str, password: str, current_user: user):
    if current_user.username == username:
        response = authenticate_user(username, password)
        if not response:
            return False
        else:
            collection.remove({"username": username})
            logger.info(f"user {username} has been removed")
        return True
    else:
        return False


def check_email(email: str):
    regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w+$'
    return re.search(regex, email)
