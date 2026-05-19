"""
CROM Azure Web App
Flask application that integrates with Azure Storage and Logic App
"""

import logging
import os
import sys
import json
from datetime import datetime
from flask import Flask, render_template, jsonify

try:
    from azure.storage.blob import BlobServiceClient
except ImportError:
    BlobServiceClient = None

import requests

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Add debugging to startup
print(f"Python version: {sys.version}", file=sys.stderr)
print(f"Current directory: {os.getcwd()}", file=sys.stderr)

# Initialize Flask app
app = Flask(__name__)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

logger.info("Starting CROM Flask application")

# Azure configuration
STORAGE_ACCOUNT_NAME = os.getenv('STORAGE_ACCOUNT_NAME', 'sacromblobstorage')
STORAGE_ACCOUNT_KEY = os.getenv('STORAGE_ACCOUNT_KEY', '')
LOGIC_APP_ENDPOINT = os.getenv('LOGIC_APP_ENDPOINT', 
    'https://prod-15.eastus.logic.azure.com:443/workflows/1906dffc4adc4cdbae960cb5235ef7c3/triggers/When_an_HTTP_request_is_received/paths/invoke?api-version=2016-10-01&sp=%2Ftriggers%2FWhen_an_HTTP_request_is_received%2Frun&sv=1.0&sig=5MxclMj9Q21lN8sMTV-S2HfQOzWqKcjWAD8GgiR84a0')
STORES_LOGIC_APP_ENDPOINT = os.getenv('STORES_LOGIC_APP_ENDPOINT',
    'https://prod-73.eastus.logic.azure.com:443/workflows/edb28f944da841b88fa8d0d923184675/triggers/When_an_HTTP_request_is_received_for_Stores_JSON_Blob/paths/invoke?api-version=2016-10-01&sp=%2Ftriggers%2FWhen_an_HTTP_request_is_received_for_Stores_JSON_Blob%2Frun&sv=1.0&sig=i_6b1gJASPMJWeW4FhZzlkzXe8zraSJfhZVTQzqHj6E')
TRAILS_LOGIC_APP_ENDPOINT = os.getenv('TRAILS_LOGIC_APP_ENDPOINT',
    'https://prod-01.eastus.logic.azure.com:443/workflows/a242a369510e4466b7853ef987c6ca16/triggers/When_an_HTTP_request_is_received_for_Trails_JSON_Blob/paths/invoke?api-version=2016-10-01&sp=%2Ftriggers%2FWhen_an_HTTP_request_is_received_for_Trails_JSON_Blob%2Frun&sv=1.0&sig=azNDWbRjc6lTY3-JcxI5S5ABem00IhCf98MM1WMGx0g')

logger.info(f"Storage account: {STORAGE_ACCOUNT_NAME}")
logger.info("Configuration loaded successfully")


def get_blob_service_client():
    """Initialize and return Azure Blob Service Client"""
    try:
        connection_string = f"DefaultEndpointsProtocol=https;AccountName={STORAGE_ACCOUNT_NAME};AccountKey={STORAGE_ACCOUNT_KEY};EndpointSuffix=core.windows.net"
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        logger.info("Blob Service Client initialized successfully")
        return blob_service_client
    except Exception as e:
        logger.error(f"Error initializing Blob Service Client: {str(e)}")
        return None


def list_blob_containers():
    """
    Stub function to list blob containers from Azure Storage
    Returns a list of container names
    """
    try:
        blob_service_client = get_blob_service_client()
        if blob_service_client is None:
            logger.warning("Blob Service Client is None, returning empty list")
            return []
        
        containers = blob_service_client.list_containers()
        container_list = [container.name for container in containers]
        logger.info(f"Retrieved {len(container_list)} containers")
        return container_list
    except Exception as e:
        logger.error(f"Error listing containers: {str(e)}")
        return []


def get_blob_data(container_name, blob_name):
    """
    Stub function to retrieve blob data from Azure Storage
    Args:
        container_name: Name of the blob container
        blob_name: Name of the blob file
    Returns:
        Blob data as string or None if error occurs
    """
    try:
        blob_service_client = get_blob_service_client()
        if blob_service_client is None:
            logger.warning("Blob Service Client is None")
            return None
        
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
        blob_data = blob_client.download_blob().readall()
        logger.info(f"Retrieved blob: {blob_name} from container: {container_name}")
        return blob_data.decode('utf-8')
    except Exception as e:
        logger.error(f"Error retrieving blob {blob_name} from {container_name}: {str(e)}")
        return None


