# CrewAI News Manager

Multi-interface AI news management system with Human-in-the-Loop workflow.

---

## 🚀 Quick Start

**Get started in 3 minutes:**

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure environment
cp .env.example .env
# Edit .env with your API keys

# 3. Run database migrations
python scripts/run_migration.py

# 4. Start an interface
streamlit run src/ui/app.py        # Web UI
# OR
python src/interfaces/slack_bot.py  # Slack Bot
# OR
python src/interfaces/email_bot.py  # Email Bot
```

**📖 See [QUICKSTART.md](QUICKSTART.md) for detailed instructions.**

---

## ✨ Features

- **🖥️ Web UI** - Interactive Streamlit dashboard
- **💬 Slack Bot** - Team collaboration with DM commands
- **📧 Email Bot** - Remote access via email commands
- **📎 File Attachments** - Upload images, PDFs, CSVs (all interfaces)
- **🔐 Human-in-the-Loop** - Proposal approval workflow
- **📊 Observability** - Real-time agent logging & dashboard
- **🗄️ Supabase Backend** - Database + file storage

---

## 📂 Project Structure

```
sfhcrewai-main/
├── src/
│   ├── agents/           # CrewAI agents
│   ├── core/             # Core utilities
│   ├── interfaces/       # User interfaces (Web, Slack, Email)
│   ├── tools/            # CrewAI tools
│   └── ui/               # Streamlit components
├── docs/
│   ├── setup/            # Setup guides
│   └── technical_specs/  # Technical documentation
├── scripts/
│   └── db_migrations/    # Database schema
├── tests/                # Test suite
├── QUICKSTART.md         # User guide
└── README.md             # This file
```

---

## 📚 Documentation

### Setup Guides

Located in [`docs/setup/`](docs/setup/):

- **[SLACK_SETUP.md](docs/setup/SLACK_SETUP.md)** - Slack bot configuration
- **[EMAIL_SETUP.md](docs/setup/EMAIL_SETUP.md)** - Email bot configuration
- **[ATTACHMENT_SETUP.md](docs/setup/ATTACHMENT_SETUP.md)** - File storage setup
- **[EMAIL_COMMAND_FILTER.md](docs/setup/EMAIL_COMMAND_FILTER.md)** - Email command format
- **[SLACK_PROPOSAL_APPROVAL.md](docs/setup/SLACK_PROPOSAL_APPROVAL.md)** - Interactive buttons

### User Guides

- **[QUICKSTART.md](QUICKSTART.md)** - Complete usage guide for all interfaces

### Technical Specs

Located in [`docs/technical_specs/`](docs/technical_specs/):
- Database schema
- API integration details
- Architecture documentation

---

## 🛠️ Configuration

### Required Environment Variables

```bash
# Supabase
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=eyJxxx...

# LLM (choose one)
OPENROUTER_API_KEY=sk-or-xxx
# OR
OPENAI_API_KEY=sk-xxx

# Slack (optional)
SLACK_USER_TOKEN=xoxp-xxx
SLACK_APP_TOKEN=xapp-xxx

# Email (optional)
EMAIL_ADDRESS=your@gmail.com
EMAIL_PASSWORD=app-password
SMTP_SERVER=smtp.gmail.com
IMAP_SERVER=imap.gmail.com
```

---

## 🎯 Usage Examples

### Web UI
```bash
streamlit run src/ui/app.py
# Open http://localhost:8501
# Chat, upload files, manage proposals
```

### Slack
```
# Direct message to bot
Create article about AI

# With attachment
[Upload image.jpg]
Create article using this image
```

### Email
```
To: your-email@gmail.com
Subject: COMMAND: Create article about blockchain
Attachments: reference.pdf
```

---

## 🧪 Testing

```bash
# Run tests
pytest

# Test Slack connection
python -c "from slack_sdk import WebClient; print('✅ Slack OK')"

# Test database
python scripts/run_migration.py
```

---

## 📦 Dependencies

Core packages:
- `crewai` - AI agent framework
- `streamlit` - Web UI
- `supabase` - Backend database + storage
- `slack_bolt` - Slack integration
- `pdfplumber` - PDF text extraction
- `Pillow` - Image processing

See [requirements.txt](requirements.txt) for complete list.

---

## 🔧 Database Setup

```bash
# Run all migrations
python scripts/run_migration.py

# Manual migration
python scripts/run_migration.py scripts/db_migrations/01_create_agent_logs.sql
```

See [`scripts/MIGRATION_INSTRUCTIONS.md`](scripts/MIGRATION_INSTRUCTIONS.md) for details.

---

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch
3. Run tests: `pytest`
4. Submit a pull request

---

## 📄 License

MIT License - see LICENSE file for details

---

## 🆘 Support

**Issues?** Check the troubleshooting section in [QUICKSTART.md](QUICKSTART.md)

**Questions?** Review the setup guides in [`docs/setup/`](docs/setup/)

---

**Built with ❤️ using CrewAI, Streamlit, and Supabase**
