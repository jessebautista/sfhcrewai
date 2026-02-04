"""
SFH CrewAI Project - Feature Report Generator
Generates a comprehensive report of all features and their dependencies.
"""
import os
import sys
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# Feature definitions with descriptions and dependencies
FEATURES = {
    "1. Slack Bot Integration": {
        "description": "Real-time Slack bot for news management with DM and channel mention support",
        "components": [
            "src/interfaces/slack_bot.py - Main bot handler",
            "Direct messaging support",
            "Channel mentions with @bot",
            "Thread-based conversations",
            "Interactive buttons for proposals"
        ],
        "dependencies": [
            "slack-bolt>=1.18.0 - Slack bot framework",
            "slack-sdk - Slack API client",
            "python-dotenv - Environment variables"
        ],
        "env_variables": [
            "SLACK_APP_TOKEN - Slack app-level token",
            "SLACK_BOT_TOKEN - Bot user OAuth token",
            "SLACK_USER_TOKEN - User token for file access"
        ],
        "database_tables": ["conversations", "conversation_messages", "agent_logs", "proposals"],
        "status": "✅ Active"
    },
    
    "2. Email Bot Integration": {
        "description": "Email-based interface for news management via Gmail",
        "components": [
            "src/interfaces/email_bot.py - Email handler",
            "Gmail API integration",
            "Email parsing and processing",
            "Attachment support (PDFs, images)"
        ],
        "dependencies": [
            "google-auth-oauthlib - Gmail authentication",
            "google-auth-httplib2 - HTTP client for Google APIs",
            "google-api-python-client - Gmail API wrapper"
        ],
        "env_variables": [
            "GMAIL_CREDENTIALS_PATH - Path to Gmail OAuth credentials",
            "GMAIL_TOKEN_PATH - Stored token location"
        ],
        "database_tables": ["agent_logs", "proposals"],
        "status": "✅ Active"
    },
    
    "3. Web UI": {
        "description": "Streamlit-based web dashboard for news article management",
        "components": [
            "src/interfaces/web_ui.py - Streamlit app",
            "Article listing and filtering",
            "Manual article creation",
            "Draft proposals management",
            "Real-time updates"
        ],
        "dependencies": [
            "streamlit - Web UI framework",
            "pandas - Data manipulation",
            "python-dotenv - Environment variables"
        ],
        "env_variables": [
            "SUPABASE_URL - Database endpoint",
            "SUPABASE_KEY - Database access key"
        ],
        "database_tables": ["news_articles", "draft_proposals"],
        "status": "✅ Active"
    },
    
    "4. News Management System": {
        "description": "Core news article operations: fetch, create, update",
        "components": [
            "src/tools/supabase_ops.py - Database operations",
            "Fetch recent articles",
            "Create new articles",
            "Update existing articles",
            "Draft proposal system"
        ],
        "dependencies": [
            "supabase>=2.0.0 - Database client",
            "postgrest - PostgreSQL REST client"
        ],
        "env_variables": [
            "SUPABASE_URL",
            "SUPABASE_KEY"
        ],
        "database_tables": ["news_articles", "draft_proposals"],
        "status": "✅ Active"
    },
    
    "5. AI Image Generation": {
        "description": "Automatic image generation for news articles using Google's Imagen",
        "components": [
            "src/tools/image_gen.py - Image generation tool",
            "Vertex AI Imagen integration",
            "Automatic prompt engineering",
            "Cloud Storage upload"
        ],
        "dependencies": [
            "google-cloud-aiplatform - Vertex AI SDK",
            "google-cloud-storage - GCS for image hosting",
            "Pillow - Image processing"
        ],
        "env_variables": [
            "GCP_PROJECT_ID - Google Cloud project",
            "GCP_LOCATION - Vertex AI region (us-central1)",
            "GCS_BUCKET_NAME - Storage bucket for images",
            "GOOGLE_APPLICATION_CREDENTIALS - Service account key"
        ],
        "database_tables": [],
        "status": "✅ Active"
    },
    
    "6. File Attachment Processing": {
        "description": "PDF and image processing for context-aware news management",
        "components": [
            "src/core/file_handler.py - File processor",
            "PDF text extraction",
            "Image upload to cloud storage",
            "Multi-file support"
        ],
        "dependencies": [
            "PyPDF2 - PDF text extraction",
            "google-cloud-storage - Image hosting",
            "Pillow - Image manipulation"
        ],
        "env_variables": [
            "GCS_BUCKET_NAME - Storage bucket"
        ],
        "database_tables": [],
        "status": "✅ Active"
    },
    
    "7. Human-in-the-Loop Workflow": {
        "description": "Proposal system for article changes requiring human approval",
        "components": [
            "Draft proposal creation",
            "Email notifications on approval/rejection",
            "Slack interactive buttons",
            "Two-stage workflow (propose → approve)"
        ],
        "dependencies": [
            "supabase - Proposal storage",
            "google-api-python-client - Gmail for notifications",
            "slack-bolt - Interactive buttons"
        ],
        "env_variables": [
            "SUPABASE_URL",
            "SUPABASE_KEY"
        ],
        "database_tables": ["draft_proposals"],
        "status": "✅ Active"
    },
    
    "8. Observability & Logging": {
        "description": "Agent execution tracking and event logging",
        "components": [
            "src/core/logger.py - Centralized logger",
            "Agent event logging",
            "Mission tracking",
            "Error monitoring"
        ],
        "dependencies": [
            "supabase - Log storage",
            "python standard library (logging)"
        ],
        "env_variables": [
            "SUPABASE_URL",
            "SUPABASE_KEY"
        ],
        "database_tables": ["agent_logs"],
        "status": "✅ Active"
    },
    
    "9. Long-Term Memory (NEW!)": {
        "description": "Persistent conversation memory for context-aware interactions",
        "components": [
            "src/core/memory_manager.py - Memory management",
            "Conversation tracking",
            "Message history storage",
            "Context retrieval (last 20 messages)",
            "Thread-aware memory for Slack",
            "User isolation (separate conversations per user)"
        ],
        "dependencies": [
            "supabase - Conversation storage",
            "python standard library (datetime, typing)"
        ],
        "env_variables": [
            "SUPABASE_URL",
            "SUPABASE_KEY"
        ],
        "database_tables": ["conversations", "conversation_messages"],
        "status": "✅ Active (Just implemented!)"
    },
    
    "10. CrewAI Agent Orchestration": {
        "description": "Multi-agent system for intelligent task delegation",
        "components": [
            "src/agents/orchestrator.py - Main coordinator",
            "src/agents/fetcher.py - Data fetcher agent",
            "Task creation and delegation",
            "Conversational AI support"
        ],
        "dependencies": [
            "crewai>=0.80.0 - Multi-agent framework",
            "langchain - LLM integration",
            "openai - GPT models"
        ],
        "env_variables": [
            "OPENAI_API_KEY - OpenAI API access"
        ],
        "database_tables": ["agent_logs"],
        "status": "✅ Active"
    }
}


