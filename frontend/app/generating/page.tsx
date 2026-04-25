"use client";
import { useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";

const steps = [
  "Pulling your match history...",
  "Counting your deaths...",
  "Consulting the lore archives...",
  "Ghostwriting your legacy...",
  "Polishing the irony...",
];

export default function Generating() {
  const params = useSearchParams();
  const router = useRouter();
  const jobId = params.get("job_id");
  const username = params.get("username");
  const [stepIndex, setStepIndex] = useState(0);

  useEffect(() => {
    // Cycle through funny loading messages
    const msgInterval = setInterval(() => {
      setStepIndex((i) => (i + 1) % steps.length);
    }, 2000);

    // Poll job status every 3 seconds
    const pollInterval = setInterval(async () => {
      const res = await fetch(`http://localhost:5000/api/job/${jobId}`);
      const data = await res.json();

      if (data.status === "done") {
        clearInterval(pollInterval);
        clearInterval(msgInterval);
        router.push(`/page/${username}`);
      } else if (data.status === "failed") {
        clearInterval(pollInterval);
        clearInterval(msgInterval);
        router.push(`/?error=generation_failed`);
      }
    }, 3000);

    return () => {
      clearInterval(pollInterval);
      clearInterval(msgInterval);
    };
  }, [jobId, username, router]);

  return (
    <main style={{ maxWidth: 480, margin: "120px auto", padding: "0 24px", fontFamily: "Georgia, serif", textAlign: "center" }}>
      <div style={{ fontSize: 48, marginBottom: 24 }}>📜</div>
      <h1 style={{ fontSize: 24, fontWeight: 400, marginBottom: 12 }}>
        Writing the legend of <em>{username}</em>
      </h1>
      <p style={{ color: "#666", fontStyle: "italic", fontSize: 15, minHeight: 24, transition: "opacity 0.3s" }}>
        {steps[stepIndex]}
      </p>
      <div style={{ marginTop: 32, height: 2, background: "#eee", borderRadius: 2, overflow: "hidden" }}>
        <div style={{
          height: "100%",
          background: "#333",
          borderRadius: 2,
          animation: "progress 6s ease-in-out infinite",
          width: "60%",
        }} />
      </div>
      <style>{`
        @keyframes progress {
          0% { width: 5%; }
          50% { width: 80%; }
          100% { width: 95%; }
        }
      `}</style>
    </main>
  );
}