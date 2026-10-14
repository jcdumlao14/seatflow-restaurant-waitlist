"""SeatFlow read-only MCP server. Run with: python mcp-server/server.py"""
from mcp.server.fastmcp import FastMCP

from seatflow_mcp_core import (
    read_approved_project_document as read_document_core,
    review_repository_structure as run_repository_review,
)

mcp = FastMCP("seatflow-readonly-review")


@mcp.tool()
def review_repository_structure() -> str:
    """Run SeatFlow's structural checks and return the verification report."""
    return run_repository_review()


@mcp.tool()
def read_approved_project_document(path: str) -> str:
    """Read one allowlisted project document; arbitrary file reads are blocked."""
    return read_document_core(path)


if __name__ == "__main__":
    mcp.run(transport="stdio")