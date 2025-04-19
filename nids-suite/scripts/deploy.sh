#!/bin/bash

# NIDS Suite Deployment Script

# Exit immediately if a command exits with a non-zero status
set -e

# Function to display usage
usage() {
    echo "Usage: $0 [options]"
    echo "Options:"
    echo "  -h, --help          Show this help message"
    echo "  -d, --docker        Deploy using Docker"
    echo "  -k, --kubernetes    Deploy to Kubernetes"
}

# Parse command line arguments
while [[ "$#" -gt 0 ]]; do
    case $1 in
        -h|--help) usage; exit 0 ;;
        -d|--docker) DEPLOY_DOCKER=true; shift ;;
        -k|--kubernetes) DEPLOY_K8S=true; shift ;;
        *) echo "Unknown option: $1"; usage; exit 1 ;;
    esac
done

# Load environment variables
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

# Build frontend
echo "Building frontend..."
cd frontend
pnpm install
pnpm build
cd ..

# Build backend
echo "Building backend..."
cd api-gateway
pnpm install
cd ..

# Deploy using Docker
if [ "$DEPLOY_DOCKER" = true ]; then
    echo "Deploying using Docker..."
    docker-compose up -d --build
fi

# Deploy to Kubernetes
if [ "$DEPLOY_K8S" = true ]; then
    echo "Deploying to Kubernetes..."
    kubectl apply -f k8s/
fi

echo "Deployment completed successfully!"