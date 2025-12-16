# Fix: __WS_TOKEN__ is not defined

## Problem
```
client.ts:33 Uncaught ReferenceError: __WS_TOKEN__ is not defined
```

This error occurs when a build-time variable `__WS_TOKEN__` is referenced in the code but not defined in the build configuration.

## Solution

The `__WS_TOKEN__` variable needs to be injected at build time. The solution depends on your build tool:

### Option 1: Vite Configuration

If using Vite, add to `vite.config.ts`:

```typescript
import { defineConfig } from 'vite'

export default defineConfig({
  define: {
    '__WS_TOKEN__': JSON.stringify(process.env.WS_TOKEN || ''),
  },
  // ... rest of config
})
```

Or use environment variables:

```typescript
import { defineConfig, loadEnv } from 'vite'

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  
  return {
    define: {
      '__WS_TOKEN__': JSON.stringify(env.WS_TOKEN || ''),
    },
  }
})
```

### Option 2: Webpack Configuration

If using Webpack, add to `webpack.config.js`:

```javascript
const webpack = require('webpack');

module.exports = {
  plugins: [
    new webpack.DefinePlugin({
      '__WS_TOKEN__': JSON.stringify(process.env.WS_TOKEN || ''),
    }),
  ],
  // ... rest of config
}
```

### Option 3: TypeScript/JavaScript Code Fix

Instead of using `__WS_TOKEN__` directly, use environment variables:

**Before:**
```typescript
const wsToken = __WS_TOKEN__;
```

**After (Vite):**
```typescript
const wsToken = import.meta.env.VITE_WS_TOKEN || '';
```

**After (Webpack/React):**
```typescript
const wsToken = process.env.REACT_APP_WS_TOKEN || '';
```

**After (Generic):**
```typescript
// Get from window object if injected via script tag
const wsToken = (window as any).__WS_TOKEN__ || '';
```

### Option 4: Runtime Injection

Inject the token at runtime via HTML:

```html
<script>
  window.__WS_TOKEN__ = 'your-websocket-token-here';
</script>
<script src="/client.js"></script>
```

Or via environment variable in Docker/Kubernetes:

```yaml
# In your deployment
env:
  - name: WS_TOKEN
    valueFrom:
      secretKeyRef:
        name: websocket-secrets
        key: token
```

Then inject in your HTML template:

```html
<script>
  window.__WS_TOKEN__ = '{{ .WS_TOKEN }}';
</script>
```

## Recommended Approach

### For Production:

1. **Store token in Kubernetes Secret:**
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: websocket-token
  namespace: marketing-automation
type: Opaque
stringData:
  token: "your-secure-websocket-token"
```

2. **Inject via ConfigMap/Environment:**
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: frontend-config
data:
  ws-token-env: "VITE_WS_TOKEN"
```

3. **Use in Build:**
```bash
# In Dockerfile or build script
ARG WS_TOKEN
ENV VITE_WS_TOKEN=$WS_TOKEN

# Build
npm run build -- --mode production
```

4. **Access in Code:**
```typescript
// client.ts
const wsToken = import.meta.env.VITE_WS_TOKEN || '';

if (!wsToken) {
  console.warn('WebSocket token not configured');
}

// Use token
const ws = new WebSocket(`wss://api.example.com/ws?token=${wsToken}`);
```

## Quick Fix (Temporary)

If you need a quick fix for development:

1. **Create `.env` file:**
```bash
WS_TOKEN=dev-token-here
```

2. **Update build config** (see Option 1 or 2 above)

3. **Or add to client.ts:**
```typescript
// Temporary fix - replace __WS_TOKEN__ with:
const WS_TOKEN = (typeof window !== 'undefined' && (window as any).__WS_TOKEN__) 
  || process.env.WS_TOKEN 
  || import.meta.env?.VITE_WS_TOKEN 
  || '';

// Then use WS_TOKEN instead of __WS_TOKEN__
```

## Verification

After applying the fix:

1. Rebuild the application
2. Check browser console - error should be gone
3. Verify WebSocket connection works
4. Check that token is properly injected (don't log it in production!)

## Security Notes

⚠️ **Important:**
- Never commit tokens to version control
- Use environment variables or secrets management
- Don't log tokens in production
- Use HTTPS/WSS for token transmission
- Rotate tokens regularly

## Next Steps

1. Identify which build tool you're using (Vite, Webpack, etc.)
2. Apply the appropriate fix from above
3. Set up proper secret management for production
4. Update deployment configuration
5. Test WebSocket connection

