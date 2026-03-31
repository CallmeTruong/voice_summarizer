import boto3
import json
import os
import zipfile
import io
from dotenv import load_dotenv

load_dotenv(".env")

REGION          = os.getenv("REGION")
BUCKET_NAME     = os.getenv("BUCKET_NAME")
VECTOR_BUCKET   = os.getenv("VECTOR_BUCKET")
INDEX_NAME      = os.getenv("INDEX_NAME")
HISTORY_TABLE   = os.getenv("HISTORY_TABLE")
USER_TABLE      = os.getenv("USER_TABLE")
MEMORY_TABLE    = os.getenv("MEMORY_TABLE")
TABLE_NAME      = os.getenv("TABLE_NAME")
SEGMENTS_PREFIX = os.getenv("SEGMENTS_PREFIX")
RAW_BUCKET_FOLDER  = os.getenv("RAW_BUCKET_FOLDER")
TEXT_BUCKET_FOLDER = os.getenv("TEXT_BUCKET_FOLDER")
EMB_DIM         = int(os.getenv("EMB_DIM"))

s3        = boto3.client("s3",        region_name=REGION)
dynamodb  = boto3.client("dynamodb",  region_name=REGION)
iam       = boto3.client("iam",       region_name=REGION)
s3vectors = boto3.client("s3vectors", region_name=REGION)
sts       = boto3.client("sts",       region_name=REGION)
lam       = boto3.client("lambda",    region_name=REGION)
cognito   = boto3.client("cognito-idp", region_name=REGION)

ACCOUNT_ID = sts.get_caller_identity()["Account"]


# ─────────────────────────────────────────
# 1. S3 BUCKET
# ─────────────────────────────────────────
def create_s3_bucket():
    print(f"\n[S3] Tạo bucket: {BUCKET_NAME}")
    try:
        if REGION == "us-east-1":
            s3.create_bucket(Bucket=BUCKET_NAME)
        else:
            s3.create_bucket(
                Bucket=BUCKET_NAME,
                CreateBucketConfiguration={"LocationConstraint": REGION}
            )
        print(f"  ✓ Tạo bucket thành công")
    except s3.exceptions.BucketAlreadyOwnedByYou:
        print(f"  ~ Bucket đã tồn tại")
    except Exception as e:
        print(f"  ✗ Lỗi: {e}")

    for prefix in [RAW_BUCKET_FOLDER, TEXT_BUCKET_FOLDER, SEGMENTS_PREFIX]:
        try:
            s3.put_object(Bucket=BUCKET_NAME, Key=f"{prefix}/")
            print(f"  ✓ Tạo prefix: {prefix}/")
        except Exception as e:
            print(f"  ✗ Lỗi tạo prefix {prefix}: {e}")

    try:
        s3.put_public_access_block(
            Bucket=BUCKET_NAME,
            PublicAccessBlockConfiguration={
                "BlockPublicAcls":       True,
                "IgnorePublicAcls":      True,
                "BlockPublicPolicy":     True,
                "RestrictPublicBuckets": True,
            }
        )
        print(f"  ✓ Block public access")
    except Exception as e:
        print(f"  ✗ Lỗi: {e}")

    try:
        s3.put_bucket_cors(
            Bucket=BUCKET_NAME,
            CORSConfiguration={
                "CORSRules": [{
                    "AllowedHeaders": ["*"],
                    "AllowedMethods": ["GET", "PUT", "POST", "DELETE", "HEAD"],
                    "AllowedOrigins": ["*"],
                    "ExposeHeaders":  ["ETag"],
                    "MaxAgeSeconds":  3000,
                }]
            }
        )
        print(f"  ✓ Cấu hình CORS")
    except Exception as e:
        print(f"  ✗ Lỗi: {e}")


# ─────────────────────────────────────────
# 2. S3 VECTOR BUCKET + INDEX
# ─────────────────────────────────────────
def create_vector_bucket():
    print(f"\n[S3Vectors] Tạo vector bucket: {VECTOR_BUCKET}")
    try:
        s3vectors.create_vector_bucket(vectorBucketName=VECTOR_BUCKET)
        print(f"  ✓ Tạo vector bucket thành công")
    except Exception as e:
        if "already exists" in str(e).lower():
            print(f"  ~ Vector bucket đã tồn tại")
        else:
            print(f"  ✗ Lỗi: {e}")

    print(f"[S3Vectors] Tạo index: {INDEX_NAME} (dim={EMB_DIM})")
    try:
        s3vectors.create_index(
            vectorBucketName=VECTOR_BUCKET,
            indexName=INDEX_NAME,
            dataType="float32",
            dimension=EMB_DIM,
            distanceMetric="cosine",
        )
        print(f"  ✓ Tạo index thành công")
    except Exception as e:
        if "already exists" in str(e).lower():
            print(f"  ~ Index đã tồn tại")
        else:
            print(f"  ✗ Lỗi: {e}")


