import hmac
import binascii
import hashlib

def sign_top_request(params, secret, sign_method):
    # 第一步：检查参数是否已经排序
    keys = sorted(params.keys())

    # 第二步：把所有参数名和参数值串在一起
    query = ""
    if sign_method == "md5":
        query += secret
    for key in keys:
        value = params[key]
        if key and value:
            query += key + f"{value}"

    # 第三步：使用MD5/HMAC加密
    if sign_method == "hmac":
        bytes_ = encrypt_hmac(query, secret.encode())
    else:
        query += secret
        bytes_ = encrypt_md5(query)

    # 第四步：把二进制转化为大写的十六进制
    return byte2hex(bytes_)

def encrypt_hmac(data, secret):
    return hmac.new(secret, data.encode(), hashlib.sha256).digest()

def encrypt_md5(data):
    return hashlib.md5(data.encode()).digest()

def byte2hex(bytes_):
    return binascii.hexlify(bytes_).decode().upper()
