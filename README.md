# Spoolio Backend (Django)

> Backend system powering a 3D printing platform with automated
> slicing-based pricing and Stripe payments.

Backend service for a **3D printing web platform**, enabling users to
upload models, configure print settings, and order prints through an
integrated payment system.

------------------------------------------------------------------------

## Highlights

-   Full-featured **Django REST backend**
-   3D printing workflow with customizable parameters
-   **Automated price estimation via PrusaSlicer**
-   Stripe payments integration
-   Dockerized dev & production environments
-   Real-world system with complex domain logic

------------------------------------------------------------------------

## Overview

Spoolio allows users to:

-   upload 3D models
-   configure printing parameters (layer height, color, etc.)
-   get price and time estimates
-   manage a cart of print jobs
-   complete purchases via Stripe
-   track order history

The backend serves a frontend built with **Nuxt3 + Three.js**.

------------------------------------------------------------------------

## Core Features

### User & Authentication

-   Registration and login
-   Profile management
-   Secured API endpoints

### 3D Printing Workflow

-   3D model upload and management
-   Custom print configuration

### Price Estimation

-   Integration with **PrusaSlicer CLI**
-   Calculates print time and cost

### Orders & Cart

-   Multi-item cart system
-   Order tracking and history

### Payments

-   Stripe payment intents
-   Secure checkout flow

------------------------------------------------------------------------

## Tech Stack

-   Python / Django
-   Django REST Framework
-   PostgreSQL
-   Redis
-   Docker / Docker Compose
-   Stripe API
-   PrusaSlicer

------------------------------------------------------------------------

## What This Project Demonstrates

-   Real-world backend system design
-   Integration of external tools into backend workflows
-   Payment system implementation
-   Handling domain-specific logic (3D printing)
-   Deployment and infrastructure setup with Docker

------------------------------------------------------------------------

## For Developers

### Running the Project

#### Development

``` bash
docker-compose -f docker-compose.dev.yml build
docker-compose -f docker-compose.dev.yml up
```

------------------------------------------------------------------------

### Database Fixtures

Run inside the web container:

``` bash
python3 manage.py dumpdata --indent 4 --natural-foreign --natural-primary \
-e contenttypes -e auth.Permission -e sessions.session -e request.request > fixtures/backup.json

python3 manage.py loaddata fixtures/backup.json
```

------------------------------------------------------------------------

### Production Deployment

Deployment is intended for a cloud VM (e.g. DigitalOcean Ubuntu
instance) using Docker.

#### Setup Steps

-   Create Ubuntu droplet
-   Enable SSH access
-   Connect via SSH:

``` bash
ssh root@<DROPLET_IP>
```

#### Optional (Shell setup)

``` bash
apt install -y zsh
sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"
```

#### Install Docker & Docker Compose

(Follow official Docker installation steps)

------------------------------------------------------------------------

### Clone Repository

``` bash
git clone git@github.com:mateoKutnjak/spoolio-backend-django.git
```

If you get:

Permission denied (publickey)

Do:

``` bash
ssh-keygen
cat ~/.ssh/id_rsa.pub
```

Add the key to your GitHub account and clone again.

------------------------------------------------------------------------

### Environment Setup

``` bash
scp .env.development .env.production .env.production.db root@<DROPLET_IP>:<PROJECT_PATH>
```

------------------------------------------------------------------------

### Permissions

``` bash
chown 1000:1000 tmp/ logs/ backups/
```

------------------------------------------------------------------------

### Build & Run

``` bash
docker-compose build
docker-compose up
```

------------------------------------------------------------------------

### HTTPS (Certbot)

Certificates are configured using Certbot and must be renewed every 90
days.

Renew manually:

``` bash
docker-compose -f docker-compose.yml up
docker-compose run --rm certbot renew
```

Make sure ports **80 and 443** are open.

------------------------------------------------------------------------

### Redis Security

Restrict remote access using firewall rules on the hosting instance.

------------------------------------------------------------------------

### Stripe Configuration

Set Stripe secret API key in environment variables to enable payment
processing.

------------------------------------------------------------------------

### PrusaSlicer Integration

Used for estimating:

-   print duration
-   material usage
-   pricing

------------------------------------------------------------------------
