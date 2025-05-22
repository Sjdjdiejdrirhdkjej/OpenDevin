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
}) => {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%', border: '1px solid #ccc', borderRadius: '8px', padding: '10px', backgroundColor: '#f9f9f9' }}>
      <h2 style={{ textAlign: 'center', marginTop: 0, marginBottom: '10px', color: '#333' }}>Workspace</h2>
      
      <div style={{ display: 'flex', flexGrow: 1, overflow: 'hidden' }}>
        {/* File List Pane */}
        <div style={{ width: '30%', borderRight: '1px solid #ddd', paddingRight: '10px', overflowY: 'auto' }}>
          <h3 style={{ marginTop: 0, marginBottom: '10px', color: '#555' }}>Files</h3>
          {files.length === 0 ? (
            <p style={{ color: '#777', fontStyle: 'italic' }}>No files in workspace.</p>
          ) : (
            <ul style={{ listStyleType: 'none', paddingLeft: 0, margin: 0 }}>
              {files.map(file => (
                <li 
                  key={file.name} 
                  onClick={() => onFileSelect(file.name)}
                  style={{ 
                    padding: '8px', 
                    cursor: 'pointer', 
                    borderRadius: '4px',
                    marginBottom: '5px',
                    backgroundColor: selectedFileContent && file.content === selectedFileContent ? '#007bff' : 'transparent', // A simple way to highlight, assumes content is unique for selected file
                    color: selectedFileContent && file.content === selectedFileContent ? 'white' : '#333',
                  }}
                  onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = selectedFileContent && file.content === selectedFileContent ? '#0056b3' :'#e9ecef')}
                  onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = selectedFileContent && file.content === selectedFileContent ? '#007bff' : 'transparent')}
                >
                  {file.name}
                </li>
              ))}
            </ul>
          )}
        </div>

        {/* File Viewer Pane */}
        <div style={{ flexGrow: 1, paddingLeft: '10px', display: 'flex', flexDirection: 'column', overflowY: 'auto' }}>
          <h3 style={{ marginTop: 0, marginBottom: '10px', color: '#555' }}>File Viewer</h3>
          {selectedFileContent !== null ? (
            <pre style={{ 
              backgroundColor: '#fff', 
              border: '1px solid #ddd', 
              padding: '10px', 
              flexGrow: 1, 
              overflowY: 'auto', 
              whiteSpace: 'pre-wrap', // Ensure text wraps
              wordBreak: 'break-all', // Ensure long words break
              borderRadius: '4px',
              margin: 0,
            }}>
              {selectedFileContent}
            </pre>
          ) : (
            <div style={{ flexGrow: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#777', fontStyle: 'italic' }}>
              Select a file to view its content.
            </div>
          )}
        </div>
      </div>

      {/* Terminal Output Pane */}
      <div style={{ marginTop: '10px', paddingTop: '10px', borderTop: '1px solid #ddd' }}>
        <h3 style={{ marginTop: 0, marginBottom: '10px', color: '#555' }}>Terminal</h3>
        <pre style={{ 
          backgroundColor: '#222', 
          color: '#0f0', // Classic green terminal text
          padding: '10px', 
          height: '150px', 
          overflowY: 'auto', 
          whiteSpace: 'pre-wrap',
          wordBreak: 'break-all',
          borderRadius: '4px',
          margin: 0,
          fontFamily: 'monospace'
        }}>
          {terminalOutput || 'No terminal output yet.'}
        </pre>
      </div>
    </div>
  );
};

export default Workspace;
