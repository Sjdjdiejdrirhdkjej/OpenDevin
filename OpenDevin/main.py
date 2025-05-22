print("Starting OpenDevin Agent demonstration...")

# Assuming OpenDevin directory is in PYTHONPATH or script is run from OpenDevin/
from src.agent import OpenDevinAgent

if __name__ == "__main__":
    # Instantiate the agent with a specific task
    task_description = (
        "Develop a simple Python script that creates a file named 'output.txt', "
        "writes 'Hello from OpenDevin AI!' into it, and then prints the content of 'output.txt' "
        "to the console. Finally, run the script."
    )
    agent = OpenDevinAgent(task=task_description)
    
    # Run the task
    agent.run_task()
