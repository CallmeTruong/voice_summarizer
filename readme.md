# Voice Summarizer

An AWS-based application for audio ingestion, transcription, semantic retrieval, and AI-assisted summarization.

This project combines a React front end, a Python backend, background workers, and multiple AWS services to process uploaded audio, generate transcripts, build vector representations, and serve AI responses in a user-facing interface.

---

## Overview

The system is designed around an AWS-first architecture:

- **Front end** serves the user interface and renders assistant responses in Markdown.
- **Backend API** handles application logic and orchestration.
- **Background workers** process heavier tasks such as audio decoding and vector generation.
- **AWS services** handle storage, metadata, triggers, and transcription.
- **LLM + embeddings** power reasoning and semantic search.

---

## Key Capabilities

- Upload and process audio files
- Store raw audio, transcript artifacts, and derived data in AWS
- Run automated triggers with AWS Lambda
- Generate transcripts with Amazon Transcribe
- Store metadata and processing status in DynamoDB
- Build embeddings for semantic search
- Render AI responses in Markdown on the front end
- Run asynchronous background jobs with Celery and Redis

---

## Architecture

### High-level Components

- **Frontend**: React + Vite, integrated with AWS Amplify and Cognito
- **Backend**: Python application served with FastAPI/Uvicorn
- **Worker Layer**: Celery + Redis for background task execution
- **Cloud Services**:
  - Amazon S3 for audio, transcript files, and vector-related artifacts
  - Amazon DynamoDB for metadata, memory, users, and processing status
  - AWS Lambda for automated event-driven processing
  - Amazon Transcribe for speech-to-text
- **Runtime Host**: EC2 (`t3.xlarge` in the current deployment notes)
- **AI Layer**:
  - Gemini 2.5 Flash for conversation and reasoning
  - Sentence Transformers (`paraphrase-multilingual-MiniLM-L12-v2`) for embeddings

### Processing Flow

1. A user uploads audio.
2. Files and processing artifacts are stored in S3.
3. Lambda and backend services trigger the processing pipeline.
4. Amazon Transcribe generates transcripts.
5. Celery workers process additional tasks such as decoding and vector generation.
6. Metadata and status are written to DynamoDB.
7. The application uses embeddings and the LLM to support search and assistant responses.

---

## Tech Stack

### Frontend

- React
- Vite
- AWS Amplify
- Amazon Cognito
- React Markdown

### Backend

- Python
- FastAPI
- Uvicorn
- Celery
- Redis

### AI / ML

- Gemini 2.5 Flash
- Sentence Transformers

### Infrastructure

- AWS Lambda
- Amazon S3
- Amazon DynamoDB
- Amazon Transcribe
- EC2
- Nginx
- Docker

---

## Project Structure

Below is a **recommended README structure section** based on the folders referenced in the current project notes. Update it to match your real repository tree.

```text
voice_summarizer/
├── api/
│   ├── main.py                  # FastAPI entrypoint
│   └── fe/                      # Frontend application
│       └── src/
│           ├── aws-config.js    # AWS frontend integration
│           ├── components/      # UI components and animations
│           ├── data/            # Frontend data modules
│           └── pages/
│               └── AssistantPage.jsx
├── core/                        # Validation and model control logic
├── infrastructure/              # Vector storage, indexing, and infrastructure helpers
│   └── setup_aws.py             # AWS bootstrap/setup script
├── worker/                      # Celery worker and background jobs
├── requirements.txt
└── README.md
```

### How to generate your actual folder tree

If you want the README to reflect the real repository structure, run one of these commands from the project root and paste the result into the `Project Structure` section.

```bash
tree -L 3
```

If `tree` is not installed:

```bash
find . -maxdepth 3 -type d | sort
```

A good practice is to keep only the most important folders in the README. Do not dump the full tree if it is too large.

---

## AWS Resources

### Storage and Processing Artifacts

The current notes mention the following core resources and data groups:

- `hash_table.json`
- `raw_audio`
- `segments`
- `transcrips`
- `AudioFiles`
- `memory_store`
- `Users`
- `voice_status_table`

### Suggested Clarification

In the actual project README, separate these into clearer categories:

- **S3 objects / prefixes**: `hash_table.json`, `raw_audio`, `segments`, `transcripts`
- **DynamoDB tables**: `AudioFiles`, `memory_store`, `Users`, `voice_status_table`

Also fix naming for consistency:

- Use `transcripts` instead of `transcrips`
- Use lowercase or PascalCase consistently, depending on whether the item is an S3 prefix, a file, or a DynamoDB table

---

## Prerequisites

Before deployment, make sure you have:

- AWS account with appropriate IAM permissions
- An EC2 instance running Amazon Linux
- Python 3.11
- Docker
- Nginx
- AWS CLI
- Git

---

## Deployment on AWS

### 1. Provision AWS Resources

Create the required AWS resources using the infrastructure bootstrap script:

```bash
python Infrastructure/setup_aws.py
```

### 2. Prepare the EC2 Instance

Install system packages:

```bash
sudo dnf update -y
sudo dnf install -y git python3.11 python3.11-pip nginx docker awscli
```

