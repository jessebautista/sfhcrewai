"""
Refactored ProposalManager using Supabase for persistent storage.
Replaces in-memory proposal with database-backed proposal management.
"""
import os
from typing import Optional, List, Dict
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()


class ProposalManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ProposalManager, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        """Initialize Supabase client"""
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_KEY")
        if not url or not key:
            raise ValueError("Supabase credentials not found in environment.")
        self.client = create_client(url, key)

    def submit_proposal(self, proposal: dict, requester_email: str = None) -> str:
        """
        Submit a proposal for review.
        
        Args:
            proposal: Dictionary with structure:
                {
                    "type": "update" | "create",
                    "id": "record_id" (only for update),
                    "data": {"field": "value"},
                    "reason": "explanation"
                }
            requester_email: Email address of the requester (for notifications)
        
        Returns:
            proposal_id: UUID of the created proposal
        """
        # Normalize legacy structure for backward compatibility
        proposal_type = proposal.get("type", "update")
        
        # Map old 'changes' key to 'data' if needed
        payload = proposal.get("data") or proposal.get("changes", {})
        
        # Prepare proposal record
        proposal_record = {
            "proposal_type": proposal_type,
            "status": "pending",
            "target_record_id": proposal.get("id"),  # None for create operations
            "payload": payload,
            "reason": proposal.get("reason", ""),
            "requester_email": requester_email
        }
        
        # Insert into database
        result = self.client.table("proposals").insert(proposal_record).execute()
        
        if result.data and len(result.data) > 0:
            proposal_id = result.data[0]["id"]
            
            # Send Slack notification with interactive buttons
            try:
                from src.interfaces.slack_bot import send_proposal_notification
                # Pass the full proposal data including the ID
                full_proposal = result.data[0]
                send_proposal_notification(full_proposal)
            except Exception as e:
                # Silent fail - don't break if Slack notification fails
                print(f"Warning: Could not send Slack notification: {e}")
            
            return proposal_id
        else:
            raise Exception("Failed to submit proposal")

    def get_pending_proposals(self) -> List[Dict]:
        """
        Get all pending proposals.
        
        Returns:
            List of proposal dictionaries
        """
        result = self.client.table("proposals").select("*").eq("status", "pending").order("created_at", desc=False).execute()
        return result.data

    def approve_proposal(self, proposal_id: str) -> Dict:
        """
        Approve a proposal and execute the corresponding database operation.
        
        Args:
            proposal_id: UUID of the proposal to approve
            
        Returns:
            Result of the executed operation
        """
        # Fetch the proposal
        proposal_result = self.client.table("proposals").select("*").eq("id", proposal_id).execute()
        
        if not proposal_result.data:
            raise ValueError(f"Proposal {proposal_id} not found")
        
        proposal = proposal_result.data[0]
        
        # Import SupabaseManager for executing the actual operation
        from src.tools.supabase_ops import SupabaseManager
        manager = SupabaseManager()
        
        try:
            # Execute the operation based on proposal type
            if proposal["proposal_type"] == "create":
                result = manager.create_record(
                    data=proposal["payload"],
                    approval_given=True
                )
            elif proposal["proposal_type"] == "update":
                result = manager.update_record(
                    record_id=proposal["target_record_id"],
                    data=proposal["payload"],
                    approval_given=True
                )
            else:
                raise ValueError(f"Unknown proposal type: {proposal['proposal_type']}")
            
            # Update proposal status to approved
            self.client.table("proposals").update({"status": "approved"}).eq("id", proposal_id).execute()
            
            # Send email notification if requester email exists
            print(f"DEBUG: Checking for requester_email in proposal: {proposal.get('requester_email')}")
            if proposal.get("requester_email"):
                print(f"DEBUG: Sending approval email to {proposal['requester_email']}")
                self._send_approval_email(proposal)
            else:
                print("DEBUG: No requester_email found, skipping email notification")
            
            return result
            
        except Exception as e:
            # Mark proposal as failed
            self.client.table("proposals").update({"status": "failed", "feedback": str(e)}).eq("id", proposal_id).execute()
            raise e

    def reject_proposal(self, proposal_id: str, feedback: str = "") -> None:
        """
        Reject a proposal with optional feedback.
        
        Args:
            proposal_id: UUID of the proposal to reject
            feedback: Optional rejection reason
        """
        self.client.table("proposals").update({
            "status": "rejected",
            "feedback": feedback
        }).eq("id", proposal_id).execute()
        
        # Send email notification if requester email exists
        proposal_data = self.client.table("proposals").select("*").eq("id", proposal_id).execute()
        if proposal_data.data and proposal_data.data[0].get("requester_email"):
            self._send_rejection_email(proposal_data.data[0], feedback)

    # Legacy methods for backward compatibility
    def get_proposal(self) -> Optional[Dict]:
        """
        Get the first pending proposal (legacy compatibility).
        
        Returns:
            First pending proposal or None
        """
        proposals = self.get_pending_proposals()
        if proposals:
            # Convert to legacy format
            p = proposals[0]
            return {
                "id": p.get("target_record_id"),
                "type": p.get("proposal_type"),
                "data": p.get("payload"),
                "reason": p.get("reason"),
                "_proposal_id": p.get("id")  # Internal ID for operations
            }
        return None
    
    def _send_approval_email(self, proposal):
        """Send email notification when proposal is approved."""
        try:
            from src.interfaces.email_bot import send_notification_email
            
            subject = "✅ Your Proposal Was Approved"
            body = f"""
Good news! Your proposal has been approved.

Proposal Type: {proposal.get('proposal_type', 'N/A').upper()}
Reason: {proposal.get('reason', 'N/A')}
Status: APPROVED

Your changes have been applied to the database.

Thank you for using CrewAI News Manager!
"""
            
            send_notification_email(
                to_address=proposal['requester_email'],
                subject=subject,
                body=body
            )
            print(f"✅ Sent approval email to {proposal['requester_email']}")
            
        except Exception as e:
            print(f"Warning: Could not send approval email: {e}")
    
    def _send_rejection_email(self, proposal, feedback):
        """Send email notification when proposal is rejected."""
        try:
            from src.interfaces.email_bot import send_notification_email
            
            subject = "❌ Your Proposal Was Rejected"
            body = f"""
Your proposal was reviewed and rejected.

Proposal Type: {proposal.get('proposal_type', 'N/A').upper()}
Reason: {proposal.get('reason', 'N/A')}
Status: REJECTED

Feedback: {feedback or 'No feedback provided'}

You can submit a new proposal with revisions.

Thank you for using CrewAI News Manager!
"""
            
            send_notification_email(
                to_address=proposal['requester_email'],
                subject=subject,
                body=body
            )
            print(f"✅ Sent rejection email to {proposal['requester_email']}")
            
        except Exception as e:
            print(f"Warning: Could not send rejection email: {e}")

    def clear_proposal(self) -> None:
        """
        Clear the first pending proposal (legacy compatibility).
        Marks it as rejected.
        """
        proposals = self.get_pending_proposals()
        if proposals:
            self.reject_proposal(proposals[0]["id"], "Cleared by user")
