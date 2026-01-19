
import streamlit as st
from crewai.tasks.task_output import TaskOutput
from crewai.agents.parser import AgentAction

# Note: CrewAI's callback system structure varies.
# We will use a custom handler class that we can pass to agents or tasks.
# For simplicity in this MVP, we'll patch/wrap the agent's execution or just
# use the step_callback if available.

class StreamlitCallbackHandler:
    def __init__(self, container):
        self.container = container
        self.logs = []

    def log_step(self, agent_output):
        # This is a generic logger function we can call from our agents
        self.logs.append(agent_output)
        with self.container:
            with st.expander(f"Agent Step: {len(self.logs)}", expanded=True):
                st.write(agent_output)

    def on_step_start(self, agent_name, step_detail):
        with self.container:
             st.info(f"**{agent_name}** is thinking...")
    
    def on_step_finish(self, agent_name, output):
        with self.container:
             st.success(f"**{agent_name}** finished: {output}")

