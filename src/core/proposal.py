
import threading

class ProposalManager:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(ProposalManager, cls).__new__(cls)
                cls._instance.pending_proposal = None
            return cls._instance

    def submit_proposal(self, proposal: dict):
        """
        Submit a proposal for review.
        proposal structure:
        {
            "type": "update" | "create",
            "id": "record_id" (only for update),
            "data": {"field": "value"},
            "reason": ""
        }
        """
        # Normalize legacy structure (update only) for backward compat if needed
        if "type" not in proposal:
            proposal["type"] = "update"
            # Remap old keys if strictly following new schema, but let's just stick to new schema in tools
            if "changes" in proposal:
                proposal["data"] = proposal.pop("changes")
            
        self.pending_proposal = proposal

    def get_proposal(self):
        return self.pending_proposal

    def clear_proposal(self):
        self.pending_proposal = None
