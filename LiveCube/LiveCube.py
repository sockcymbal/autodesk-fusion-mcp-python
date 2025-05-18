#!/usr/bin/env python3
# LiveCube.py - A Fusion 360 add-in that creates cubes via HTTP endpoint
import adsk.core, adsk.fusion, adsk.cam, traceback
import threading, json, os
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

# Global variables
app = None
ui = None
handlers = []
server_thread = None
DEFAULT_PORT = 18080

def run(context):
    global app, ui, server_thread
    
    try:
        # Get the Fusion application object
        app = adsk.core.Application.get()
        ui = app.userInterface
        
        # Start the HTTP server in a separate thread
        server_thread = threading.Thread(target=start_server)
        server_thread.daemon = True
        server_thread.start()
        
        ui.messageBox('Cube MCP Server started on port 18080.\nSend HTTP GET requests to http://127.0.0.1:18080/cmd?edge=SIZE')
        
    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

def stop(context):
    global server_thread
    
    try:
        ui.messageBox('Cube MCP Server stopping...')
        # Server will stop when Fusion closes as it's a daemon thread
    except:
        if ui:
            ui.messageBox('Failed to stop:\n{}'.format(traceback.format_exc()))

def create_cube(edge_mm=20.0):
    """Create a cube with the specified edge length in mm"""
    try:
        app = adsk.core.Application.get()
        design = adsk.fusion.Design.cast(app.activeProduct)
        if not design:
            app.activeDocument.close(False)  # Don't save
            app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
            design = app.activeProduct
        
        root = design.rootComponent

        # Create sketch on XY plane
        sketches = root.sketches
        xyPlane = root.xYConstructionPlane
        sketch = sketches.add(xyPlane)
        
        # Draw a square centered at origin
        lines = sketch.sketchCurves.sketchLines
        half_edge = edge_mm / 2
        lines.addCenterPointRectangle(
            adsk.core.Point3D.create(0, 0, 0),
            adsk.core.Point3D.create(half_edge, half_edge, 0)
        )
        
        # Extrude to create a cube
        extrudes = root.features.extrudeFeatures
        distance = adsk.core.ValueInput.createByReal(edge_mm)
        profile = sketch.profiles.item(0)
        extInput = extrudes.createInput(
            profile, adsk.fusion.FeatureOperations.NewBodyFeatureOperation
        )
        extInput.setDistanceExtent(False, distance)
        extrude = extrudes.add(extInput)
        
        # Set a nice view of the cube
        cam = app.activeViewport.camera
        cam.viewOrientation = adsk.core.ViewOrientations.IsometricViewOrientation
        cam.isFitView = True
        app.activeViewport.camera = cam
        
        # Return success message with cube dimensions
        return {"status": "success", "cube": f"{edge_mm}mm edge cube created"}
    
    except Exception as e:
        return {"status": "error", "message": str(e)}

class CubeRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            # Parse the URL
            url = urlparse(self.path)
            
            # Basic routing
            if url.path == "/cmd":
                # Parse query parameters
                query = parse_qs(url.query)
                
                # Get the edge parameter or use default
                edge_mm = 20.0
                if "edge" in query and query["edge"][0]:
                    try:
                        edge_mm = float(query["edge"][0])
                    except ValueError:
                        pass
                
                # Create the cube in the main thread
                result = create_cube(edge_mm)
                
                # Send response
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(result).encode('utf-8'))
            else:
                # Not found
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b'{"status": "error", "message": "Path not found"}')
                
        except Exception as e:
            # Internal error
            self.send_response(500)
            self.end_headers()
            self.wfile.write(json.dumps({"status": "error", "message": str(e)}).encode('utf-8'))
            
    def log_message(self, format, *args):
        # Silence the HTTP server logs
        pass

def start_server():
    """Start the HTTP server on localhost:18080"""
    try:
        server = HTTPServer(('127.0.0.1', DEFAULT_PORT), CubeRequestHandler)
        print(f"Server started at http://127.0.0.1:{DEFAULT_PORT}")
        server.serve_forever()
    except Exception as e:
        if ui:
            ui.messageBox(f"Failed to start server: {str(e)}")
