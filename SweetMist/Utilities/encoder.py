from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Hash import SHA256
from Crypto.Util.Padding import pad, unpad
import base64

def generate_key(passphrase):
    hash_func = SHA256.new()
    filtered_passphrase = passphrase.replace(";", "")  # Remove semicolons
    hash_func.update(filtered_passphrase.encode())
    return hash_func.digest()  # 32 bytes (256 bits)

def encrypt_data(data, key):
    iv = get_random_bytes(AES.block_size)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    padded_data = pad(data.encode(), AES.block_size)
    encrypted_data = cipher.encrypt(padded_data)
    return iv + encrypted_data

def decrypt_data(encrypted_data):
    passphrase = 'divyamshah'
    key = generate_key(passphrase)
    iv = encrypted_data[:AES.block_size]
    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted_data = cipher.decrypt(encrypted_data[AES.block_size:])
    unpadded_data = unpad(decrypted_data, AES.block_size)
    return unpadded_data.decode()

def encode_base64(data):
    return base64.b64encode(data).decode().replace(";", "").replace("=", "")

def decode_base64(data):
    # Add padding back if necessary before decoding
    padded_data = data + '=' * (len(data) % 4)
    return decrypt_data(base64.b64decode(padded_data))

# Example usage
# passphrase = 'divyamshah'
# key = generate_key(passphrase)

# data = 'cUGLjUu3qV3NXlo7Dv2Hk/IFG/AqNLVUFSUUK6mDWRF5y4ec2X7bN2llCbq4ReCw'

# encrypted_data = encrypt_data(data, key)
# encoded_encrypted_data = encode_base64(encrypted_data)
# print("Encrypted data:", encoded_encrypted_data)

# decoded_encrypted_data = decode_base64(data)
# decrypted_data = decrypt_data(decoded_encrypted_data, key)
# print("Decrypted data:", decoded_encrypted_data)


# class AESCipher:
#     def __init__(self, key, key_is_hex=True):
#         self.size = len(key)

#         if key_is_hex:
#             self.key = bytes.fromhex(key)
#         else:
#             self.key = bytes(key, "UTF-8")

#     def encrypt(self, raw, padData=True):

#         raw = pad(raw)
#         iv = self.key[:16]
#         cipher = AES.new(self.key, AES.MODE_CBC, iv)

#         return base64.b64encode(cipher.encrypt(raw))

#     def decrypt(self, enc):
#         enc = base64.b64decode(enc)

#         iv = self.key[:16]
#         cipher = AES.new(self.key, AES.MODE_CBC, iv)
#         d = cipher.decrypt(enc)

#         return unpad(d).decode("utf8")
