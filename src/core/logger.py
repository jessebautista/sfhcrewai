import threading
import datetime
import json
from src.tools.supabase_ops import SupabaseManager

class AgentLogger:
    def __init__(self):
        # We initialize SupabaseManager lazily or catch errors to avoid crashing if config is missing during init
        pass

    def log(self, agent_name: str, event_type: str, message: str, metadata: dict = None, status: str = "info"):
        """
        Log an event to the agent_logs table asynchronously.
        """
        payload = {
            "agent_name": agent_name,
            "event_type": event_type,
            "message": message,
            "metadata": metadata or {},
            "status": status,
            "created_at": datetime.datetime.utcnow().isoformat()
        }
        
        # Run in a separate thread to prevent blocking agent execution
        threading.Thread(target=self._push_to_db, args=(payload,)).start()

    def _push_to_db(self, payload: dict):
        try:
            manager = SupabaseManager()
            # We use the underlying client directly
            # Note: This assumes the 'agent_logs' table exists.
            manager.client.table("agent_logs").insert(payload).execute()
        except Exception as e:
            # Silently fail or print to stderr to avoid disrupting the main app
            print(f"[AgentLogger Error] Failed to log event: {e}")
