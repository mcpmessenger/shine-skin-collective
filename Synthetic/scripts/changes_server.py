#!/usr/bin/env python3
"""
HTTP Server for Dermatologist Changes API
Provides REST endpoints for saving changes made in the dermatologist tool
"""

import json
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from save_changes_api import DermatologistChangesAPI
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ChangesAPIHandler(BaseHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self.api = DermatologistChangesAPI(".")
        super().__init__(*args, **kwargs)
    
    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()
    
    def do_POST(self):
        """Handle POST requests"""
        try:
            # Parse URL
            parsed_url = urlparse(self.path)
            path = parsed_url.path
            
            # Get request body
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            
            if content_length > 0:
                try:
                    data = json.loads(post_data.decode('utf-8'))
                except json.JSONDecodeError:
                    self._send_error_response(400, "Invalid JSON in request body")
                    return
            else:
                data = {}
            
            # Route requests
            if path == '/api/move-image':
                self._handle_move_image(data)
            elif path == '/api/delete-image':
                self._handle_delete_image(data)
            elif path == '/api/batch-changes':
                self._handle_batch_changes(data)
            else:
                self._send_error_response(404, "Endpoint not found")
                
        except Exception as e:
            logger.error(f"Error handling POST request: {str(e)}")
            self._send_error_response(500, f"Internal server error: {str(e)}")
    
    def _handle_move_image(self, data):
        """Handle move image request"""
        required_fields = ['filename', 'oldCategory', 'oldSeverity', 'newCategory', 'newSeverity']
        
        if not all(field in data for field in required_fields):
            self._send_error_response(400, f"Missing required fields: {required_fields}")
            return
        
        result = self.api.move_image(
            data['filename'],
            data['oldCategory'],
            data['oldSeverity'],
            data['newCategory'],
            data['newSeverity']
        )
        
        self._send_json_response(200 if result['success'] else 400, result)
    
    def _handle_delete_image(self, data):
        """Handle delete image request"""
        required_fields = ['filename', 'category', 'severity']
        
        if not all(field in data for field in required_fields):
            self._send_error_response(400, f"Missing required fields: {required_fields}")
            return
        
        result = self.api.delete_image(
            data['filename'],
            data['category'],
            data['severity']
        )
        
        self._send_json_response(200 if result['success'] else 400, result)
    
    def _handle_batch_changes(self, data):
        """Handle batch changes request"""
        if 'changes' not in data:
            self._send_error_response(400, "Missing 'changes' field in request body")
            return
        
        if not isinstance(data['changes'], list):
            self._send_error_response(400, "'changes' must be an array")
            return
        
        result = self.api.batch_process_changes(data['changes'])
        self._send_json_response(200, result)
    
    def _send_json_response(self, status_code, data):
        """Send JSON response"""
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        response_json = json.dumps(data, indent=2)
        self.wfile.write(response_json.encode('utf-8'))
    
    def _send_error_response(self, status_code, message):
        """Send error response"""
        error_data = {
            "success": False,
            "error": message,
            "status_code": status_code
        }
        self._send_json_response(status_code, error_data)
    
    def log_message(self, format, *args):
        """Override to use our logger"""
        logger.info(f"{self.address_string()} - {format % args}")

def run_server(port=8001):
    """Run the changes API server"""
    server_address = ('', port)
    httpd = HTTPServer(server_address, ChangesAPIHandler)
    
    print(f"🔄 Dermatologist Changes API Server running on port {port}")
    print(f"📡 API Endpoints:")
    print(f"   • POST /api/move-image - Move image between categories")
    print(f"   • POST /api/delete-image - Delete an image")
    print(f"   • POST /api/batch-changes - Process multiple changes")
    print(f"   • OPTIONS /* - CORS preflight")
    print(f"\n🌐 Access at: http://localhost:{port}")
    print("⌨️  Press Ctrl+C to stop the server")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Changes API Server stopped")
        httpd.shutdown()

if __name__ == "__main__":
    run_server()
