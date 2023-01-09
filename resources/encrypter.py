from base64 import b64encode, b64decode
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes


def encrypt_text(text_decripted):
    data = bytes(text_decripted, encoding='utf8')
    key = get_random_bytes(16)
    cipher = AES.new(key, AES.MODE_CBC)
    ct_bytes = cipher.encrypt(pad(data, AES.block_size))
    iv = b64encode(cipher.iv).decode('utf-8')
    ct = b64encode(ct_bytes).decode('utf-8')
    text_encripted = ct
    return text_encripted, iv, key


def decrypt_text(text_encripted, iv, key):
    iv, ct = b64decode(iv), b64decode(text_encripted)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    pt = unpad(cipher.decrypt(ct), AES.block_size)
    text_decripted = str(pt, 'utf-8')
    return text_decripted
