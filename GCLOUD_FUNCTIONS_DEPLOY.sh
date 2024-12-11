
gcloud functions deploy cloud_function \
    --runtime python310 \
    --trigger-http \
    --allow-unauthenticated
