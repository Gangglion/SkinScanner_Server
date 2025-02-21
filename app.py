from flask import Flask, request
import os
import io
from http import HTTPStatus
from ApiResponse import ApiResponse
from Crypto import Crypto
import subprocess
import click

app = Flask(__name__)

# 모델 경로 설정
MODEL_FOLDER = "/SkinScanner/model"
ENC_MODEL_NAME="model.tflite" # 암호화된 모델 파일명
ENCRYPTED_MODEL_PATH = os.path.join(MODEL_FOLDER, ENC_MODEL_NAME) # 암호화된 모델 파일 경로

@app.route('/')
def welcomeFlask():
    return "Hello Flask"

# 클라이언트로부터 RSA 공개키 받아옴
# request : { "pKey" : RSA 공개키 }
# response : { "data" : { "key" : key, "iv" : iv } } RSA 공개키로 암호화한 AES 키 전송
@app.route('/exchangeKey', methods=['POST'])
def exchange_key():
    params = request.get_json()
    try:
        publicRsaKey = params["pKey"]
        crypto = Crypto()
        if not publicRsaKey : # 받은 공개키가 없을때
            return ApiResponse.error("Request is empty")
        else:
            print(f"클라이언트에서 보내준 공개키 받음 : \n{publicRsaKey}") 
            file_path = os.path.join('/SkinScanner/key', 'KeyIv.bin')
            if not os.path.exists(file_path): # 저장된 AES 키 파일이 없을때
                return ApiResponse.error("Server Error. Key file does not exist", HTTPStatus.INTERNAL_SERVER_ERROR)
            with open(file_path, "rb") as f:
                key = f.read(32)
                iv = f.read(16)
            encryptedKey = crypto.encryptRSA(publicRsaKey, key)
            encryptedIv = crypto.encryptRSA(publicRsaKey, iv)
            return ApiResponse.success(data = { "key" : encryptedKey, "iv" : encryptedIv })
    except Exception as e:
        print(f"exchange_key Exception :: {e}")
        return ApiResponse.error("Exception!!", HTTPStatus.INTERNAL_SERVER_ERROR)

# 클라이언트에서 보내진 file hash 와 서버의 file hash 검사
# request : { "value" : fileHash }
# response : { "needUpdate" : Bool }
@app.route('/checkFile', methods=['POST'])
def file_hash_check():
    params = request.get_json()
    try:
        clientHash = params["value"]
        crypto = Crypto()
        modelHash = crypto.calculate_file_hash(file_path = ENCRYPTED_MODEL_PATH)
        print(f"Hash value of existing file : {modelHash}")
        if not clientHash :
            return ApiResponse.error(message = "Request is empty")
        if not modelHash:
            return ApiResponse.error(message = "Failed to get Model")
        if clientHash == modelHash :
            return ApiResponse.success(data = {"needUpdate" : False})
        else:
            return ApiResponse.success(data = {"needUpdate" : True})
    except Exception as e:
        return ApiResponse.error()

# "flask upload-file bucket-name" 명령어를 통해 model/model.tflite 을 암호화 한 뒤 amazon S3 에 전송
@app.cli.command("upload-file")
@click.argument("bucket_name")
def run_upload_file(bucket_name):
    print("Uploading...")
    result = subprocess.run(["python", "upload_file.py", bucket_name], capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print(f"에러가 발생했습니다 : {result.stderr}")

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=6700)
