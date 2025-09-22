# api/index.py - COMPLETE FIXED VERSION

from flask import Flask, request, jsonify
import boto3
from botocore.auth import SigV4Auth
from botocore.awsrequest import AWSRequest
from botocore.credentials import Credentials
from datetime import datetime
import json
import traceback

app = Flask(__name__)

@app.route('/api/textract-signature', methods=['POST'])
def generate_textract_signature():
    try:
        # Get request data
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No JSON data provided'
            }), 400
        
        # Validate required fields
        required_fields = ['access_key', 'secret_key']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        # AWS credentials
        access_key = data.get('access_key')
        secret_key = data.get('secret_key')
        region = data.get('region', 'us-east-1')
        
        # Textract setup
        service = 'textract'
        method = 'POST'
        url = f'https://textract.{region}.amazonaws.com/'
        
        # Headers
        headers = {
            'Content-Type': 'application/x-amz-json-1.1',
            'X-Amz-Target': 'Textract.AnalyzeDocument'
        }
        
        # Request body
        document_bytes = data.get('document_bytes', '')
        feature_types = data.get('feature_types', ['TABLES', 'FORMS'])
        
        request_body = {
            'Document': {
                'Bytes': document_bytes
            },
            'FeatureTypes': feature_types
        }
        
        body_string = json.dumps(request_body, separators=(',', ':'))
        
        # Create AWS request
        aws_request = AWSRequest(
            method=method,
            url=url,
            data=body_string,
            headers=headers
        )
        
        # Create credentials
        credentials = Credentials(
            access_key=access_key,
            secret_key=secret_key
        )
        
        # Sign the request
        SigV4Auth(credentials, service, region).add_auth(aws_request)
        
        # Return signed request data
        return jsonify({
            'success': True,
            'signed_headers': dict(aws_request.headers),
            'body': request_body,
            'url': url,
            'method': method,
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        })
        
    except Exception as e:
        # Log error for debugging
        error_trace = traceback.format_exc()
        print(f"Error in generate_textract_signature: {error_trace}")
        
        return jsonify({
            'success': False,
            'error': str(e),
            'type': 'signature_generation_error'
        }), 500

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'healthy',
        'service': 'AWS Signature Generator',
        'version': '1.0.0',
        'timestamp': datetime.utcnow().isoformat() + 'Z'
    })

@app.route('/', methods=['GET'])
def root():
    return jsonify({
        'message': 'AWS Signature Service',
        'endpoints': {
            'health': '/api/health',
            'textract_signature': '/api/textract-signature'
        }
    })

# Export for Vercel
handler = app

if __name__ == '__main__':
    app.run(debug=True)