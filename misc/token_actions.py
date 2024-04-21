import base64

from misc.encode_sha256 import encode_to_sha256

def gen_login_token(login: str, password: str):
    encode_pass = encode_to_sha256(password)
    encode_login = base64.b64encode(login.encode()).decode()

    return f"{encode_login}|||{encode_pass}"


def check_valid_token(login: str, encode_password: str, token: str):
    encode_login = base64.b64encode(login.encode()).decode()
    
    return f"{encode_login}|||{encode_password}" == token


def get_login_from_token(token: str):
    encode_login, encode_password = token.split("|||")
    decode_login = base64.b64decode(encode_login.encode()).decode()

    return decode_login