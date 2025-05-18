### Q Developer CLI example

See the [Q Developer CLI documentation](https://docs.aws.amazon.com/amazonq/latest/qdeveloper-ug/command-line-mcp-configuration.html)
for instructions on managing MCP configuration.

In `~/.aws/amazonq/mcp.json`:

```json
{
  "mcpServers": {
    "strands": {
      "command": "uvx",
      "args": ["strands-agents-mcp-server"]
    }
  }
}
```
