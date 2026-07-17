"use client";

import { useEffect, useRef, useState } from "react";
import { useParams } from "next/navigation";
import CodeEditorPanel from "@/components/CodeEditorPanel";
import {
  endSession,
  getWorkspace,
  heartbeatSession,
  saveDraft,
  startSession,
  submitSolution,
  type WorkspaceData,
} from "@/services/editor.service";

const HEARTBEAT_INTERVAL_MS = 60_000;
const AUTOSAVE_DEBOUNCE_MS = 2_000;

function formatRemainingTime(seconds: number | null): string {
  if (seconds === null) return "No active hackathon timer";
  const hrs = Math.floor(seconds / 3600);
  const mins = Math.floor((seconds % 3600) / 60);
  const secs = seconds % 60;
  return `${hrs}h ${mins}m ${secs}s`;
}

export default function EditorWorkspacePage() {
  const params = useParams();
  const problemId = params.problemId as string;

  const [workspace, setWorkspace] = useState<WorkspaceData | null>(null);
  const [code, setCode] = useState("");
  const [language, setLanguage] = useState("python");
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [saveStatus, setSaveStatus] = useState<"idle" | "saving" | "saved" | "error">("idle");
  const [submitStatus, setSubmitStatus] = useState<string | null>(null);
  const [fullScreen, setFullScreen] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const saveTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

  // Load workspace + open/resume an editor session on mount.
  useEffect(() => {
    getWorkspace(problemId)
      .then(async (res) => {
        const data = res.data;
        if (!data) return;
        setWorkspace(data);
        setCode(data.draft?.code ?? "");
        setLanguage(data.draft?.language ?? "python");
        setSubmitStatus(data.latest_submission_status);

        if (data.active_session) {
          setSessionId(data.active_session.id);
        } else {
          const sessionRes = await startSession(problemId, data.draft?.language ?? "python");
          if (sessionRes.data) setSessionId(sessionRes.data.id);
        }
      })
      .catch(() => setError("Unable to load this problem's workspace."));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [problemId]);

  // Heartbeat keeps the session marked active for admin monitoring.
  useEffect(() => {
    if (!sessionId) return;
    const interval = setInterval(() => {
      heartbeatSession(sessionId).catch(() => {
        /* best-effort; a missed heartbeat is not fatal */
      });
    }, HEARTBEAT_INTERVAL_MS);
    return () => clearInterval(interval);
  }, [sessionId]);

  // End the session when the student navigates away.
  useEffect(() => {
    return () => {
      if (sessionId) endSession(sessionId).catch(() => {});
    };
  }, [sessionId]);

  function handleCodeChange(value: string) {
    setCode(value);
    setSaveStatus("idle");
    if (saveTimer.current) clearTimeout(saveTimer.current);
    saveTimer.current = setTimeout(() => triggerSave(value, language), AUTOSAVE_DEBOUNCE_MS);
  }

  function triggerSave(codeValue: string, languageValue: string) {
    setSaveStatus("saving");
    saveDraft(problemId, languageValue, codeValue)
      .then(() => setSaveStatus("saved"))
      .catch(() => setSaveStatus("error"));
  }

  function handleLanguageChange(value: string) {
    setLanguage(value);
    triggerSave(code, value);
  }

  async function handleManualSave() {
    triggerSave(code, language);
  }

  async function handleSubmit() {
    try {
      const res = await submitSolution(problemId, code, language);
      setSubmitStatus(res.data?.status ?? "PENDING");
    } catch {
      setError("Submission failed. Please try again.");
    }
  }

  if (error) {
    return (
      <main className="flex min-h-screen items-center justify-center p-8">
        <p className="text-red-600">{error}</p>
      </main>
    );
  }

  if (!workspace) {
    return (
      <main className="flex min-h-screen items-center justify-center p-8">
        <p className="text-gray-500">Loading workspace...</p>
      </main>
    );
  }

  return (
    <main className="min-h-screen p-6">
      <div className="mx-auto max-w-5xl space-y-4">
        {/* Problem Header */}
        <header className="rounded border p-4">
          <div className="flex items-center justify-between">
            <h1 className="text-xl font-semibold">{workspace.problem.title}</h1>
            <p className="text-sm text-gray-500">
              {workspace.student_full_name} · Max score {workspace.problem.max_score}
            </p>
          </div>
          <p className="mt-2 text-sm text-gray-700">{workspace.problem.description}</p>
          <p className="mt-2 text-sm font-medium">
            Time remaining: {formatRemainingTime(workspace.remaining_seconds)}
          </p>
        </header>

        {/* Code Editor Panel */}
        <CodeEditorPanel
          language={language}
          code={code}
          onLanguageChange={handleLanguageChange}
          onCodeChange={handleCodeChange}
          fullScreen={fullScreen}
        />

        {/* Action Toolbar */}
        <div className="flex items-center gap-3">
          <button
            onClick={handleManualSave}
            className="rounded border px-4 py-2 text-sm hover:bg-gray-50"
          >
            Save Draft
          </button>
          <button
            onClick={handleSubmit}
            className="rounded bg-black px-4 py-2 text-sm text-white"
          >
            Submit Solution
          </button>
          <button
            onClick={() => setFullScreen((prev) => !prev)}
            className="rounded border px-4 py-2 text-sm hover:bg-gray-50"
          >
            {fullScreen ? "Exit Full Screen" : "Full Screen"}
          </button>

          <span className="ml-auto text-sm text-gray-500">
            {saveStatus === "saving" && "Saving..."}
            {saveStatus === "saved" && "Draft saved"}
            {saveStatus === "error" && "Failed to save draft"}
          </span>
        </div>

        {/* Submission Status Panel */}
        <section className="rounded border p-4">
          <h2 className="font-medium">Submission Status</h2>
          <p className="mt-1 text-sm text-gray-700">
            {submitStatus ? submitStatus : "No submission yet for this problem."}
          </p>
        </section>
      </div>
    </main>
  );
}
