import React, { useState, useEffect, useRef } from 'react';
import ChatUI, { Message } from '../components/ChatUI';
import Workspace, { WorkspaceFile } from '../components/Workspace';
import { Agent, AgentAction } from '../agent/Agent'; // Import Agent and AgentAction

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
        addNewMessage('agent', `Agent: Executing command "${action.command}"...`);
        let cmdOutput = '';
        const parts = action.command.split(' ');
        const cmd = parts[0];
        const arg = parts.slice(1).join(' ');

        if (cmd === 'ls') {
          cmdOutput = files.length > 0 ? files.map(f => f.name).join('\n') : '(empty directory)';
        } else if (cmd === 'cat') {
          const fileToCat = files.find(f => f.name === arg);
          cmdOutput = fileToCat ? fileToCat.content : `cat: ${arg}: No such file or directory`;
        } else if (cmd === 'echo') {
          cmdOutput = arg;
        } else {
          cmdOutput = `Command not recognized or not supported in simulation: ${action.command}`;
        }
        setTerminalOutput(prev => `${prev}\n$ ${action.command}\n${cmdOutput}\n`);
        addNewMessage('agent', `Agent: Command output:\n${cmdOutput}`);
        break;
      case 'patch_file':
        addNewMessage('agent', `Agent: Patching file "${action.fileName}"...`);
        let patched = false;
        setFiles(prevFiles =>
          prevFiles.map(file => {
            if (file.name === action.fileName) {
              // Simple append for this simulation. Real patching is complex.
              const updatedContent = file.content + '\n# Patch Applied:\n' + action.patchContent;
              if (file.name === selectedFileName) {
                setSelectedFileContent(updatedContent);
              }
              patched = true;
              return { ...file, content: updatedContent };
            }
            return file;
          })
        );
        if (patched) {
          addNewMessage('agent', `Agent: File "${action.fileName}" patched.`);
        } else {
          addNewMessage('agent', `Agent: File "${action.fileName}" not found for patching.`);
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
    <div style={{ display: 'flex', height: '100vh', fontFamily: 'sans-serif' }}>
      <div style={{ flex: 1, padding: '10px' }}>
        <ChatUI messages={messages} onSendMessage={handleSendMessage} />
      </div>
      <div style={{ flex: 2, padding: '10px' }}>
        <Workspace 
          files={files} 
          terminalOutput={terminalOutput}
          selectedFileContent={selectedFileContent}
          onFileSelect={handleFileSelect}
          {/* Workspace props are: files, terminalOutput, selectedFileContent, onFileSelect */}
          {/* onExecuteCommand and onFileUpdate are App functions, not directly passed to Workspace unless Workspace is enhanced */}
        />
      </div>
    </div>
  );
};

export default App;
