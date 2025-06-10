from flask import Flask, request, Response
from app import app as flask_app
import json

# This is the entry point for Vercel serverless functions
def handler(event, context):
    """Handle serverless function requests"""
    try:
        # Get the request path and method
        path = event.get('path', '/')
        method = event.get('httpMethod', 'GET')
        
        # Get headers and query parameters
        headers = event.get('headers', {})
        query_params = event.get('queryStringParameters', {}) or {}
        
        # Get request body
        body = event.get('body', '')
        if body and headers.get('content-type') == 'application/json':
            body = json.loads(body)
        
        # Create a Flask test request context
        with flask_app.test_request_context(
            path=path,
            method=method,
            headers=headers,
            query_string=query_params,
            json=body if method in ['POST', 'PUT', 'PATCH'] else None
        ):
            # Process the request
            response = flask_app.full_dispatch_request()
            
            # Convert Flask response to API Gateway format
            return {
                'statusCode': response.status_code,
                'headers': dict(response.headers),
                'body': response.get_data(as_text=True)
            }
            
    except Exception as e:
        # Log the error and return a 500 response
        print(f"Error in handler: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'error': 'Internal server error',
                'message': str(e)
            })
        } 