import io
import zipfile

import requests
import threading

import os 
import json
from base64 import b64encode

from flask import Flask, request
from flask import request, jsonify
from flask import render_template

import actions_tools 


#-----------------------------------------------------------------------------#
#-----------------------------------------------------------------------------#
def cloud_function(request):
    internal_ctx = app.test_request_context(path=request.full_path,
                                            method=request.method)
    
    internal_ctx.request.data = request.data
    internal_ctx.request.headers = request.headers
    
    internal_ctx.push()
    return_value = app.full_dispatch_request()

    internal_ctx.pop()
    return return_value

app = Flask("internal")


#-----------------------------------------------------------------------------#
#-----------------------------------------------------------------------------#
"""
app = Flask(__name__, template_folder='./')  

@app.route('/')
def home():
    return render_template('index.html')  

#"""

#-----------------------------------------------------------------------------#
@app.route('/trigger_workflow/<string:file_name>', methods=['GET', 'POST'])
def trigger_workflow(file_name):
    run_id = actions_tools.trigger_github_workflow(file_name+".yaml") 
    print(f"[trigger_workflow] run_id:'{run_id}'")
    return jsonify({'run_id':run_id}), 200 
  
  
#-----------------------------------------------------------------------------#
@app.route('/check_status/<string:run_id>', methods=['GET', 'POST'])
def check_status(run_id):
    print(f"[check_status] Raw Data:'{request.data}'")    
    print(f"[check_status] Request Headers:'{request.headers}'")

    try:
        json_data = json.loads(request.data.decode('utf-8')) 
        print(f"[check_status] Parsed JSON: {json_data}")
    except json.JSONDecodeError as e:
        print(f"[check_status] Error decoding JSON: {str(e)}")
        json_data = None

    status = actions_tools.fetch_workflow_run_details(run_id) 
    print(f"[check_status] run_id:'{run_id}' status:'{status}' ")
    return jsonify({'status': status, 'run_id':run_id}), 200 

  
#-----------------------------------------------------------------------------#
@app.route('/get_artifact/<string:run_id>', methods=['GET', 'POST'])
def get_artifact(run_id) :
    print(f"[get_artifact] Raw Data:'{request.data}'")    
    print(f"[get_artifact] Request Headers:'{request.headers}'")

    json_data = None
    try:
        json_data = json.loads(request.data.decode('utf-8')) 
    except json.JSONDecodeError as e:
        print(f"[get_artifact] Error decoding JSON: {str(e)}")        
    print(f"[get_artifact] Parsed JSON: {json_data}")

    message_data = {} 

    file_name = json_data.get("file_name")
    extract_to = json_data.get("extract_to")
    artifact_name = json_data.get("artifact_name")

    if actions_tools.check_run_status(run_id) :
        artifact_zip = actions_tools.download_artifact(run_id, artifact_name)
        actions_tools.extract_artifact(artifact_name, artifact_zip, extract_to)

        print("[get_artifact] files:", os.listdir(extract_to))

        try : 
          file = open(f"{extract_to}/{file_name}", 'r') 
          print(f"[get_artifact] file:'{file}' ")
          content = file.read()
          print(f"[get_artifact] content:'{content}' ")
          message_data = content
          #message_data = json.load(file)
        except Exception as e:
          message_data = f"{e}"

    print(f"[get_artifact] message_data:'{message_data}'")    
    return jsonify({"artifact": message_data}), 200 


#-----------------------------------------------------------------------------#    
"""
if __name__ == '__main__':
    app.run(debug=True)
"""
    
#-----------------------------------------------------------------------------#    
"""

curl.exe https://simplest-rest-api.glitch.me/items

Invoke-RestMethod -Uri "https://simplest-rest-api.glitch.me/items" -Method POST -Headers @{ "Content-Type" = "application/json" } -Body '{"id": 4, "name": "Item 4"}'

https://github.com/jmake/GlitchSimplestApi/tree/main

"""

#-----------------------------------------------------------------------------#
"""
## gcloud functions -> 

app = Flask("internal")

def cloud_function(request):
    internal_ctx = app.test_request_context(path=request.full_path,
                                            method=request.method)
    
    internal_ctx.request.data = request.data
    internal_ctx.request.headers = request.headers
    
    internal_ctx.push()
    return_value = app.full_dispatch_request()

    internal_ctx.pop()
    return return_value

#SEE:
#https://medium.com/google-cloud/use-multiple-paths-in-cloud-functions-python-and-flask-fc6780e560d3
"""