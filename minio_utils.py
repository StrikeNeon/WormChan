from minio import Minio, error
from os import remove
from os.path import basename
from io import BytesIO
from zipfile import ZipFile
from consts import MINIO_CONNECTION, MINIO_ACCESS_KEY, MINIO_SECRET_KEY
from PIL import Image
import imagehash

client = Minio(
        MINIO_CONNECTION,
        access_key=MINIO_ACCESS_KEY,
        secret_key=MINIO_SECRET_KEY,
        secure=False
    )


def save_to_minio(bucket, filename, data, file_size):
    try:
        client.put_object(
                bucket, filename, BytesIO(data), file_size,
                )
    except error.S3Error:
        return None


def get_from_minio(bucketname, filename):
    try:
        return client.get_object(bucketname, filename)
    except error.S3Error:
        return None


def compute_image_hash(bucketname, filename):
    content = get_from_minio(bucketname, filename)
    image_hash = imagehash.average_hash(Image.open(BytesIO(content.read())))
    return image_hash


def remove_from_minio(client, bucket, filename):
    try:
        client.remove_object(bucket, filename)
    except error.S3Error:
        return None


def list_all_files(username: str, verbose: bool = False):
    output = {}
    buckets = [f"{username}_main", f"{username}_saved", f"{username}_pepes"]
    for bucket in buckets:
        if not verbose:
            output[bucket] = len([file for file
                                  in client.list_objects(bucket)])
        else:
            output[bucket] = [file.object_name for file
                              in client.list_objects(bucket)]
    return output


def list_unsaved_files(username: str, verbose: bool = False):
    output = {}
    if not verbose:
        output[f"{username}_main"] = len([file for file
                                          in
                                          client.list_objects(f"{username}_main")])
    else:
        output[f"{username}_main"] = [file.object_name for file
                                      in client.list_objects(f"{username}_main")]
    return output


def list_saved_files(username: str, verbose: bool = False):
    output = {}
    if not verbose:
        output[f"{username}_saved"] = len([file for file
                                           in
                                           client.list_objects(f"{username}_saved")])
    else:
        output[f"{username}_saved"] = [file.object_name for file
                                       in client.list_objects(f"{username}_saved")]
    return output


def list_pepes(username: str, verbose: bool = False):
    output = {}
    if not verbose:
        output[f"{username}_pepes"] = len([file for file
                                           in
                                           client.list_objects(f"{username}_pepes")])
    else:
        output[f"{username}_pepes"] = [file.object_name for file
                                       in client.list_objects(f"{username}_pepes")]
    return output


def purge_all_files(username: str):
    buckets = [f"{username}_main", f"{username}_saved"]
    for bucket in buckets:
        for file in client.list_objects(bucket):
            client.remove_object(bucket, file.object_name)
    return {"message": "all files purged"}


def purge_unsaved_files(username: str):
    bucket = f"{username}_main"
    for file in client.list_objects(bucket):
        client.remove_object(bucket, file.object_name)
    return {"message": "unsaved purged"}


def purge_saved_files(username: str):
    bucket = f"{username}_saved"
    for file in client.list_objects(bucket):
        client.remove_object(bucket, file.object_name)
    return {"message": "saved files purged"}


def purge_pepes(username: str):
    bucket = f"{username}_pepes"
    for file in client.list_objects(bucket):
        client.remove_object(bucket, file.object_name)
    return {"message": "all pepes purged"}


def extract_saved_files(username: str):
    bucket = f"{username}_saved"
    with ZipFile(f"./BASE/{bucket}/{username}_arch_saved_pics.zip", 'r') as zip_file:
        zip_file.extractall(f"./BASE/{bucket}")
    remove(f"./BASE/{bucket}/{username}_arch_saved_pics.zip")
    return {"message": "saved files extracted"}


def extract_pepes(username: str):
    bucket = f"{username}_pepes"
    with ZipFile(f"./BASE/{bucket}/{username}_arch_pepes.zip", 'r') as zip_file:
        zip_file.extractall(f"./BASE/{bucket}")
    remove(f"./BASE/{bucket}/{username}_arch_pepes.zip")
    return {"message": "pepes extracted"}


def zip_saved_files(username: str):
    bucket = f"{username}_saved"
    file_paths = list_saved_files(username, verbose=True)
    if len(file_paths.get(bucket)) != 0:
        path_list = file_paths.get(bucket)
        with ZipFile(f'./BASE/{bucket}/{username}_arch_saved_pics.zip', 'w') as zip_file:
            # writing each file one by one
            while len(path_list) != 0:
                file = path_list.pop()
                if ".zip" not in file:
                    file_path = f"./BASE/{bucket}/{file}"
                    zip_file.write(file_path, basename(file_path))
                    remove(file_path)
        return f'{username}_arch_saved_pics.zip'


def zip_pepes(username: str):
    bucket = f"{username}_pepes"
    file_paths = list_pepes(username, verbose=True)
    if len(file_paths.get(bucket)) != 0:
        path_list = file_paths.get(bucket)
        with ZipFile(f'./BASE/{bucket}/{username}_arch_pepes.zip', 'w') as zip_file:
            # writing each file one by one
            while len(path_list) != 0:
                file = path_list.pop()
                if ".zip" not in file:
                    file_path = f"./BASE/{bucket}/{file}"
                    zip_file.write(file_path, basename(file_path))
                    remove(file_path)
        return f'{username}_arch_pepes.zip'
