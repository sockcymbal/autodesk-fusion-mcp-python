# fusion_mcp.py  – bare-bones Fusion Design-Automation MCP server
#
# Rename your folder to fusion_mcp/ and launch with:
#   uv run fusion_mcp.py
#
# Environment variables expected (put them in keys.env or .env):
#   APS_CLIENT_ID
#   APS_CLIENT_SECRET
#   FUSION_ACTIVITY_ID      # ← activity you registered in APS; see README
#   APS_BASE=https://developer.api.autodesk.com   # optional override

from mcp.server.fastmcp import FastMCP
import httpx, os, asyncio, logging, argparse
from dotenv import load_dotenv
from datetime import datetime, timezone

# ────────────────────────────  Bootstrap  ────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

mcp = FastMCP("fusion")          # server name Windsurf will show
load_dotenv("keys.env")          # same pattern you had before

APS_BASE = os.getenv("APS_BASE", "https://developer.api.autodesk.com")
CLIENT_ID = os.environ["APS_CLIENT_ID"]
CLIENT_SECRET = os.environ["APS_CLIENT_SECRET"]
ACTIVITY_ID = os.environ["FUSION_ACTIVITY_ID"]      # e.g. <nick>.GenerateCube+prod

TOKEN_URL      = f"{APS_BASE}/authentication/v2/token"            #  [oai_citation:0‡Autodesk Platform Services](https://aps.autodesk.com/en/docs/oauth/v2/reference/http/gettoken-POST?utm_source=chatgpt.com)
WORKITEMS_URL  = f"{APS_BASE}/da/us-east/v3/workitems"            #   "   turn0search1
POLL_INTERVAL  = 4                                                # seconds

# ───────────────────────  APS helper functions  ──────────────────────
async def get_oauth_token() -> str:
    """
    Fetches a 2-legged OAuth token good for 60 minutes.
    APS OAuth v2 expects Basic-auth header with client-credentials.    [oai_citation:1‡Autodesk Platform Services](https://aps.autodesk.com/en/docs/oauth/v2/tutorials/get-2-legged-token?utm_source=chatgpt.com) [oai_citation:2‡Autodesk Platform Services](https://aps.autodesk.com/en/docs/oauth/v2/developers_guide/field-guide?utm_source=chatgpt.com)
    """
    headers = httpx.BasicAuth(CLIENT_ID, CLIENT_SECRET).auth_header
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            TOKEN_URL,
            headers={"Authorization": headers},
            data={"grant_type": "client_credentials", "scope": "data:read data:write code:all"}
        )
        resp.raise_for_status()
        return resp.json()["access_token"]

async def submit_cube_workitem(edge_mm: float, token: str) -> str:
    """
    Launches a Design-Automation workitem that calls the pre-registered
    Fusion activity (ACTIVITY_ID) and returns the workitem ID.
    The activity script inside Fusion should read the `edge_mm` param,
    create a cube, export STL → OSS.                       [oai_citation:3‡Autodesk Platform Services](https://aps.autodesk.com/en/docs/design-automation/v3/reference/?utm_source=chatgpt.com)
    """
    payload = {
        "activityId" : ACTIVITY_ID,
        "arguments"  : {
            "edge_mm": { "value": edge_mm },
            # output 'result' will be uploaded to a temp OSS bucket
            "result" : { "verb": "put", "url": "urn:adsk.objects:os.object:destination/result.stl" }
        }
    }
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            WORKITEMS_URL,
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
            json=payload
        )
        resp.raise_for_status()
        return resp.json()["id"]                 # workitem ID

async def wait_for_workitem(work_id: str, token: str) -> dict:
    """
    Polls GET /workitems/{id} until status ∈ {success,failed}.        [oai_citation:4‡Autodesk Platform Services](https://aps.autodesk.com/blog/design-automation-get-workitemsid-will-be-enforced-rate-limit-150-rate-minute-rpm?utm_source=chatgpt.com)
    Returns the final JSON (includes output URLs if success).
    """
    async with httpx.AsyncClient() as client:
        url = f"{WORKITEMS_URL}/{work_id}"
        while True:
            resp = await client.get(url, headers={"Authorization": f"Bearer {token}"})
            resp.raise_for_status()
            data = resp.json()
            state = data.get("status")
            if state in ("success", "failed"):
                return data
            await asyncio.sleep(POLL_INTERVAL)

# ──────────────────────────────  MCP Tool  ───────────────────────────
@mcp.tool()
async def generate_cube(edge_mm: float = 20.0) -> str:
    """
    Create a parametric cube with the given edge length (mm) via
    Autodesk Fusion Design Automation and return a signed STL URL.
    """
    try:
        token   = await get_oauth_token()
        work_id = await submit_cube_workitem(edge_mm, token)
        logging.info(f"WorkItem {work_id} submitted for {edge_mm} mm cube")
        result  = await wait_for_workitem(work_id, token)

        if result["status"] != "success":
            return f"WorkItem failed: {result.get('reportUrl')}"
        stl_url = result["arguments"]["result"]["url"]   # pre-signed URL
        return f"✅ Cube ready: {stl_url}"
    except Exception as e:
        logging.exception("generate_cube failed")
        return f"❌ Error creating cube: {e}"

# ──────────────────────────────  Main  ───────────────────────────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Fusion MCP Server – headless Fusion automation via APS"
    )
    parser.add_argument(
        "--transport",
        default="stdio",
        choices=["stdio", "http"],
        help="Transport mechanism for the MCP server (default: stdio)",
    )
    args = parser.parse_args()
    logging.info(f"Starting Fusion MCP server with transport: {args.transport}")
    mcp.run(transport=args.transport)