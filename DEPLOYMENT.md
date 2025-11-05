# AdoptIQ Production Deployment Guide

## Prerequisites

- Docker & Docker Compose installed
- Node.js 20+ (for smart contract deployment)
- Domain name configured with DNS
- SSL certificate (Let's Encrypt recommended)
- RPC provider accounts (Alchemy, Infura, or QuickNode)

## Step 1: Environment Configuration

### Backend Environment

Create `/backend/.env` from the example:

```bash
cp backend/.env.example backend/.env
```

Configure the following critical variables:

```env
SECRET_KEY=your-production-secret-key-here
DEBUG=False
ALLOWED_HOSTS=your-domain.com,www.your-domain.com

DB_NAME=adoptiq_prod
DB_USER=adoptiq
DB_PASSWORD=strong-password-here
DB_HOST=postgres
DB_PORT=5432

REDIS_URL=redis://redis:6379/0

JWT_SECRET_KEY=different-jwt-secret-here

ETHEREUM_RPC_URL=https://eth-mainnet.g.alchemy.com/v2/YOUR_API_KEY
POLYGON_RPC_URL=https://polygon-mainnet.g.alchemy.com/v2/YOUR_API_KEY

AI_AUDIT_API_URL=https://your-ai-service.com
AI_AUDIT_API_KEY=your-ai-api-key

CORS_ORIGINS=https://your-domain.com
```

### Frontend Environment

Create environment variables for the build:

```bash
export VITE_API_BASE_URL=https://your-domain.com
export VITE_WS_BASE_URL=wss://your-domain.com
```

### Contracts Environment

Create `/contracts/.env`:

```bash
cp contracts/.env.example contracts/.env
```

Configure:

```env
PRIVATE_KEY=your-deployer-private-key
ETHEREUM_RPC_URL=https://eth-mainnet.g.alchemy.com/v2/YOUR_API_KEY
POLYGON_RPC_URL=https://polygon-mainnet.g.alchemy.com/v2/YOUR_API_KEY
ETHERSCAN_API_KEY=your-etherscan-api-key
```

## Step 2: Deploy Smart Contracts

```bash
cd contracts
npm install
npx hardhat compile

npx hardhat run scripts/deploy.js --network ethereum

npx hardhat verify --network ethereum BILLING_CONTRACT_ADDRESS
npx hardhat verify --network ethereum CERTIFICATE_REGISTRY_ADDRESS
```

Save the deployed contract addresses and update `backend/.env`:

```env
BILLING_CONTRACT_ADDRESS=0xYourBillingContractAddress
CERTIFICATE_REGISTRY_ADDRESS=0xYourCertificateRegistryAddress
```

## Step 3: SSL Certificate Setup

### Using Let's Encrypt (Recommended)

```bash
docker run -it --rm --name certbot \
  -v "/etc/letsencrypt:/etc/letsencrypt" \
  -v "/var/lib/letsencrypt:/var/lib/letsencrypt" \
  certbot/certbot certonly --standalone \
  -d your-domain.com -d www.your-domain.com \
  --email your-email@example.com \
  --agree-tos --no-eff-email
```

Copy certificates:

```bash
mkdir -p infrastructure/nginx/ssl
sudo cp /etc/letsencrypt/live/your-domain.com/fullchain.pem infrastructure/nginx/ssl/
sudo cp /etc/letsencrypt/live/your-domain.com/privkey.pem infrastructure/nginx/ssl/
```

### Update Nginx Configuration

Edit `infrastructure/nginx/conf.d/default.conf` to enable HTTPS.

## Step 4: Build and Start Services

```bash
docker-compose -f docker-compose.prod.yml up -d --build
```

## Step 5: Initialize Database

```bash
docker-compose -f docker-compose.prod.yml exec backend python manage.py migrate

docker-compose -f docker-compose.prod.yml exec backend python manage.py createsuperuser
```

## Step 6: Collect Static Files

```bash
docker-compose -f docker-compose.prod.yml exec backend python manage.py collectstatic --noinput
```

## Step 7: Verify Deployment

Check service health:

```bash
curl https://your-domain.com/health/
curl https://your-domain.com/ready/
curl https://your-domain.com/alive/
```

Expected responses:

```json
{
  "status": "healthy",
  "checks": {
    "database": "healthy",
    "cache": "healthy"
  }
}
```

Check logs:

```bash
docker-compose -f docker-compose.prod.yml logs -f backend

docker-compose -f docker-compose.prod.yml logs -f celery_worker

docker-compose -f docker-compose.prod.yml logs -f nginx
```

## Step 8: Post-Deployment Tasks

### Configure Token Support in Billing Contract

```bash
cast send BILLING_CONTRACT_ADDRESS \
  "setSupportedToken(address,bool)" \
  0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48 true \
  --rpc-url $ETHEREUM_RPC_URL \
  --private-key $PRIVATE_KEY
```

### Set Up Monitoring

1. Configure error tracking (Sentry)
2. Set up log aggregation
3. Configure uptime monitoring
4. Set up alerts for critical metrics

### Backup Strategy

1. Database backups (daily):
   ```bash
   docker-compose -f docker-compose.prod.yml exec postgres pg_dump -U adoptiq adoptiq_prod > backup.sql
   ```

2. Upload to S3 or similar storage
3. Test restoration procedure

## Scaling Considerations

### Horizontal Scaling

For high traffic, scale individual services:

```bash
docker-compose -f docker-compose.prod.yml up -d --scale celery_worker=10
```

### Database Optimization

1. Enable connection pooling
2. Add read replicas
3. Configure proper indexes

### Redis Optimization

1. Enable persistence
2. Configure max memory
3. Set up Redis Cluster for high availability

## Security Checklist

- [ ] All secrets in environment variables
- [ ] HTTPS enforced (HSTS enabled)
- [ ] CORS properly configured
- [ ] Rate limiting active
- [ ] Database access restricted to internal network
- [ ] Regular security updates
- [ ] Monitoring and alerting configured
- [ ] Backups tested and automated
- [ ] Smart contracts audited
- [ ] API keys rotated regularly

## Troubleshooting

### Service Won't Start

Check logs:
```bash
docker-compose -f docker-compose.prod.yml logs backend
```

### Database Connection Issues

Verify connection:
```bash
docker-compose -f docker-compose.prod.yml exec backend python manage.py dbshell
```

### WebSocket Not Working

Check Daphne service:
```bash
docker-compose -f docker-compose.prod.yml logs daphne
```

Verify Nginx WebSocket configuration.

### High Memory Usage

Monitor containers:
```bash
docker stats
```

Adjust worker counts and memory limits in `docker-compose.prod.yml`.

## Rollback Procedure

1. Stop services:
   ```bash
   docker-compose -f docker-compose.prod.yml down
   ```

2. Restore previous images:
   ```bash
   docker-compose -f docker-compose.prod.yml pull
   ```

3. Restore database backup:
   ```bash
   docker-compose -f docker-compose.prod.yml exec -T postgres psql -U adoptiq < backup.sql
   ```

4. Restart services:
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

## Support

For issues:
- GitHub Issues: https://github.com/yourusername/AdoptIQ/issues
- Documentation: Check README.md
- Health endpoint: https://your-domain.com/health/
