# WealthOps – Kubernetes Deployment & AWS ECR

1. Project Overview

WealthOps is a Flask-based portfolio management application integrated with PostgreSQL and the Upstox API.

The project was initially developed and tested locally and was then containerized and deployed to a local Kubernetes cluster using Kind.

The deployment architecture currently consists of:
Developer Machine
       |
       | Docker Build
       v
Docker Image
       |
       | Docker Push
       v
AWS ECR
       |
       | Image Pull
       v
Kind Kubernetes Cluster
       |
       +----------------------+
       |                      |
       v                      v
WealthOps Application      PostgreSQL
       |                      |
       |                      v
       |                 Persistent Storage
       |
       v
NGINX Ingress
       |
       v
HTTPS / OAuth
       |
       v
Upstox API

```

---

# Tech Stack

- Python Flask
- SQLAlchemy
- PostgreSQL 17
- Docker
- Kubernetes
- Amazon ECR
- Docker Desktop Kubernetes (kind)
- AWS IAM

---

# Project Structure

```
wealthops/
│
├── app.py
├── config.py
├── requirements.txt
├── Dockerfile
│
├── k8s/
│   ├── namespace.yaml
│   ├── postgres.yaml
│   ├── wealthops-deployment.yaml
│   ├── wealthops-service.yaml
│   ├── configmap.yaml
│   ├── secret.yaml
│   └── ingress.yaml
│
├── database/
├── models/
├── services/
├── routes/
└── templates/
```

---

# Features

- Portfolio Dashboard
- PostgreSQL Database
- Kubernetes Deployment
- Docker Image
- Private Amazon ECR
- Persistent Storage
- ConfigMaps
- Secrets
- Ready for Helm
- Ready for Ingress

---

# Deployment Steps

## 1. Build Docker Image

```bash
docker build -t wealthops-wealthops:latest .
```

---

## 2. Tag Image

```bash
docker tag wealthops-wealthops:latest \
ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/wealthops:latest
```

---

## 3. Login to ECR

```bash
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com
```

---

## 4. Push Image

```bash
docker push ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/wealthops:latest
```

---

## 5. Create Namespace

```bash
kubectl apply -f namespace.yaml
```

---

## 6. Deploy PostgreSQL

```bash
kubectl apply -f postgres/
```

---

## 7. Create ECR Secret

```powershell
$password = aws ecr get-login-password --region us-east-1

kubectl create secret docker-registry ecr-secret `
--docker-server=ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com `
--docker-username=AWS `
--docker-password=$password `
-n wealthops
```

---

## 8. Deploy Application

```bash
kubectl apply -f wealthops-deployment.yaml
kubectl apply -f wealthops-service.yaml
```

---

## 9. Verify Deployment

```bash
kubectl get all -n wealthops
```

---

## 10. Access Application

```bash
kubectl port-forward svc/wealthops 5000:5000 -n wealthops
```

Open

```
http://localhost:5000
```

---

# Troubleshooting

## ErrImageNeverPull

Cause

```
imagePullPolicy: Never
```

Fix

```
imagePullPolicy: Always
```

---

## ImagePullBackOff

Cause

No ECR credentials.

Fix

```
kubectl create secret docker-registry
```

---

## No basic auth credentials

Cause

Docker not logged into ECR.

Fix

```
aws ecr get-login-password
```

---

## Password Authentication Failed

Cause

Application used

```
wealthuser
```

while PostgreSQL created

```
postgres
```

Fix

Replace hardcoded database URL with environment variables.

---

## Could not translate host postgres

Cause

PostgreSQL Service missing.

Fix

```
kubectl get svc
```

Verify service name.

---

## Verify Resources

Pods

```
kubectl get pods -n wealthops
```

Deployments

```
kubectl get deployment -n wealthops
```

Services

```
kubectl get svc -n wealthops
```

PVC

```
kubectl get pvc -n wealthops
```

Logs

```
kubectl logs deployment/wealthops -n wealthops
```

Describe Pod

```
kubectl describe pod POD_NAME -n wealthops
```

---

# AWS Services Used

- IAM
- ECR
- Docker
- Kubernetes

---

# Future Enhancements

- Helm Charts
- Ingress
- NGINX Ingress Controller
- TLS using Cert Manager
- AWS EKS
- AWS ALB Ingress
- GitHub Actions CI/CD
- ArgoCD
- Prometheus
- Grafana
- Horizontal Pod Autoscaler

---

# Skills Demonstrated

- Docker
- Kubernetes
- AWS IAM
- Amazon ECR
- Flask
- PostgreSQL
- Persistent Volumes
- Services
- Deployments
- Secrets
- ConfigMaps
- Debugging Kubernetes
- Image Pull Authentication
- Cloud Native Deployment

---

# Screenshots

(Add screenshots of)

- Dashboard
- Pods
- Services
- Deployments
- ECR Repository
- Kubernetes Dashboard
