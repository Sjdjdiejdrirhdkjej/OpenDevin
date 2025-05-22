# OpenDevin

OpenDevin is an automated development agent that can understand tasks, create plans, and execute them to build or modify software.

## Project Purpose

The goal of OpenDevin is to simulate a developer's workflow, including:
- Creating and modifying files.
- Running shell commands.
- Generating execution plans based on a given task.
- Basic debugging by observing command outputs.

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
    Replace `'your_api_key_here'` with your actual API key.

## Setup and Running the Example

To run the current demonstration:
1. Clone the repository (if you haven't already).
   ```bash
   # git clone <repository_url> # Replace with actual URL if applicable
   # cd OpenDevin # Or your repository directory
   ```
2. Set your `MISTRAL_API_KEY` environment variable as described in the "Mistral AI Integration" section above.
3. Install the necessary Python packages. Navigate to the project's root directory (where `requirements.txt` is located) and run:
   ```bash
   pip install -r requirements.txt
   ```
4. Ensure you have Python installed (Python 3.7+ recommended).
5. Navigate to the `OpenDevin` directory in your terminal (if not already there).
6. Run the main entrypoint script:
   ```bash
   python main.py
   ```
This will execute a task using AI-generated plans, such as creating a script, writing to a file, and printing its content.