Enable Docker and Nginx:

```bash
sudo systemctl enable docker
sudo systemctl start docker
sudo systemctl enable nginx
```

Allow `ec2-user` to use Docker:

```bash
sudo usermod -aG docker ec2-user
newgrp docker
```

### 3. Clone the Repository

```bash
sudo mkdir -p /opt/myapp
sudo chown ec2-user:ec2-user /opt/myapp
cd /opt/myapp
git clone https://github.com/CallmeTruong/voice_summarizer.git
cd /opt/myapp/voice_summarizer
```

### 4. Create the Python Environment

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip setuptools wheel uvicorn fastapi redis
pip install -r requirements.txt
```

If you hit a temporary directory or cache-related installation issue:

```bash
mkdir -p ~/tmp ~/pip-cache
TMPDIR=$HOME/tmp TEMP=$HOME/tmp TMP=$HOME/tmp PIP_CACHE_DIR=$HOME/pip-cache \
pip install -r requirements.txt --no-cache-dir
```

### 5. Run Redis with Docker

```bash
docker run -d \
  --name redis \
  --restart unless-stopped \
  -p 127.0.0.1:6379:6379 \
  -v redis_data:/data \
  redis:7 redis-server --appendonly yes
```

Verify Redis:

```bash
docker ps
docker exec -it redis redis-cli ping
```

Expected result:

```text
PONG
```

### 6. Configure Environment Variables

```bash
sudo mkdir -p /etc/voice-summarizer
sudo nano /etc/voice-summarizer/app.env
```

Copy the content from your project `.env` file into `/etc/voice-summarizer/app.env`.

### 7. Attach IAM Role to EC2

Attach an IAM role to the instance with the required AWS permissions.

The current notes mention:

- `AmazonS3FullAccess`
- `AmazonDynamoDBFullAccess`

For production, consider replacing broad managed policies with **least-privilege custom policies**.

### 8. Create the FastAPI systemd Service

Create `/etc/systemd/system/fastapi.service`:

```ini
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
```

### 9. Create the Celery systemd Service

Create `/etc/systemd/system/celery.service`:

```ini
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
```

Enable and start the services:

```bash
sudo systemctl daemon-reload
sudo systemctl enable fastapi
sudo systemctl enable celery
sudo systemctl start fastapi
sudo systemctl start celery
```

### 10. Configure Nginx

Create `/etc/nginx/conf.d/voice-summarizer.conf`:

```nginx
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
```

Validate and restart Nginx:

```bash
sudo nginx -t
sudo systemctl restart nginx
sudo systemctl status nginx --no-pager -l
```

### 11. Health Checks

```bash
curl http://127.0.0.1
curl http://127.0.0.1/health
```

### 12. Security Group

Open **HTTP port 80** in the EC2 Security Group.

Recommended:

- Allow traffic only from the Application Load Balancer (ALB), if used

Less restrictive option:

- Allow `0.0.0.0/0` for public HTTP access

---

## Frontend Notes

The current project notes reference the following frontend locations:

- `api/fe/src/data`
- `api/fe/src/components`
- `api/fe/src/aws-config.js`
- `api/fe/src/pages/AssistantPage.jsx`

Suggested README improvement:

Add a dedicated frontend section with:

- how to install dependencies
- how to run the frontend locally
- required environment variables
- build command
- deployment target (Amplify, S3, CloudFront, etc.)

Example placeholder:

```bash
cd api/fe
npm install
npm run dev
```

---

## Recommended Additional Sections

These sections are commonly added to make a project easier to understand:

### 1. Features
Describe the product from a user perspective.

### 2. Architecture Diagram
A simple diagram helps readers understand the flow much faster.

### 3. Environment Variables
List all required variables and describe what each one does.

Example:

```env
AWS_REGION=
S3_BUCKET_NAME=
DYNAMODB_TABLE_AUDIOFILES=
REDIS_URL=
GEMINI_API_KEY=
```

### 4. Local Development
Explain how to run backend, frontend, and workers locally.

### 5. API Reference
Document core endpoints such as:

- `GET /health`
- `POST /upload`
- `POST /chat`
- `GET /audio/{id}`

### 6. Troubleshooting
Capture known issues such as:

- package installation problems
- Redis container issues
- missing IAM permissions
- service startup failures

### 7. Security Notes
Mention IAM scope, secrets handling, and network exposure.

### 8. Roadmap
Useful if the project is still evolving.

---

## Suggested README Order

A cleaner README usually follows this order:

1. Project name
2. One-paragraph summary
3. Features
4. Architecture / system overview
5. Tech stack
6. Project structure
7. Setup and local development
8. Deployment
9. Environment variables
10. API reference
11. Troubleshooting
12. License

---

## Notes on Consistency

To keep the README clean and professional:

- Use **English only** throughout the document
- Use one naming style consistently
- Keep headings short and descriptive
- Separate infrastructure, application logic, and deployment notes
- Move long shell instructions into clearly labeled code blocks
- Avoid mixing folder descriptions, runtime architecture, and deployment commands in the same section

---

## License

Add your license here if the repository is intended to be shared publicly.

For example:

```text
MIT License
```

