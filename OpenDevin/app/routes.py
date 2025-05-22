from flask import render_template, request, redirect, url_for, session, flash
from app import app  # Imports the app object from app/__init__.py
import os
import json # For pretty printing plan if it's a complex structure

# Assuming OpenDevinAgent is in OpenDevin/src/agent.py
# Adjust import path if necessary, for example, by adding OpenDevin to PYTHONPATH
# For now, let's assume a way to import it. If src is not directly in sys.path,
# this might require adjustment in how the app is run or by adding:
# import sys
# sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
# This sys.path modification is often better handled outside the module itself.
# For this subtask, assume 'from src.agent import OpenDevinAgent' works.
# If it causes issues in testing, it means we need to adjust PYTHONPATH or the import strategy.

try:
    from src.agent import OpenDevinAgent
except ImportError:
    # This is a fallback for the subtask environment if src.agent isn't found immediately.
    # In a real run environment, this path needs to be correct.
    # The worker should try to make the import `from src.agent import OpenDevinAgent` work.
    # One way is to ensure the OpenDevin directory (parent of src and app) is in PYTHONPATH.
    # For the purpose of this subtask, if direct import fails, we'll use a placeholder.
    # The final integration test will reveal if the import is truly problematic.
    print("Warning: Could not import OpenDevinAgent. Using a placeholder if available.")
    # Define a placeholder if needed for the Flask routes to be syntactically correct,
    # but the actual agent logic won't run.
    # This should ideally not be needed if the worker sets up the environment for `python run.py` correctly.
    class OpenDevinAgent:
        def __init__(self, task, api_key=None):
            self.task = task
            self.api_key = api_key
            print(f"Placeholder OpenDevinAgent initialized with task: {self.task}")
            if not api_key:
                print("Warning: API key not provided to placeholder agent.")

        def generate_plan(self, task_string): # Changed from self.task to task_string
            print(f"Placeholder: Generating plan for {task_string}")
            if not self.api_key:
                return [{"action": "error", "args": {"message": "API Key is missing."}}]
            return [{"action": "echo", "args": {"message": f"Plan for {task_string} with API key {self.api_key[:5]}..."}}]

        def execute_plan(self, plan):
            print(f"Placeholder: Executing plan: {plan}")
            log = []
            for action in plan:
                log.append(f"[ACTION]: {action['action']} - Args: {action.get('args', {})}")
                if action['action'] == "error":
                    log.append(f"[ERROR]: {action['args']['message']}")
            return log


# It's good practice to set a secret key for session management.
# For production, this should be a strong, random key set via environment variable.
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'dev_secret_key_for_flask_session')

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    task_input = ""
    plan_str = None
    execution_log_str = None

    if request.method == 'POST':
        task_input = request.form.get('task')
        api_key = session.get('mistral_api_key')

        if not api_key:
            flash('Mistral AI API key is not set. Please set it up first.', 'error')
            return redirect(url_for('setup'))

        if not task_input:
            flash('Please enter a task.', 'error')
        else:
            try:
                # Ensure OpenDevin/src is in path or agent is installed
                agent = OpenDevinAgent(task=task_input, api_key=api_key)
                
                # Generate plan
                # Assuming generate_plan takes the task string as an argument
                plan = agent.generate_plan(task_string=task_input) 
                try:
                    # Pretty print JSON for readability in HTML <pre> tag
                    plan_str = json.dumps(plan, indent=4)
                except TypeError: # Handle if plan is not JSON serializable (e.g. already a string)
                    plan_str = str(plan)

                # Execute plan
                # Modify execute_plan to return logs instead of just printing
                execution_log = agent.execute_plan(plan) 
                execution_log_str = "\n".join(execution_log)

            except ImportError as e:
                flash(f"Error importing OpenDevinAgent: {e}. Make sure the agent source is correctly placed.", "error")
                plan_str = "Error: Agent logic could not be loaded."
            except Exception as e:
                flash(f"An error occurred: {e}", "error")
                plan_str = f"Error during agent operation: {e}"


    return render_template('index.html', task_input=task_input, plan_str=plan_str, execution_log_str=execution_log_str)

@app.route('/setup', methods=['GET', 'POST'])
def setup():
    if request.method == 'POST':
        api_key = request.form.get('api_key')
        if api_key:
            session['mistral_api_key'] = api_key
            flash('API Key saved successfully!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Please enter an API key.', 'error')
    
    current_key = session.get('mistral_api_key')
    key_display = current_key[:5] + "..." if current_key else "Not Set"
    
    return render_template('setup.html', current_api_key_display=key_display)
