from user_utils import hash_collection
from PIL import Image
import imagehash
from io import BytesIO


class method_error(Exception):
    pass

def hamming_distance(hash_1, hash_2):
    #  Calculated Hamming distance of two pictures
    assert len(hash_1) == len(hash_2)
    return sum([char_1 != char_2 for char_1, char_2 in zip(hash_1, hash_2)])


def compute_image_hash(content, method, hash_size=8):
    if method not in ["avg_hash", "p_hash", "diff_hash"]:
        hash_dict = {"avg_hash": imagehash.average_hash(Image.open(BytesIO(content)), hash_size),
                     "p_hash": imagehash.phash(Image.open(BytesIO(content)), hash_size),
                     "diff_hash": imagehash.dhash(Image.open(BytesIO(content)), hash_size),
                     }
        image_hash = hash_dict.get(method)
        return image_hash
    else:
        raise method_error
