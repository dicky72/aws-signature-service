from flask import Flask, request, jsonify
import boto3
from botocore.auth import SigV4Auth
from botocore.awsrequest import AWSRequest
from botocore.credentials import Credentials
from datetime import datetime
import json

app = Flask(__name__)

@app.route('/api/textract-signature', methods=['POST'])
def generate_textract_signature():
    try:
        data = request.json
        
        # AWS credentials
        access_key = data.get('access_key')
        secret_key = data.get('secret_key')
        region = data.get('region', 'us-east-1')
        
        # Textract specific setup
        service = 'textract'
        method = 'POST'
        url = f'https://textract.{region}.amazonaws.com/'
        
        # Headers
        headers = {
            'Content-Type': 'application/x-amz-json-1.1',
            'X-Amz-Target': 'Textract.AnalyzeDocument'
        }
        
        # Body (dari n8n)
        document_bytes = data.get('document_bytes')
        feature_types = data.get('feature_types', ['TABLES', 'FORMS'])
        
        request_body = {
            'Document': {
                'Bytes': document_bytes
            },
            'FeatureTypes': feature_types
        }
        
        body_string = json.dumps(request_body, separators=(',', ':'))
        
        # Create and sign request
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
        
        # Return signed request data
        return jsonify({
            'success': True,
            'signed_headers': dict(aws_request.headers),
            'body': request_body,
            'url': url,
            'method': method
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy', 'service': 'AWS Signature Generator'})

# Export for Vercel
app = app