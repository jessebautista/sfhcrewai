
from crewai import Agent, Task, Crew, Process
from src.agents.fetcher import FetcherAgent
from src.tools.supabase_ops import SupabaseManager, SupabaseTools
from src.tools.image_gen import ImageGenTool



class OrchestratorAgent(Agent):

    def __init__(self, **kwargs):
        config = {
            "role": "Orchestrator",
            "goal": "Coordinate news management tasks efficiently.",
            "backstory": "You are the central intelligence managing news updates.",
            "allow_delegation": True,
            "verbose": True
        }
        config.update(kwargs)
        super().__init__(**config)
        # self.validator = ValidatorAgent(...) # To be implemented
        # self.supabase = SupabaseManager() # Instantiated locally if needed

    def run_mission(self, instruction: str, callback_handler=None):
        """
        Executes a mission based on user instruction.
        Constructs a Crew on the fly.
        """
        # Instantiate sub-agents locally to avoid Pydantic attribute issues
        # Equip with Fetch, Submit Update, Submit Create, and Image Gen tools
        fetcher = FetcherAgent(tools=[
            SupabaseTools.fetch_recent_news, 
            SupabaseTools.submit_draft_update,
            SupabaseTools.submit_draft_creation,
            ImageGenTool.generate_image
        ])
        
        # 1. Analyze instruction
        # Enhanced task description to handle both conversation and news tasks
        task_desc = (
            f"Analyze the request: '{instruction}'.\n\n"
            "You are a helpful AI assistant for news management. Follow these guidelines:\n\n"
            "1. **For conversational messages** (greetings, introductions, questions about yourself):\n"
            "   - Respond naturally and warmly\n"
            "   - Acknowledge and remember user information\n"
            "   - Example: 'My name is Alice' → 'Nice to meet you, Alice! I'm your AI news assistant.'\n\n"
            "2. **For checking news**: Use 'Fetch Recent News' tool and present results nicely.\n\n"
            "3. **For UPDATING articles**: Use 'Submit Draft Update' tool.\n\n"
            "4. **For CREATING articles**:\n"
            "   - Generate image first using 'Generate News Image' tool\n"
            "   - Use 'Submit Draft Creation' with title, HTML content, and image URL\n\n"
            "IMPORTANT: If conversational (greeting/introduction), respond WITHOUT using tools."
        )

        fetch_task = Task(
            description=task_desc,
            expected_output="A helpful response that either: (1) Answers conversationally if it's a greeting/introduction/question, OR (2) Confirms the news management action was completed (fetch/draft submission).",
            agent=fetcher
        )
        
        # Create Crew
        crew = Crew(
            agents=[fetcher],
            tasks=[fetch_task],
            verbose=True,
            process=Process.sequential
        )
        
        # Initialize Logger
        from src.core.logger import AgentLogger
        logger = AgentLogger()
        logger.log("Orchestrator", "mission_start", "Starting mission", {"instruction": instruction})

        # Run
        # Note: CrewAI doesn't natively support per-step streaming callbacks easily in all versions.
        # We will manually log start/end for the MVP via the handler if provided.
        if callback_handler:
            callback_handler.on_step_start("Crew", "Starting mission...")
            
        try:
            result = crew.kickoff()
            logger.log("Orchestrator", "mission_end", "Mission completed", {"result": str(result)}, status="success")
        except Exception as e:
            logger.log("Orchestrator", "error", f"Mission failed: {str(e)}", status="failure")
            raise e
        
        if callback_handler:
            callback_handler.on_step_finish("Crew", str(result))
            
        return result