@app.route('/')
def home():
    """Root route - displays welcome message"""
    logger.info("Home route accessed")
    return render_template('index.html')


@app.route('/api/call-logic-app', methods=['GET', 'POST'])
def call_logic_app():
    """
    Call the Azure Logic App endpoint and return the response
    Logs the HTTP response and returns success/failure message with JSON data
    """
    try:
        logger.info("Calling Logic App endpoint")
        
        # Make HTTP request to Logic App
        response = requests.get(LOGIC_APP_ENDPOINT, timeout=30)
        
        # Log the response
        logger.info(f"Logic App response status: {response.status_code}")
        logger.info(f"Logic App response body: {response.text}")
        
        # Check if request was successful
        if response.status_code == 200:
            try:
                response_json = response.json()
            except:
                response_json = {"raw_response": response.text}
            
            return jsonify({
                "status": "success",
                "message": "Logic App call succeeded",
                "data": response_json
            }), 200
        else:
            return jsonify({
                "status": "error",
                "message": f"Logic App call failed with status {response.status_code}",
                "details": response.text
            }), response.status_code
            
    except requests.exceptions.Timeout:
        logger.error("Logic App request timed out")
        return jsonify({
            "status": "error",
            "message": "Logic App call timed out"
        }), 504
    except Exception as e:
        logger.error(f"Error calling Logic App: {str(e)}")
        return jsonify({
            "status": "error",
            "message": "Error calling Logic App",
            "details": str(e)
        }), 500


@app.route('/api/call-logic-app-json', methods=['GET', 'POST'])
def call_logic_app_json():
    """
    Route to call the Logic App endpoint and return JSON response.
    Sends GET request to the Logic App, logs the response, and returns JSON.
    """
    logger.info("Logic App JSON call initiated")
    
    try:
        # Send GET request to the Logic App
        response = requests.get(LOGIC_APP_ENDPOINT, timeout=30)
        
        # Log the response
        logger.info(f"Logic App Response Status: {response.status_code}")
        logger.info(f"Logic App Response Headers: {response.headers}")
        logger.info(f"Logic App Response Body: {response.text}")
        
        # Check if request was successful
        if response.status_code == 200:
            try:
                response_json = response.json()
                response_data = response_json
            except:
                response_data = response.text
            
            result = {
                "status": "success",
                "message": "Logic App call succeeded",
                "status_code": response.status_code,
                "response": response_data,
                "timestamp": datetime.utcnow().isoformat()
            }
        else:
            try:
                response_data = response.json()
            except:
                response_data = response.text
            
            result = {
                "status": "error",
                "message": f"Logic App returned status code {response.status_code}",
                "status_code": response.status_code,
                "response": response_data,
                "timestamp": datetime.utcnow().isoformat()
            }
        
        return jsonify(result), response.status_code
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Error calling Logic App: {str(e)}")
        
        return jsonify({
            "status": "error",
            "message": f"Failed to call Logic App endpoint",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }), 500


