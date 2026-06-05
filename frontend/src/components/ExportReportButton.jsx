import React, { useState, useCallback } from "react";

// Empty default => dev calls "/api/reports/..." through the Vite proxy; prod uses
// VITE_API_URL (backend origin), giving "${VITE_API_URL}/api/reports/...".
const API = import.meta.env.VITE_API_URL || "";

const POLL_INTERVAL_MS = 1500;
const MAX_POLLS = 40; // 60s timeout

export default function ExportReportButton({ cityId, cityName, subscriptionTier = "developer" }) {
  const [state, setState] = useState("idle"); // idle | queued | running | ready | failed | blocked
  const [jobId, setJobId] = useState(null);
  const [downloadUrl, setDownloadUrl] = useState(null);
  const [error, setError] = useState(null);
  const [pollCount, setPollCount] = useState(0);

  const isPro = ["pro", "enterprise"].includes(subscriptionTier?.toLowerCase());

  const startReport = useCallback(async () => {
    if (!isPro) {
      setState("blocked");
      return;
    }
    setState("queued");
    setError(null);
    setDownloadUrl(null);
    setJobId(null);
    setPollCount(0);

    try {
      const resp = await fetch(`${API}/api/reports/${cityId}`, { method: "POST" });
      if (resp.status === 403) {
        setState("blocked");
        return;
      }
      if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
      const data = await resp.json();
      setJobId(data.job_id);
      setState("running");
      pollStatus(data.job_id, 0);
    } catch (e) {
      setState("failed");
      setError(e.message);
    }
  }, [cityId, isPro]);

  const pollStatus = useCallback(async (jid, count) => {
    if (count > MAX_POLLS) {
      setState("failed");
      setError("Report generation timed out");
      return;
    }
    await new Promise((r) => setTimeout(r, POLL_INTERVAL_MS));
    try {
      const resp = await fetch(`${API}/api/reports/jobs/${jid}`);
      if (!resp.ok) {
        setState("failed");
        setError(`Poll error HTTP ${resp.status}`);
        return;
      }
      const job = await resp.json();
      setPollCount(count + 1);

      if (job.status === "ready") {
        setDownloadUrl(`${API}${job.download_url}`);
        setState("ready");
      } else if (job.status === "failed") {
        setState("failed");
        setError(job.error || "Generation failed");
      } else {
        setState(job.status);
        pollStatus(jid, count + 1);
      }
    } catch (e) {
      setState("failed");
      setError(e.message);
    }
  }, []);

  const triggerDownload = useCallback(() => {
    if (!downloadUrl) return;
    const a = document.createElement("a");
    a.href = downloadUrl;
    a.download = `LandAI_${cityId}_report.pdf`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  }, [downloadUrl, cityId]);

  const reset = () => {
    setState("idle");
    setJobId(null);
    setDownloadUrl(null);
    setError(null);
  };

  // ── Render helpers ──────────────────────────────────────────────────────────
  if (state === "blocked") {
    return (
      <div className="export-btn-blocked">
        <div className="export-btn-blocked-icon">🔒</div>
        <div className="export-btn-blocked-text">
          <strong>Pro Feature</strong>
          <p>PDF export requires a Pro or Enterprise subscription.</p>
        </div>
        <a href="/billing/upgrade" className="export-btn-upgrade">
          Upgrade to Pro →
        </a>
      </div>
    );
  }

  if (state === "ready") {
    return (
      <div className="export-btn-ready">
        <div className="export-btn-ready-inner">
          <span className="export-btn-ready-icon">✅</span>
          <div>
            <strong>Report Ready</strong>
            <p>{cityName} land intelligence report (PDF)</p>
          </div>
        </div>
        <div className="export-btn-actions">
          <button className="export-btn export-btn--download" onClick={triggerDownload}>
            ⬇ Download PDF
          </button>
          <button className="export-btn export-btn--new" onClick={reset}>
            Generate New
          </button>
        </div>
      </div>
    );
  }

  if (state === "failed") {
    return (
      <div className="export-btn-failed">
        <span>⚠ Report generation failed</span>
        {error && <span className="export-btn-error-msg"> — {error}</span>}
        <button className="export-btn export-btn--retry" onClick={reset}>
          Retry
        </button>
      </div>
    );
  }

  if (state === "queued" || state === "running") {
    const dots = ".".repeat((Math.floor(Date.now() / 500) % 3) + 1);
    return (
      <div className="export-btn-progress">
        <div className="export-btn-spinner" aria-hidden="true" />
        <div className="export-btn-progress-text">
          <strong>Generating report{dots}</strong>
          <p>Building provenance-stamped PDF for {cityName}</p>
        </div>
      </div>
    );
  }

  // Idle state
  return (
    <button
      id={`export-report-${cityId}`}
      className={`export-btn export-btn--primary ${!isPro ? "export-btn--locked" : ""}`}
      onClick={startReport}
      aria-label={`Export PDF report for ${cityName}`}
    >
      <span className="export-btn-icon">
        {isPro ? "📄" : "🔒"}
      </span>
      <span className="export-btn-label">
        {isPro ? "Export PDF Report" : "Export PDF (Pro)"}
      </span>
    </button>
  );
}
