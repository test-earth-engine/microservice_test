

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
    --runtime python312 `
    --trigger-http `
    --allow-unauthenticated `
    --region us-central1

    #$URL="https://us-central1-undp-population.cloudfunctions.net/cloud_function"
    #(Invoke-WebRequest -Uri "$URL/workflow_dispatch/test1").Content 
}

function __API_GACTIONS_STATUS_POST__
{
    $json_body = @{ key1 = "value1"; key2 = "value2" } | ConvertTo-Json -Depth 10
    Write-Output "Sending Body: $json_body"

    $workflow_id = "12289280715"
    $response = Invoke-WebRequest -Uri "$URL/check_status/$workflow_id" `
        -Method POST `
        -ContentType "application/json" `
        -Body $json_body `
        -Headers @{ "Accept" = "application/json" }
    echo "API_GACTIONS_STATUS_POST:", $response 

    #$content = $response.Content | ConvertFrom-Json
    #echo $content 
}


function API_GACTIONS_DISPATCH 
{
    param([string]$workflow_name, [string]$url)

    $response = Invoke-WebRequest -Uri "$url/trigger_workflow/${workflow_name}"
    $content = $response.Content | ConvertFrom-Json
    #echo "API_GACTIONS_DISPATCH:", $content 

    $workflow_id = $content.run_id    
    return $workflow_id
}


function API_GACTIONS_STATUS_GET
{
    param([string]$url, [string]$workflow_id)

    $response = Invoke-WebRequest -Uri "$url/check_status/$workflow_id"

    $content = $response.Content | ConvertFrom-Json
    #echo "API_GACTIONS_STATUS_GET:", $response.Content 

    $runId = $content.run_id
    $status = $content.status
    return $status
}


function API_GACTIONS_ARTIFACT_POST
{
    param([string]$url, [string]$workflow_id)

    $json_body = @{`
        file_name = "artifact_1.txt"; `
        extract_to = "extract_to"; `
        artifact_name = "artifact_name" `
    } | ConvertTo-Json -Depth 10

    Write-Output "Sending Body: $json_body"

    $response = Invoke-WebRequest -Uri "$url/get_artifact/$workflow_id" `
        -Body $json_body `
        -Method POST `
        -ContentType "application/json" `
        -Headers @{ "Accept" = "application/json" }

    $content = $response.Content | ConvertFrom-Json
    #echo "API_GACTIONS_ARTIFACT_POST:", $response.Content 

    $content = $response.Content | ConvertFrom-Json
    return $content.artifact 
}

## https://console.cloud.google.com/functions/details/us-central1/cloud_function?project=undp-population
#FUNCTION_DEPLOY
#$URL="https://us-central1-undp-population.cloudfunctions.net/cloud_function"

$URL="https://simplest-rest-api-a.glitch.me/"

##$workflow_id = 12300478184
$workflow_id = API_GACTIONS_DISPATCH -url $URL -workflow_name "simplest_workflow_dispatch"
echo "workflow_id:'$workflow_id'" 

while ($true) 
{
    $workflow_status = API_GACTIONS_STATUS_GET -url $URL -workflow_id $workflow_id
    echo "Current workflow_status: '$workflow_status'"

    if ($workflow_status -eq "completed") { break }
    Start-Sleep -Seconds 2
}

$workflow_response = API_GACTIONS_ARTIFACT_POST -url $URL -workflow_id $workflow_id
echo "workflow_response: $workflow_response"
