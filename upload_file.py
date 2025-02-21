import os
import io
from Crypto import Crypto
import boto3
import sys
from boto3.s3.transfer import S3Transfer
from botocore.exceptions import NoCredentialsError

# 모델 경로 설정
MODEL_FOLDER = "model"
MODEL_NAME = "model.tflite"
MODEL_PATH = os.path.join(MODEL_FOLDER, MODEL_NAME)
ENC_MODEL_NAME="encrypted_model.tflite" # 암호화된 모델 파일명
ENCRYPTED_MODEL_PATH = os.path.join(MODEL_FOLDER, ENC_MODEL_NAME) # 암호화된 모델 파일 경로

if len(sys.argv) > 2:
    print("Error : Bucket name is required")
    sys.exit(1)
    
bucket_name = sys.argv[1]

class ProcessPercentage(object):
    def __init__(self, filename):
        self.filename = filename
        self.size = float(self._get_file_size())
        self.bytes_uploaded = 0
    
    def _get_file_size(self):
        """returns the file size"""
        return os.path.getsize(self.filename)
    
    def __call__(self, bytes_amount):
        """업로드 되는 동안 주기적으로 호출되어 퍼센트를 알려줌"""
        self.bytes_uploaded += bytes_amount
        progress = float(self.bytes_uploaded) / self.size * 100
        sys.stdout.write(f"upload {self.filename} : {progress:.2f}%")
        sys.stdout.flush()
        
# S3로 파일 업로드
def upload_to_s3(filename, object_name=None):
    """S3 로 파일 업로드"""
    if object_name is None:
        object_name = filename
    s3_client = boto3.client('s3')
    transfer = S3Transfer(s3_client)
    
    try:
        print("Starting file Upload")
        transfer.upload_file(filename, bucket_name, object_name, callback = ProcessPercentage(filename))
        print("\nUpload completed")
    except NoCredentialsError:
        print("Credentials not available")
    except Exception as e:
        print(f"Error uploading file : {e}")
        
if __name__ == "__main__":
    try:
        if not os.path.exists(MODEL_PATH):
            print("File is not Found. Check file path or name")
        else:
            # tflite 모델 파일 암호화
            crypto = Crypto()
            encrypted_file = io.BytesIO(crypto.encryptAES(file_path = MODEL_PATH))
            encrypted_file.seek(0)
            
            # 암호화한 tflite 모델 파일 model 폴더에 저장
            with open(ENCRYPTED_MODEL_PATH, 'wb') as f:
                f.write(encrypted_file.read())
            
            # 암호화환 파일 amazon S3 에 업로드
            upload_to_s3(filename = ENCRYPTED_MODEL_PATH)
            
            
    except Exception as e:
        print(f"UnExpectedError : {e}")