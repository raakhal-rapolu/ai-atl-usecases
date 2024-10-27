#!/bin/bash

# Set variables
PROJECT_ID=$(gcloud config get-value project)
REGION=us-central1
SERVICE_NAME="usecase-svc"
IMAGE="usecase-svc-image"
REPOSITORY="usecase-svc-repo"

# Authenticate with GCP
gcloud auth configure-docker $REGION-docker.pkg.dev -q

# Create the Artifact Registry repository if it doesn't exist
gcloud artifacts repositories create $REPOSITORY \
  --repository-format=docker \
  --location=$REGION \
  --description="Docker repository for usecase service" || true

# Build Docker image
docker build -t $REGION-docker.pkg.dev/$PROJECT_ID/$REPOSITORY/$IMAGE .

# Tag Docker image
docker tag $REGION-docker.pkg.dev/$PROJECT_ID/$REPOSITORY/$IMAGE $REGION-docker.pkg.dev/$PROJECT_ID/$REPOSITORY/$IMAGE:latest

# Push Docker image to Google Artifact Registry
docker push $REGION-docker.pkg.dev/$PROJECT_ID/$REPOSITORY/$IMAGE:latest

# Deploy to Cloud Run
gcloud run deploy $SERVICE_NAME \
  --image $REGION-docker.pkg.dev/$PROJECT_ID/$REPOSITORY/$IMAGE:latest \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \

echo "Deployment successful!"
