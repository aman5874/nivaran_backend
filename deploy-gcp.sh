#!/bin/bash
set -e

# Configuration
PROJECT_ID="your-gcp-project-id"  # Replace with your actual GCP project ID
IMAGE_NAME="nivaran-ai-app"
REGION="asia-south1"  # Change to your preferred region
SERVICE_NAME="nivaran-ai-service"

# Build the Docker image
echo "Building Docker image..."
docker build -t "gcr.io/$PROJECT_ID/$IMAGE_NAME" .

# Push the image to Google Container Registry
echo "Pushing image to Google Container Registry..."
docker push "gcr.io/$PROJECT_ID/$IMAGE_NAME"

# Deploy to Cloud Run
echo "Deploying to Cloud Run..."
gcloud run deploy $SERVICE_NAME \
  --image "gcr.io/$PROJECT_ID/$IMAGE_NAME" \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --memory 512Mi \
  --set-env-vars="LOG_LEVEL=INFO"

echo "Deployment complete!"
echo "Your service will be available at the URL shown above." 