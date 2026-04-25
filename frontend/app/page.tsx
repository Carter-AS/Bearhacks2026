"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";

export default function Home() {
  const [riotUsername, setRiotUsername] = useState("");
  const [steamUsername, setSteamUsername] = useState("");
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

    const res = await fetch("http://localhost:5000/api/generate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        riot_username: riotUsername,
        steam_username: steamUsername,
      }),
    });

    const data = await res.json();
    setLoading(false);

    if (!res.ok) {
      setError(data.error || "Something went wrong.");
      return;
    }

    // Redirect to polling page with the job id
    router.push(`/generating?job_id=${data.job_id}&username=${riotUsername || steamUsername}`);
  }

  async function handleSearch(e: React.FormEvent) {
    e.preventDefault();
    const query = (e.target as any).search.value.trim();
    if (query) router.push(`/search?q=${encodeURIComponent(query)}`);
  }

  return (
    <main style={{ maxWidth: 680, margin: "0 auto", padding: "60px 24px", fontFamily: "Georgia, serif" }}>
      <h1 style={{ fontSize: 42, fontWeight: 400, marginBottom: 4 }}>WikiGamer</h1>
      <p style={{ color: "#555", marginBottom: 40, fontStyle: "italic" }}>
        The free ironic encyclopedia of gamers who should know better.
      </p>

      {/* Search existing pages */}
      <form onSubmit={handleSearch} style={{ display: "flex", gap: 8, marginBottom: 48 }}>
        <input
          name="search"
          placeholder="Search existing pages..."
          style={{ flex: 1, padding: "10px 14px", fontSize: 14, border: "1px solid #ccc", borderRadius: 2 }}
        />
        <button type="submit" style={{ padding: "10px 18px", fontSize: 14, cursor: "pointer" }}>
          Search
        </button>
      </form>

      {/* Generate new page */}
      <div style={{ borderTop: "1px solid #ddd", paddingTop: 32 }}>
        <h2 style={{ fontSize: 22, fontWeight: 400, marginBottom: 16 }}>Generate a new page</h2>

        <div style={{ display: "flex", flexDirection: "column", gap: 12, marginBottom: 20 }}>
          <input
            placeholder="Riot ID (e.g. Faker#KR1)"
            value={riotUsername}
            onChange={(e) => setRiotUsername(e.target.value)}
            style={{ padding: "10px 14px", fontSize: 14, border: "1px solid #ccc", borderRadius: 2 }}
          />
          <input
            placeholder="Steam username (optional)"
            value={steamUsername}
            onChange={(e) => setSteamUsername(e.target.value)}
            style={{ padding: "10px 14px", fontSize: 14, border: "1px solid #ccc", borderRadius: 2 }}
          />
        </div>

        {error && <p style={{ color: "#cc3333", fontSize: 13, marginBottom: 12 }}>{error}</p>}

        <button
          onClick={handleGenerate}
          disabled={loading}
          style={{ padding: "10px 24px", fontSize: 14, cursor: loading ? "not-allowed" : "pointer", opacity: loading ? 0.6 : 1 }}
        >
          {loading ? "Queuing..." : "Generate page"}
        </button>
      </div>
    </main>
  );
}