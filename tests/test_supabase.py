
import pytest
from unittest.mock import MagicMock, patch
import os

# Mock environment before importing SupabaseManager
os.environ["SUPABASE_URL"] = "https://example.supabase.co"
os.environ["SUPABASE_KEY"] = "exampleservicekey"

from src.tools.supabase_ops import SupabaseManager

@patch("src.tools.supabase_ops.create_client")
def test_supabase_init(mock_create):
    """Test that client initializes with env vars."""
    manager = SupabaseManager()
    assert manager.allow_delete is False
    mock_create.assert_called_once()

@patch("src.tools.supabase_ops.create_client")
def test_fetch_recent_news(mock_create):
    """Test fetching news calls select/order."""
    mock_client = MagicMock()
    mock_create.return_value = mock_client
    
    # Mock chain: from_ -> select -> order -> limit -> execute
    mock_query = mock_client.from_.return_value.select.return_value.order.return_value.limit.return_value
    mock_query.execute.return_value.data = [{"id": 1, "title": "Test"}]

    manager = SupabaseManager()
    results = manager.fetch_recent_news(limit=5)
    
    assert len(results) == 1
    mock_client.from_.assert_called_with("news")

@patch("src.tools.supabase_ops.create_client")
def test_update_record_no_approval(mock_create):
    """Test update fails without approval."""
    manager = SupabaseManager()
    with pytest.raises(PermissionError):
        manager.update_record("123", {"title": "New"}, approval_given=False)

@patch("src.tools.supabase_ops.create_client")
def test_update_record_with_approval(mock_create):
    """Test update succeeds with approval."""
    mock_client = MagicMock()
    mock_create.return_value = mock_client
    
    manager = SupabaseManager()
    manager.update_record("123", {"title": "New"}, approval_given=True)
    
    # Verify update chain
    mock_client.from_.assert_called_with("news")
    mock_client.from_.return_value.update.assert_called_with({"title": "New"})