# ─────────────────────────────────────────
# 3. DYNAMODB TABLES
# ─────────────────────────────────────────
def create_dynamodb_table(table_name, pk, sk=None):
    print(f"\n[DynamoDB] Tạo table: {table_name}")
    key_schema = [{"AttributeName": pk, "KeyType": "HASH"}]
    attr_defs  = [{"AttributeName": pk, "AttributeType": "S"}]
    if sk:
        key_schema.append({"AttributeName": sk, "KeyType": "RANGE"})
        attr_defs.append( {"AttributeName": sk, "AttributeType": "S"})
    try:
        dynamodb.create_table(
            TableName=table_name,
            KeySchema=key_schema,
            AttributeDefinitions=attr_defs,
            BillingMode="PAY_PER_REQUEST",
        )
        waiter = boto3.client("dynamodb", region_name=REGION).get_waiter("table_exists")
        waiter.wait(TableName=table_name)
        print(f"  ✓ Tạo table thành công")
    except dynamodb.exceptions.ResourceInUseException:
        print(f"  ~ Table đã tồn tại")
    except Exception as e:
        print(f"  ✗ Lỗi: {e}")

def create_all_dynamodb():
    create_dynamodb_table(HISTORY_TABLE, pk="raw_id")
    create_dynamodb_table(USER_TABLE,    pk="user_id", sk="raw_id")
    create_dynamodb_table(MEMORY_TABLE,  pk="raw_id")
    # Users table cho Cognito trigger
    create_dynamodb_table("Users", pk="user_id")


# ─────────────────────────────────────────
# 4. IAM ROLE CHO LAMBDA
# ─────────────────────────────────────────
def create_lambda_role(role_name: str, policy_doc: dict) -> str:
    print(f"\n[IAM] Tạo Lambda role: {role_name}")

    trust_policy = json.dumps({
        "Version": "2012-10-17",
        "Statement": [{
            "Effect":    "Allow",
            "Principal": {"Service": "lambda.amazonaws.com"},
            "Action":    "sts:AssumeRole"
        }]
    })

    try:
        res = iam.create_role(
            RoleName=role_name,
            AssumeRolePolicyDocument=trust_policy,
            Description=f"Role cho Lambda {role_name}"
        )
        role_arn = res["Role"]["Arn"]
        print(f"  ✓ Tạo role thành công: {role_arn}")
    except iam.exceptions.EntityAlreadyExistsException:
        role_arn = f"arn:aws:iam::{ACCOUNT_ID}:role/{role_name}"
        print(f"  ~ Role đã tồn tại: {role_arn}")

    # Gắn AWSLambdaBasicExecutionRole (CloudWatch logs)
    try:
        iam.attach_role_policy(
            RoleName=role_name,
            PolicyArn="arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
        )
        print(f"  ✓ Gắn AWSLambdaBasicExecutionRole")
    except Exception as e:
        print(f"  ~ {e}")

    # Gắn inline policy
    try:
        iam.put_role_policy(
            RoleName=role_name,
            PolicyName=f"{role_name}-policy",
            PolicyDocument=json.dumps(policy_doc)
        )
        print(f"  ✓ Gắn inline policy")
    except Exception as e:
        print(f"  ✗ Lỗi gắn policy: {e}")

    # Chờ role propagate
    import time
    time.sleep(10)
    return role_arn


# ─────────────────────────────────────────
# 5. DEPLOY LAMBDA FUNCTIONS
# ─────────────────────────────────────────
def zip_lambda(file_path: str) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.write(file_path, "lambda_function.py")
    return buf.getvalue()


def deploy_lambda(function_name, file_path, role_arn, env_vars, timeout=60, memory=256):
    print(f"\n[Lambda] Deploy: {function_name}")
    zip_bytes = zip_lambda(file_path)

    config = dict(
        FunctionName=function_name,
        Runtime="python3.11",
        Role=role_arn,
        Handler="lambda_function.lambda_handler",
        Code={"ZipFile": zip_bytes},
        Timeout=timeout,
        MemorySize=memory,
        Environment={"Variables": env_vars},
    )

    try:
        lam.create_function(**config)
        print(f"  ✓ Tạo Lambda thành công")
    except lam.exceptions.ResourceConflictException:
        # Đã tồn tại → update code + config
        lam.update_function_code(
            FunctionName=function_name,
            ZipFile=zip_bytes,
        )
        lam.update_function_configuration(
            FunctionName=function_name,
            Role=role_arn,
            Timeout=timeout,
            MemorySize=memory,
            Environment={"Variables": env_vars},
        )
        print(f"  ~ Cập nhật Lambda thành công")
    except Exception as e:
        print(f"  ✗ Lỗi: {e}")
        return

    # Chờ Lambda active
    waiter = lam.get_waiter("function_active")
    waiter.wait(FunctionName=function_name)
    print(f"  ✓ Lambda active")


