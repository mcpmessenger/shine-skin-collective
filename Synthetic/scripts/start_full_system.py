#!/usr/bin/env python3
"""
Full Dermatologist System Startup Script
Starts both the image server and the changes API server
"""

import subprocess
import sys
import time
import threading
import os
from pathlib import Path

def run_server(script_name, port, description):
    """Run a server script in a separate process"""
    try:
        print(f"🚀 Starting {description} on port {port}...")
        process = subprocess.Popen([
            sys.executable, script_name
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # Give it a moment to start
        time.sleep(2)
        
        if process.poll() is None:
            print(f"✅ {description} started successfully on port {port}")
            return process
        else:
            stdout, stderr = process.communicate()
            print(f"❌ Failed to start {description}: {stderr}")
            return None
    except Exception as e:
        print(f"❌ Error starting {description}: {e}")
        return None

def main():
    """Start the full dermatologist system"""
    print("🩺 Starting Full Dermatologist System")
    print("=" * 50)
    
    # Change to the correct directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    processes = []
    
    try:
        # Start the image server (port 8000)
        image_server = run_server(
            "start_dermatologist_server.py", 
            8000, 
            "Image Server"
        )
        if image_server:
            processes.append(image_server)
        
        # Start the changes API server (port 8001)
        changes_server = run_server(
            "changes_server.py", 
            8001, 
            "Changes API Server"
        )
        if changes_server:
            processes.append(changes_server)
        
        if not processes:
            print("❌ No servers started successfully")
            return
        
        print("\n" + "=" * 50)
        print("🎉 System is running!")
        print("\n📋 Available Services:")
        print("   • Image Server: http://localhost:8000")
        print("   • Changes API: http://localhost:8001")
        print("   • Main Tool: http://localhost:8000/dermatologist_swipe_tool.html")
        print("   • Server Tool: http://localhost:8000/dermatologist_swipe_tool_server.html")
        print("\n🔧 API Endpoints:")
        print("   • POST http://localhost:8001/api/move-image")
        print("   • POST http://localhost:8001/api/delete-image")
        print("   • POST http://localhost:8001/api/batch-changes")
        print("\n⌨️  Press Ctrl+C to stop all servers")
        print("=" * 50)
        
        # Keep the main process alive
        try:
            while True:
                time.sleep(1)
                
                # Check if any process has died
                for i, process in enumerate(processes):
                    if process.poll() is not None:
                        print(f"⚠️  Server {i+1} has stopped unexpectedly")
                        processes.remove(process)
                
                if not processes:
                    print("❌ All servers have stopped")
                    break
                    
        except KeyboardInterrupt:
            print("\n🛑 Stopping all servers...")
            
    finally:
        # Clean up all processes
        for process in processes:
            if process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
        
        print("👋 All servers stopped. Thanks for using the Dermatologist System!")

if __name__ == "__main__":
    main()
