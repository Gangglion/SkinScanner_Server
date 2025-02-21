import hashlib
import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
import base64

KEY_FOLDER = "/SkinScanner/key"
KEY_FILE = "KeyIv.bin"

class Crypto:
    def calculate_file_hash(self, file_path, algorithm="sha256"):
        """저장된 모델 파일의 해시값(sha256 방식 사용) 리턴
        """
        try:
            hash_func = hashlib.new(algorithm)
            with open(file_path, "rb") as file:
                while chunk := file.read(8192):
                    hash_func.update(chunk)
            return hash_func.hexdigest()
        except Exception as e:
            return None
        
    def getAESKey(self):
        """저장된 키파일에서 Key 와 Iv 값 뽑아옴"""
        full_path = os.path.join(KEY_FOLDER, KEY_FILE)
        with open(full_path, "rb") as f:
            key = f.read(32)
            iv = f.read(16)
        print(f"Loaded AES Key : {key.hex()}")
        print(f"Loaded IV : {iv.hex()}")
        return key, iv
        
    def encryptAES(self, file_path):
        """해당 경로의 파일을 AES 로 암호화한 텍스트 리턴

        Args:
            file_path (string): 파일의 경로
        """
        key, iv = self.getAESKey()
        with open(file_path, 'rb') as f:
            plaintext = f.read()
        
        cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend)
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(plaintext) + encryptor.finalize()
        
        return ciphertext
        
    def encryptRSA(self, rsaKey, origin):
        """인자로 받아온 rsaKey 로 서버에 저장된 AES 키를 암호화해서 리턴
        
        Args:
            rsaKey (string) : 클라이언트의 RSA 공개키
            origin (string) : 암호화 할 원본 string
        """
        # 클라이언트의 RSA 공개키 (PEM 형식) 로드
        public_key = serialization.load_pem_public_key(rsaKey.encode())
        
        # origin 암호화
        encrypted_data = public_key.encrypt(
            origin,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA1()),
                algorithm=hashes.SHA1(),
                label=None
            )
        )
        # 암호화된 데이터를 Base64 로 인코딩하여 반환
        return base64.b64encode(encrypted_data).decode()
        
# if __name__ == "__main__":
#     crypto = Crypto()
#     crypto.getAESKey()