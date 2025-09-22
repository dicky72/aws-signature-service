# api/index.py - VERSI BERSIH

from flask import Flask, request, jsonify
import boto3
from botocore.auth import SigV4Auth
from botocore.awsrequest import AWSRequest
from botocore.credentials import Credentials
from datetime import datetime
import json
import traceback

app = Flask(__name__)

# Route ini akan diakses melalui /textract-signature
@app.route('/textract-signature', methods=['POST'])
def generate_textract_signature():
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No JSON data provided'
            }), 400
        
        required_fields = ['access_key', 'secret_key']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        access_key = data.get('access_key')
        secret_key = data.get('secret_key')
        region = data.get('region', 'us-east-1')
        
        service = 'textract'
        method = 'POST'
        url = f'https://textract.{region}.amazonaws.com/'
        
        headers = {
            'Content-Type': 'application/x-amz-json-1.1',
            'X-Amz-Target': 'Textract.AnalyzeDocument'
        }
        
        document_bytes = data.get('document_bytes', '')
        feature_types = data.get('feature_types', ['TABLES', 'FORMS'])
        
        request_body = {
            'Document': {
                'Bytes': document_bytes
            },
            'FeatureTypes': feature_types
        }
        
        body_string = json.dumps(request_body, separators=(',', ':'))
        
        aws_request = AWSRequest(
            method=method,
            url=url,
            data=body_string,
            headers=headers
        )
        
        credentials = Credentials(
            access_key=access_key,
            secret_key=secret_key
        )
        
        SigV4Auth(credentials, service, region).add_auth(aws_request)
        
        return jsonify({
            'success': True,
            'signed_headers': dict(aws_request.headers),
            'body': request_body,
            'url': url,
            'method': method,
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        })
        
    except Exception as e:
        error_trace = traceback.format_exc()
        print(f"Error in generate_textract_signature: {error_trace}")
        
        return jsonify({
            'success': False,
            'error': str(e),
            'type': 'signature_generation_error'
        }), 500

# Route ini akan diakses melalui /health
@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'healthy',
        'service': 'AWS Signature Generator',
        'version': '1.0.0',
        'timestamp': datetime.utcnow().isoformat() + 'Z'
    })

# Route ini akan diakses melalui /
@app.route('/', methods=['GET'])
def root():
    return jsonify({
        'message': 'AWS Signature Service is running!',
        'note': 'This is the root of the Flask app, accessible via the /api path.',
        'endpoints': {
            'health': '/api/health',
            'textract_signature': '/api/textract-signature'
        }
    })

# Export untuk Vercel
handler = app