@app.route('/api/blobs', methods=['GET'])
def get_blobs():
    """
    Endpoint to retrieve available blobs from the json container
    Returns list of blob metadata
    """
    try:
        logger.info("Fetching blobs from json container")
        blob_service_client = get_blob_service_client()
        
        if blob_service_client is None:
            return jsonify({
                "status": "error",
                "message": "Unable to connect to Storage Account"
            }), 500
        
        container_name = "json"
        blob_client = blob_service_client.get_container_client(container_name)
        blobs = blob_client.list_blobs()
        
        blob_list = [{"name": blob.name, "size": blob.size} for blob in blobs]
        logger.info(f"Retrieved {len(blob_list)} blobs from json container")
        
        return jsonify({
            "status": "success",
            "blobs": blob_list
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching blobs: {str(e)}")
        return jsonify({
            "status": "error",
            "message": "Error fetching blobs",
            "details": str(e)
        }), 500


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for monitoring"""
    logger.info("Health check requested")
    return jsonify({"status": "healthy"}), 200


@app.route('/api/get-stores-json', methods=['GET', 'POST'])
def call_logic_app_stores_json():
    """
    Route to call the Stores Logic App endpoint and return JSON response.
    Sends GET request to the Stores Logic App, logs the response, and returns JSON.
    """
    logger.info("Stores Logic App JSON call initiated")
    
    try:
        # Send GET request to the Stores Logic App
        response = requests.get(STORES_LOGIC_APP_ENDPOINT, timeout=30)
        
        # Log the response
        logger.info(f"Stores Logic App Response Status: {response.status_code}")
        logger.info(f"Stores Logic App Response Headers: {response.headers}")
        logger.info(f"Stores Logic App Response Body: {response.text}")
        
        # Check if request was successful
        if response.status_code == 200:
            try:
                response_json = response.json()
                response_data = response_json
            except:
                response_data = response.text
            
            result = {
                "status": "success",
                "message": "Stores Logic App call succeeded",
                "status_code": response.status_code,
                "response": response_data,
                "timestamp": datetime.utcnow().isoformat()
            }
        else:
            try:
                response_data = response.json()
            except:
                response_data = response.text
            
            result = {
                "status": "error",
                "message": f"Stores Logic App returned status code {response.status_code}",
                "status_code": response.status_code,
                "response": response_data,
                "timestamp": datetime.utcnow().isoformat()
            }
        
        return jsonify(result), response.status_code
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Error calling Stores Logic App: {str(e)}")
        
        return jsonify({
            "status": "error",
            "message": f"Failed to call Stores Logic App endpoint",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }), 500


@app.route('/api/get-trails-json', methods=['GET', 'POST'])
def call_logic_app_trails_json():
    """
    Route to call the Trails Logic App endpoint and return JSON response.
    Sends GET request to the Trails Logic App, logs the response, and returns JSON.
    """
    logger.info("Trails Logic App JSON call initiated")
    
    try:
        # Send GET request to the Trails Logic App
        response = requests.get(TRAILS_LOGIC_APP_ENDPOINT, timeout=30)
        
        # Log the response
        logger.info(f"Trails Logic App Response Status: {response.status_code}")
        logger.info(f"Trails Logic App Response Headers: {response.headers}")
        logger.info(f"Trails Logic App Response Body: {response.text}")
        
        # Check if request was successful
        if response.status_code == 200:
            try:
                response_json = response.json()
                response_data = response_json
            except:
                response_data = response.text
            
            result = {
                "status": "success",
                "message": "Trails Logic App call succeeded",
                "status_code": response.status_code,
                "response": response_data,
                "timestamp": datetime.utcnow().isoformat()
            }
        else:
            try:
                response_data = response.json()
            except:
                response_data = response.text
            
            result = {
                "status": "error",
                "message": f"Trails Logic App returned status code {response.status_code}",
                "status_code": response.status_code,
                "response": response_data,
                "timestamp": datetime.utcnow().isoformat()
            }
        
        return jsonify(result), response.status_code
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Error calling Trails Logic App: {str(e)}")
        
        return jsonify({
            "status": "error",
            "message": f"Failed to call Trails Logic App endpoint",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }), 500


@app.route('/api/call-logic-app-html', methods=['GET'])
def call_logic_app_html():
    """
    Route to call the Logic App endpoint and return HTML response.
    Sends GET request to the Logic App and renders the response as HTML.
    """
    logger.info("Logic App HTML call initiated")
    
    try:
        # Send GET request to the Logic App
        response = requests.get(LOGIC_APP_ENDPOINT, timeout=30)
        
        # Log the response
        logger.info(f"Logic App Response Status: {response.status_code}")
        
        # Check if request was successful
        if response.status_code == 200:
            try:
                response_data = response.json()
                # Format as HTML table if it's a list
                if isinstance(response_data, list):
                    html_content = "<table style='width:100%; border-collapse: collapse;'>"
                    if response_data and isinstance(response_data[0], dict):
                        # Create header row
                        html_content += "<thead><tr style='background-color: #667eea; color: white;'>"
                        for key in response_data[0].keys():
                            html_content += f"<th style='padding: 10px; text-align: left; border: 1px solid #ddd;'>{key}</th>"
                        html_content += "</tr></thead>"
                        
                        # Create data rows
                        html_content += "<tbody>"
                        for idx, item in enumerate(response_data):
                            row_color = "#f9f9f9" if idx % 2 == 0 else "white"
                            html_content += f"<tr style='background-color: {row_color};'>"
                            for value in item.values():
                                html_content += f"<td style='padding: 10px; border: 1px solid #ddd;'>{value}</td>"
                            html_content += "</tr>"
                        html_content += "</tbody>"
                    html_content += "</table>"
                else:
                    # For non-list responses, display as formatted JSON
                    html_content = f"<pre style='background-color: #f5f5f5; padding: 15px; border-radius: 5px; overflow-x: auto;'>{json.dumps(response_data, indent=2)}</pre>"
            except:
                response_data = response.text
                html_content = f"<pre style='background-color: #f5f5f5; padding: 15px; border-radius: 5px; overflow-x: auto;'>{response_data}</pre>"
            
            return f"""
            <html>
            <head>
                <title>CROM - Logic App Response</title>
                <style>
                    body {{
                        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        min-height: 100vh;
                        padding: 40px 20px;
                    }}
                    .container {{
                        max-width: 1200px;
                        margin: 0 auto;
                        background: white;
                        padding: 30px;
                        border-radius: 10px;
                        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
                    }}
                    h1 {{
                        color: #333;
                        border-bottom: 3px solid #667eea;
                        padding-bottom: 15px;
                    }}
                    .info {{
                        background-color: #f0f0f0;
                        padding: 15px;
                        border-radius: 5px;
                        margin-bottom: 20px;
                    }}
                    table {{
                        width: 100%;
                        border-collapse: collapse;
                    }}
                    th {{
                        background-color: #667eea;
                        color: white;
                        padding: 12px;
                        text-align: left;
                        border: 1px solid #ddd;
                    }}
                    td {{
                        padding: 10px;
                        border: 1px solid #ddd;
                    }}
                    .back-link {{
                        margin-top: 20px;
                    }}
                    .back-link a {{
                        color: #667eea;
                        text-decoration: none;
                        font-weight: bold;
                    }}
                    .back-link a:hover {{
                        text-decoration: underline;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>🚀 CROM - Logic App Response</h1>
                    <div class="info">
                        <p><strong>Status:</strong> Success</p>
                        <p><strong>Status Code:</strong> {response.status_code}</p>
                        <p><strong>Timestamp:</strong> {datetime.utcnow().isoformat()}</p>
                    </div>
                    <div>
                        {html_content}
                    </div>
                    <div class="back-link">
                        <a href="/">← Back to Home</a>
                    </div>
                </div>
            </body>
            </html>
            """, 200, {'Content-Type': 'text/html'}
        else:
            return f"""
            <html>
            <head>
                <title>CROM - Logic App Error</title>
                <style>
                    body {{
                        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        min-height: 100vh;
                        padding: 40px 20px;
                    }}
                    .container {{
                        max-width: 1200px;
                        margin: 0 auto;
                        background: white;
                        padding: 30px;
                        border-radius: 10px;
                        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
                    }}
                    .error {{
                        background-color: #f8d7da;
                        color: #721c24;
                        padding: 15px;
                        border-radius: 5px;
                        border-left: 4px solid #f5c6cb;
                    }}
                    .back-link {{
                        margin-top: 20px;
                    }}
                    .back-link a {{
                        color: #667eea;
                        text-decoration: none;
                        font-weight: bold;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>⚠️ CROM - Logic App Error</h1>
                    <div class="error">
                        <p><strong>Status Code:</strong> {response.status_code}</p>
                        <p><strong>Error:</strong> {response.text}</p>
                    </div>
                    <div class="back-link">
                        <a href="/">← Back to Home</a>
                    </div>
                </div>
            </body>
            </html>
            """, response.status_code, {'Content-Type': 'text/html'}
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Error calling Logic App: {str(e)}")
        
        return f"""
        <html>
        <head>
            <title>CROM - Logic App Error</title>
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    min-height: 100vh;
                    padding: 40px 20px;
                }}
                .container {{
                    max-width: 1200px;
                    margin: 0 auto;
                    background: white;
                    padding: 30px;
                    border-radius: 10px;
                    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
                }}
                .error {{
                    background-color: #f8d7da;
                    color: #721c24;
                    padding: 15px;
                    border-radius: 5px;
                    border-left: 4px solid #f5c6cb;
                }}
                .back-link {{
                    margin-top: 20px;
                }}
                .back-link a {{
                    color: #667eea;
                    text-decoration: none;
                    font-weight: bold;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>❌ CROM - Error</h1>
                <div class="error">
                    <p><strong>Error:</strong> {str(e)}</p>
                </div>
                <div class="back-link">
                    <a href="/">← Back to Home</a>
                </div>
            </div>
        </body>
        </html>
        """, 500, {'Content-Type': 'text/html'}
    # Run the app
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV', 'production') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug)
