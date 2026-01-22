import os
from supabase import create_client, Client
from dotenv import load_dotenv
from crewai.tools import tool

load_dotenv()

from src.core.proposal import ProposalManager

class SupabaseTools:
    @tool("Fetch Recent News")
    def fetch_recent_news(limit: int = 5):
        """Fetch the latest news articles from the database. Useful for getting context on existing news."""
        # Note: In a real app, we'd instantiate the manager properly or use a singleton.
        # For simplicity, we'll reconnect or assume env vars are present.
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_KEY")
        client = create_client(url, key)
        data = client.from_("news").select("*").order("created_at", desc=True).limit(limit).execute()
        return str(data.data)

    @tool("Submit Draft Update")
    def submit_draft_update(record_id: str, changes: str, reason: str):
        """
        Propose an update to a news record. DOES NOT write to database immediately.
        Requires human approval.
        Args:
            record_id: The ID of the record to update.
            changes: A JSON string representation of the dictionary of changes (e.g., '{"news_title": "New Title"}').
            reason: The reason for the change.
        """
        import json
        try:
            changes_dict = json.loads(changes)
        except json.JSONDecodeError:
            return "Error: Changes must be valid JSON string."

        proposal = {
            "id": record_id,
            "changes": changes_dict,
            "reason": reason
        }
        ProposalManager().submit_proposal(proposal)
        return "Draft submitted for approval. Please wait for human review."

    @tool("Submit Draft Creation")
    def submit_draft_creation(title: str, content: str, image_url: str = None, reason: str = "New article"):
        """
        Propose a NEW news article. DOES NOT write to database immediately.
        Requires human approval.
        Args:
            title: The title of the new article.
            content: The HTML content of the article (for 'tiny' field).
            image_url: Optional URL for the main image.
            reason: Context for why this is being created.
        """
        import datetime
        import re

        # Generate slug from title
        slug = re.sub(r'[^a-zA-Z0-9\s]', '', title).lower().strip().replace(' ', '-')
        
    @tool("Submit Draft Creation")
    def submit_draft_creation(title: str, content: str, image_url: str = None, reason: str = "New article"):
        """
        Propose a NEW news article. DOES NOT write to database immediately.
        Requires human approval.
        Args:
            title: The title of the new article.
            content: The HTML content of the article (for 'tiny' field).
            image_url: Optional URL for the main image.
            reason: Context for why this is being created.
        """
        import datetime
        import re
        import random

        # Generate slug from title
        slug = re.sub(r'[^a-zA-Z0-9\s]', '', title).lower().strip().replace(' ', '-')
        
        # Current timestamp
        now = datetime.datetime.now().isoformat()
        
        # Generate random ID (Int32 safe)
        rand_id = random.randint(100000, 999999)

        proposal = {
            "type": "create",
            "data": {
                "id": rand_id, # Required by DB schema
                "news_title": title,
                "tiny": content,
                "news_content": {"content": "content"}, # Default structure seen in existing records
                "news_image": image_url or "",
                "news_status": "draft", # Explicit status
                "news_date": now,
                "created_at": now,
                "news_url": slug,
                "news_excerpt": "New article draft." # Default excerpt
            },
            "reason": reason
        }
        
        # Get requester email from context if available
        try:
            from src.core.request_context import get_requester_email
            requester_email = get_requester_email()
        except:
            requester_email = None
        
        ProposalManager().submit_proposal(proposal, requester_email=requester_email)
        return "New article draft submitted for approval."



class SupabaseManager:
    def __init__(self):
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_KEY")
        if not url or not key:
            raise ValueError("Supabase credentials not found in environment.")
        
        self.client: Client = create_client(url, key)
        self.allow_delete = False # Strict safety rule

    def fetch_recent_news(self, limit: int = 5):
        """Fetch latest news articles."""
        data = self.client.from_("news").select("*").order("created_at", desc=True).limit(limit).execute()
        return data.data

    def get_article_by_id(self, article_id: str):
        """Fetch single article by ID."""
        data = self.client.from_("news").select("*").eq("id", article_id).execute()
        return data.data[0] if data.data else None

    
    def create_record(self, data: dict, approval_given: bool = False):
        """
        Create a new record safely.
        Requires explicit approval_given=True.
        """
        if not approval_given:
             raise PermissionError("Approval not given for write operation.")
        
        response = self.client.from_("news").insert(data).execute()
        return response.data

    def update_record(self, record_id: str, data: dict, approval_given: bool = False):
        """
        Update a record safely.
        Requires explicit approval_given=True.
        """
        if not approval_given:
            raise PermissionError("Approval not given for write operation.")
        
        # Safety check: ensure no delete-like operations (updates are fine, but be careful)
        if "delete" in data:
             raise ValueError("Delete operations are strictly prohibited.")

        response = self.client.from_("news").update(data).eq("id", record_id).execute()
        return response.data

