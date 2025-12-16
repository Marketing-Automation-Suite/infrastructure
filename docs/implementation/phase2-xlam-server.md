# Phase 2: The Brain - AI Function Calling Server Implementation

## Objectives

Create `xlam-server` repository with model-agnostic function calling capabilities.

## Repository Setup

1. Create repository: `Marketing-Automation-Suite/xlam-server`
2. Initialize with Python project structure
3. Set up git submodule for `shared-libraries`

## Key Implementation Files

### src/server.py (FastAPI Entrypoint)

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI(title="AI Function Calling Server", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health():
    return {"status": "healthy"}

# OpenAI-compatible endpoint
@app.post("/v1/chat/completions")
async def chat_completions(request: dict):
    # Implementation in formatting.py and engine.py
    pass
```

### src/formatting.py (Tool Formatting)

```python
def format_tools_for_model(tools: list, format_type: str = "json") -> str:
    """
    Convert JSON tool definitions to model-specific format.
    
    Supports multiple formats:
    - "json": Standard JSON format (default)
    - "xml": XML format for models requiring <tools>...</tools>
    - "function_calling": OpenAI function calling format
    
    Args:
        tools: List of tool definitions
        format_type: Output format ("json", "xml", "function_calling")
    """
    if format_type == "xml":
        xml_parts = ["<tools>"]
        for tool in tools:
            xml_parts.append(f"<tool name='{tool['function']['name']}'>")
            # Add function parameters
            xml_parts.append("</tool>")
        xml_parts.append("</tools>")
        return "".join(xml_parts)
    elif format_type == "function_calling":
        # OpenAI function calling format
        return {"tools": tools}
    else:
        # Standard JSON
        return tools
```

### src/engine.py (Model Interface)

```python
def call_model(prompt: str, tools: str, model_config: dict):
    """
    Call AI model for function calling.
    
    Model-agnostic interface that supports:
    - vLLM
    - Ollama
    - OpenAI-compatible APIs
    - Custom model backends
    
    Args:
        prompt: User prompt
        tools: Formatted tools (format depends on model)
        model_config: Model-specific configuration
    """
    # Implementation using configured model backend
    # Supports raw mode if model requires it
    # Returns function call response
    pass
```

## Critical Requirements

1. **Model-Agnostic Design:** Support multiple model backends (vLLM, Ollama, OpenAI-compatible)
2. **Flexible Tool Formatting:** Support JSON, XML, or function calling formats as needed
3. **Raw Mode Support:** Optional raw mode for models that require it
4. **Submodule:** Include `shared-libraries` as git submodule for `jarvis_core`
5. **Configuration-Driven:** Model selection and formatting via configuration

## Testing

```bash
# Test endpoint
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"messages": [{"role": "user", "content": "test"}]}'
```

## Milestone

✅ You can `curl localhost:8000/v1/chat` and get a function call response back

