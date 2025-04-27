import os
import json
import http.server
import socketserver
from urllib.parse import urlparse, unquote
from pathlib import Path

class DebateViewerHandler(http.server.SimpleHTTPRequestHandler):
    """Custom HTTP handler for the Debate Viewer application"""
    
    def do_GET(self):
        """Handle GET requests"""
        # Parse the URL path
        parsed_url = urlparse(self.path)
        path = unquote(parsed_url.path)
        
        if path == "/list-debates":
            self.handle_list_debates()
        elif path.startswith("/debate-agent/output/") and path.endswith(".json"):
            # Handle direct requests for debate JSON files
            self.serve_debate_file(path)
        else:
            # Default to serving static files
            return http.server.SimpleHTTPRequestHandler.do_GET(self)
    
    def handle_list_debates(self):
        """Handle request to list debate files"""
        try:
            # Define the path to the output directory
            output_dir = Path.cwd().parent / "debate-agent" / "output"
            # output_dir = os.path.join(os.path.dirname(os.getcwd()), "debate-agent", "output")

            # Check if directory exists
            if not os.path.exists(output_dir):
                self.send_json_response([])
                return
            
            # Get all JSON files in the directory
            files = [f for f in os.listdir(output_dir) if f.endswith('.json')]
            
            # Return the list of files
            self.send_json_response(files)
            
        except Exception as e:
            print(f"Error listing debates: {e}")
            self.send_error(500, f"Server error: {str(e)}")
    
    def serve_debate_file(self, path):
        """Serve a debate JSON file from the output directory"""
        try:
            # Extract the filename from the path
            filename = os.path.basename(path)
            
            # Construct the actual file path relative to project root
            base_dir = Path.cwd().parent
            file_path = base_dir / "debate-agent" / "output" / filename
            
            if not os.path.exists(file_path):
                self.send_error(404, f"File not found: {path}")
                return
            
            # Read and serve the file
            with open(file_path, 'rb') as f:
                content = f.read()
            
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.send_header("Content-Length", str(len(content)))
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
            self.send_header("Access-Control-Allow-Headers", "Content-Type")
            self.end_headers()
            
            # Write the file content
            self.wfile.write(content)
            
        except Exception as e:
            print(f"Error serving debate file: {e}")
            self.send_error(500, f"Server error: {str(e)}")
    
    def send_json_response(self, data):
        """Send JSON response with appropriate headers"""
        response_data = json.dumps(data).encode('utf-8')
        
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.send_header("Content-Length", str(len(response_data)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        
        # Write the response data after sending all headers
        self.wfile.write(response_data)

def run_server(port=8000):
    """Run the HTTP server"""
    # Force the server to serve the current directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Use ThreadingTCPServer to handle multiple requests
    class ThreadedHTTPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
        allow_reuse_address = True
    
    # Create and start the server
    server = ThreadedHTTPServer(("", port), DebateViewerHandler)
    
    print(f"Server running at http://localhost:{port}/")
    print(f"Open http://localhost:{port}/viewer.html to view debates")
    print("Press Ctrl+C to stop the server")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        server.shutdown()

if __name__ == "__main__":
    run_server()
