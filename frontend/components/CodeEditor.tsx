"use client";

import Editor from "@monaco-editor/react";

export default function CodeEditor() {
  return (
    <div className="border rounded-lg">
      <Editor
        height="500px"
        defaultLanguage="python"
        defaultValue={`def solve():
    pass`}
        theme="vs-dark"
      />
    </div>
  );
}
