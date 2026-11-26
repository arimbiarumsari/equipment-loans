# Equipment Loans API (AWS Track B: EC2 + Docker + ECR)

Individual project, AWS Cloud Computing. A small REST API for managing equipment loans.

## Architecture

```
Client -> Internet -> Security Group (8080; SSH only from my IP)
       -> EC2 t3.small (Amazon Linux 2023, LabInstanceProfile)
            +-- docker compose
                 +-- api  (Flask + gunicorn, image pulled from ECR)
                 |     |
                 |     v  internal Docker network
                 +-- db   (postgres:16-alpine, volume pgdata, no public port)
```

| Component | Purpose |
|---|---|
| ECR `equipment-api` | Private registry for the API image |
| EC2 t3.small | Runs both containers with Docker Compose |
| Security Group `equipment-sg` | 22 from my IP, 8080 public |
| LabInstanceProfile (LabRole) | Lets EC2 pull from ECR without static credentials |

Architecture diagram: `docs/architecture.png`

## Entity

`equipment`: `id`, `name`, `category`, `status` (`available` | `borrowed`), `borrower`, `created_at`

## API

| Method | Endpoint | Description |
|---|---|---|
| GET | `/health` | Health and DB connectivity check |
| POST | `/equipment` | Create item (`name`, `category`) |
| GET | `/equipment` | List items |
| GET | `/equipment/{id}` | Item detail |
| PUT | `/equipment/{id}` | Update item / borrow (`status`, `borrower`) |
| DELETE | `/equipment/{id}` | Delete item |

## Run locally

```bash
cp .env.example .env      # edit DB_PASSWORD
docker compose up -d --build
./scripts/test-api.sh http://localhost:8080
```

## Deployment plan (AWS Learner Lab, us-east-1)

1. Start Learner Lab, open the AWS Console.
2. Create private ECR repository `equipment-api`.
3. Create Security Group `equipment-sg` (22 from My IP, 8080 from 0.0.0.0/0).
4. Launch EC2: t3.small, Amazon Linux 2023, 20 GB gp3, new key pair, `equipment-sg`, IAM instance profile `LabInstanceProfile`.
5. SSH in and install Docker, Compose plugin and git:
   ```bash
   sudo dnf install -y docker git
   sudo systemctl enable --now docker
   sudo usermod -aG docker ec2-user   # re-login afterwards
   sudo mkdir -p /usr/local/lib/docker/cli-plugins
   sudo curl -SL https://github.com/docker/compose/releases/latest/download/docker-compose-linux-x86_64 \
     -o /usr/local/lib/docker/cli-plugins/docker-compose
   sudo chmod +x /usr/local/lib/docker/cli-plugins/docker-compose
   ```
6. Clone this repo on EC2, create `.env` from `.env.example` (set account ID, image URI, password).
7. Build and push image: `./scripts/push-image.sh`
8. Deploy: `./scripts/deploy.sh`
9. Verify: `./scripts/test-api.sh http://<EC2-PUBLIC-IP>:8080`

## Cost control

Estimated total about 5 USD (EC2 ~120 active hours, 20 GB EBS, public IPv4, ECR under 1 GB), roughly 12% of the 40 USD budget (ceiling: 60%).
No NAT Gateway, ALB or RDS. EC2 is **stopped** after each work session. Public IP changes after every start.

## Security notes

- DB port is not published; only the `api` container can reach it.
- SSH restricted to my IP; no static AWS keys on the instance (instance profile only).
- `.env` and `*.pem` are git-ignored.

## Evidence

Screenshots and outputs are stored in `docs/evidence/`.
