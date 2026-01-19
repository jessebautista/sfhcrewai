
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
        # We need a more comprehensive task description to handle creation/update logic
        task_desc = (
            f"Analyze the request: '{instruction}'.\n"
            "1. If checking news, fetch recent articles.\n"
            "2. If needing to UPDATE an existing article, use 'Submit Draft Update'.\n"
            "3. If needing to CREATE a NEW article:\n"
            "   - You MUST generate a high-quality image using 'Generate News Image' tool first.\n"
            "   - Then use 'Submit Draft Creation' with the new title, content, and the generated image URL.\n"
            "   - Content should be HTML formatted (simple tags like <p>, <b>, etc.)."
        )

        fetch_task = Task(
            description=task_desc,
            expected_output="Final confirmation that the request was processed or draft submitted.",
            agent=fetcher
        )
        
        # Create Crew
        crew = Crew(
            agents=[fetcher],
            tasks=[fetch_task],
            verbose=True,
            process=Process.sequential
        )
        
        # Run
        # Note: CrewAI doesn't natively support per-step streaming callbacks easily in all versions.
        # We will manually log start/end for the MVP via the handler if provided.
        if callback_handler:
            callback_handler.on_step_start("Crew", "Starting mission...")
            
        result = crew.kickoff()
        
        if callback_handler:
            callback_handler.on_step_finish("Crew", str(result))
            
        return result

