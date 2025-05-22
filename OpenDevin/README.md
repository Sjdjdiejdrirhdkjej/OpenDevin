# OpenDevin

OpenDevin is an automated development agent that can understand tasks, create plans, and execute them to build or modify software.

## Project Purpose

The goal of OpenDevin is to simulate a developer's workflow, including:
- Creating and modifying files.
- Running shell commands.
- Generating execution plans based on a given task.
- Basic debugging by observing command outputs.

OpenDevin now utilizes the `smolagents` library to define and manage its core operations as discrete `Task` objects. This provides a more modular and extensible architecture. The agent, powered by Mistral AI for plan generation, translates these plans into a sequence of `smolagents` tasks for execution.

This project is an exploration into automated software development processes.

## Mistral AI Integration

The agent now uses Mistral AI for dynamic plan generation. This allows it to handle a wider variety of tasks by creating plans on-the-fly.

To enable this functionality, you need to provide your Mistral AI API key:
1.  Set your Mistral AI API key as an environment variable named `MISTRAL_API_KEY`.

    *   **Linux/macOS (bash/zsh):**
        ```bash
        export MISTRAL_API_KEY='your_api_key_here'
        ```
    *   **Windows (Command Prompt):**
        ```cmd
        set MISTRAL_API_KEY=your_api_key_here
        ```
    *   **Windows (PowerShell):**
        ```powershell
        $env:MISTRAL_API_KEY='your_api_key_here'
        ```
    Replace `'your_api_key_here'` with your actual API key. If this key is not set, the agent (both web and CLI) will not be able to generate plans using Mistral AI.

## Core Dependencies

The project relies on several Python packages. Key dependencies include:
- `mistralai`: For interacting with the Mistral AI API.
- `Flask`: For the web application interface.
- `smolagents`: For structuring agent operations as discrete tasks.

These and other necessary packages are listed in `requirements.txt`.

## Running the Web Application

This is the primary way to interact with OpenDevin.
1.  **Set API Key**: Ensure your `MISTRAL_API_KEY` environment variable is set as described in the "Mistral AI Integration" section. This is crucial for the web application to function correctly.
2.  **Install Dependencies**: Navigate to the project's root directory (the one containing `OpenDevin/` and `requirements.txt`) and install all necessary packages, including Flask:
    ```bash
    pip install -r requirements.txt
    ```
    (You might need to use `pip3` depending on your Python installation.)
3.  **Navigate to Project Root**: Ensure your terminal is in the `OpenDevin` root directory.
4.  **Run the Application**: Execute the following command:
    ```bash
    python run.py
    ```
    (Or `python3 run.py` if `python` defaults to Python 2 for you.)
5.  **Access in Browser**: Open your web browser and go to `http://127.0.0.1:5000/`.

### Using the Web Interface
-   **Setting the API Key**: If you haven't set the `MISTRAL_API_KEY` as an environment variable, or if you need to override it for the session, use the "Setup API Key" link on the web page. Enter your key there and save it. This key will be stored in your browser session for the web interface.
-   **Submitting a Task**: On the main page, type your desired task into the text area (e.g., "Create a Python script that lists files in the current directory.") and click "Run Task".
-   **Viewing Results**:
    -   **Generated Plan**: The plan created by the Mistral AI to address your task will appear in a designated section.
    -   **Execution Log**: The step-by-step execution of this plan by the agent, including outputs from commands or file operations, will be shown in the execution log section.

## Running the Command-Line Interface (CLI)

For direct command-line interaction or testing, you can use `main.py`.
1.  **Clone Repository**: If you haven't already, clone the project.
    ```bash
    # git clone <repository_url> # Replace with actual URL if applicable
    # cd OpenDevin
    ```
2.  **Set API Key**: Ensure your `MISTRAL_API_KEY` environment variable is set (see "Mistral AI Integration").
3.  **Install Dependencies**: Run `pip install -r requirements.txt` from the project root.
4.  **Ensure Python Version**: Python 3.7+ is recommended.
5.  **Navigate to Directory**: Change to the `OpenDevin` directory.
6.  **Run the Script**: Execute the `main.py` script:
    ```bash
    python main.py
    ```
This will run a predefined task (currently configured in `main.py`) using the agent, printing output to the console. This is useful for quick tests of the agent's core logic.
