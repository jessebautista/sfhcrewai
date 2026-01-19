
from src.tools.supabase_ops import SupabaseManager
import random

def test():
    m = SupabaseManager()
    
    # Test 1: Insert without ID
    print("\n--- Test 1: No ID ---")
    try:
        data = {"news_title": "Test No ID", "news_status": "draft"}
        res = m.create_record(data, approval_given=True)
        print("Success:", res)
    except Exception as e:
        print("Failed:", e)

    # Test 2: Insert with Int ID
    print("\n--- Test 2: Int ID ---")
    try:
        rand_id = random.randint(10000, 90000)
        data = {"id": rand_id, "news_title": "Test Int ID", "news_status": "draft"}
        res = m.create_record(data, approval_given=True)
        print("Success:", res)
    except Exception as e:
        print("Failed:", e)

if __name__ == "__main__":
    test()
