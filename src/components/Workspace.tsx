import React from 'react';

// Type for a file in the workspace
export interface WorkspaceFile {
  name: string;
  content: string; // For now, content is simple text. Could be more complex later.
}

// Props for the Workspace component
interface WorkspaceProps {
  files: WorkspaceFile[];
  terminalOutput: string;
  selectedFileContent: string | null;
  onFileSelect: (fileName: string) => void;
  // onExecuteCommand: (command: string) => void; // Kept for potential future use, but not used in this version
  // onFileUpdate: (fileName: string, newContent: string) => void; // Kept for potential future use
}

const Workspace: React.FC<WorkspaceProps> = ({
  files,
  terminalOutput,
  selectedFileContent,
  onFileSelect,
  // selectedFileName prop is needed to determine which file is selected for styling
  // This was not explicitly in the original props but is implied by "visual indicator for selected file"
  // Let's assume selectedFileName is passed down from App.tsx (it is already being managed there)
  selectedFileName, 
}) => {
  return (
    <div className="workspace-container">
      <h2 className="workspace-title">Workspace</h2>
      
      <div className="workspace-main-area">
        {/* File List Pane */}
        <div className="file-list-pane">
          <h3 className="file-list-title">Files</h3>
          {files.length === 0 ? (
            <p style={{ color: '#777', fontStyle: 'italic' }}>No files in workspace.</p> // Inline style for simple placeholder
          ) : (
            <ul className="file-list">
              {files.map(file => (
                <li 
                  key={file.name} 
                  onClick={() => onFileSelect(file.name)}
                  // Apply 'file-list-item' and conditional 'selected' class
                  className={`file-list-item ${file.name === selectedFileName ? 'selected' : ''}`}
                >
                  {file.name}
                </li>
              ))}
            </ul>
          )}
        </div>

        {/* File Viewer Pane */}
        <div className="file-viewer-pane">
          <h3 className="file-viewer-title">File Viewer</h3>
          {selectedFileContent !== null ? (
            <pre className="file-viewer-content">
              {selectedFileContent}
            </pre>
          ) : (
            <div className="file-viewer-placeholder">
              Select a file to view its content.
            </div>
          )}
        </div>
      </div>

      {/* Terminal Output Pane */}
      <div className="terminal-pane">
        <h3 className="terminal-title">Terminal</h3>
        <pre className="terminal-output">
          {terminalOutput || 'No terminal output yet.'}
        </pre>
      </div>
    </div>
  );
};

export default Workspace;
