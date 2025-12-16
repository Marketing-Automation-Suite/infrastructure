# Phase 4: The Nervous System - AI Function Calling Integration

## Objectives

Connect n8n to AI function calling server, create Router Workflow, build custom AI Node.

## Custom AI Function Calling Node for n8n

### Location

`n8n-orchestration/custom-nodes/ai-function-caller/`

### Node Structure

```javascript
// package.json
{
  "name": "n8n-node-ai-function-caller",
  "version": "1.0.0",
  "description": "Custom n8n node for AI function calling (model-agnostic)"
}

// src/AiFunctionCaller.ts
export class AiFunctionCaller implements INodeType {
  description: INodeTypeDescription = {
    displayName: 'AI Function Caller',
    name: 'aiFunctionCaller',
    // Node configuration
  };
  
  async execute(this: IExecuteFunctions): Promise<INodeExecutionData[][]> {
    // Call AI function calling server API
    // Process function call response
    // Route to appropriate n8n node
  }
}
```

## Router Workflow

### Workflow Structure

1. **Webhook Trigger** - Receives natural language command
2. **AI Function Caller Node** - Calls AI server with prompt + tool definitions
3. **Switch Node** - Routes based on function name returned by AI
4. **Action Nodes** - Execute the function (CRM, Mautic, etc.)
5. **Response Node** - Return results

### Tool Definitions

Define n8n tools that the AI can call:

```json
{
  "tools": [
    {
      "type": "function",
      "function": {
        "name": "crm_create_lead",
        "description": "Create a new lead in CRM",
        "parameters": {
          "type": "object",
          "properties": {
            "name": {"type": "string"},
            "email": {"type": "string"}
          }
        }
      }
    }
  ]
}
```

## Testing

1. Send webhook: `POST /webhook/router`
2. Body: `{"prompt": "Add John Doe to CRM"}`
3. Verify AI returns: `{"tool": "crm_create_lead", "params": {...}}`
4. Verify n8n routes to CRM node
5. Verify lead is created in Twenty CRM

## Milestone

✅ You type "Add John Doe to CRM" in a test webhook, and the AI correctly triggers the n8n logic

