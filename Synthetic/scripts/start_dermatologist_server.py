#!/usr/bin/env python3
"""
Dermatologist Swipe Tool Server
Serves the dermatologist labeling tool and synthetic face dataset images via HTTP
to avoid CORS issues when loading images in the browser.
"""

import http.server
import socketserver
import os
import sys
import webbrowser
from pathlib import Path

# Configuration
PORT = 8000
HOST = 'localhost'

class DermatologistHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """Custom HTTP request handler with CORS headers and proper MIME types"""
    
    def end_headers(self):
        # Add CORS headers to allow cross-origin requests
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()
    
    def guess_type(self, path):
        """Override to set proper MIME types for our files"""
        mimetype, encoding = super().guess_type(path)
        
        # Ensure PNG images are served with correct MIME type
        if path.endswith('.png'):
            return 'image/png'
        elif path.endswith('.json'):
            return 'application/json'
        elif path.endswith('.html'):
            return 'text/html'
        
        return mimetype

def find_project_root():
    """Find the project root directory"""
    current_dir = Path(__file__).parent.absolute()
    
    # Look for the main project directory (containing package.json or similar)
    while current_dir != current_dir.parent:
        if (current_dir / 'package.json').exists() or (current_dir / 'next.config.mjs').exists():
            return current_dir
        current_dir = current_dir.parent
    
    # Fallback to current directory
    return Path(__file__).parent.absolute()

def main():
    """Start the dermatologist tool server"""
    print("🩺 Starting Dermatologist Swipe Tool Server")
    print("=" * 50)
    
    # Find the project root
    project_root = find_project_root()
    print(f"📁 Project root: {project_root}")
    
    # Change to the Synthetic Face Dataset directory
    dataset_dir = project_root / "Synthetic Face Dataset"
    if not dataset_dir.exists():
        print(f"❌ Error: Dataset directory not found at {dataset_dir}")
        print("Please run this script from the project root or ensure the dataset exists.")
        sys.exit(1)
    
    os.chdir(dataset_dir)
    print(f"📂 Serving from: {dataset_dir}")
    
    # Check if output_images directory exists
    output_images_dir = dataset_dir / "output_images"
    if not output_images_dir.exists():
        print(f"⚠️  Warning: output_images directory not found at {output_images_dir}")
        print("The tool will work but no images will be available for labeling.")
    
    # Create the server
    try:
        with socketserver.TCPServer((HOST, PORT), DermatologistHTTPRequestHandler) as httpd:
            print(f"🚀 Server running at http://{HOST}:{PORT}")
            print(f"🖼️  Dermatologist tool: http://{HOST}:{PORT}/dermatologist_swipe_tool.html")
            print(f"📊 Server tool: http://{HOST}:{PORT}/dermatologist_swipe_tool_server.html")
            print("\n📋 Available endpoints:")
            print(f"   • Main tool: http://{HOST}:{PORT}/dermatologist_swipe_tool.html")
            print(f"   • Server tool: http://{HOST}:{PORT}/dermatologist_swipe_tool_server.html")
            print(f"   • Images: http://{HOST}:{PORT}/output_images/")
            print(f"   • API: http://{HOST}:{PORT}/relabel_api.py")
            print("\n⌨️  Press Ctrl+C to stop the server")
            print("=" * 50)
            
            # Try to open the browser automatically
            try:
                webbrowser.open(f'http://{HOST}:{PORT}/dermatologist_swipe_tool.html')
                print("🌐 Opening dermatologist tool in your default browser...")
            except Exception as e:
                print(f"⚠️  Could not open browser automatically: {e}")
                print(f"Please manually open: http://{HOST}:{PORT}/dermatologist_swipe_tool.html")
            
            # Start serving
            httpd.serve_forever()
            
    except OSError as e:
        if e.errno == 48:  # Address already in use
            print(f"❌ Error: Port {PORT} is already in use.")
            print(f"Please stop any other server running on port {PORT} or change the PORT variable.")
        else:
            print(f"❌ Error starting server: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n🛑 Server stopped by user")
        print("👋 Thanks for using the Dermatologist Swipe Tool!")

if __name__ == "__main__":
    main()
