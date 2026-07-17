"use client";

import dynamic from "next/dynamic";

const MonacoEditor = dynamic(() => import("@monaco-editor/react"), { ssr: false });

const SUPPORTED_LANGUAGES = ["python", "javascript", "typescript", "java", "cpp"] as const;

interface CodeEditorPanelProps {
  language: string;
  code: string;
  onLanguageChange: (language: string) => void;
  onCodeChange: (code: string) => void;
  fullScreen?: boolean;
}

export default function CodeEditorPanel({
  language,
  code,
  onLanguageChange,
  onCodeChange,
  fullScreen = false,
}: CodeEditorPanelProps) {
  return (
    <div className={fullScreen ? "fixed inset-0 z-50 bg-white" : "rounded border"}>
      <div className="flex items-center justify-between border-b bg-gray-50 px-3 py-2">
        <select
          value={language}
          onChange={(e) => onLanguageChange(e.target.value)}
          className="rounded border px-2 py-1 text-sm"
        >
          {SUPPORTED_LANGUAGES.map((lang) => (
            <option key={lang} value={lang}>
              {lang}
            </option>
          ))}
        </select>
      </div>
      <MonacoEditor
        height={fullScreen ? "calc(100vh - 45px)" : "480px"}
        language={language}
        value={code}
        onChange={(value) => onCodeChange(value ?? "")}
        options={{
          minimap: { enabled: false },
          fontSize: 14,
          lineNumbers: "on",
          automaticLayout: true,
          tabSize: 4,
          wordWrap: "on",
        }}
      />
    </div>
  );
}
