#!/usr/bin/env bash
# Run on the EC2 instance: login to ECR, pull latest image, start the stack.
set -euo pipefail
cd "$(dirname "$0")/.."

set -a; source .env; set +a
REGISTRY="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"

aws ecr get-login-password --region "$AWS_REGION" \
  | docker login --username AWS --password-stdin "$REGISTRY"

docker compose pull api
docker compose up -d --no-build
docker compose ps
