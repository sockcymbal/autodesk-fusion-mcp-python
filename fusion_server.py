"""
fusion_server.py - Intermediary server that communicates between MCP and Fusion 360
"""
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import urllib.parse
import sys
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

class FusionRequestHandler(BaseHTTPRequestHandler):
    """
    HTTP request handler for the Fusion 360 intermediary server.
    Receives requests from the MCP server and forwards them to Fusion 360.
    """
    def do_GET(self):
        """Handle GET requests from the MCP server"""
        try:
            # Parse the URL and query parameters
            parsed_path = urllib.parse.urlparse(self.path)
            params = dict(urllib.parse.parse_qsl(parsed_path.query))
            
            # Handle different endpoints
            if parsed_path.path == "/create_cube":
                self._handle_create_cube(params)
            else:
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b"Not found")
        except Exception as e:
            logger.error(f"Error handling request: {e}")
            self.send_response(500)
            self.end_headers()
            self.wfile.write(f"Error: {str(e)}".encode())
    
    def _handle_create_cube(self, params):
        """Handle cube creation requests"""
        try:
            # Extract cube dimensions from parameters
            width = float(params.get("width", 50.0))
            height = float(params.get("height", 50.0))
            depth = float(params.get("depth", 50.0))
            
            logger.info(f"Creating cube with dimensions: W:{width}mm, H:{height}mm, D:{depth}mm")
            
            # In a real implementation, this would communicate with Fusion 360 via its API
            # For this example, we'll just return a success response
            
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({
                "status": "success",
                "message": f"Cube created with dimensions: W:{width}mm, H:{height}mm, D:{depth}mm"
            }).encode())
            
        except Exception as e:
            logger.error(f"Error creating cube: {e}")
            self.send_response(500)
            self.end_headers()
            self.wfile.write(f"Error creating cube: {str(e)}".encode())

def run_server(host="localhost", port=8000):
    """Run the Fusion 360 intermediary server"""
    server_address = (host, port)
    httpd = HTTPServer(server_address, FusionRequestHandler)
    logger.info(f"Starting Fusion 360 intermediary server on {host}:{port}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
    finally:
        httpd.server_close()
        logger.info("Server closed")

if __name__ == "__main__":
    run_server()
