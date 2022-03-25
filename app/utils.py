from fastapi import HTTPException, status
from passlib.context import CryptContext
from typing import Union
from PIL import Image

import PIL
import sys
import io

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
MAX_IMAGE_DIM = 1024, 1024
MAX_FILE_SIZE = 2831200 + sys.getsizeof(bytes())  # Maximum file size 2.7MB with bytes object size included
ALLOWED_IMAGE_TYPES = ('PNG', 'JPEG', 'JPG')


def pwd_hash(password: str):
    return pwd_context.hash(password)


def verify(plain_password: str, hashed_password: str):  # Verify if password matches with hash in DB
    return pwd_context.verify(plain_password, hashed_password)


def remove_none_from_dict(data: dict) -> dict:
    filtered = {key: value for key, value in data.items() if value is not None}
    return filtered


def verify_image(file: bytes) -> Union[bytes, HTTPException]:  # Verify if image is suitable to upload
    ex_unsupported = HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                                   detail="Unsupported file or media type")

    try:
        im = Image.open(io.BytesIO(file))
    except PIL.UnidentifiedImageError:
        return ex_unsupported
    except Exception:
        return ex_unsupported

    if im.format not in ALLOWED_IMAGE_TYPES:
        return ex_unsupported

    im_size = sys.getsizeof(file)
    if im_size > MAX_FILE_SIZE:
        return HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="Image too large")

    if im.size[0] > MAX_IMAGE_DIM[0] or im.size[0] > MAX_IMAGE_DIM[1]:
        im.thumbnail(MAX_IMAGE_DIM, Image.ANTIALIAS)
        img_bytes = io.BytesIO()
        im.save(img_bytes, format=im.format)
        return img_bytes.getvalue()

    return file
