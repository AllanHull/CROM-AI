"""
CROM Azure Web App
Flask application that integrates with Azure Storage and Logic App
"""

import logging
import os
from flask import Flask, render_template, jsonify
from azure.storage.blob import BlobServiceClient
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Azure configuration
STORAGE_ACCOUNT_NAME = os.getenv('STORAGE_ACCOUNT_NAME', 'sacromblobstorage')
STORAGE_ACCOUNT_KEY = os.getenv('STORAGE_ACCOUNT_KEY', '')
LOGIC_APP_ENDPOINT = os.getenv('LOGIC_APP_ENDPOINT', 
    'https://prod-15.eastus.logic.azure.com:443/workflows/1906dffc4adc4cdbae960cb5235ef7c3/triggers/When_an_HTTP_request_is_received/paths/invoke?api-version=2016-10-01&sp=%2Ftriggers%2FWhen_an_HTTP_request_is_received%2Frun&sv=1.0&sig=5MxclMj9Q21lN8sMTV-S2HfQOzWqKcjWAD8GgiR84a0')


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


@app.route('/api/call-logic-app', methods=['POST'])
def call_logic_app():
    """
    Call the Azure Logic App endpoint and return the response
    Logs the HTTP response and returns success/failure message with JSON data
    """
    try:
        logger.info("Calling Logic App endpoint")
        
        # Make HTTP request to Logic App
        response = requests.post(LOGIC_APP_ENDPOINT, timeout=30)
        
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


if __name__ == '__main__':
    # Run the app
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV', 'production') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug)
