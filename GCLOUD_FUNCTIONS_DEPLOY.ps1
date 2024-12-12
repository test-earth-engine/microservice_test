

$GCLOUD="F:\z2024_11\UNDP\Github\google-cloud-sdk\bin\gcloud.ps1" 

$G_PROJECT=$(& $GCLOUD config get project)

<#
& $GCLOUD --version 

& $GCLOUD info


##  Cloud Run Admin API
& $GCLOUD services enable run.googleapis.com --project $G_PROJECT

& $GCLOUD services list --enabled 

& $GCLOUD functions list --project=$G_PROJECT
#>

function FUNCTION_DEPLOY
{
    & $GCLOUD functions deploy cloud_function `
    --project $G_PROJECT `
    --runtime python310 `
    --trigger-http `
    --allow-unauthenticated `
    --region us-central1
}

#FUNCTION_DEPLOY


$URL="https://us-central1-undp-population.cloudfunctions.net/cloud_function/workflow_dispatch"
(Invoke-WebRequest -Uri "$URL/abc").Content 


$URL="https://us-central1-undp-population.cloudfunctions.net/cloud_function/workflow_dispatch"
(Invoke-WebRequest -Uri "$URL/def").Content 

