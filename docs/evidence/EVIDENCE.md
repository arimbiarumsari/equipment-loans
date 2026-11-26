# AWS Evidence Checklist

Save screenshots in this folder with the file names below.

| # | File name | What it must show |
|---|---|---|
| 1 | 01-budget-before.png | Learner Lab page: remaining budget before starting |
| 2 | 02-ecr-repository.png | ECR repository `equipment-api` (private) |
| 3 | 03-security-group.png | `equipment-sg` inbound rules (22 My IP, 8080) |
| 4 | 04-ec2-running.png | EC2 instance in *running* state, with instance type |
| 5 | 05-iam-instance-profile.png | EC2 Security tab showing `LabInstanceProfile` |
| 6 | 06-docker-installed.png | Terminal: `docker --version` and `docker compose version` |
| 7 | 07-ecr-push.png | Terminal output of `./scripts/push-image.sh` |
| 8 | 08-ecr-image.png | ECR console showing image tag `latest` |
| 9 | 09-docker-ps.png | `docker ps` with two containers (api, db) |
| 10 | 10-curl-health.png | `curl http://<EC2-IP>:8080/health` returns status ok |
| 11 | 11-crud-test.png | Output of `./scripts/test-api.sh http://<EC2-IP>:8080` |
| 12 | 12-github-commits.png | GitHub commit history |
| 13 | 13-budget-after.png | Learner Lab remaining budget after finishing |

Blur or crop account ID, public IP and any secrets if the repo is public.
