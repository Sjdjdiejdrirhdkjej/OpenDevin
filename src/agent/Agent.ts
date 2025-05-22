// src/agent/Agent.ts

export interface CreateFileAction {
  type: 'create_file';
  fileName: string;
  content?: string;
}

export interface ShellCommandAction {
  type: 'shell';
  command: string;
}

export interface PatchFileAction {
  type: 'patch_file';
  fileName: string;
  patchContent: string; // This would typically be a diff string or specific patch instructions
}

export interface AgentMessageAction {
  type: 'message';
  text: string;
}

export type AgentAction = 
  | CreateFileAction 
  | ShellCommandAction 
  | PatchFileAction
  | AgentMessageAction;

type OnAgentActionCallback = (action: AgentAction) => void;

export class Agent {
  private onAgentAction: OnAgentActionCallback;

  constructor(onAgentAction: OnAgentActionCallback) {
    if (typeof onAgentAction !== 'function') {
      throw new Error('onAgentAction callback must be a function.');
    }
    this.onAgentAction = onAgentAction;
  }

  public processUserMessage(messageText: string): void {
    let action: AgentAction | null = null;

    // Regex for @create_file(fileName) content
    const createFileRegex = /@create_file\(([^)]+)\)(?:\s+(.*))?/s;
    const createFileMatch = messageText.match(createFileRegex);

    // Regex for @shell(command)
    const shellCommandRegex = /@shell\(([^)]+)\)/;
    const shellCommandMatch = messageText.match(shellCommandRegex);

    // Regex for [PATCH]: fileName\n\n<patch_content>
    // This regex assumes patch content starts after two newlines.
    const patchFileRegex = /^\[PATCH\]:\s*(\S+)\s*\n\n([\s\S]*)/;
    const patchFileMatch = messageText.match(patchFileRegex);

    if (createFileMatch) {
      const fileName = createFileMatch[1].trim();
      const content = createFileMatch[2]?.trim(); // content is optional
      action = { type: 'create_file', fileName, content };
    } else if (shellCommandMatch) {
      const command = shellCommandMatch[1].trim();
      action = { type: 'shell', command };
    } else if (patchFileMatch) {
      const fileName = patchFileMatch[1].trim();
      const patchContent = patchFileMatch[2]; // patchContent includes newlines etc.
      action = { type: 'patch_file', fileName, patchContent };
    } else {
      // Command not recognized by any regex
      action = { type: 'message', text: `Agent: Error - Unrecognized command or syntax: "${messageText}"` };
    }

    // Ensure action is always non-null before calling onAgentAction
    // Though in current logic, 'action' will always be assigned.
    if (action) {
      this.onAgentAction(action);
    } else {
      // Should not happen if there's a default action, but as a fallback:
      this.onAgentAction({ type: 'message', text: `Agent could not process: "${messageText}"`});
    }
  }
}

// Example usage (for testing purposes, not part of the final implementation here)
/*
const agent = new Agent((action) => {
  console.log("Agent action:", action);
});

agent.processUserMessage("Hello there!");
agent.processUserMessage("@create_file(test.txt)");
agent.processUserMessage("@create_file(another.txt) This is some content.");
agent.processUserMessage("@shell(ls -la)");
agent.processUserMessage(`[PATCH]: myFile.txt

<<<<<<< ORIGINAL
Some original content
=======
Some new content
>>>>>>> MODIFIED
`);
agent.processUserMessage("@unknown_command(test)");
*/
