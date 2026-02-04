
from crewai import Agent, Task, Crew, Process
from src.agents.fetcher import FetcherAgent
from src.tools.supabase_ops import SupabaseManager, SupabaseTools
from src.tools.image_gen import ImageGenTool



class OrchestratorAgent(Agent):

    def __init__(self, **kwargs):
        config = {
            "role": "Professional AI Assistant",
            "goal": "Provide excellent service for news management and IT support tasks with professional, supportive communication.",
            "backstory": (
                "You are a professional AI assistant maintaining high standards of service excellence. "
                "You communicate with a calm, respectful, and supportive tone. "
                "You systematically gather information, ask one question at a time, and provide clear, concise responses. "
                "You are the central intelligence managing news updates and IT support requests."
            ),
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
        
        # Import BehavioralConfig for professional communication guidelines
        from src.core.behavioral_config import BehavioralConfig
        
        # Generate enhanced task description with behavioral guidelines
        task_desc = BehavioralConfig.get_enhanced_task_description(instruction)

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

