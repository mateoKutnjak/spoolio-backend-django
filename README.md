# Spoolio Web REST API server

## How to run it?

### Development

- Checkout to branch [TODO]
`git checkout [TODO]`
- Build docker images
`docker-compose -f docker-compose.dev.yml build`
- Run docker compose for development
`docker-compose -f docker-compose.dev.yml up`
- Fixtures load/dump (commands inside `web` docker service container)
`python3 manage.py dumpdata --indent 4 --natural-foreign --natural-primary -e contenttypes -e auth.Permission -e sessions.session -e request.request > fixtures/backup.json`
`python3 manage.py loaddata fixtures/backup.json`

### Production

Running production has to be done on hosting service instance (for example Digital Ocean Ubuntu machine) through docker-compose.

#### From scratch

- Create Ubuntu instance (droplet) on Digital Ocean
  - Enable SSH key authentication
- Connect to running instance with VS Code using `ssh root@<DROPLET_IP>`
- [OPTIONAL] Install `zsh` with command `apt install -y zsh`
- [OPTIONAL] Install `oh-my-zsh` with command `sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"`
- Install Docker by following this [commands in step 1](https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-on-ubuntu-20-04#step-1-installing-docker)
- Install docker-compose by following this [commands in step 1](https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-compose-on-ubuntu-20-04#step-1-installing-docker-compose)
- `git clone git@github.com:mateoKutnjak/spoolio-backend-django.git`
  - if error `Permission denied (publickey)`
    - generate SSH key pair with command `ssh-keygen` and press ENTER for every question without any inputs
    - copy terminal output of command `cat .ssh/id_rsa.pub` and add new SSH key to github settings
    - `git clone` again
- dont forget to `git checkout <branch_name>`
- copy environment files with command `scp .env.development .env.production .env.production.db root@<DROPLET_IP>:<PATH_TO_PROJECT_ROOT>`
- change ownership of direcories that docker uses through volume: `chown 1000:1000 tmp/ logs/ backups/`
- build docker images using `docker-compose build`

#### Start docker-compose services

- Using command `docker-compose up` all services are started

#### Certbot

Using this [guide](https://mindsers.blog/post/https-using-nginx-certbot-docker/) certbot was set up. It also has part for renewing through `docker-compose` service. It needs to be renewed every 90 days.

#### Redis

To protect remote access to redis instance through add firewall to Digital Ocean droplet. See this [screenshot](https://www.dropbox.com/s/v3qbmwkqb0ztchn/Screenshot%20from%202023-04-18%2012-48-01.png?dl=0)

#### Stripe

Django backend uses `secret` API key from Stripe developer webpage to create payment intents.

#### Prusa slicer price/duration estimation

See this [flowchart](https://ibb.co/KNPJTch)

## TODOs

- To which branch should be checkout when cloning project for development/production?
