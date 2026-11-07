# Jupyter MCP Server and AWS MCP dependencies for Braket notebook instances

The Braket notebook lifecycle configuration (LCC) installs these packages.
This folder is the only source of these pins.

- Jupyter MCP Server: the LCC build resolves these pins for Python 3.10 and downloads all the wheels. At notebook start, the LCC adds to `JupyterSystemEnv` only the packages that it does not have. The notebook keeps its own version of each other package. The notebook integration tests fail if the notebook packages do not satisfy the added packages.
- AWS MCP proxy: the pipeline builds `mcp-proxy-environment.yml` with conda and packs it, like the Braket environment. The notebook unpacks it.

| File | Use |
|---|---|
| `jupyter-ai-requirements.txt` | Jupyter MCP Server packages for `JupyterSystemEnv` (Python 3.10). |
| `mcp-proxy-requirements.txt` | AWS MCP proxy. It has its own conda environment (Python 3.13). |
| `mcp-proxy-environment.yml` | The conda environment for the AWS MCP proxy. It installs `mcp-proxy-requirements.txt`. |

Pin each package exactly. The pipeline resolves the other packages when it builds the LCC, like the Braket environment.
