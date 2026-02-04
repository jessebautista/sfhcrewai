"""
Comprehensive Feature Testing Script
Tests all features of the SFH CrewAI project
"""
import os
import sys
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()

def print_header(title):
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def print_test(name, status, details=""):
    status_symbol = "✅" if status else "❌"
    print(f"{status_symbol} {name}")
    if details:
        print(f"   {details}")

# TEST 1: Environment Configuration
def test_environment():
    print_header("TEST 1: Environment Configuration")
    
    required_vars = {
        "SUPABASE_URL": os.environ.get("SUPABASE_URL"),
        "SUPABASE_KEY": os.environ.get("SUPABASE_KEY"),
        "OPENROUTER_API_KEY": os.environ.get("OPENROUTER_API_KEY"),
    }
    
    optional_vars = {
        "SLACK_USER_TOKEN": os.environ.get("SLACK_USER_TOKEN"),
        "SLACK_APP_TOKEN": os.environ.get("SLACK_APP_TOKEN"),
        "EMAIL_ADDRESS": os.environ.get("EMAIL_ADDRESS"),
        "EMAIL_PASSWORD": os.environ.get("EMAIL_PASSWORD"),
    }
    
    print("\nRequired Variables:")
    for var, value in required_vars.items():
        print_test(var, bool(value), f"Value: {'Set' if value else 'Not Set'}")
    
    print("\nOptional Variables (for integrations):")
    for var, value in optional_vars.items():
        print_test(var, bool(value), f"Value: {'Set' if value else 'Not Set'}")
    
    return all(required_vars.values())

# TEST 2: Database Connection
def test_database_connection():
    print_header("TEST 2: Database Connection")
    
    try:
        from supabase import create_client
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_KEY")
        
        client = create_client(url, key)
        print_test("Supabase Client Creation", True, "Client initialized successfully")
        
        # Try to query a table
        try:
            response = client.from_("news").select("id").limit(1).execute()
            print_test("Database Query (news table)", True, f"Query successful, returned {len(response.data)} records")
            return True
        except Exception as e:
            print_test("Database Query (news table)", False, str(e))
            return False
            
    except Exception as e:
        print_test("Supabase Client Creation", False, str(e))
        return False

# TEST 3: Database Tables
def test_database_tables():
    print_header("TEST 3: Database Tables")
    
    try:
        from supabase import create_client
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_KEY")
        client = create_client(url, key)
        
        tables = ["news", "agent_logs", "proposals"]
        all_exist = True
        
        for table in tables:
            try:
                response = client.from_(table).select("*").limit(1).execute()
                print_test(f"Table: {table}", True, f"Table exists and accessible")
            except Exception as e:
                print_test(f"Table: {table}", False, str(e))
                all_exist = False
        
        return all_exist
        
    except Exception as e:
        print_test("Database Table Check", False, str(e))
        return False

# TEST 4: Proposal Manager
def test_proposal_manager():
    print_header("TEST 4: Proposal Manager")
    
    try:
        from src.core.proposal import ProposalManager
        
        manager = ProposalManager()
        print_test("ProposalManager Initialization", True, "Manager created successfully")
        
        # Test get_pending_proposals
        try:
            proposals = manager.get_pending_proposals()
            print_test("Get Pending Proposals", True, f"Found {len(proposals)} pending proposal(s)")
        except Exception as e:
            print_test("Get Pending Proposals", False, str(e))
            return False
        
        return True
        
    except Exception as e:
        print_test("ProposalManager Initialization", False, str(e))
        return False

# TEST 5: File Handler
def test_file_handler():
    print_header("TEST 5: File Handler")
    
    try:
        from src.core.file_handler import process_files
        print_test("File Handler Import", True, "Module imported successfully")
        
        # Note: We can't test actual file processing without files
        print_test("File Processing Function", True, "Function available (needs files to test)")
        return True
        
    except Exception as e:
        print_test("File Handler Import", False, str(e))
        return False

