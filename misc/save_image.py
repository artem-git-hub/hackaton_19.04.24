import os

import base64
import random


def save_image_to_disk(image: str, team_name: str) -> str:
    # Создаем директорию для изображений, если ее еще нет
    image_dir = f"images/{team_name}"
    os.makedirs(image_dir, exist_ok=True)

    header, base64_data = image.split(',')
    image_type = header.split(';')[0].split('/')[-1]


    # Генерируем уникальное имя для изображения
    image_path = os.path.join(image_dir, "image_" + str(random.randint(1, 100000)) + f".{image_type}" )


    # Сохраняем изображение на диск
    with open(image_path, "wb") as buffer:

        image_data = base64.decodebytes(base64_data.encode())\

        buffer.write(image_data)

    return image_path
