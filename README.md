# AdoptIQ - Web3 Adoption Platform

AdoptIQ is a comprehensive Web3 adoption platform that enables blockchain projects to run measurable adoption campaigns, obtain verifiable smart contract audits, and manage crypto-native subscriptions.

## Features

- **Mission System**: Create and manage on-chain adoption campaigns with automatic verification
- **Smart Contract Audits**: AI-powered security audits with on-chain certificates
- **Crypto-Native Billing**: Decentralized subscription management with multi-token support
- **Real-Time Analytics**: Comprehensive dashboards with WebSocket updates
- **Fraud Detection**: Advanced algorithms to prevent bot and Sybil attacks
- **Multi-Chain Support**: Ethereum, Polygon, and expandable to other EVM chains

## Tech Stack

### Backend
- Django 5.0 + Django REST Framework
- PostgreSQL 16
- Redis 7
- Celery for background tasks
- Channels for WebSocket support
- Web3.py for blockchain interaction

### Frontend
- SvelteKit 2.0
- TailwindCSS 3.4
- Ethers.js 6.0
- Chart.js for visualizations
- Axios for API calls

### Smart Contracts
- Solidity 0.8.20
- OpenZeppelin Contracts
- Hardhat for development
- Multi-chain deployment support

### Infrastructure
- Docker & Docker Compose
- Nginx reverse proxy
- GitHub Actions CI/CD
- PostgreSQL with extensions

## Quick Start

### Prerequisites
- Docker and Docker Compose
- Node.js 20+
- Python 3.11+
- MetaMask or compatible wallet

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/AdoptIQ.git
cd AdoptIQ
```

2. Set up environment variables:
```bash
cp backend/.env.example backend/.env
cp contracts/.env.example contracts/.env
```

3. Start services with Docker Compose:
```bash
docker-compose up -d
```

4. Run database migrations:
```bash
docker-compose exec backend python manage.py migrate
```

5. Create superuser:
```bash
docker-compose exec backend python manage.py createsuperuser
```

6. Access the application:
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000/api
- Admin Panel: http://localhost:8000/admin

### Local Development

#### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

#### Frontend
```bash
cd frontend
npm install
npm run dev
```

#### Smart Contracts
```bash
cd contracts
npm install
npx hardhat compile
npx hardhat test
```

## Deployment

### Smart Contracts
```bash
cd contracts
npx hardhat run scripts/deploy.js --network ethereum
```

### Backend & Frontend
```bash
docker-compose -f docker-compose.prod.yml up -d
```

## Architecture

```
AdoptIQ/
├── backend/          # Django application
│   ├── adoptiq/      # Project settings
│   ├── apps/         # Django apps
│   │   ├── core/     # Authentication & utilities
│   │   ├── users/    # User management
│   │   ├── missions/ # Mission system
│   │   ├── audits/   # Audit system
│   │   ├── billing/  # Subscription management
│   │   └── analytics/# Analytics & reporting
│   └── manage.py
├── frontend/         # SvelteKit application
│   ├── src/
│   │   ├── lib/      # Utilities & stores
│   │   ├── routes/   # Pages
│   │   └── components/
│   └── package.json
├── contracts/        # Solidity smart contracts
│   ├── BillingContract.sol
│   ├── CertificateRegistry.sol
│   └── scripts/
├── infrastructure/   # Docker & deployment
│   ├── nginx/
│   └── docker/
└── database/         # Database scripts
```

## API Documentation

API documentation is available at: http://localhost:8000/api/docs/

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT License - see LICENSE file for details

## Support

For issues and questions:
- GitHub Issues: https://github.com/yourusername/AdoptIQ/issues
- Documentation: https://docs.adoptiq.com
- Email: support@adoptiq.com
