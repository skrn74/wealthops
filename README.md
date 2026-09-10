# WealthOps

WealthOps is a Flask-based portfolio management application integrated with **PostgreSQL** and the **Upstox API**. The application was initially developed and tested locally, then containerized with Docker and deployed to Kubernetes using both a local **Kind** environment and **Amazon EKS**.

The project demonstrates a production-style application and cloud platform workflow covering:

- Flask application architecture
- PostgreSQL persistence
- Upstox OAuth and portfolio synchronization
- Docker containerization
- Amazon ECR
- Kubernetes / Kind
- Amazon EKS
- IAM and EKS Pod Identity
- Amazon EBS CSI persistent storage
- Helm
- AWS Load Balancer Controller
- Kubernetes Ingress
- Internet-facing AWS Application Load Balancer
- Kubernetes configuration and secrets
- Troubleshooting and operational workflows

---

## Table of Contents

- [Architecture Overview](#architecture-overview)
- [Application Structure](#application-structure)
- [Tech Stack](#tech-stack)
- [Environment Configuration](#environment-configuration)
- [Docker](#docker)
- [Amazon ECR](#amazon-ecr)
- [IAM Architecture](#iam-architecture)
- [Local Kind Kubernetes](#local-kind-kubernetes)
- [Amazon EKS Deployment](#amazon-eks-deployment)
  - [EKS Cluster](#eks-cluster)
  - [Configure kubectl](#configure-kubectl)
  - [Namespace](#namespace)
  - [ECR Image Pull from EKS](#ecr-image-pull-from-eks)
  - [PostgreSQL and Persistent Storage](#postgresql-and-persistent-storage)
  - [EBS CSI Driver](#ebs-csi-driver)
  - [EKS Pod Identity](#eks-pod-identity)
  - [WealthOps Deployment](#wealthops-deployment)
  - [Services](#services)
  - [AWS Load Balancer Controller](#aws-load-balancer-controller)
  - [Helm](#helm)
  - [Internet-Facing ALB Ingress](#internet-facing-alb-ingress)
  - [Final EKS Request Flow](#final-eks-request-flow)
- [Local Kind vs EKS](#local-kind-vs-eks)
- [Upstox OAuth](#upstox-oauth)
- [Troubleshooting](#troubleshooting)
- [Useful Commands](#useful-commands)
- [Security Considerations](#security-considerations)
- [Current Status](#current-status)
- [Roadmap](#roadmap)
- [Interview Perspective](#interview-perspective)

---

# Architecture Overview

## Overall Application and Platform Architecture

```text
                         Developer / Git
                                |
                                v
                         GitLab / Source
                                |
                                v
                           Docker Build
                                |
                                v
                         Amazon ECR
                                |
                                v
                    +----------------------+
                    |      Amazon EKS      |
                    |                      |
                    |  +----------------+  |
                    |  | AWS Load       |  |
Internet ----------+->| Balancer       |  |
                    |  | Controller     |  |
                    |  +-------+--------+  |
                    |          |           |
                    |       Ingress        |
                    |          |           |
                    |          v           |
                    |  +----------------+  |
                    |  | WealthOps      |  |
                    |  | Service        |  |
                    |  +-------+--------+  |
                    |          |           |
                    |          v           |
                    |  +----------------+  |
                    |  | WealthOps Pod  |  |
                    |  +-------+--------+  |
                    |          |           |
                    |          v           |
                    |  +----------------+  |
                    |  | PostgreSQL Pod |  |
                    |  +-------+--------+  |
                    |          |           |
                    |          v           |
                    |       EBS gp3        |
                    +----------------------+

                           ^
                           |
                        Upstox API
                    OAuth / Portfolio Sync
```

## AWS EKS Traffic Flow

```text
Internet
    |
    v
AWS Application Load Balancer
    |
    v
Kubernetes Ingress
wealthops-alb
    |
    v
WealthOps Service :5000
    |
    v
WealthOps Pod
    |
    v
PostgreSQL Service :5432
    |
    v
PostgreSQL Pod
    |
    v
EBS gp3 Persistent Volume
```

---

# Application Structure

The Flask application is organized by responsibility rather than keeping the application logic in a single file.

```text
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

### Request Flow

```text
Browser
   |
   v
Flask Route / Blueprint
   |
   v
Service Layer
   |
   +----> PostgreSQL
   |
   +----> External API / Upstox
   |
   v
Response
   |
   v
Browser
```

### Portfolio Sync Flow

```text
User
  |
  v
WealthOps UI
  |
  v
Upstox OAuth
  |
  v
Upstox API
  |
  v
Portfolio / Holdings Data
  |
  v
Portfolio Service
  |
  v
PostgreSQL
  |
  v
Dashboard
```

---

# Tech Stack

| Layer | Technology |
|---|---|
| Application | Flask / Python |
| Database | PostgreSQL 17 |
| External API | Upstox API |
| Authentication | Upstox OAuth 2.0 |
| Containerization | Docker |
| Image Registry | Amazon ECR |
| Local Kubernetes | Kind |
| Cloud Kubernetes | Amazon EKS |
| Kubernetes Packaging | Helm |
| Local Ingress | NGINX Ingress Controller |
| AWS Ingress | AWS Load Balancer Controller |
| AWS Load Balancing | Application Load Balancer |
| Persistent Storage | Amazon EBS / EBS CSI Driver |
| Workload IAM | EKS Pod Identity |
| Configuration | Kubernetes ConfigMap |
| Secrets | Kubernetes Secret |
| Infrastructure Tooling | eksctl / AWS CLI / kubectl |

---

# Environment Configuration

WealthOps uses environment variables for database and external API configuration.

### Database Configuration

| Variable | Description |
|---|---|
| `DB_HOST` | PostgreSQL Service name inside Kubernetes |
| `DB_PORT` | PostgreSQL port, normally `5432` |
| `DB_NAME` | Database name |
| `DB_USER` | Database user |
| `DB_PASSWORD` | Database password |

Inside Kubernetes, the application connects to:

```text
postgres:5432
```

`postgres` is the Kubernetes Service name rather than a Pod IP. This allows PostgreSQL Pods to be recreated or rescheduled without changing the application connection configuration.

### Upstox Configuration

| Variable | Description |
|---|---|
| `UPSTOX_BASE_URL` | Upstox API base URL |
| `UPSTOX_CLIENT_ID` | OAuth client ID |
| `UPSTOX_CLIENT_SECRET` | OAuth client secret |
| `UPSTOX_REDIRECT_URI` | OAuth callback URL |

Application configuration is stored separately from sensitive values.

Example ConfigMap:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: wealthops-config
  namespace: wealthops
data:
  DB_HOST: "postgres"
  DB_PORT: "5432"
  DB_NAME: "wealthops"
  UPSTOX_BASE_URL: "https://api.upstox.com/v2"
```

Sensitive values are provided through a Kubernetes Secret.

> Never commit real credentials, client secrets, passwords, temporary AWS credentials, or tokens to Git.

At application startup, SQLAlchemy ensures required tables exist. Existing tables and data are not intentionally dropped or recreated. For production schema management, **Alembic** is planned for controlled database migrations.

---

# Docker

The application is containerized using Docker.

### Build

```powershell
docker build -t wealthops-wealthops:latest .
```

### Verify

```powershell
docker images
```

### Docker Image Flow

```text
Source Code
    |
    v
Docker Build
    |
    v
Local Docker Image
    |
    v
Amazon ECR
```

The Docker image is designed to run the Flask application on port `5000`.

---

# Amazon ECR

Amazon ECR is used as the private container image registry.

Repository:

```text
wealthops
```

Image:

```text
<AWS_ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com/wealthops:latest
```

> The real AWS account ID and private resource identifiers should not be committed to public documentation.

### Authenticate Docker with ECR

```powershell
aws ecr get-login-password --region us-east-1 |
docker login --username AWS --password-stdin <AWS_ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com
```

### Tag Image

```powershell
docker tag wealthops-wealthops:latest `
  <AWS_ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com/wealthops:latest
```

### Push Image

```powershell
docker push `
  <AWS_ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com/wealthops:latest
```

### Important Image Naming Note

The local image name must match the image being tagged and pushed.

For example:

```text
docker build
    |
    +--> wealthops-wealthops:latest
                 |
                 v
docker tag
                 |
                 v
ECR wealthops:latest
```

Building one local tag and accidentally pushing a different older local tag can result in stale application versions being deployed.

---

# IAM Architecture

WealthOps uses separate IAM identities for different responsibilities.

```text
                         AWS
                          |
        +-----------------+------------------+
        |                 |                  |
        v                 v                  v
 EKS Provisioner      Worker Node       EBS CSI Controller
        |                 |                  |
        |                 |                  |
 Infrastructure       ECR Pull           EBS Permissions
 Management           Access
        |                 |                  |
        v                 v                  v
WealthOpsEKS       Node Instance Role   AmazonEKS_EBS_CSI_
Provisioner                              DriverRole
                                             |
                                             v
                                    AmazonEBSCSIDriverPolicyV2


                    AWS Load Balancer Controller
                                  |
                                  v
                            Pod Identity
                                  |
                                  v
                       WealthOpsALBControllerRole
                                  |
                                  v
                    AWSLoadBalancerControllerIAMPolicy
                                  |
                                  v
                            AWS ALB APIs
```

## Identity Responsibilities

### EKS Provisioner

Used for infrastructure provisioning and administration during the POC:

```text
GitLabuser
    |
    v
AssumeRole
    |
    v
WealthOpsEKSProvisioner
```

The provisioning role is **not** used by application Pods.

> For production, long-lived IAM users should preferably be replaced with IAM Identity Center / federation and tightly scoped roles.

### Worker Node IAM Role

Worker nodes use an IAM instance role for node-level operations, including access required to pull private ECR images.

### EBS CSI IAM Role

The EBS CSI Controller uses:

```text
AmazonEKS_EBS_CSI_DriverRole
```

with:

```text
AmazonEBSCSIDriverPolicyV2
```

### AWS Load Balancer Controller IAM Role

The AWS Load Balancer Controller uses:

```text
WealthOpsALBControllerRole
```

with:

```text
AWSLoadBalancerControllerIAMPolicy
```

This separation follows the principle of assigning AWS permissions according to workload responsibility.

---

# Local Kind Kubernetes

WealthOps was first deployed to a local Kind Kubernetes cluster running through Docker Desktop.

## Local Architecture

```text
Docker Desktop
      |
      v
Kind Kubernetes
      |
      +-----------------------+
      |                       |
      v                       v
WealthOps Pod           PostgreSQL Pod
      |                       |
      |                       v
      |                  Persistent Storage
      |
      v
NGINX Ingress Controller
      |
      v
Local HTTPS
wealthops.local:8443
```

## Local Namespace

```text
wealthops
```

Ingress controller namespace:

```text
ingress-nginx
```

## Local Ingress

The local environment uses the NGINX Ingress Controller.

Example:

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: wealthops-ingress
  namespace: wealthops
spec:
  ingressClassName: nginx
  tls:
    - hosts:
        - wealthops.local
      secretName: wealthops-tls
  rules:
    - host: wealthops.local
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: wealthops
                port:
                  number: 5000
```

## Local TLS

A self-signed certificate was used for local HTTPS:

```text
wealthops.local.crt
wealthops.local.key
```

Stored as:

```text
wealthops-tls
```

## Local DNS

For local testing, `wealthops.local` is mapped to:

```text
127.0.0.1
```

through the Windows hosts file.

## Local Port Forwarding

NGINX HTTPS can be exposed using:

```powershell
kubectl port-forward `
  -n ingress-nginx `
  service/ingress-nginx-controller `
  8443:443
```

Local URL:

```text
https://wealthops.local:8443
```

---

# Amazon EKS Deployment

The application was subsequently deployed to Amazon EKS.

## EKS Cluster

AWS Region:

```text
us-east-1
```

Cluster:

```text
wealthops-eks
```

Managed node group:

```text
wealthops-ng
```

Node instance type:

```text
t3.medium
```

Desired nodes:

```text
2
```

Example `eksctl` configuration:

```yaml
apiVersion: eksctl.io/v1alpha5
kind: ClusterConfig

metadata:
  name: wealthops-eks
  region: us-east-1

managedNodeGroups:
  - name: wealthops-ng
    instanceType: t3.medium
    minSize: 1
    desiredCapacity: 2
    maxSize: 3
    volumeSize: 30
    privateNetworking: false
```

The cluster was created using `eksctl`.

---

## Configure kubectl

Configure the local kubeconfig:

```powershell
aws eks update-kubeconfig `
  --region us-east-1 `
  --name wealthops-eks
```

Verify:

```powershell
kubectl config current-context
```

Check nodes:

```powershell
kubectl get nodes
```

Expected:

```text
NAME                           STATUS   ROLES    VERSION
ip-xxx-xxx-xxx-xxx...          Ready    <none>   v1.34.x
ip-xxx-xxx-xxx-xxx...          Ready    <none>   v1.34.x
```

---

## Namespace

WealthOps workloads run in the dedicated:

```text
wealthops
```

namespace.

```powershell
kubectl get namespace wealthops
kubectl get all -n wealthops
```

The namespace contains application resources such as:

```text
wealthops
├── WealthOps Deployment
├── WealthOps Pod
├── PostgreSQL Deployment
├── PostgreSQL Pod
├── Services
├── PVC
├── ConfigMap
├── Secrets
└── Ingress
```

---

# ECR Image Pull from EKS

The EKS environment does **not** use the local Kind `ecr-secret` approach.

Instead, EKS worker nodes use their AWS IAM role to obtain the permissions required to pull images from private ECR.

```text
GitLab / Developer
       |
       v
Docker Build
       |
       v
Amazon ECR
       |
       v
EKS Deployment
       |
       v
Kubernetes Scheduler
       |
       v
Worker Node
       |
       v
Node IAM Role
       |
       v
ECR Read Permissions
       |
       v
Private Image Pull
       |
       v
WealthOps Pod
```

This avoids embedding AWS access keys in the application Pod.

---

# PostgreSQL and Persistent Storage

PostgreSQL runs inside Kubernetes using:

```text
postgres:17
```

The PostgreSQL Service is:

```text
postgres:5432
```

The database uses a PersistentVolumeClaim:

```text
postgres-pvc
```

## EKS StorageClass

A `gp3` StorageClass was created using the AWS EBS CSI provisioner:

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: gp3

provisioner: ebs.csi.aws.com

volumeBindingMode: WaitForFirstConsumer

parameters:
  type: gp3
  encrypted: "true"

reclaimPolicy: Delete
allowVolumeExpansion: true
```

The PVC uses:

```yaml
storageClassName: gp3
```

Verify:

```powershell
kubectl get pvc -n wealthops
```

Expected:

```text
NAME           STATUS   VOLUME        CAPACITY   ACCESS MODES   STORAGECLASS
postgres-pvc   Bound    pvc-xxxx      5Gi        RWO            gp3
```

## Storage Flow

```text
PostgreSQL Pod
      |
      v
Volume Mount
      |
      v
PersistentVolumeClaim
postgres-pvc
      |
      v
PersistentVolume
      |
      v
AWS EBS gp3
```

---

# EBS CSI Driver

The EBS CSI Driver integrates Kubernetes persistent storage with Amazon EBS.

## Controller

The EBS CSI Controller performs AWS-side control operations such as creating and managing EBS volumes.

```text
EBS CSI Controller
       |
       v
AWS EBS / EC2 APIs
```

## Node

The EBS CSI Node component runs on worker nodes and mounts the EBS volume for application Pods.

```text
EBS CSI Node
       |
       v
Mounted EBS Volume
       |
       v
PostgreSQL Pod
```

### Controller vs Node

```text
Controller = Talks to AWS
Node       = Mounts storage into Pods
```

---

# EKS Pod Identity

EKS Pod Identity provides a secure mechanism for connecting Kubernetes workload identities to AWS IAM roles.

The EKS Pod Identity Agent runs in:

```text
kube-system
```

Typically, one agent Pod runs on each worker node.

Install:

```powershell
.\eksctl create addon `
  --name eks-pod-identity-agent `
  --cluster wealthops-eks `
  --region us-east-1
```

Verify:

```powershell
kubectl get pods -n kube-system |
Select-String pod-identity
```

## Pod Identity Mental Model

```text
Kubernetes ServiceAccount
          |
          v
     EKS Pod Identity
          |
          v
       IAM Role
          |
          v
      IAM Policy
          |
          v
       AWS APIs
```

A simple way to remember the roles:

```text
ServiceAccount = Who is this workload?
Pod Identity   = Secure bridge between Kubernetes and AWS identity
IAM Role       = AWS identity / ID card
IAM Policy     = What the identity is allowed to do
AWS API        = Performs the requested operation
```

Pod Identity enables workloads to obtain temporary AWS credentials instead of storing permanent AWS access keys inside Pods.

---

# EBS CSI Pod Identity

The EBS CSI Controller uses:

```text
ServiceAccount:
ebs-csi-controller-sa
```

The ServiceAccount is associated with:

```text
IAM Role:
AmazonEKS_EBS_CSI_DriverRole
```

The role uses:

```text
IAM Policy:
AmazonEBSCSIDriverPolicyV2
```

Architecture:

```text
EBS CSI Controller
        |
        v
ebs-csi-controller-sa
        |
        v
EKS Pod Identity
        |
        v
AmazonEKS_EBS_CSI_DriverRole
        |
        v
AmazonEBSCSIDriverPolicyV2
        |
        v
AWS EBS / EC2 APIs
```

---

# WealthOps Deployment

The WealthOps Deployment uses the private ECR image.

Conceptually:

```text
Deployment
    |
    v
ReplicaSet
    |
    v
WealthOps Pod
    |
    v
Flask Container :5000
```

Example:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: wealthops
  namespace: wealthops

spec:
  replicas: 1

  selector:
    matchLabels:
      app: wealthops

  template:
    metadata:
      labels:
        app: wealthops

    spec:
      containers:
        - name: wealthops
          image: <AWS_ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com/wealthops:latest
          imagePullPolicy: Always

          envFrom:
            - configMapRef:
                name: wealthops-config

            - secretRef:
                name: wealthops-secrets

          ports:
            - containerPort: 5000
```

Verify:

```powershell
kubectl get deployment wealthops -n wealthops
kubectl get pods -n wealthops
kubectl logs deployment/wealthops -n wealthops
```

---

# Services

The application uses Kubernetes Services for stable internal networking.

## PostgreSQL

```text
Service: postgres
Type: ClusterIP
Port: 5432
```

## WealthOps

The WealthOps Service exposes:

```text
Service: wealthops
Port: 5000
Target Port: 5000
```

The AWS ALB uses the Service as the Kubernetes backend.

Verify:

```powershell
kubectl get svc -n wealthops
```

Traffic inside Kubernetes:

```text
WealthOps Service :5000
        |
        v
WealthOps Pod :5000
```

---

# AWS Load Balancer Controller

The AWS Load Balancer Controller watches Kubernetes resources such as Ingress and creates/manages AWS load-balancing resources.

```text
Kubernetes Ingress
       |
       v
AWS Load Balancer Controller
       |
       v
AWS APIs
       |
       v
Application Load Balancer
```

The controller runs in:

```text
kube-system
```

and has a dedicated IAM identity.

---

# Load Balancer Controller IAM Policy

The official controller IAM policy was downloaded from the AWS Load Balancer Controller project:

```powershell
Invoke-WebRequest `
  -Uri "https://raw.githubusercontent.com/kubernetes-sigs/aws-load-balancer-controller/v2.14.1/docs/install/iam_policy.json" `
  -OutFile "iam_policy.json"
```

The policy was created in AWS IAM:

```powershell
aws iam create-policy `
  --policy-name AWSLoadBalancerControllerIAMPolicy `
  --policy-document file://iam_policy.json
```

Policy:

```text
AWSLoadBalancerControllerIAMPolicy
```

The policy defines the AWS permissions required by the controller.

---

# Load Balancer Controller IAM Role

A dedicated IAM role was created:

```text
WealthOpsALBControllerRole
```

The role uses:

```text
AWSLoadBalancerControllerIAMPolicy
```

Architecture:

```text
WealthOpsALBControllerRole
        |
        v
AWSLoadBalancerControllerIAMPolicy
        |
        v
AWS ALB / EC2 APIs
```

---

# Load Balancer Controller Pod Identity

The Kubernetes ServiceAccount is:

```text
aws-load-balancer-controller
```

It is associated with:

```text
WealthOpsALBControllerRole
```

Association:

```powershell
.\eksctl create podidentityassociation `
  --cluster wealthops-eks `
  --region us-east-1 `
  --namespace kube-system `
  --service-account-name aws-load-balancer-controller `
  --role-name WealthOpsALBControllerRole `
  --permission-policy-arns arn:aws:iam::<AWS_ACCOUNT_ID>:policy/AWSLoadBalancerControllerIAMPolicy
```

Verify:

```powershell
.\eksctl get podidentityassociation `
  --cluster wealthops-eks `
  --region us-east-1
```

The relationship is:

```text
AWS Load Balancer Controller
          |
          v
aws-load-balancer-controller
          |
          v
EKS Pod Identity
          |
          v
WealthOpsALBControllerRole
          |
          v
AWSLoadBalancerControllerIAMPolicy
          |
          v
AWS ALB APIs
```

---

# Helm

Helm is used to install and manage the AWS Load Balancer Controller Kubernetes resources.

Verify Helm:

```powershell
helm version
```

Add the AWS EKS Helm repository:

```powershell
helm repo add eks https://aws.github.io/eks-charts
```

Update repository metadata:

```powershell
helm repo update
```

Search for the controller:

```powershell
helm search repo eks/aws-load-balancer-controller
```

During the deployment, the available chart was:

```text
Chart Version: 3.5.0
App Version:   v3.5.0
```

## Helm Installation

```powershell
helm install aws-load-balancer-controller `
  eks/aws-load-balancer-controller `
  --namespace kube-system `
  --set clusterName=wealthops-eks `
  --set region=us-east-1 `
  --set serviceAccount.create=true `
  --set serviceAccount.name=aws-load-balancer-controller
```

Verify the Helm release:

```powershell
helm list -A
```

Verify the controller:

```powershell
kubectl get deployment `
  aws-load-balancer-controller `
  -n kube-system
```

Expected:

```text
aws-load-balancer-controller   2/2   2   2
```

### Helm Workflow

```text
Helm Repository
      |
      v
Helm Chart
      |
      v
helm install
      |
      v
Helm Release
      |
      v
Kubernetes Deployment / ServiceAccount / Resources
```

Helm provides a repeatable and parameterized way to install and manage Kubernetes components.

---

# Internet-Facing ALB Ingress

The WealthOps application is exposed through an AWS Application Load Balancer using Kubernetes Ingress.

File:

```text
k8s/wealthops-alb-ingress.yml
```

Configuration:

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress

metadata:
  name: wealthops-alb
  namespace: wealthops

  annotations:
    alb.ingress.kubernetes.io/scheme: internet-facing
    alb.ingress.kubernetes.io/target-type: ip

spec:
  ingressClassName: alb

  rules:
    - http:
        paths:
          - path: /
            pathType: Prefix

            backend:
              service:
                name: wealthops
                port:
                  number: 5000
```

Apply:

```powershell
kubectl apply -f .\k8s\wealthops-alb-ingress.yml
```

Check:

```powershell
kubectl get ingress -n wealthops
```

Example:

```text
NAME            CLASS   HOSTS   ADDRESS
wealthops-alb   alb     *       k8s-wealthop-xxxx.us-east-1.elb.amazonaws.com
```

The AWS Load Balancer Controller automatically provisions the AWS Application Load Balancer based on the Kubernetes Ingress.

---

# ALB Target Type

The Ingress uses:

```yaml
alb.ingress.kubernetes.io/target-type: ip
```

This allows the ALB to route directly to the IP addresses of the application Pods.

```text
Internet
   |
   v
AWS ALB
   |
   v
WealthOps Pod IP
   |
   v
Flask :5000
```

This avoids requiring the ALB to route through a NodePort for this workload.

---

# Final EKS Request Flow

The completed AWS request path is:

```text
                         Internet
                            |
                            | HTTP :80
                            v
                  +----------------------+
                  | AWS Application      |
                  | Load Balancer        |
                  +----------+-----------+
                             |
                             v
                  +----------------------+
                  | Kubernetes Ingress   |
                  | wealthops-alb         |
                  +----------+-----------+
                             |
                             v
                  +----------------------+
                  | WealthOps Service    |
                  | :5000                |
                  +----------+-----------+
                             |
                             v
                  +----------------------+
                  | WealthOps Pod        |
                  | Flask :5000          |
                  +----------+-----------+
                             |
                             v
                  +----------------------+
                  | PostgreSQL Service   |
                  | :5432                |
                  +----------+-----------+
                             |
                             v
                  +----------------------+
                  | PostgreSQL Pod       |
                  | EBS gp3 storage      |
                  +----------------------+
```

The application was successfully accessed through the AWS-generated ALB DNS hostname.

---

# Local Kind vs EKS

The project now supports two deployment environments.

## Local

```text
Docker Desktop
      |
      v
Kind Kubernetes
      |
      v
NGINX Ingress Controller
      |
      v
wealthops.local:8443
      |
      v
WealthOps
```

## AWS

```text
AWS EKS
      |
      v
AWS Load Balancer Controller
      |
      v
AWS Application Load Balancer
      |
      v
Kubernetes Ingress
      |
      v
WealthOps
```

These are separate Kubernetes environments. The application code can remain the same while the ingress and infrastructure layer changes.

## Switching Kubernetes Contexts

View available contexts:

```powershell
kubectl config get-contexts
```

Switch to Kind:

```powershell
kubectl config use-context kind-desktop
```

Switch to EKS:

```powershell
kubectl config use-context <EKS_CONTEXT>
```

Always verify before running administrative commands:

```powershell
kubectl config current-context
```

This is especially important before running:

```text
kubectl apply
kubectl delete
kubectl rollout restart
kubectl scale
```

to avoid modifying the wrong cluster.

---

# Upstox OAuth

WealthOps integrates with Upstox using OAuth.

## OAuth Flow

```text
Browser
   |
   v
WealthOps
   |
   v
Upstox Authorization
   |
   v
User Login / Consent
   |
   v
OAuth Authorization Code
   |
   v
Callback URL
   |
   v
WealthOps Flask Callback
   |
   v
Access Token
   |
   v
Upstox API
   |
   v
Portfolio / Holdings
   |
   v
PostgreSQL
   |
   v
Dashboard
```

## Local OAuth

The local environment uses:

```text
https://wealthops.local:8443/upstox/callback
```

with the local NGINX TLS configuration.

## EKS OAuth

The AWS ALB currently exposes WealthOps using an AWS-generated ALB hostname over HTTP.

The public showcase page therefore works without owning a domain.

However, the current Upstox application configuration requires a suitable HTTPS redirect URI. A trusted public HTTPS callback using the AWS ALB hostname would require a domain and certificate.

Therefore:

- Public WealthOps showcase: **works through the ALB hostname**
- Local Upstox OAuth: **continues to use the local HTTPS setup**
- Public Upstox OAuth: **requires a future domain + HTTPS/ACM setup**

No domain was purchased for the current showcase.

---

# Troubleshooting

## PVC Stuck in Pending

Initial error:

```text
pod has unbound immediate PersistentVolumeClaims
```

### Cause

The PostgreSQL PVC did not have an appropriate StorageClass.

### Resolution

Created the `gp3` StorageClass and configured:

```yaml
storageClassName: gp3
```

The PVC subsequently became:

```text
Bound
```

---

## EBS CSI Controller CrashLoopBackOff

Initial error:

```text
403 UnauthorizedOperation
ec2:DescribeAvailabilityZones
```

### Cause

The EBS CSI Controller did not have sufficient AWS permissions.

### Resolution

Configured EKS Pod Identity:

```text
EBS CSI Controller
        |
        v
ebs-csi-controller-sa
        |
        v
EKS Pod Identity
        |
        v
AmazonEKS_EBS_CSI_DriverRole
        |
        v
AmazonEBSCSIDriverPolicyV2
        |
        v
AWS EBS / EC2 APIs
```

After restarting the controller, it became healthy.

---

## PostgreSQL Initialization Failure

Initial error:

```text
directory "/var/lib/postgresql/data" exists but is not empty
It contains a lost+found directory
```

### Cause

The root of the mounted Linux filesystem contained `lost+found`.

### Resolution

Configured PostgreSQL to use a clean subdirectory:

```yaml
env:
  - name: PGDATA
    value: /var/lib/postgresql/data/pgdata
```

PostgreSQL then initialized successfully.

---

## WealthOps Pod Failed Because Secret Was Missing

Error:

```text
secret "wealthops-secrets" not found
```

### Resolution

Applied the secret manifest:

```powershell
kubectl apply -f .\k8s\secret.local.yaml
```

Restarted the application:

```powershell
kubectl rollout restart deployment/wealthops -n wealthops
```

> The local secret manifest contains sensitive values and must remain excluded from Git.

---

## Incorrect Kubernetes Deployment YAML

Initial errors included:

```text
unknown field "spec.template.spec.replicas"
unknown field "spec.template.spec.selector"
```

### Cause

Kubernetes Deployment fields were placed at incorrect levels in the YAML hierarchy.

### Correct structure

```text
Deployment
└── spec
    ├── replicas
    ├── selector
    └── template
        └── spec
            └── containers
```

---

## ECR Image Pull Problems

### Kind

The local Kind environment uses an ECR image pull secret:

```text
ECR
  |
  v
ECR credentials
  |
  v
Kubernetes Secret
ecr-secret
  |
  v
imagePullSecrets
  |
  v
WealthOps Pod
```

### EKS

The EKS environment uses the worker node IAM role for ECR access instead of the local pull secret.

```text
EKS Worker Node
      |
      v
Node IAM Role
      |
      v
ECR Read Permissions
      |
      v
Private ECR
```

---

## Ingress Resource Not Found

Always verify the actual resource name:

```powershell
kubectl get ingress -n wealthops
```

Then use:

```powershell
kubectl describe ingress <actual-name> -n wealthops
```

The local and EKS environments intentionally use different ingress resources:

```text
Local:
wealthops-ingress

EKS:
wealthops-alb
```

---

## Wrong Kubernetes Context

Before applying or deleting resources:

```powershell
kubectl config current-context
```

If required:

```powershell
kubectl config use-context <context>
```

---

# Useful Commands

## Cluster

```powershell
kubectl cluster-info
kubectl get nodes
kubectl get namespaces
kubectl config current-context
kubectl config get-contexts
```

## WealthOps Namespace

```powershell
kubectl get all -n wealthops
kubectl get pods -n wealthops
kubectl get svc -n wealthops
kubectl get pvc -n wealthops
```

## WealthOps Logs

```powershell
kubectl logs deployment/wealthops -n wealthops
```

## PostgreSQL Logs

```powershell
kubectl logs deployment/postgres -n wealthops
```

## Deployment

```powershell
kubectl get deployment wealthops -n wealthops
kubectl describe deployment wealthops -n wealthops
kubectl rollout status deployment/wealthops -n wealthops
kubectl rollout restart deployment/wealthops -n wealthops
```

## Services

```powershell
kubectl get svc -n wealthops
kubectl describe svc wealthops -n wealthops
kubectl get endpoints -n wealthops
```

## Ingress

```powershell
kubectl get ingress -n wealthops
kubectl describe ingress wealthops-alb -n wealthops
```

## EKS Pod Identity

```powershell
.\eksctl get podidentityassociation `
  --cluster wealthops-eks `
  --region us-east-1
```

## Helm

```powershell
helm list -A
helm repo list
helm search repo eks/aws-load-balancer-controller
helm status aws-load-balancer-controller -n kube-system
```

## AWS Load Balancer Controller

```powershell
kubectl get deployment `
  aws-load-balancer-controller `
  -n kube-system

kubectl get pods -n kube-system |
Select-String aws-load-balancer
```

---

# Security Considerations

The current implementation is a production-style POC. The following improvements are planned for production hardening.

## Current Practices

- Application credentials are injected through Kubernetes Secrets.
- AWS permissions are separated by workload.
- EKS workloads use IAM-based access instead of embedded AWS access keys.
- ECR is private.
- The AWS Load Balancer Controller has a dedicated IAM role.
- The EBS CSI Controller has a dedicated IAM role.
- The EKS provisioning role is separate from application runtime identities.
- Local secret manifests are excluded from source control.

## Planned Production Improvements

```text
AWS Secrets Manager
        |
        v
External Secrets
        |
        v
Kubernetes Secret
        |
        v
WealthOps Pod
```

Additional improvements:

- IAM least-privilege review
- IAM Identity Center / federation instead of long-lived IAM users
- Network isolation and private subnets
- AWS WAF
- HTTPS using ACM
- Domain-based routing
- RDS instead of PostgreSQL running inside the application cluster
- Kubernetes NetworkPolicies
- Resource requests and limits
- Pod security controls
- Container image scanning
- Image version pinning instead of `latest`
- Automated database migrations using Alembic

---

# Current Status

## Application

- [x] Flask application
- [x] Layered application structure
- [x] PostgreSQL integration
- [x] Upstox OAuth integration
- [x] Upstox holdings synchronization
- [x] Dashboard
- [x] Privacy mode for dashboard financial values

## Containerization

- [x] Dockerfile
- [x] Docker image build
- [x] Amazon ECR repository
- [x] Private ECR image

## Local Kubernetes

- [x] Kind cluster
- [x] WealthOps namespace
- [x] PostgreSQL
- [x] Persistent storage
- [x] NGINX Ingress
- [x] Local TLS
- [x] Local DNS
- [x] Local OAuth callback

## Amazon EKS

- [x] EKS cluster
- [x] Managed node group
- [x] Two healthy worker nodes
- [x] ECR image pull through node IAM
- [x] WealthOps Deployment
- [x] PostgreSQL Deployment
- [x] EBS gp3 persistent storage
- [x] EBS CSI Driver
- [x] EKS Pod Identity Agent
- [x] EBS CSI Pod Identity
- [x] AWS Load Balancer Controller
- [x] Load Balancer Controller Pod Identity
- [x] Helm
- [x] Kubernetes Ingress
- [x] Internet-facing AWS ALB
- [x] WealthOps accessible through AWS ALB DNS

## Current Public AWS Architecture

```text
Internet
   |
   v
AWS ALB
   |
   v
Kubernetes Ingress
   |
   v
WealthOps Service
   |
   v
WealthOps Pod
   |
   v
PostgreSQL
   |
   v
EBS gp3
```

---

# Roadmap

## Phase 1 - Application

- [x] Flask application
- [x] PostgreSQL
- [x] Upstox OAuth
- [x] Portfolio synchronization
- [x] Dashboard

## Phase 2 - Containerization

- [x] Docker
- [x] Amazon ECR

## Phase 3 - Local Kubernetes

- [x] Kind
- [x] Kubernetes Deployment
- [x] Kubernetes Services
- [x] PostgreSQL persistence
- [x] NGINX Ingress
- [x] Local TLS

## Phase 4 - AWS EKS

- [x] EKS cluster
- [x] Managed node group
- [x] ECR integration
- [x] IAM
- [x] EBS CSI
- [x] EKS Pod Identity
- [x] Helm
- [x] AWS Load Balancer Controller
- [x] Internet-facing ALB

## Phase 5 - Production Hardening

- [ ] GitLab CI/CD
- [ ] Automated Docker build
- [ ] Automated ECR push
- [ ] Automated EKS deployment
- [ ] Image versioning / immutable tags
- [ ] AWS Secrets Manager
- [ ] External Secrets
- [ ] HTTPS / ACM
- [ ] Domain-based routing
- [ ] AWS WAF
- [ ] CloudWatch logging
- [ ] Prometheus / Grafana
- [ ] Resource requests and limits
- [ ] Horizontal Pod Autoscaler
- [ ] Alembic migrations
- [ ] Amazon RDS for PostgreSQL
- [ ] Backup and disaster recovery
- [ ] Security scanning

---

# Interview Perspective

WealthOps is positioned as a **production-style hands-on cloud and DevOps implementation**, rather than simply a sample Flask application.

### Short Interview Summary

> I designed and deployed a containerized WealthOps application on Amazon EKS. I integrated Amazon ECR for private image delivery, configured IAM-based access for EKS worker nodes and Kubernetes controllers, implemented EKS Pod Identity for workload-level AWS permissions, configured persistent PostgreSQL storage through the EBS CSI Driver, and used Helm to deploy the AWS Load Balancer Controller. Kubernetes Ingress was then used to provision an internet-facing AWS Application Load Balancer and route traffic to the application.

### Key Architecture Concepts Demonstrated

```text
Docker
   |
   v
Amazon ECR
   |
   v
Amazon EKS
   |
   +---- IAM / Node Role
   |
   +---- EKS Pod Identity
   |        |
   |        +---- EBS CSI Controller
   |        |
   |        +---- AWS Load Balancer Controller
   |
   +---- EBS CSI / gp3
   |
   +---- Kubernetes Service
   |
   +---- Kubernetes Ingress
   |
   v
AWS Application Load Balancer
```

### Strong Interview Talking Points

#### ECR

> EKS worker nodes use their IAM role to pull private container images from ECR, avoiding AWS credentials inside application Pods.

#### Pod Identity

> Kubernetes ServiceAccounts identify workloads, while EKS Pod Identity provides the secure mapping to AWS IAM roles and enables temporary AWS credentials for those workloads.

#### EBS CSI

> The EBS CSI Controller communicates with AWS to manage volumes, while the EBS CSI Node component mounts those volumes on worker nodes.

#### Helm

> Helm is used to package and manage Kubernetes components. In WealthOps, Helm was used to install and manage the AWS Load Balancer Controller.

#### ALB

> Kubernetes Ingress defines the desired routing, while the AWS Load Balancer Controller translates that configuration into an AWS Application Load Balancer and associated AWS resources.

#### Local vs EKS

> Local development uses Kind and NGINX Ingress with local TLS, while the AWS deployment uses EKS, the AWS Load Balancer Controller, and an internet-facing ALB.

---

# Final Architecture Summary

```text
                         WealthOps
                            |
              +-------------+-------------+
              |                           |
              v                           v
        Local Kind                    AWS EKS
              |                           |
              v                           v
       NGINX Ingress             AWS Load Balancer
              |                    Controller
              v                           |
      Local HTTPS/TLS                    v
              |                    Kubernetes Ingress
              v                           |
          WealthOps                      v
                                       AWS ALB
                                         |
                                         v
                                    WealthOps
                                         |
                                         v
                                    PostgreSQL
                                         |
                                         v
                                      EBS gp3


              AWS IAM / EKS Pod Identity
                         |
            +------------+------------+
            |                         |
            v                         v
       EBS CSI Controller      ALB Controller
            |                         |
            v                         v
       EBS APIs                  ALB APIs
```

This provides a complete progression from **local containerized development to a cloud-native Kubernetes deployment on AWS EKS**.
