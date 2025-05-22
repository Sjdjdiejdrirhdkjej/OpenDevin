print("Starting OpenDevin Agent demonstration...")

# Assuming OpenDevin directory is in PYTHONPATH or script is run from OpenDevin/
from src.agent import OpenDevinAgent

if __name__ == "__main__":
    # Instantiate the agent with a specific task
    agent = OpenDevinAgent(task="create a hello world python script and run it")
    
    # Run the task
    agent.run_task()
