WealthOps – Kubernetes Deployment & AWS ECR
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
--docker-password=eyJwYXlsb2FkIjoiTlZaYm1HTXJ4VmlXcjE2U1hwY0VieXNSOWRNM0lpNnZhWmo5ZWQxQ2dUU25rZHBXUTlNR3FoUi95MlkrS2FjR3EwYUhQUUdoYkdZaVNUTHorWHoyUHdoUGUyb0RMYllEeU9LM2pTcXNseTBOTmFrcDBJRGVaTmZzamJOVndBbnNZODV2Y3A1OFZwQWF1VEQzNHBRSWYzTk94VldJbHZma0hsS0NweGM4cjM3eTdvS25IamduODdKYkJFa0RQVTJiM3hHdm1UZHVmWlhEdWpCelZ5bWFNTmpzYkdGNG1tWXRNcHVBbytYVU55VmN6MTR6OVJVd2w1cldKYWJVcVBZRUtFekpPd3lsNHlIbWlGWDk1YmtSamZER2dZZnhWTGFyc2xuU2NsblI4NjdhRENDSFhOUGN3YnN5aXFTbUVWQXNsZFprSXMwbzVLc0ZVWDhWSC9WNDVkWWo1cTdKeEZicWloKzNGUEpmcXJ1MTRzWnhMQ1g5RWdLUk04ZjdjYzUvNkFtamI3UzA5cDNmVDV6QXR1czZudDdQQ1AvSnk2alJ0bnUzOUFmN2ZqQUlhNUlZRDQyUE5XWHhCSWhTckI0M1ltaWRrYmwvWjJ3L050ZkVJaDA5UjBUQlJxN3J0eEdseGFQcGFQV2FnS05BZzliMzEwZlhtWmt4NGplNDNxY21IU0lDZTRGYTJydjg4SzV6UWVEejRraTNzdXpYTVBBbkdscDBJV0Y5MDR6bFYxRENkQTRyNTcrRUJYUDdjNHJUdzVsSDlicElIZUR5TGZEOC9XQWJURzZadE90a21pWlZCTTRJT3lYQXJsNUNneDBYWm5vY1k4emhBOG9SQzBiRXBLUnRYbFNQNi83RFBzd2lrODVENS9mUmt1bVVvbWM0eGtiWjdsQ0dBdk1IUHVrL3ZKZHFDYzFDeWVHVVhnRHRVN0MwRFBQZjlnMjVzZGZCSnFOVGJMY2lRVWtCVzJVdnNMWkJYcHN1cFd2NGcvUVV0VVRtM1NrSGV4YTlvNXJoaGtNUnYyRHhOR0s2MWFHTy9nTnRPczc2T1Rjc000eDNIUmNrcFovZ3YyckFaVnZJalVYQnBxbUdOdXk3Ym9EeWQ1UWh3SVdDTXNwbmVTNEVDS2ZyQ0E5bE9sOFpSQjBYYjI2MWE0bnhEZ0JCT1czUFNoUGJXUXM1VlRNNzlTREhuMjdaNXBoWmJqN2sydi9nTGhFQjFuTnEyci8rUmhYK095UFVTWlQrSDJrN1BuK2RNOFZpd2h3UHZTQThreU1XUGN0Z1k3dEVBVG0zZWV2QXVrZkRldDVudmh3bGgwbEJCSDNsSkN1bXdPbXlPQ084aDNJa0cwYmY0aHNSIiwiZGF0YWtleSI6IkFRRUJBSGh3bTBZYUlTSmVSdEptNW4xRzZ1cWVla1h1b1hYUGU1VUZjZTlScTgvMTR3QUFBSDR3ZkFZSktvWklodmNOQVFjR29HOHdiUUlCQURCb0Jna3Foa2lHOXcwQkJ3RXdIZ1lKWUlaSUFXVURCQUV1TUJFRURLM2lDbXB3UEVXazQ4ZVROQUlCRUlBN2N2aENzdERTNjhXZ1c3OURyZ1VlTGVleXFzWlo4OVBNZEI5ZHVwSHY4T24xMUFQamVDZnZyQ0RTaWJDazc2QjJnc1pHOVFpajY3RUVWTU09IiwidmVyc2lvbiI6IjIiLCJ0eXBlIjoiREFUQV9LRVkiLCJleHBpcmF0aW9uIjoxNzg3ODY5NTkzfQ== `
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