from asyncio import trsock
import os

import base64
import random
from PIL import Image
from io import BytesIO



import hashlib


def save_image_to_disk(image: str, team_name: str) -> str:
    # Создаем директорию для изображений, если ее еще нет
    image_dir = f"images/{team_name}"
    os.makedirs(image_dir, exist_ok=True)

    header, base64_data = image.split(',')
    image_type = header.split(';')[0].split('/')[-1]

    # image_data = base64.b64decode(base64_data)

    # image_data = Image.open(BytesIO(image.encode()))


    # Генерируем уникальное имя для изображения
    image_path = os.path.join(image_dir, "image_" + str(random.randint(1, 10000)) + f".{image_type}" )


    # Сохраняем изображение на диск
    with open(image_path, "wb") as buffer:

        image_data = base64.decodebytes(base64_data.encode())

        # image_data = base64.b64decode(image)

        buffer.write(image_data)

    return image_path



def encode_to_sha256(input_string):
    # Преобразование строки в байтовый объект (требуется для хеширования)
    input_bytes = input_string.encode('utf-8')
    
    # Вычисление хеша SHA256
    sha256_hash = hashlib.sha256(input_bytes)
    
    # Получение шестнадцатеричного представления хеша
    sha256_hex = sha256_hash.hexdigest()
    
    return sha256_hex


def gen_login_token(login: str, password: str):
    encode_pass = encode_to_sha256(password)
    encode_login = base64.b64encode(login.encode()).decode()

    return f"{encode_login}|||{encode_pass}"


def check_valid_token(login: str, encode_password: str, token: str):
    encode_login = base64.b64encode(login.encode()).decode()
    
    return f"{encode_login}|||{encode_password}" == token


def get_login_from_roken(token: str):
    encode_login, encode_password = token.split("|||")
    decode_login = base64.b64decode(encode_login.encode()).decode()

    return decode_login