import boto3
from botocore.exceptions import ClientError
import os
import time
from dotenv import load_dotenv

load_dotenv(".env")
REGION = os.getenv("REGION")
bucket = os.getenv("BUCKET_NAME")
path = f"{os.getenv('RAW_BUCKET_FOLDER')}/"

s3 = boto3.client("s3", REGION)


def is_file_uploaded(key: str) -> bool:
    try:
        s3.head_object(Bucket=bucket, Key=key)
        return True
    except ClientError as e:
        error_code = e.response.get("Error", {}).get("Code")
        if error_code in ["404", "NoSuchKey", "NotFound"]:
            return False
        raise


def wait_until_uploaded(
    key: str,
    interval_seconds: int = 10,
    timeout_seconds: int = 36000,
):
    start_time = time.time()
    key = f"{path}{key}"
    print(key)
    while True:
        try:
            if is_file_uploaded(key):
                print(f"File đã upload xong: s3://{bucket}/{key}")
                return True

            elapsed = time.time() - start_time
            if elapsed >= timeout_seconds:
                print("Hết thời gian chờ, file vẫn chưa thấy trên S3")
                return False

            print(f"Chưa có file, đợi {interval_seconds}s rồi check lại...")
            time.sleep(interval_seconds)

        except Exception as e:
            print(f"Lỗi khi kiểm tra S3: {e}")
            return False


if __name__ == "__main__":
    bucket = os.getenv("BUCKET_NAME")
    print("REGION =", REGION)
    print("BUCKET_NAME =", bucket)
    print("RAW_BUCKET_FOLDER =", os.getenv("RAW_BUCKET_FOLDER"))
    wait_until_uploaded(
        key="eec92ed5882ab11a5345c4ceadba1e52e477528021f9f5261d230540e27c596a",
        interval_seconds=5,
        timeout_seconds=120,
    )
 