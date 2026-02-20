from mcp.server.fastmcp import FastMCP

app=FastMCP("MCP-Server-Demo")
def main():
    print("Hello from mcp-server-demo!")

@app.tool()
def add_numbers(a: int, b: int)->int:
    """Add two numbers"""
    return a + b

if __name__ == "__main__":

    main()
