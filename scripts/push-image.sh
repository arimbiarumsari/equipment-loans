#!/usr/bin/env bash
# Build the API image and push it to ECR (run on laptop or EC2).
set -euo pipefail
cd "$(dirname "$0")/.."

set -a; source .env; set +a
REGISTRY="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"

aws ecr get-login-password --region "$AWS_REGION" \
  | docker login --username AWS --password-stdin "$REGISTRY"

# linux/amd64 because EC2 t3.small is x86_64 (matters on Apple Silicon laptops)
docker build --platform linux/amd64 -t equipment-api ./app
docker tag equipment-api:latest "${REGISTRY}/equipment-api:latest"
docker push "${REGISTRY}/equipment-api:latest"
