import asyncio
from pathlib import Path
import sys
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

ROOT = Path(__file__).resolve().parents[1]
SERVER = ROOT / "mcp-server" / "server.py"

async def main():
    params = StdioServerParameters(command=sys.executable, args=[str(SERVER)])
    async with stdio_client(params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            listing = await session.list_tools()
            names = {tool.name for tool in listing.tools}
            expected = {
                "review_repository_structure",
                "read_approved_project_document",
            }
            if not expected.issubset(names):
                raise AssertionError(f"Expected {expected}; got {names}")
            print("MCP tools discovered:", ", ".join(sorted(names)))

            document = await session.call_tool(
                "read_approved_project_document", {"path": "README.md"}
            )
            if document.isError or not any(
                getattr(item, "text", "").strip()
                for item in document.content
            ):
                raise AssertionError(f"Document tool failed: {document.content}")
            print("Approved-document tool: PASS")

            review = await session.call_tool("review_repository_structure", {})
            if review.isError:
                raise AssertionError(f"Review tool failed: {review.content}")
            output = "\n".join(
                getattr(item, "text", "") for item in review.content
            )
            if "failed': 0" not in output and '"failed": 0' not in output:
                raise AssertionError("Review did not report zero failures:\n" + output)
            print("Repository-review tool: PASS")
            print(output)

if __name__ == "__main__":
    asyncio.run(main())
