from json import load
from os import environ
# openssl rand -hex 32
try:
    with open('conf.json', 'r') as config_file:
        DEBUG = True
        secret_keys = load(config_file)

        # get yours! openssl rand -hex 32
        SECRET_KEY = secret_keys['SECRET_KEY']
        MINIO_CONNECTION = secret_keys['MINIO_CONNECTION']
        MINIO_ACCESS_KEY = secret_keys['MINIO_ACCESS_KEY']
        MINIO_SECRET_KEY = secret_keys['MINIO_SECRET_KEY']

except FileNotFoundError:

    #  TODO figure out why the server fails with debug set to false
    DEBUG = True

    SECRET_KEY = environ['SECRET_KEY']
    MINIO_CONNECTION = environ['MINIO_CONNECTION']
    MINIO_ACCESS_KEY = environ['MINIO_ACCESS_KEY']
    MINIO_SECRET_KEY = environ['MINIO_SECRET_KEY']

ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_MINUTES = 30

# getting program and resouce paths
glob_boards = ["a", "c", "g",
               "k", "m", "o",
               "p", "v", "vg",
               "vm", "vmg", "vr",
               "vrpg", "vst", "w",
               "vip", "qa", "cm",
               "lgbt", "3", "adv",
               "an", "asp",
               "biz", "cgi", "ck",
               "co", "diy", "fa",
               "fit", "gd", "his",
               "int", "jp", "lit",
               "mlp", "mu", "n",
               "news", "out", "pol",
               "qst", "sci", "sp",
               "tg", "toy", "trv",
               "tv", "vp", "wsg",
               "wsr", "x", "r9k",
               "b", "s4s"]
