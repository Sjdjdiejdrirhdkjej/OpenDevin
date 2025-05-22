import React, { useState, useEffect, useRef } from 'react';
import ChatUI, { Message } from '../components/ChatUI';
import Workspace, { WorkspaceFile } from '../components/Workspace';
import { Agent, AgentAction } from '../agent/Agent'; // Import Agent and AgentAction
import './App.css'; // Import the CSS file

const App: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([
    { id: '1', sender: 'agent', text: 'Hello! How can I help you today? Try commands like @create_file(test.txt) file_content or @shell(ls)' }
  ]);
  const [files, setFiles] = useState<WorkspaceFile[]>([]);
  const [terminalOutput, setTerminalOutput] = useState<string>('');
  const [selectedFileName, setSelectedFileName] = useState<string | null>(null);
  const [selectedFileContent, setSelectedFileContent] = useState<string | null>(null);

  const agentRef = useRef<Agent | null>(null);

  // Helper to add new messages (user or agent)
  const addNewMessage = (sender: 'user' | 'agent', text: string) => {
    const newMessage: Message = {
      id: `${Date.now()}-${Math.random().toString(16).slice(2)}`, // More unique ID
      sender,
      text,
    };
    setMessages(prevMessages => [...prevMessages, newMessage]);
  };

  // Agent action handler
  const handleAgentAction = (action: AgentAction) => {
    switch (action.type) {
      case 'create_file':
        addNewMessage('agent', `Agent: Creating file "${action.fileName}"...`);
        setFiles(prevFiles => {
          const existingFileIndex = prevFiles.findIndex(f => f.name === action.fileName);
          const newFile = { name: action.fileName, content: action.content || "" };
          if (existingFileIndex !== -1) {
            const updatedFiles = [...prevFiles];
            updatedFiles[existingFileIndex] = newFile; // Overwrite
            addNewMessage('agent', `Agent: File "${action.fileName}" updated.`);
            if (action.fileName === selectedFileName) {
              setSelectedFileContent(newFile.content);
            }
            return updatedFiles;
          } else {
            addNewMessage('agent', `Agent: File "${action.fileName}" created.`);
            return [...prevFiles, newFile];
          }
        });
        break;
      case 'shell':
        {
          addNewMessage('agent', `Agent: Executing command "${action.command}"...`);
          let cmdOutput = '';
          const fullCommand = action.command;
          const commandParts = fullCommand.split(' ');
          const baseCmd = commandParts[0];
          const args = commandParts.slice(1);
          const firstArg = args[0]; // Could be undefined
          const remainingArgs = args.slice(1); // Could be empty

          if (baseCmd === 'ls') {
            if (!firstArg || firstArg === '.') {
              cmdOutput = files.length > 0 ? files.map(f => f.name).join('\n') : '(empty directory)';
            } else {
              // Basic simulation: if ls has an argument, assume it's a path.
              // We don't have real directories, so we'll filter files that "start with" the path.
              const pathPrefix = firstArg.endsWith('/') ? firstArg : `${firstArg}/`;
              const dirFiles = files.filter(f => f.name.startsWith(pathPrefix));
              if (dirFiles.length > 0) {
                cmdOutput = dirFiles.map(f => f.name.substring(pathPrefix.length) || f.name).join('\n');
              } else {
                // Check if 'firstArg' itself is a file or a simulated directory (if we add that later)
                const exactMatchFile = files.find(f => f.name === firstArg);
                if (exactMatchFile) {
                  cmdOutput = exactMatchFile.name; // ls on a file name just lists the file name
                } else {
                  cmdOutput = `ls: cannot access '${firstArg}': No such file or directory (or directory is empty)`;
                }
              }
            }
          } else if (baseCmd === 'cat') {
            if (!firstArg) {
              cmdOutput = 'cat: missing filename';
            } else {
              const fileToCat = files.find(f => f.name === firstArg);
              cmdOutput = fileToCat ? fileToCat.content : `cat: ${firstArg}: No such file or directory`;
            }
          } else if (baseCmd === 'echo') {
            // The agent passes the full string after `echo ` (if any) as part of `action.command`.
            // So, action.command might be "echo hello world" or "echo \"quoted text\"".
            // We just need to take the substring after "echo ".
            cmdOutput = fullCommand.substring(baseCmd.length + 1).trim(); // +1 for the space
          } else if (baseCmd === 'mkdir') {
            if (!firstArg) {
              cmdOutput = 'mkdir: missing operand';
            } else {
              // For now, just a message. No actual directory creation in files state.
              // We could validate dirname (e.g. no slashes, not existing file name)
              if (files.some(f => f.name === firstArg || f.name.startsWith(`${firstArg}/`))) {
                cmdOutput = `mkdir: cannot create directory ‘${firstArg}’: File or directory exists`;
              } else {
                cmdOutput = `Directory "${firstArg}" created successfully. (Simulated: no actual change in file system yet)`;
                 // Optional: Add a simulated directory entry if desired for 'ls'
                 // setFiles(prevFiles => [...prevFiles, { name: `${firstArg}/`, content: '', type: 'directory' }]);
              }
            }
          } else if (baseCmd === 'pwd') {
            cmdOutput = '/app/simulated_root';
          } else if (baseCmd === 'clear') {
            setTerminalOutput(''); // Clear the terminal output directly
            addNewMessage('agent', 'Agent: Terminal cleared.');
            // No cmdOutput needed as the terminal itself is cleared.
            // We break early to avoid appending to terminalOutput.
            return; // Important to return to avoid default terminal output handling
          }
          else {
            cmdOutput = `Command not found: ${fullCommand}`;
          }
          setTerminalOutput(prev => `${prev}\n$ ${fullCommand}\n${cmdOutput}\n`);
          
          // Refined chat message for shell command errors
          const isErrorOutput = /No such file|Command not found|missing operand|cannot access|cannot create directory/i.test(cmdOutput);
          const chatMessagePrefix = isErrorOutput ? `Agent: Error executing command "${fullCommand}":` : `Agent: Command output for "${fullCommand}":`;
          addNewMessage('agent', `${chatMessagePrefix}\n${cmdOutput}`);
        }
        break;
      case 'patch_file':
        addNewMessage('agent', `Agent: Attempting to patch file "${action.fileName}"...`);
        let filePatched = false;
        setFiles(prevFiles =>
          prevFiles.map(file => {
            if (file.name === action.fileName) {
              // Replace the entire content with the patchContent
              const updatedContent = action.patchContent;
              if (file.name === selectedFileName) {
                setSelectedFileContent(updatedContent);
              }
              filePatched = true;
              return { ...file, content: updatedContent };
            }
            return file;
          })
        );
        if (filePatched) {
          addNewMessage('agent', `Agent: File "${action.fileName}" patched successfully.`);
        } else {
          addNewMessage('agent', `Agent: Error patching. File "${action.fileName}" not found.`);
        }
        break;
      case 'message':
        addNewMessage('agent', action.text);
        break;
      default:
        // Should be exhaustive, but good to have a default
        console.warn('Unknown agent action:', action);
        addNewMessage('agent', 'Agent attempted an unknown action.');
    }
  };
  
  // Initialize agent
  useEffect(() => {
    if (!agentRef.current) {
      agentRef.current = new Agent(handleAgentAction);
    }
  }, []); // Empty dependency array means this runs once on mount

  const handleSendMessage = (userMessage: string) => {
    addNewMessage('user', userMessage);
    if (agentRef.current) {
      agentRef.current.processUserMessage(userMessage);
    } else {
      // This case should ideally not happen if agent is initialized on mount
      addNewMessage('agent', 'Error: Agent not available.');
      console.error('Agent not initialized when trying to send message.');
    }
  };

  // handleExecuteCommand is largely superseded by agent's @shell.
  // It could be repurposed for a direct terminal input in Workspace if desired later.
  /*
  const handleExecuteCommand = (command: string) => {
    setTerminalOutput(prevOutput => prevOutput + `\n$ ${command}\n`);
    // ... existing simulation ...
  };
  */
  
  // handleFileUpdate is for direct edits (e.g., if a text editor for files is added)
  // The agent uses patch_file for its modifications.
  const handleFileUpdate = (fileName: string, newContent: string) => {
    setFiles(prevFiles => 
      prevFiles.map(file => 
        file.name === fileName ? { ...file, content: newContent } : file
      )
    );
    if (fileName === selectedFileName) {
      setSelectedFileContent(newContent);
    }
    // Optionally, could inform agent or add a system message about direct update
    // addNewMessage('system', `File ${fileName} was updated directly.`);
  };

  const handleFileSelect = (fileName: string) => {
    const file = files.find(f => f.name === fileName);
    if (file) {
      setSelectedFileName(file.name);
      setSelectedFileContent(file.content);
    } else {
      setSelectedFileName(null);
      setSelectedFileContent(null);
      // Optionally, add a message to terminalOutput if file not found, though this case should be rare if selection is from the list
      setTerminalOutput(prev => prev + `\nError: File "${fileName}" not found for selection.\n`);
    }
  };

  return (
    <div className="app-container"> {/* Use className for App.css styling */}
      <div className="chat-column"> {/* Use className */}
        <ChatUI messages={messages} onSendMessage={handleSendMessage} />
      </div>
      <div className="workspace-column"> {/* Use className */}
        <Workspace 
          files={files} 
          terminalOutput={terminalOutput}
          selectedFileContent={selectedFileContent}
          selectedFileName={selectedFileName} // Pass selectedFileName
          onFileSelect={handleFileSelect}
        />
      </div>
    </div>
  );
};

export default App;
