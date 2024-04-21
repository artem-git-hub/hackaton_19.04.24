import hashlib


def encode_to_sha256(input_string):
    # Преобразование строки в байтовый объект (требуется для хеширования)
    input_bytes = input_string.encode('utf-8')
    
    # Вычисление хеша SHA256
    sha256_hash = hashlib.sha256(input_bytes)
    
    # Получение шестнадцатеричного представления хеша
    sha256_hex = sha256_hash.hexdigest()
    
    return sha256_hex
