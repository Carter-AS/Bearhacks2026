"use client";
import { useEffect, useState } from "react";
import { useSearchParams, useRouter } from "next/navigation";

export default function SearchPage() {
  const params = useSearchParams();
  const router = useRouter();
  const query = params.get("q") || "";
  const [results, setResults] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`http://localhost:5000/api/search?q=${encodeURIComponent(query)}`)
      .then((r) => r.json())
      .then((data) => {
        setResults(data.results || []);
        setLoading(false);
      });
  }, [query]);

  return (
    <main style={{ maxWidth: 680, margin: "0 auto", padding: "40px 24px", fontFamily: "Georgia, serif" }}>
      <p style={{ fontSize: 12, color: "#666", marginBottom: 16 }}>
        ← <span style={{ cursor: "pointer", color: "#3366cc" }} onClick={() => router.push("/")}>WikiGamer</span>
      </p>
      <h1 style={{ fontSize: 28, fontWeight: 400, marginBottom: 4 }}>Search results</h1>
      <p style={{ color: "#666", fontSize: 13, marginBottom: 24 }}>Results for: <em>"{query}"</em></p>

      {loading && <p style={{ color: "#888" }}>Searching...</p>}

      {!loading && results.length === 0 && (
        <div>
          <p style={{ color: "#555", marginBottom: 16 }}>No pages found for "{query}".</p>
          <button onClick={() => router.push(`/?riot=${encodeURIComponent(query)}`)} style={{ cursor: "pointer" }}>
            Generate a page for "{query}" →
          </button>
        </div>
      )}

      {results.map((r: any) => (
        <div
          key={r.username}
          onClick={() => router.push(`/page/${r.username}`)}
          style={{ borderBottom: "1px solid #eee", padding: "12px 0", cursor: "pointer" }}
        >
          <p style={{ color: "#3366cc", fontSize: 16, marginBottom: 4 }}>{r.username}</p>
          <p style={{ color: "#666", fontSize: 13 }}>{r.summary}</p>
        </div>
      ))}
    </main>
  );
}