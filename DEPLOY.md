# Deploying Nivaran AI to GCP with Docker

This guide explains how to deploy the Nivaran AI application to Google Cloud Platform using Docker and Cloud Run.

## Prerequisites

1. [Docker](https://docs.docker.com/get-docker/) installed locally
2. [Google Cloud SDK](https://cloud.google.com/sdk/docs/install) installed and configured
3. A Google Cloud Platform account with billing enabled
4. Access to the Google Container Registry (GCR) and Cloud Run services

## Setup

1. Create or select a Google Cloud Project:

   ```
   gcloud projects create [PROJECT_ID] --name="Nivaran AI"
   gcloud config set project [PROJECT_ID]
   ```

2. Enable required APIs:

   ```
   gcloud services enable containerregistry.googleapis.com
   gcloud services enable run.googleapis.com
   ```

3. Authenticate Docker with GCR:

   ```
   gcloud auth configure-docker
   ```

4. Configure the deployment script:

   Edit `deploy-gcp.sh` and update:

   - `PROJECT_ID` with your GCP project ID
   - `REGION` with your preferred GCP region
   - `SERVICE_NAME` as desired
   - Add any environment variables needed by your application

## Environment Variables

Create a `.env` file in your project (this won't be included in the Docker image, you'll set these in Cloud Run):

```
OPENAI_API_KEY=your_openai_api_key
# Add other required environment variables here
```

## Deployment

1. Make the deployment script executable:

   ```
   chmod +x deploy-gcp.sh
   ```

2. Run the deployment script:

   ```
   ./deploy-gcp.sh
   ```

3. Set environment variables in Cloud Run:
   ```
   gcloud run services update nivaran-ai-service \
     --update-env-vars="OPENAI_API_KEY=your_key_here" \
     --region=asia-south1
   ```

## Manual Deployment Steps

If you prefer to run the commands manually:

1. Build the Docker image:

   ```
   docker build -t gcr.io/[PROJECT_ID]/nivaran-ai-app .
   ```

2. Push to Container Registry:

   ```
   docker push gcr.io/[PROJECT_ID]/nivaran-ai-app
   ```

3. Deploy to Cloud Run:
   ```
   gcloud run deploy nivaran-ai-service \
     --image gcr.io/[PROJECT_ID]/nivaran-ai-app \
     --platform managed \
     --region asia-south1 \
     --allow-unauthenticated \
     --memory 512Mi
   ```

## Continuous Deployment

For continuous deployment, consider setting up a [Google Cloud Build](https://cloud.google.com/build) pipeline or using GitHub Actions to automate the build and deployment process.
