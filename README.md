# Autodesk Fusion 360 MCP Integration

The Fusion MCP (Model Context Protocol) application is an integration system that enables AI assistants to interact programmatically with Autodesk Fusion 360. This implementation specifically demonstrates how to create parametric 3D models through simple API calls, bridging the gap between conversational AI and CAD software.

## Overview

The Fusion 360 MCP Integration enables AI assistants to control Fusion 360 for 3D modeling tasks. This project is particularly valuable for:

- AI-assisted CAD design workflows
- Parametric 3D model generation
- Automating repetitive design tasks in Fusion 360
- Creating programmatic interfaces to Fusion 360

## Components

The integration consists of three main components:

### 1. LiveCube Script (`LiveCube.py` & `LiveCube.manifest`)

A Fusion 360 add-in that:
- Runs inside Fusion 360 as a script
- Creates parametric cubes with specified dimensions
- Exposes an HTTP endpoint on port 18080 to receive commands
- Can be triggered via simple HTTP GET requests

### 2. Fusion Server (`fusion_server.py`)

An intermediary server that:
- Acts as a bridge between MCP and Fusion 360
- Listens on port 8000 for MCP requests
- Translates MCP calls into formats Fusion 360 can understand
- Handles communication with the LiveCube script

### 3. MCP Server (`fusion_mcp.py`)

The Model Context Protocol server that:
- Provides tools AI assistants can use
- Integrates with Autodesk Platform Services (APS) for cloud automation
- Offers the `generate_cube` tool for creating parametric cubes
- Uses OAuth authentication for secure access to APS

## Features

- **Cube Creation**: Generate parametric cubes with specified dimensions
- **Autodesk Platform Services Integration**: Use APS Design Automation for complex operations
- **Simple HTTP Interface**: Easy-to-use API for controlling Fusion 360
- **MCP Standard Compliance**: Works with any MCP-compatible AI assistant

## Installation

### Prerequisites

- Autodesk Fusion 360 (2023 or newer)
- Python 3.9+ with pip
- Autodesk Platform Services account with API access
- MCP-compatible AI assistant (like Claude in Windsurf environments)

### Setup Instructions

1. **Install Python Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set Up Environment Variables**:
   Create a `keys.env` file with your Autodesk Platform Services credentials:
   ```
   APS_CLIENT_ID=your_client_id
   APS_CLIENT_SECRET=your_client_secret
   FUSION_ACTIVITY_ID=your_activity_id
   ```

3. **Install LiveCube Script in Fusion 360**:
   - Open Fusion 360
   - Navigate to Scripts and Add-Ins (Shift+S)
   - Click the green "+" button and select "Add script"
   - Browse to and select the `LiveCube` folder in this repository
   - The script should now appear in your scripts list

## Usage

### Starting the Servers

1. **Start the Fusion Server**:
   ```bash
   python fusion_server.py
   ```
   This will start listening on http://localhost:8000

2. **Run the LiveCube Script**:
   - In Fusion 360, go to Scripts and Add-Ins
   - Select LiveCube and click "Run"
   - This will start the HTTP server inside Fusion 360 on port 18080

3. **Start the MCP Server**:
   ```bash
   python fusion_mcp.py
   ```
   This will start the MCP server with stdio transport by default.

### Using with AI Assistants

Configure your MCP-compatible AI assistant to connect to the Fusion MCP server. For example, with Claude Desktop:

```json
{
  "mcpServers": {
    "fusion": {
      "command": "python",
      "args": ["/path/to/fusion_mcp.py"]
    }
  }
}
```

The AI can then use the `generate_cube` tool to create cubes in Fusion 360.

### Direct API Access

You can also directly interact with the LiveCube script HTTP endpoint:

```
GET http://127.0.0.1:18080/cmd?edge=50
```

This would create a cube with 50mm edge length in Fusion 360.

## Developer Notes

- The MCP server communicates with Autodesk Platform Services (APS) using OAuth 2.0 authentication
- For advanced use cases, modify `fusion_mcp.py` to add additional tools beyond cube creation
- The system architecture can be extended to support other Fusion 360 operations by adding new handlers in `fusion_server.py` and corresponding Fusion 360 scripts

## License

MIT

## Acknowledgments

- Autodesk for the Fusion 360 API and Platform Services
- Model Context Protocol (MCP) creators for enabling AI-tool interoperability
npx @modelcontextprotocol/server-everything
```

### Or specify stdio explicitly
```shell
npx @modelcontextprotocol/server-everything stdio
```

### Run the SSE server
```shell
npx @modelcontextprotocol/server-everything sse
```

### Run the streamable HTTP server
```shell
npx @modelcontextprotocol/server-everything streamableHttp
```

