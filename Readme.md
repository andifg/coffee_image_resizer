# Coffee App Image Resizer

## Context
This repository is part of the coffee rating application project. The project
provides a rating appliation for coffees where its possible to add/delete and
rate different coffee beans. The project consists of the following repositories:
- [Frontend](https://github.com/andifg/coffee_frontend_ts.git) - A react typescript progressive web app
- [Backend](https://github.com/andifg/coffee_backend.git) - Fastapi based python backend
- [Resizer](https://github.com/andifg/coffee_image_resizer.git) - Python based image resizer listening on kafka messages
- [Helm Chart](https://github.com/andifg/coffee-app-chart.git) - Helm Chart deploying front and backend together with database and minio hem charts
- [GitOps](https://github.com/andifg/coffee-app-gitops.git) - Gitops repository for ArgoCD reflecting deployed applications for test and prod env

## Prerequesits

- Install pre-commit hocks and install them via
```bash
pre-commit install
```

- [Install poetry](https://python-poetry.org/)

## Test
```bash
poetry run ./scripts/test.sh
```

## Format & Lint
```bash
poetry run ./scripts/format.sh
```

## Run locally without container
```bash
poetry run python3 -m resize
```

## Build locally
```bash
docker build -t resizer:v1 -f ./Containerfile .
```

## Run locally with container
- Build container first

```bash
docker run -it -p 9000:8000  --name resizer resizer:v1
```

## Local End To End Dev & Test Environment

In order to execute local end to end test for the coffee app its possible to
start the docker-compose inside the devservice directory that is part of the
[backend repository](https://github.com/andifg/coffee_backend.git).

## Kcat example messages:

Kcat can be used to send test messages to the running kafka cluster:

```bash
echo 'coffee-images/original/018e1559-fe33-798d-b184-6f97ffd630a7:{"data":"3"}' | kcat -b localhost:9094 -t coffee-images -P -K :
```