#!/bin/bash
# Koe — Cloud Run Deployment Script
# Fill in PROJECT, REGION, and secret values before running.
# Run from the repo root: bash setup/deploy.sh

set -e

PROJECT="your-gcp-project-id"
REGION="asia-south1"
BACKEND_IMAGE="gcr.io/$PROJECT/koe-backend"
MCP_IMAGE="gcr.io/$PROJECT/koe-mcp-server"

echo "=== Deploying Koe to Cloud Run ==="

# Upload model assets to Cloud Storage
echo "--- Uploading model assets ---"
gsutil -m cp model/koe_models/koe_mlp.tflite       gs://$PROJECT-koe-models/koe_models/
gsutil -m cp model/koe_models/koe_model_config.json gs://$PROJECT-koe-models/koe_models/
gsutil -m cp model/koe_models/label_encoder.pkl     gs://$PROJECT-koe-models/koe_models/
gsutil -m cp model/koe_models/X_mean.npy            gs://$PROJECT-koe-models/koe_models/
gsutil -m cp model/koe_models/X_std.npy             gs://$PROJECT-koe-models/koe_models/

# Build and push backend
echo "--- Building backend ---"
docker build -t $BACKEND_IMAGE ./koe-backend
docker push $BACKEND_IMAGE

# Deploy MCP server first (backend depends on its URL)
echo "--- Deploying MCP server ---"
gcloud run deploy koe-mcp-server \
  --image $MCP_IMAGE \
  --region $REGION \
  --platform managed \
  --no-allow-unauthenticated \
  --port 8081 \
  --memory 512Mi \
  --min-instances 0 \
  --max-instances 5

MCP_URL=$(gcloud run services describe koe-mcp-server \
  --region $REGION --format "value(status.url)")

echo "MCP server URL: $MCP_URL"

# Deploy backend
echo "--- Deploying backend ---"
gcloud run deploy koe-backend \
  --image $BACKEND_IMAGE \
  --region $REGION \
  --platform managed \
  --no-allow-unauthenticated \
  --port 8080 \
  --memory 2Gi \
  --min-instances 0 \
  --max-instances 10 \
  --set-secrets "GOOGLE_API_KEY=koe-google-api-key:latest,CLERK_SECRET_KEY=koe-clerk-secret:latest" \
  --set-env-vars "GOOGLE_CLOUD_PROJECT=$PROJECT,BIGQUERY_DATASET=koe_analytics,FIRESTORE_PROJECT=$PROJECT,MODEL_BUCKET=$PROJECT-koe-models,MCP_SERVER_URL=$MCP_URL,TTS_LANGUAGE_CODES=en-US,ur-PK"

BACKEND_URL=$(gcloud run services describe koe-backend \
  --region $REGION --format "value(status.url)")

echo ""
echo "=== Deploy complete ==="
echo "Backend:    $BACKEND_URL"
echo "MCP server: $MCP_URL"
echo ""
echo "Set VITE_API_URL=$BACKEND_URL in Vercel environment variables."
