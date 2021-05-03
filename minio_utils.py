from minio import Minio, error
from io import BytesIO
from consts import MINIO_CONNECTION, MINIO_ACCESS_KEY, MINIO_SECRET_KEY

client = Minio(
        MINIO_CONNECTION,
        access_key=MINIO_ACCESS_KEY,
        secret_key=MINIO_SECRET_KEY,
        secure=False
    )


def save_to_minio(client, bucket, filename, data, file_size):
    client.put_object(
             bucket, filename, BytesIO(data), file_size,
            )


def get_from_minio(client, bucketname, filename):
    try:
        return client.get_object(bucketname, filename)
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