def setup_audio2text_lambda():
    role_name = "lambda-audio2text-role"
    policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid":    "S3Read",
                "Effect": "Allow",
                "Action": ["s3:GetObject", "s3:HeadObject"],
                "Resource": f"arn:aws:s3:::{BUCKET_NAME}/*"
            },
            {
                "Sid":    "TranscribeStart",
                "Effect": "Allow",
                "Action": [
                    "transcribe:StartTranscriptionJob",
                    "transcribe:GetTranscriptionJob",
                ],
                "Resource": "*"
            },
            {
                "Sid":    "TranscribeOutputS3",
                "Effect": "Allow",
                "Action": ["s3:PutObject"],
                "Resource": f"arn:aws:s3:::{BUCKET_NAME}/{TEXT_BUCKET_FOLDER}/*"
            },
        ]
    }
    role_arn = create_lambda_role(role_name, policy)

    deploy_lambda(
        function_name="audio2text",
        file_path="api/lambda_function/audio2text_lambda.py",
        role_arn=role_arn,
        env_vars={
            "OUTPUT_BUCKET":    BUCKET_NAME,
            "OUTPUT_PREFIX":    f"{TEXT_BUCKET_FOLDER}/",
            "HASH_TABLE_KEY":   f"{TABLE_NAME}.json",
        },
        timeout=60,
        memory=256,
    )

    # Gắn S3 trigger cho Lambda
    setup_s3_trigger("audio2text")


def setup_user_creation_lambda():
    role_name = "lambda-user-creation-role"
    policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid":    "DynamoDBWrite",
                "Effect": "Allow",
                "Action": ["dynamodb:PutItem", "dynamodb:GetItem"],
                "Resource": f"arn:aws:dynamodb:{REGION}:{ACCOUNT_ID}:table/Users"
            },
        ]
    }
    role_arn = create_lambda_role(role_name, policy)

    deploy_lambda(
        function_name="user-creation-db",
        file_path="api/lambda_function/user_creation_db.py",
        role_arn=role_arn,
        env_vars={"DYNAMODB_REGION": REGION},
        timeout=30,
        memory=128,
    )

    print(f"\n  → Vào Cognito Console → User Pool → Triggers → Post confirmation")
    print(f"  → Chọn Lambda: user-creation-db")


# ─────────────────────────────────────────
# 6. S3 TRIGGER → LAMBDA
# ─────────────────────────────────────────
def setup_s3_trigger(function_name: str):
    print(f"\n[S3 Trigger] Gắn trigger s3://{BUCKET_NAME}/{RAW_BUCKET_FOLDER}/ → {function_name}")

    lambda_arn = f"arn:aws:lambda:{REGION}:{ACCOUNT_ID}:function:{function_name}"

    # Cấp quyền cho S3 invoke Lambda
    try:
        lam.add_permission(
            FunctionName=function_name,
            StatementId="s3-invoke-permission",
            Action="lambda:InvokeFunction",
            Principal="s3.amazonaws.com",
            SourceArn=f"arn:aws:s3:::{BUCKET_NAME}",
            SourceAccount=ACCOUNT_ID,
        )
        print(f"  ✓ Cấp quyền S3 invoke Lambda")
    except lam.exceptions.ResourceConflictException:
        print(f"  ~ Permission đã tồn tại")
    except Exception as e:
        print(f"  ✗ Lỗi: {e}")

    # Gắn S3 event notification
    try:
        s3.put_bucket_notification_configuration(
            Bucket=BUCKET_NAME,
            NotificationConfiguration={
                "LambdaFunctionConfigurations": [{
                    "LambdaFunctionArn": lambda_arn,
                    "Events":            ["s3:ObjectCreated:*"],
                    "Filter": {
                        "Key": {
                            "FilterRules": [{
                                "Name":  "prefix",
                                "Value": f"{RAW_BUCKET_FOLDER}/"
                            }]
                        }
                    }
                }]
            }
        )
        print(f"  ✓ Gắn S3 event notification thành công")
    except Exception as e:
        print(f"  ✗ Lỗi: {e}")


# ─────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 50)
    print("VOICE SUMMARIZER — AWS SETUP")
    print("=" * 50)
    print(f"Region:  {REGION}")
    print(f"Account: {ACCOUNT_ID}")

    create_s3_bucket()
    create_vector_bucket()
    create_all_dynamodb()
    setup_audio2text_lambda()
    setup_user_creation_lambda()

    print("\n" + "=" * 50)
    print("✓ SETUP HOÀN TẤT")
    print("=" * 50)
    print("\nCác bước thủ công còn lại:")
    print("1. Cognito → User Pool → Triggers → Post confirmation → chọn Lambda: user-creation-db")