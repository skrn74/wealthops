# WealthOps

WealthOps is a Flask-based portfolio management application integrated with **PostgreSQL** and the **Upstox API**. It was initially developed and tested locally, then containerized with Docker and deployed to a local **Kind** Kubernetes cluster, using **AWS ECR** as the container image registry.

---

## Table of Contents

- [Architecture Overview](#architecture-overview)
- [Application Structure](#application-structure)
- [Tech Stack](#tech-stack)
- [Environment Variables](#environment-variables)
- [Docker](#docker)
- [AWS ECR](#aws-ecr)
- [IAM & ECR Authentication](#iam--ecr-authentication)
- [Kubernetes Setup](#kubernetes-setup)
  - [Namespace](#namespace)
  - [PostgreSQL](#postgresql)
  - [WealthOps Deployment](#wealthops-deployment)
  - [Services](#services)
  - [Ingress](#ingress)
  - [TLS / HTTPS](#tls--https)
  - [Local DNS](#local-dns)
  - [Port Forwarding](#port-forwarding)
- [Upstox OAuth Flow](#upstox-oauth-flow)
- [Troubleshooting](#troubleshooting)
- [Useful Kubernetes Commands](#useful-kubernetes-commands)
- [Current Status](#current-status)
- [Roadmap](#roadmap)

---

## Architecture Overview

```
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

### Current running architecture

```
                         Internet
                            |
                         Upstox
                            |
                     OAuth Callback
                            |
                            v
                  ┌──────────────────┐
                  │ NGINX Ingress    │
                  │ HTTPS / TLS      │
                  └────────┬─────────┘
                           |
                           v
                  ┌──────────────────┐
                  │ WealthOps        │
                  │ Service (NodePort)│
                  └────────┬─────────┘
                           |
                           v
                  ┌──────────────────┐
                  │ WealthOps Pod    │
                  │ (Flask)          │
                  └────────┬─────────┘
                           |
                    postgres:5432
                           |
                           v
                  ┌──────────────────┐
                  │ PostgreSQL       │
                  │ Service          │
                  └────────┬─────────┘
                           |
                           v
                  ┌──────────────────┐
                  │ PostgreSQL Pod   │
                  └────────┬─────────┘
                           |
                           v
                     postgres-pvc
```

---

## Application Structure

The Flask application is organized by responsibility:

```
wealthops/
│
├── models/
├── routes/
├── services/
├── utils/
├── templates/
├── static/
├── database/
├── monitoring/
├── scripts/
├── config.py
└── app.py
```

**Request flow:**

```
Browser → Flask Route → Service Layer → Database / External API → Response → Browser
```

**Example — portfolio sync flow:**

```
User → WealthOps UI → Upstox Route → Upstox Service → Upstox API
     → Portfolio Data → PostgreSQL → Dashboard
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Application | Flask (Python) |
| Database | PostgreSQL 17 |
| External API | Upstox API (OAuth) |
| Containerization | Docker |
| Image Registry | AWS ECR |
| Orchestration | Kubernetes (Kind, local) |
| Ingress | NGINX Ingress Controller |
| TLS | Self-signed cert for local HTTPS |

---

## Environment Variables

The application connects to PostgreSQL using environment variables — no hardcoded credentials:

| Variable | Description |
|---|---|
| `DB_HOST` | Database host (in-cluster: `postgres`, the Service name) |
| `DB_PORT` | Database port (`5432`) |
| `DB_NAME` | Database name (`wealthops`) |
| `DB_USER` | Database user |
| `DB_PASSWORD` | Database password |

> Inside Kubernetes, the app connects to `postgres:5432` — the **Service name**, not the Pod IP — so the connection survives Pod restarts/rescheduling.

At startup, SQLAlchemy initializes the database and ensures required tables exist. Existing tables and data are **not** dropped or recreated. For production, a migration tool such as **Alembic** is recommended for controlled schema changes.

---

## Docker

The Dockerfile packages the Python runtime, application code, and dependencies.

**Build the image:**
```bash
docker build -t wealthops-wealthops:latest .
```

**Verify:**
```bash
docker images
```

---

## AWS ECR

Amazon ECR is used as the container image registry.

- **Repository:** `wealthops`
- **Image URI:** `076194732097.dkr.ecr.us-east-1.amazonaws.com/wealthops:latest`

```
Developer Machine → docker build → Local Docker Image → docker push → Amazon ECR
```

---

## IAM & ECR Authentication

An **IAM user** was created for AWS CLI / ECR operations from the developer machine, with the required ECR permissions.

```
Developer Machine → AWS CLI → IAM User → ECR
```

### Kubernetes image pull (Kind cluster)

The current cluster is a local **Kind** cluster, so it does **not** use an EKS IAM role. Instead, ECR credentials are provided via a Kubernetes **image pull secret**:

```
ECR → ECR credentials → Kubernetes Secret → Kubernetes → WealthOps Pod
```

Referenced in the Deployment as:
```yaml
imagePullSecrets:
  - name: ecr-secret
```

> **Note:** For **EKS**, authentication will move to IAM-role-based access for ECR instead of a pull secret.

| Path | Flow |
|---|---|
| Push (dev machine) | IAM User → AWS CLI → Push image → ECR |
| Pull (Kind cluster) | Kubernetes → `imagePullSecret` → Pull image ← ECR |

---

## Kubernetes Setup

### Namespace

All application resources live in a dedicated namespace: `wealthops`

```bash
kubectl get namespaces
kubectl get all -n wealthops
```

```
Kubernetes Cluster
│
├── kube-system
├── ingress-nginx
└── wealthops
    ├── WealthOps Deployment
    ├── WealthOps Pod
    ├── PostgreSQL Deployment
    ├── PostgreSQL Pod
    ├── Services
    ├── PVC
    ├── Secrets
    └── Ingress
```

### PostgreSQL

Deployed as a Kubernetes Deployment using image **`postgres:17`**.

```bash
kubectl get deployment postgres -n wealthops
kubectl get pods -n wealthops
kubectl logs deployment/postgres -n wealthops
```

**Persistent storage:** a `PersistentVolumeClaim` (`postgres-pvc`) decouples database data from the Pod lifecycle — if the Pod is recreated, the same storage is remounted.

```
PostgreSQL Pod → Volume Mount → postgres-pvc → Persistent Volume
```

**Service:** `postgres` (ClusterIP, port `5432`)

```bash
kubectl get svc -n wealthops
```

### WealthOps Deployment

```
Deployment → ReplicaSet → WealthOps Pod → Flask Container
```

Uses the ECR image: `076194732097.dkr.ecr.us-east-1.amazonaws.com/wealthops:latest`

```bash
kubectl get deployment wealthops -n wealthops
kubectl get pods -n wealthops
kubectl logs deployment/wealthops -n wealthops
kubectl get deployment wealthops -n wealthops -o yaml
kubectl describe deployment wealthops -n wealthops
```

### Services

| Service | Type | Port | Target Port | NodePort |
|---|---|---|---|---|
| `postgres` | ClusterIP | 5432 | — | — |
| `wealthops` | NodePort | 5000 | 5000 | 30080 |

```bash
kubectl get svc -n wealthops
```

Traffic flow:
```
Node : 30080 → Service : 5000 → Pod : 5000
```

### Ingress

**NGINX Ingress Controller** runs in its own namespace, `ingress-nginx`, separate from the application namespace.

```
ingress-nginx
    └── ingress-nginx-controller (Pod)
```

**Ingress resource:** `wealthops-ingress` (namespace: `wealthops`, class: `nginx`)

```
wealthops.local → / → wealthops Service → WealthOps Pod
```

```bash
kubectl get ingress -n wealthops
kubectl describe ingress wealthops-ingress -n wealthops
```

### TLS / HTTPS

Upstox OAuth requires an HTTPS redirect URI, so a local TLS certificate was generated for `wealthops.local`:

- `wealthops.local.crt`
- `wealthops.local.key`

Stored as Kubernetes TLS Secret `wealthops-tls`:

```bash
kubectl get secret wealthops-tls -n wealthops
```

**TLS flow:**
```
Browser → HTTPS → NGINX Ingress → TLS termination → WealthOps Service → WealthOps Pod
```

### Local DNS

For local testing, `wealthops.local` is mapped to `127.0.0.1` via the Windows hosts file.

```bash
ping wealthops.local
```

### Port Forwarding

Since this is a local Kind environment, NGINX HTTPS is exposed via `kubectl port-forward`:

```bash
kubectl port-forward -n ingress-nginx service/ingress-nginx-controller 8443:443
```

```
localhost:8443 → NGINX Service :443 → Ingress → WealthOps Service → WealthOps Pod
```

---

## Upstox OAuth Flow

The app generates an authorization URL containing `client_id`, `redirect_uri`, and `response_type=code`. After the user authorizes, Upstox redirects to:

```
https://wealthops.local:8443/upstox/callback
```

**Full flow:**
```
Browser → WealthOps → Upstox Login → User Authorization → OAuth Callback
        → NGINX Ingress → WealthOps Flask Route → Access Token → Upstox API
        → Portfolio Data → PostgreSQL → Dashboard
```

✅ The complete OAuth flow has been tested successfully end-to-end.

---

## Troubleshooting

### `ErrImageNeverPull`
- **Cause:** `imagePullPolicy: Never` prevented Kubernetes from pulling the ECR image.
- **Fix:** Changed to `imagePullPolicy: Always` and configured the ECR image reference.

### Image pull / ECR authentication failure
- **Cause:** Kubernetes couldn't retrieve the image from ECR.
- **Fix:** Configured ECR authentication and created an `ecr-secret`, referenced via `imagePullSecrets`.

### ECR IAM permission error (`AccessDeniedException`)
- **Cause:** IAM user lacked permissions (e.g. `ecr:DescribeRepositories`).
- **Fix:** Added the required ECR permissions to the IAM user.

### PostgreSQL password authentication failed
- **Cause:** App connected as `wealthuser`, but PostgreSQL was initialized with the `postgres` role — role mismatch.
- **Fix:** Aligned app and database credentials, and moved connection details into environment variables instead of hardcoding them.

### `could not translate host name "postgres"`
- **Cause:** App couldn't resolve the `postgres` hostname.
- **Fix:** Verified the PostgreSQL Service existed and exposed port `5432` via `kubectl get svc -n wealthops`. Inside Kubernetes, apps should always reference the **Service name**, not a Pod IP.

### Ingress: Service not found
- **Cause:** Ran `kubectl describe svc wealthops-service` — but the actual Service was named `wealthops`.
- **Fix:** Used the correct name: `kubectl describe svc wealthops -n wealthops`.
- **Lesson:** Always run `kubectl get` to confirm the actual resource name before `describe`, `logs`, or `port-forward`.

---

## Useful Kubernetes Commands

```bash
# Check everything in the namespace
kubectl get all -n wealthops

# Pods
kubectl get pods -n wealthops
kubectl describe pod <pod-name> -n wealthops

# Logs
kubectl logs deployment/wealthops -n wealthops
kubectl logs deployment/postgres -n wealthops

# Services
kubectl get svc -n wealthops
kubectl describe svc wealthops -n wealthops
kubectl get endpoints -n wealthops

# Deployments
kubectl get deployments -n wealthops
kubectl get deployment wealthops -n wealthops -o yaml
kubectl rollout restart deployment/wealthops -n wealthops
kubectl rollout status deployment/wealthops -n wealthops

# Ingress
kubectl get ingress -n wealthops
kubectl describe ingress wealthops-ingress -n wealthops
```

---

## Current Status

- ✅ Flask application containerized and running in a local Kind Kubernetes cluster
- ✅ PostgreSQL deployed with persistent storage
- ✅ Docker images pushed to and pulled from AWS ECR via an IAM user + image pull secret
- ✅ NGINX Ingress configured with local TLS for HTTPS
- ✅ Upstox OAuth flow tested end-to-end
- ✅ Common deployment issues documented with root cause and resolution

## Roadmap

- [ ] Move to **EKS** with IAM role-based ECR authentication (replacing the image pull secret)
- [ ] Introduce **Alembic** for controlled database migrations
- [ ] Replace local self-signed TLS with a proper certificate (e.g. via cert-manager) for non-local environments
- [ ] Add CI/CD pipeline for automated build → push → deploy