def generate_report():
    """Generate a comprehensive feature report."""
    report = []
    
    # Header
    report.append("=" * 80)
    report.append("SFH CREWAI NEWS MANAGER - FEATURE REPORT")
    report.append("=" * 80)
    report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("")
    
    # Summary
    report.append("SUMMARY")
    report.append("-" * 80)
    report.append(f"Total Features: {len(FEATURES)}")
    active_features = sum(1 for f in FEATURES.values() if "✅" in f['status'])
    report.append(f"Active Features: {active_features}")
    report.append("")
    
    # All unique dependencies
    all_deps = set()
    all_env_vars = set()
    all_tables = set()
    
    for feature in FEATURES.values():
        all_deps.update(feature.get('dependencies', []))
        all_env_vars.update(feature.get('env_variables', []))
        all_tables.update(feature.get('database_tables', []))
    
    report.append(f"Total Unique Dependencies: {len(all_deps)}")
    report.append(f"Total Environment Variables: {len(all_env_vars)}")
    report.append(f"Total Database Tables: {len(all_tables)}")
    report.append("")
    report.append("")
    
    # Detailed feature breakdown
    report.append("DETAILED FEATURE BREAKDOWN")
    report.append("=" * 80)
    report.append("")
    
    for feature_name, feature_data in FEATURES.items():
        report.append(f"{feature_name}")
        report.append("-" * 80)
        report.append(f"Status: {feature_data['status']}")
        report.append("")
        
        report.append(f"Description:")
        report.append(f"  {feature_data['description']}")
        report.append("")
        
        if feature_data.get('components'):
            report.append(f"Components:")
            for component in feature_data['components']:
                report.append(f"  • {component}")
            report.append("")
        
        if feature_data.get('dependencies'):
            report.append(f"Dependencies:")
            for dep in feature_data['dependencies']:
                report.append(f"  • {dep}")
            report.append("")
        
        if feature_data.get('env_variables'):
            report.append(f"Environment Variables Required:")
            for env_var in feature_data['env_variables']:
                report.append(f"  • {env_var}")
            report.append("")
        
        if feature_data.get('database_tables'):
            report.append(f"Database Tables:")
            for table in feature_data['database_tables']:
                report.append(f"  • {table}")
            report.append("")
        
        report.append("")
    
    # All dependencies consolidated
    report.append("=" * 80)
    report.append("CONSOLIDATED DEPENDENCY LIST")
    report.append("=" * 80)
    report.append("")
    
    # Group by category
    core_deps = [d for d in all_deps if any(x in d.lower() for x in ['crewai', 'langchain', 'openai'])]
    cloud_deps = [d for d in all_deps if any(x in d.lower() for x in ['google', 'gcp'])]
    slack_deps = [d for d in all_deps if 'slack' in d.lower()]
    db_deps = [d for d in all_deps if any(x in d.lower() for x in ['supabase', 'postgrest'])]
    ui_deps = [d for d in all_deps if any(x in d.lower() for x in ['streamlit', 'pandas', 'pillow', 'pypdf'])]
    other_deps = [d for d in all_deps if d not in core_deps + cloud_deps + slack_deps + db_deps + ui_deps]
    
    if core_deps:
        report.append("AI/Agent Framework:")
        for dep in sorted(core_deps):
            report.append(f"  • {dep}")
        report.append("")
    
    if cloud_deps:
        report.append("Google Cloud Platform:")
        for dep in sorted(cloud_deps):
            report.append(f"  • {dep}")
        report.append("")
    
    if slack_deps:
        report.append("Slack Integration:")
        for dep in sorted(slack_deps):
            report.append(f"  • {dep}")
        report.append("")
    
    if db_deps:
        report.append("Database:")
        for dep in sorted(db_deps):
            report.append(f"  • {dep}")
        report.append("")
    
    if ui_deps:
        report.append("UI & File Processing:")
        for dep in sorted(ui_deps):
            report.append(f"  • {dep}")
        report.append("")
    
    if other_deps:
        report.append("Other:")
        for dep in sorted(other_deps):
            report.append(f"  • {dep}")
        report.append("")
    
    # Database schema
    report.append("=" * 80)
    report.append("DATABASE SCHEMA")
    report.append("=" * 80)
    report.append("")
    for table in sorted(all_tables):
        report.append(f"  • {table}")
    report.append("")
    
    # Environment setup
    report.append("=" * 80)
    report.append("REQUIRED ENVIRONMENT VARIABLES")
    report.append("=" * 80)
    report.append("")
    for env_var in sorted(all_env_vars):
        report.append(f"  • {env_var}")
    report.append("")
    
    report.append("=" * 80)
    report.append("END OF REPORT")
    report.append("=" * 80)
    
    return "\n".join(report)


def save_report(report_content, filename="feature_report.txt"):
    """Save report to file."""
    output_path = os.path.join(os.path.dirname(__file__), filename)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(report_content)
    return output_path


if __name__ == "__main__":
    print("🔍 Generating SFH CrewAI Feature Report...\n")
    
    report = generate_report()
    
    # Print to console
    print(report)
    
    # Save to file
    try:
        filepath = save_report(report)
        print(f"\n📄 Report saved to: {filepath}")
    except Exception as e:
        print(f"\n⚠️ Could not save report to file: {e}")
    
    print("\n✅ Report generation complete!")