# TEST 6: Slack Integration
def test_slack_integration():
    print_header("TEST 6: Slack Integration")
    
    slack_token = os.environ.get("SLACK_USER_TOKEN")
    slack_app_token = os.environ.get("SLACK_APP_TOKEN")
    
    if not slack_token or not slack_app_token:
        print_test("Slack Configuration", False, "Slack tokens not configured in .env")
        return False
    
    try:
        from slack_sdk import WebClient
        client = WebClient(token=slack_token)
        print_test("Slack SDK Import", True, "SDK imported successfully")
        
        # Test connection
        try:
            response = client.auth_test()
            print_test("Slack Connection", True, f"Connected as: {response['user']}")
            return True
        except Exception as e:
            print_test("Slack Connection", False, str(e))
            return False
            
    except Exception as e:
        print_test("Slack SDK Import", False, str(e))
        return False

# TEST 7: Email Integration
def test_email_integration():
    print_header("TEST 7: Email Integration")
    
    email_address = os.environ.get("EMAIL_ADDRESS")
    email_password = os.environ.get("EMAIL_PASSWORD")
    
    if not email_address or not email_password:
        print_test("Email Configuration", False, "Email credentials not configured in .env")
        return False
    
    try:
        import smtplib
        from email.mime.text import MIMEText
        
        print_test("Email Libraries Import", True, "Libraries imported successfully")
        
        # Test SMTP connection
        try:
            smtp_server = os.environ.get("EMAIL_SMTP_SERVER", "smtp.gmail.com")
            smtp_port = int(os.environ.get("EMAIL_SMTP_PORT", 587))
            
            server = smtplib.SMTP(smtp_server, smtp_port, timeout=10)
            server.starttls()
            server.login(email_address, email_password)
            server.quit()
            
            print_test("SMTP Connection", True, f"Connected to {smtp_server}")
            return True
        except Exception as e:
            print_test("SMTP Connection", False, str(e))
            return False
            
    except Exception as e:
        print_test("Email Libraries Import", False, str(e))
        return False

# TEST 8: CrewAI Agent
def test_crewai_agent():
    print_header("TEST 8: CrewAI Agent System")
    
    try:
        from src.agents.orchestrator import OrchestratorAgent
        print_test("OrchestratorAgent Import", True, "Agent module imported successfully")
        
        # Try to create agent instance
        try:
            agent = OrchestratorAgent()
            print_test("OrchestratorAgent Initialization", True, "Agent created successfully")
            return True
        except Exception as e:
            print_test("OrchestratorAgent Initialization", False, str(e))
            return False
            
    except Exception as e:
        print_test("OrchestratorAgent Import", False, str(e))
        return False

# TEST 9: Observability (Agent Logs)
def test_observability():
    print_header("TEST 9: Observability System")
    
    try:
        from supabase import create_client
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_KEY")
        client = create_client(url, key)
        
        # Check if agent_logs table exists and has data
        try:
            response = client.from_("agent_logs").select("*").limit(5).execute()
            print_test("Agent Logs Table", True, f"Table exists with {len(response.data)} recent log(s)")
            return True
        except Exception as e:
            print_test("Agent Logs Table", False, str(e))
            return False
            
    except Exception as e:
        print_test("Observability System", False, str(e))
        return False

# Main Test Runner
def main():
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " "*15 + "SFH CREWAI FEATURE TEST" + " "*20 + "║")
    print("╚" + "="*58 + "╝")
    
    results = {
        "Environment Configuration": test_environment(),
        "Database Connection": test_database_connection(),
        "Database Tables": test_database_tables(),
        "Proposal Manager": test_proposal_manager(),
        "File Handler": test_file_handler(),
        "Slack Integration": test_slack_integration(),
        "Email Integration": test_email_integration(),
        "CrewAI Agent System": test_crewai_agent(),
        "Observability System": test_observability(),
    }
    
    print_header("TEST SUMMARY")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "PASS" if result else "FAIL"
        symbol = "✅" if result else "❌"
        print(f"{symbol} {test_name:<35} {status}")
    
    print("\n" + "-"*60)
    print(f"TOTAL: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    print("-"*60 + "\n")
    
    return results

if __name__ == "__main__":
    results = main()
    
    # Exit with error code if any tests failed
    if not all(results.values()):
        sys.exit(1)
