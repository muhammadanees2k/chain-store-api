# ChainStore E-Commerce API

A high-performance, production-ready REST API engineered for a modern e-commerce platform. Built with Django REST Framework, featuring a dual-gateway financial architecture that supports traditional Fiat payments (Stripe) and decentralized Web3 payments (MetaMask/Ethereum).

***Live API Documentation:*** http://54.253.53.16/api/docs/

***Live Landing Page:*** http://54.253.53.16

## Architecture & Tech Stack
TECHNOLOGY STACK

1. API Framework
   Technology: Django 4.x / Django REST Framework (DRF)
   Purpose: Handles core business logic, API endpoints, and data serialization.

2. Database
   Technology: MySQL 8.0
   Purpose: Stores relational data with ACID-compliant transactions.

3. Authentication
   Technology: Djoser / SimpleJWT
   Purpose: Provides secure, stateless JWT-based authentication.

4. Fiat Payments
   Technology: Stripe Checkout & Webhooks
   Purpose: Processes credit card payments securely and handles payment events.

5. Crypto Payments
   Technology: Web3.py / Sepolia RPC
   Purpose: Verifies blockchain transactions without relying on third-party trust.

6. Media Storage
   Technology: Cloudinary
   Purpose: Stores and delivers optimized images and media files.

7. API Documentation
   Technology: DRF Spectacular (Swagger/OpenAPI)
   Purpose: Generates interactive API documentation.

8. Server
   Technology: Gunicorn
   Purpose: Runs the Django application in production.

9. Infrastructure
   Technology: Docker / AWS EC2 (Free Tier)
   Purpose: Containerized deployment and cloud hosting with memory optimization.

SUMMARY

Frontend → API Requests
        →
Django + DRF
        →
MySQL Database
        →
Authentication (JWT)
        →
Payments (Stripe + Crypto)
        →
Cloudinary Media Storage
        →
Gunicorn Server
        →
Docker Containers
        →
AWS EC2 Hosting

## Key Features

### E-Commerce Core

**Product Catalog:** Full CRUD for Products, Collections, and optimized image delivery via Cloudinary.

**Smart Cart System:** UUID-based carts with atomic quantity updates and dynamic price calculation.

**Order Engine:** Transaction-safe order creation (cart → order conversion) using django.db.transaction.atomic.

**Nested Routing:** Clean API structure (e.g., /store/products/{id}/images/) using drf-nested-routers.

### Security & Authentication

**Custom User Model:** Extended AbstractUser with email-based uniqueness.

**JWT Lifecycle:** Secure access/refresh token rotation with a 24-hour access lifetime.

**Nested Profile Updates:** Atomic updates to both User and Customer profiles in a single PATCH request.

**Permission Classes:** Granular access control (IsAdminOrReadOnly, FullDjangoModelPermissions).

### Dual Payment Gateway

**Stripe Integration:**

Server-side Checkout Session generation.

Idempotent webhook handler (stripe_webhook) that cryptographically verifies signatures before updating order status to Complete.

**Web3 / MetaMask Integration:**

Frontend requests eth_sendTransaction via MetaMask.

Zero-Trust Verification: Django uses web3.py to independently query the Ethereum Sepolia RPC node via wait_for_transaction_receipt. The backend verifies the blockchain ledger directly, preventing frontend data manipulation.

### DevOps & Infrastructure

**Docker Compose:** Multi-container setup (Web + MySQL) with restart: always policies for high availability.

**Database Seeding:** Custom management command (seed_db) utilizing raw SQL with foreign key checks disabled for rapid environment setup.

**AWS Deployment:** Deployed on a t2/t3 micro instance with a 2GB swap file to handle memory spikes during Docker builds.

## Getting Started (Local Development)

### Prerequisites

1. Docker & Docker Compose
2. .env file (see configuration below)

#### 1. Clone this repository
``` 
https://github.com/muhammadanees2k/chain-store-api.git
```

```
cd chain-store
```

### 2. Configure Environment Variables
Create a .env file in the project root:

```
SECRET_KEY=your_super_secret_random_key_here
STRIPE_PUBLIC_KEY=pk_test_...
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
WEB3_PROVIDER_URI=[https://ethereum-sepolia-rpc.publicnode.com](https://ethereum-sepolia-rpc.publicnode.com)
ALLOWED_HOSTS=localhost,127.0.0.1
```

### 3. Build and Launch
```
docker compose up -d --build
```

### 4. Populate the Database
Wait 15 seconds for MySQL to initialize, then run:

```
docker compose exec web python manage.py migrate
docker compose exec web python manage.py seed_db
```

### 5. Access the Application

**API Root:**
```
http://127.0.0.1:8000/store/
```

**Swagger Docs:** 

```
http://127.0.0.1:8000/api/docs/
```

## Testing

The project includes a robust test suite using pytest and Django's APITestCase covering:

Auth lifecycle (Registration, JWT creation/verification, Password resets).

CRUD permissions (Admin vs Anonymous vs Authenticated users).

Nested serializer validation.

```
# Run tests inside the Docker container
docker compose exec web pytest
```
