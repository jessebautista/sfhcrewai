# CrewAI News Manager for Sing for Hope

An intelligent, multi-agent system designed to manage news content for Sing for Hope. This application uses [CrewAI](https://crewai.com) for agent orchestration, [Supabase](https://supabase.com) as the backend database, and [Streamlit](https://streamlit.io) for the Human-in-the-Loop (HITL) user interface.

## 🚀 Features

-   **Multi-Agent Orchestration**: Specialized agents for fetching, drafting, and creating news content.
-   **Human-in-the-Loop (HITL)**: Strict approval workflow. Agents can only *propose* changes or new articles; write operations require explicit human approval via the UI.
-   **Supabase Integration**: Securely manages news records in a PostgreSQL database using Supabase.
-   **Image Generation**: Integrated DALL-E 3 support for generating relevant news imagery automatically.
-   **Real-time "Thinking" Interaction**: Watch the agents plan and execute tasks in real-time within the Streamlit interface.

## 🛠️ Tech Stack

-   **Framework**: Python 3.10+
-   **Agents**: CrewAI
-   **UI**: Streamlit
-   **Database**: Supabase (PostgreSQL)
-   **AI/LLM**: OpenAI (GPT-4o) or OpenRouter compatible models

## 📦 Installation

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/jessebautista/sfhcrewai.git
    cd sfhcrewai
    ```

2.  **Set up Virtual Environment**:
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # On Windows: .venv\Scripts\activate
    ```

3.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure Environment**:
    Copy the example environment file and fill in your credentials:
    ```bash
    cp .env.example .env
    ```
    
    Required variables in `.env`:
    -   `SUPABASE_URL`: Your Supabase project URL.
    -   `SUPABASE_KEY`: Your Supabase Service Role Key.
    -   `OPENAI_API_KEY`: Your OpenAI API Key (or OpenRouter key).
    -   `OPENAI_API_BASE`: (Optional) Base URL if using a proxy/OpenRouter.
    -   `OPENAI_MODEL_NAME`: (Optional) Model to use (default: `gpt-4o-mini`).

## 🏃‍♂️ Running the Application

To start the Streamlit interface:

```bash
PYTHONPATH=. streamlit run src/ui/app.py
```

The application will open in your default browser at `http://localhost:8501`.

## 🧪 Testing

This project follows a Test-Driven Development (TDD) approach. To run the test suite:

```bash
pytest
```

## 🛡️ Security

-   **Write Protection**: The `SupabaseManager` is designed to reject direct write operations from agents.
-   **Proposal System**: All changes are channeled through a `ProposalManager` singleton, ensuring they are reviewed in the "Admin Controls" sidebar before execution.

## 📂 Project Structure

-   `src/agents`: Definitions for CrewAI agents (Orchestrator, Fetcher/Content).
-   `src/tools`: Tools for agents (Supabase Ops, Image Gen).
-   `src/core`: Core logic (Proposal Manager).
-   `src/ui`: Streamlit application and custom callback handlers.
-   `tests`: Pytest test suite.
