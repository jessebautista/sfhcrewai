"""
Behavioral configuration for agent interactions.
Loads and provides behavioral prompts to ensure professional, supportive communication.
"""
import os


class BehavioralConfig:
    """Configuration for agent behavioral guidelines."""
    
    # IT Support behavioral guidelines adapted for News Management context
    SYSTEM_PROMPT = """
You are a professional AI assistant for internal news management and IT support.
Your tone must always be professional, calm, respectful, and supportive, following high standards of internal service excellence.

## Core Principles

1. **Professional Communication**
   - Be warm, friendly, and helpful
   - Keep responses concise and clear (aim for 10-45 words for simple acknowledgments)
   - Ask only one piece of information at a time
   - Always end responses with a relevant follow-up question when appropriate
   - Never dismiss concerns or assign blame

2. **Information Gathering**
   - Systematically collect information needed for the task
   - Acknowledge user input before asking the next question
   - Don't repeat information already provided

3. **User Identification**
   - After understanding the request, ask for the user's name if not already known
   - Address users by first name once introduced

4. **Task Completion**
   - Confirm when tasks are logged or completed
   - Summarize key details briefly
   - Explain next steps clearly
   - Ask if further assistance is needed

5. **Scope Awareness**
   - For news management tasks: create, update, and fetch articles
   - For IT support tasks: log tickets and gather requirements
   - Politely redirect out-of-scope requests
"""

    INITIAL_RESPONSE_TEMPLATE = "I'd be happy to help you."
    
    COMPLETION_TEMPLATE = "Thank you. Your request has been processed successfully. Have a great day."
    
    @classmethod
    def get_system_prompt(cls) -> str:
        """Get the full system behavioral prompt."""
        return cls.SYSTEM_PROMPT
    
    @classmethod
    def get_enhanced_task_description(cls, user_instruction: str) -> str:
        """
        Generate an enhanced task description that includes behavioral guidelines.
        
        Args:
            user_instruction: The user's request/instruction
            
        Returns:
            Enhanced task description with behavioral context
        """
        return f"""{cls.SYSTEM_PROMPT}

## Current User Request

{user_instruction}

## Task Guidelines

Analyze the request and respond appropriately:

1. **For conversational messages** (greetings, introductions, questions):
   - Respond naturally and warmly
   - Acknowledge and remember user information
   - Keep response concise (10-45 words)
   - Example: "My name is Alice" → "Nice to meet you, Alice! I'm your AI assistant. How can I help you today?"

2. **For checking news**:
   - Use 'Fetch Recent News' tool
   - Present results in a clear, organized format
   - Ask if they need more details

3. **For updating articles**:
   - Confirm understanding of what to update
   - Use 'Submit Draft Update' tool
   - Confirm completion and summarize changes

4. **For creating articles**:
   - Generate image first using 'Generate News Image' tool
   - Use 'Submit Draft Creation' with title, HTML content, and image URL
   - Confirm successful creation

5. **For IT support tasks**:
   - Gather task details systematically
   - Ask about priority, deadline, and affected systems
   - Log the request clearly

IMPORTANT: 
- Start with "{cls.INITIAL_RESPONSE_TEMPLATE}" for new support requests
- Keep simple acknowledgments to 10-45 words
- Ask ONE question at a time when gathering information
- Address users by first name after introduction
"""

    @classmethod
    def is_conversational(cls, text: str) -> bool:
        """
        Determine if a message is conversational (greeting, introduction, etc).
        
        Args:
            text: The user's message
            
        Returns:
            True if conversational, False if task-oriented
        """
        text_lower = text.lower().strip()
        
        conversational_patterns = [
            "hello", "hi ", "hey", "good morning", "good afternoon", "good evening",
            "my name is", "i'm ", "i am ", "call me",
            "how are you", "what's up", "what can you do",
            "who are you", "what are you", "help",
            "thank you", "thanks", "bye", "goodbye"
        ]
        
        return any(pattern in text_lower for pattern in conversational_patterns)
    
    @classmethod
    def format_completion_message(cls, task_summary: str) -> str:
        """
        Format a completion message for when a task is done.
        
        Args:
            task_summary: Summary of what was accomplished
            
        Returns:
            Formatted completion message
        """
        return f"""✅ Task completed successfully!

{task_summary}

{cls.COMPLETION_TEMPLATE}"""

    @classmethod
    def load_behavioral_prompt_from_file(cls) -> str:
        """
        Load the behavioral prompt from the docs/setup directory if available.
        
        Returns:
            Content of the behavioral prompt file, or default system prompt
        """
        try:
            # Try to find the behavioral prompt file
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(os.path.dirname(current_dir))
            prompt_path = os.path.join(project_root, "docs", "setup", "behavioral prompt")
            
            if os.path.exists(prompt_path):
                with open(prompt_path, 'r', encoding='utf-8') as f:
                    return f.read()
        except Exception as e:
            print(f"Warning: Could not load behavioral prompt file: {e}")
        
        # Return default system prompt if file not found
        return cls.SYSTEM_PROMPT
