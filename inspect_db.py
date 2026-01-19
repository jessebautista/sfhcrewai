
import os
import json
from dotenv import load_dotenv
from src.tools.supabase_ops import SupabaseManager

load_dotenv()

def inspect():
    try:
        manager = SupabaseManager()
        # Fetch 2 records to compare (hopefully getting the 'good' one and the 'new' one)
        data = manager.fetch_recent_news(limit=5)
        print(json.dumps(data, indent=2, default=str))
    except Exception as e:
        print(e)

if __name__ == "__main__":
    inspect()
