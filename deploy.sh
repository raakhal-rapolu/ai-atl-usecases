#!/bin/bash

# Set variables
PROJECT_ID="<GCP_PROJECT_ID>"
REGION=us-central1
SERVICE_NAME="usecase-svc"

# Authenticate with GCP
gcloud auth configure-docker $REGION-docker.pkg.dev

# Build Docker image
docker build -t $REGION-docker.pkg.dev/$PROJECT_ID/$SERVICE_NAME .

# Push Docker image to Google Artifact Registry
docker push $REGION-docker.pkg.dev/$PROJECT_ID/$SERVICE_NAME

# Deploy to Cloud Run
gcloud run deploy $SERVICE_NAME \
  --image $REGION-docker.pkg.dev/$PROJECT_ID/$SERVICE_NAME \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --set-env-vars GEMINI_URL=$GEMINI_URL,ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY
