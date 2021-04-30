from json import load
from os import environ
# openssl rand -hex 32
try:
    with open('conf.json', 'r') as f:
        DEBUG = True
        secret_keys = load(f)

        # get yours! openssl rand -hex 32
        SECRET_KEY = secret_keys['SECRET_KEY']

except FileNotFoundError:

    #  TODO figure out why the server fails with debug set to false
    DEBUG = True

    SECRET_KEY = environ['SECRET_KEY']

ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_MINUTES = 30

# getting program and resouce paths
pic_folder = 'pics'
pdf_folder = 'pdfs'
swf_folder = 'swf'
webm_folder = 'webms'
gif_folder = 'gifs'
SATAN_folder = '666'

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


folder_setup = ['pics', 'pdfs', 'swf', 'webms', 'gifs', '666']
