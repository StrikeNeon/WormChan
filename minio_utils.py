from minio import Minio, error
from io import BytesIO

client = Minio(
        "127.0.0.1:9000",
        access_key="minioadmin",
        secret_key="minioadmin",
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
        return {"message": "file not found"}


def list_all_files(verbose=False):
    output = {}
    buckets = client.list_buckets()
    for bucket in buckets:
        if not verbose:
            output[bucket.name] = len([file for file
                                       in client.list_objects(bucket.name)])
        else:
            output[bucket.name] = [file.object_name for file
                                   in client.list_objects(bucket.name)]
    return output


def list_unsaved_files(verbose=False):
    output = {}
    buckets = client.list_buckets()
    for bucket in buckets:
        if "saved" not in bucket.name:
            if not verbose:
                output[bucket.name] = len([file for file
                                           in
                                           client.list_objects(bucket.name)])
            else:
                output[bucket.name] = [file.object_name for file
                                       in client.list_objects(bucket.name)]
    return output


def list_saved_files(verbose=False):
    output = {}
    buckets = client.list_buckets()
    for bucket in buckets:
        if "saved" in bucket.name:
            if not verbose:
                output[bucket.name] = len([file for file
                                           in
                                           client.list_objects(bucket.name)])
            else:
                output[bucket.name] = [file.object_name for file
                                       in client.list_objects(bucket.name)]
    return output


def purge_all_files():
    buckets = client.list_buckets()
    for bucket in buckets:
        for file in client.list_objects(bucket.name):
            client.remove_object(bucket.name, file.object_name)
    return {"message": "all files purged"}


def purge_unsaved_files():
    buckets = client.list_buckets()
    for bucket in buckets:
        if "saved" not in bucket.name and bucket.name != "PEPE":
            for file in client.list_objects(bucket.name):
                client.remove_object(bucket.name, file.object_name)
    return {"message": "unsaved purged"}


def purge_saved_files():
    buckets = client.list_buckets()
    for bucket in buckets:
        if "saved" in bucket.name and bucket.name != "PEPE":
            for file in client.list_objects(bucket.name):
                client.remove_object(bucket.name, file.object_name)
    return {"message": "saved files purged"}


def purge_pepes():
    for file in client.list_objects("PEPE"):
        client.remove_object("PEPE", file.object_name)
    return {"message": "all pepes purged"}


# print(list_all_files(verbose = True))
# print(purge_all_files())
