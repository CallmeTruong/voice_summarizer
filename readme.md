# main.py

Rewrite of `main.py` for AWS-only runtime:

- Front-end: static assets on amplify, cognito, route53
- Backend: single Lambda for triggering S3 bucket (hash_table.json, raw_audio, segments, transcrips) and S3 vector
- Data: DynamoDB to store AudioFiles, memory_store, Users, voice_status_table
- AWS services: Amazon Transcribe
- Server: EC2 (t3.xlarge)

# Front-end

- React & Vite: `api\fe\src\data` : Building front-end with high effieciently
- UX/UI: `api\fe\src\components` : Design UX/UI and animation
- Aws Amplify: `api\fe\src\aws-config.js` : integrating services AWS into Front-end
- React Markdown: `api\fe\src\pages\AssistantPage.jsx`: Display the AI's response in Markdown format.

# Back-end & Worker
- Python `core`: for validating data and controlling model
- Celery & Redis: `worker`: The system queues additional processing tasks (background work) for audio decoding and vector generation
- Python `infrastructure`: to manage vector of sentences, index and store it

# Cloud & Infrastructure (Aws - Region `ap-southeast-2`)
- AWS Lambda: Serverless functions (thư mục `lambda_function`) that handle automated trigger events (such as a new audio file upload or a database trigger).
- Amazon S3: Stores the original audio files, transcript files, and Vector Spaces.
- Amazon DynamoDB: Stores metadata, processing statuses, and chat context memory (Memory Store).

Core Variables used by backend:
- Hash_table.json
- Raw_audio
- Segments
- Transcrips
- AudioFiles
- memory_store
- Users
- voice_status_table

# AI & Machine Learning
- Gemini 2.5 Flash: The primary LLM responsible for reasoning and conversing with users.
- Sentence Transformers (`paraphrase-multilingual-MiniLM-L12-v2`): Converts text into vectors (Embeddings) to facilitate Semantic Search.

# Deploy in AWS

1. Run `Infrastructure/setup_aws.py` to create entities in cloud services.
2. Create EC2 `t3.xlarge`: Amazon Linux
3. Run the code in the terminal in the following order.


# Download package for system
sudo dnf update -y
sudo dnf install -y git python3.11 python3.11-pip nginx docker awscli


# Reun Docker and Nginx:
sudo systemctl enable docker
sudo systemctl start docker
sudo systemctl enable nginx


# Give ec2-user using Docker:
sudo usermod -aG docker ec2-user
newgrp docker

# Create folder app and clone repository

sudo mkdir -p /opt/myapp
sudo chown ec2-user:ec2-user /opt/myapp
cd /opt/myapp
git clone https://github.com/CallmeTruong/voice_summarizer.git
cd /opt/myapp/voice_summarizer

# Create virtualenv and set-up Python package

python3.11 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip setuptools wheel uvicorn fastapi redis
pip install -r requirements.txt

# If there is error ('/temp'), running this parapraph:

mkdir -p ~/tmp ~/pip-cache
TMPDIR=$HOME/tmp TEMP=$HOME/tmp TMP=$HOME/tmp PIP_CACHE_DIR=$HOME/pip-cache \
pip install -r requirements.txt --no-cache-dir


# Run Redis by Docker

docker run -d \
  --name redis \
  --restart unless-stopped \
  -p 127.0.0.1:6379:6379 \
  -v redis_data:/data \
  redis:7 redis-server --appendonly yes

# Douple Check

docker ps
docker exec -it redis redis-cli ping

# PONG is successful.

# return home

cd /

# Create file env for service

sudo mkdir -p /etc/voice-summarizer
sudo nano /etc/voice-summarizer/app.env

dán nội dung từ .env vào

# Save CtrlO + enter + CtrlX

# Intergrate AWS policies for EC2

# AWS Console:

IAM → Roles → Create role
Trusted entity: AWS service
Use case: EC2
# Intergrate policy test:
AmazonS3FullAccess
AmazonDynamoDBFullAccess

# Intergate created role 
EC2 → Instances → chọn máy
Actions → Security → Modify IAM role



# Create server for running FastAPI on 24/24

sudo nano /etc/systemd/system/fastapi.service

# Input content

[Unit]
Description=FastAPI app
After=network.target docker.service
Requires=docker.service

[Service]
Type=simple
User=ec2-user
Group=ec2-user
WorkingDirectory=/opt/myapp/voice_summarizer
EnvironmentFile=/etc/voice-summarizer/app.env
ExecStart=/opt/myapp/voice_summarizer/.venv/bin/python -m uvicorn api.main:app --host 127.0.0.1 --port 8000
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target

Lưu CtrlO + enter + CtrlX

# Create service for running Celery on 24/24

sudo nano /etc/systemd/system/celery.service

# Input content

[Unit]
Description=Celery Worker
After=network.target docker.service
Requires=docker.service

[Service]
Type=simple
User=ec2-user
Group=ec2-user
WorkingDirectory=/opt/myapp/voice_summarizer
EnvironmentFile=/etc/voice-summarizer/app.env
ExecStart=/opt/myapp/voice_summarizer/.venv/bin/python -m celery -A worker.celery_app.celery_app worker --pool=prefork --loglevel=INFO
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target


# Turn on 2 service

sudo systemctl daemon-reload
sudo systemctl enable fastapi
sudo systemctl enable celery
sudo systemctl start fastapi
sudo systemctl start celery


# Nginx configuration

sudo nano /etc/nginx/conf.d/voice-summarizer.conf

# input contetn 

server {
    listen 80;
    server_name _;

    client_max_body_size 50M;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

Lưu

# Processing

sudo nginx -t
sudo systemctl restart nginx
sudo systemctl status nginx --no-pager -l


# Test on ec2 

curl http://127.0.0.1
curl http://127.0.0.1/health


# Security Group
Trong EC2 Security Group:
Mở HTTP port 80 source ALB đã setup hoặc all 0.0.0.0/0
