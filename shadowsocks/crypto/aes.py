'''
提供AES系列加密解密
'''
import os

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import (Cipher, algorithms, modes)

from shadowsocks.crypto.utils import evp_bytestokey


class AESCipher:
    '''
    doc:
    https://cryptography.io/en/latest/hazmat/primitives/symmetric-encryption/
    '''

    # 不同加密方式对应的 block size
    SUPPORT_METHODS = {
        'aes-128-cfb': 16,
        'aes-192-cfb': 24,
        'aes-256-cfb': 32,
    }

    def __init__(self, method, password):
        self._method = method.lower()
        if self._method not in AESCipher.SUPPORT_METHODS:
            raise NotImplementedError

        self._bs = AESCipher.SUPPORT_METHODS[self._method]
        self._key = evp_bytestokey(password.encode(), self._bs)

        self._iv_len = 16
        self._encryptor = None
        self._decryptor = None
        self._first_package = True

    def __del__(self):
        '''gc时finalize'''
        if self._encryptor is not None:
            self._encryptor.finalize()
        if self._decryptor is not None:
            self._decryptor.finalize()

    def _make_cipher(self):
        cipher = Cipher(
            algorithms.AES(self._key),
            modes.CFB(self._iv),
            backend=default_backend()
        )
        return cipher

    def encrypt(self, data):
        if self._first_package:
            self._first_package = False
            self._iv = os.urandom(self._iv_len)
            self._encryptor = self._make_cipher().encryptor()
            return self._iv + self._encryptor.update(data)
        return self._encryptor.update(data)

    def decrypt(self, data):
        if self._first_package:
            self._first_package = False
            self._iv, data = data[:self._iv_len], data[self._iv_len:]
            self._decryptor = self._make_cipher().decryptor()
        return self._decryptor.update(data)
