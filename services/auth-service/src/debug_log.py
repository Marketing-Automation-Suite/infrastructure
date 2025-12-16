"""
Debug logging helper - safe logging that doesn't crash if file can't be written
"""
import json
import os

LOG_PATH = '/Users/jimmy/Documents/Repos/Private_Repos/Marketing_Automation_Pipeline/.cursor/debug.log'

def debug_log(session_id, run_id, hypothesis_id, location, message, data=None):
    """Safely write debug log entry"""
    try:
        os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
        with open(LOG_PATH, 'a') as f:
            f.write(json.dumps({
                "sessionId": session_id,
                "runId": run_id,
                "hypothesisId": hypothesis_id,
                "location": location,
                "message": message,
                "data": data or {},
                "timestamp": int(__import__('time').time() * 1000)
            }) + '\n')
    except Exception:
        pass  # Silently fail - don't crash the service

