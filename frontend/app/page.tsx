"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";

export default function Home() {
  const [riotUsername, setRiotUsername] = useState("");
  const [steamUsername, setSteamUsername] = useState("");
  const [searchQuery, setSearchQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const router = useRouter();

  async function handleGenerate() {
    if (!riotUsername && !steamUsername) {
      setError("Enter at least one username.");
      return;
    }
    setLoading(true);
    setError("");
    try {
      const res = await fetch("http://localhost:5000/api/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ riot_username: riotUsername, steam_username: steamUsername }),
      });
      const data = await res.json();
      if (!res.ok) { setError(data.error || "Something went wrong."); setLoading(false); return; }
      router.push(`/page/${encodeURIComponent(data.username)}`);
    } catch {
      setError("Could not connect to server.");
      setLoading(false);
    }
  }

  function handleSearch(e: React.FormEvent) {
    e.preventDefault();
    if (searchQuery.trim()) router.push(`/search?q=${encodeURIComponent(searchQuery.trim())}`);
  }

  return (
    <main style={{ minHeight: "100vh", background: "#f8f9fa", fontFamily: "Georgia, 'Linux Libertine', serif" }}>
      {/* Header bar */}
      <div style={{ background: "#fff", borderBottom: "1px solid #a2a9b1", padding: "8px 24px", display: "flex", alignItems: "center", gap: 16 }}>
        <span style={{ fontSize: 20, fontWeight: 700, fontFamily: "sans-serif", color: "#202122" }}>Gamerpedia</span>
        <span style={{ fontSize: 12, color: "#54595d", fontFamily: "sans-serif" }}>The free ironic encyclopedia</span>
        <form onSubmit={handleSearch} style={{ marginLeft: "auto", display: "flex", gap: 6 }}>
          <input
            value={searchQuery}
            onChange={e => setSearchQuery(e.target.value)}
            placeholder="Search Gamerpedia..."
            style={{ padding: "5px 10px", fontSize: 13, border: "1px solid #a2a9b1", borderRadius: 2, width: 240, fontFamily: "sans-serif" }}
          />
          <button type="submit" style={{ padding: "5px 12px", fontSize: 13, cursor: "pointer", fontFamily: "sans-serif", background: "#f8f9fa", border: "1px solid #a2a9b1", borderRadius: 2 }}>Search</button>
        </form>
      </div>

      <div style={{ maxWidth: 780, margin: "60px auto", padding: "0 24px" }}>
        {/* Hero */}
        <div style={{ textAlign: "center", marginBottom: 48 }}>
          <h1 style={{ fontSize: 52, fontWeight: 400, marginBottom: 8, color: "#202122", letterSpacing: "-0.5px" }}>Gamerpedia</h1>
          <p style={{ fontSize: 16, color: "#54595d", fontStyle: "italic", marginBottom: 4 }}>The free ironic encyclopedia that anyone can be embarrassed by.</p>
          <p style={{ fontSize: 13, color: "#72777d", fontFamily: "sans-serif" }}>1 article · Written in irony · Est. 2026</p>
        </div>

        {/* Generate card */}
        <div style={{ background: "#fff", border: "1px solid #a2a9b1", borderRadius: 2, padding: 32, marginBottom: 24 }}>
          <h2 style={{ fontSize: 22, fontWeight: 400, marginBottom: 6, color: "#202122", borderBottom: "1px solid #eaecf0", paddingBottom: 8 }}>
            Generate a new article
          </h2>
          <p style={{ fontSize: 13, color: "#54595d", fontFamily: "sans-serif", marginBottom: 20 }}>
            Enter a Riot ID or Steam username to generate an ironic Wikipedia-style article about a gamer.
          </p>

          <div style={{ display: "flex", flexDirection: "column", gap: 10, marginBottom: 16 }}>
            <div>
              <label style={{ fontSize: 12, fontFamily: "sans-serif", color: "#54595d", display: "block", marginBottom: 4 }}>Riot ID</label>
              <input
                placeholder="e.g. Faker#KR1"
                value={riotUsername}
                onChange={e => setRiotUsername(e.target.value)}
                onKeyDown={e => e.key === "Enter" && handleGenerate()}
                style={{ width: "100%", padding: "8px 12px", fontSize: 14, border: "1px solid #a2a9b1", borderRadius: 2, fontFamily: "sans-serif", boxSizing: "border-box" }}
              />
            </div>
            <div>
              <label style={{ fontSize: 12, fontFamily: "sans-serif", color: "#54595d", display: "block", marginBottom: 4 }}>Steam username <span style={{ color: "#72777d" }}>(optional)</span></label>
              <input
                placeholder="e.g. gaben"
                value={steamUsername}
                onChange={e => setSteamUsername(e.target.value)}
                onKeyDown={e => e.key === "Enter" && handleGenerate()}
                style={{ width: "100%", padding: "8px 12px", fontSize: 14, border: "1px solid #a2a9b1", borderRadius: 2, fontFamily: "sans-serif", boxSizing: "border-box" }}
              />
            </div>
          </div>

          {error && <p style={{ color: "#cc3333", fontSize: 13, fontFamily: "sans-serif", marginBottom: 12 }}>{error}</p>}

          <button
            onClick={handleGenerate}
            disabled={loading}
            style={{ padding: "8px 20px", fontSize: 14, cursor: loading ? "not-allowed" : "pointer", opacity: loading ? 0.6 : 1, fontFamily: "sans-serif", background: "#f8f9fa", border: "1px solid #a2a9b1", borderRadius: 2 }}
          >
            {loading ? "Generating..." : "Generate article →"}
          </button>
        </div>

        {/* Browse link */}
        <div style={{ textAlign: "center" }}>
          <span
            onClick={() => router.push("/browse")}
            style={{ fontSize: 13, color: "#3366cc", cursor: "pointer", fontFamily: "sans-serif", textDecoration: "underline" }}
          >
            Browse all articles
          </span>
        </div>
      </div>
    </main>
  );
}