"use client";
import { useEffect, useState, Suspense } from "react";
import { useSearchParams, useRouter } from "next/navigation";

function SearchResults() {
  const params = useSearchParams();
  const router = useRouter();
  const query = params.get("q") || "";
  const [results, setResults] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`http://localhost:5000/api/search?q=${encodeURIComponent(query)}`)
      .then(r => r.json())
      .then(data => { setResults(data.results || []); setLoading(false); });
  }, [query]);

  return (
    <main style={{ minHeight: "100vh", background: "#f8f9fa", fontFamily: "Georgia, serif" }}>
      <div style={{ background: "#fff", borderBottom: "1px solid #a2a9b1", padding: "8px 24px", display: "flex", alignItems: "center", gap: 16 }}>
        <span onClick={() => router.push("/")} style={{ fontSize: 18, fontWeight: 700, fontFamily: "sans-serif", color: "#202122", cursor: "pointer" }}>Gamerpedia</span>
      </div>
      <div style={{ maxWidth: 780, margin: "32px auto", padding: "0 24px" }}>
        <h1 style={{ fontSize: 26, fontWeight: 400, marginBottom: 4 }}>Search results</h1>
        <p style={{ fontSize: 13, color: "#54595d", fontFamily: "sans-serif", marginBottom: 24 }}>
          {loading ? "Searching..." : `${results.length} result${results.length !== 1 ? "s" : ""} for `}
          {!loading && <em>"{query}"</em>}
        </p>

        {!loading && results.length === 0 && (
          <div style={{ background: "#fff", border: "1px solid #a2a9b1", padding: 24, borderRadius: 2 }}>
            <p style={{ fontFamily: "sans-serif", fontSize: 14, marginBottom: 12 }}>No articles found for "{query}".</p>
            <button
              onClick={() => router.push(`/?riot=${encodeURIComponent(query)}`)}
              style={{ cursor: "pointer", fontFamily: "sans-serif", fontSize: 13, padding: "6px 14px", background: "#f8f9fa", border: "1px solid #a2a9b1", borderRadius: 2 }}
            >
              Generate an article for "{query}" →
            </button>
          </div>
        )}

        {results.map((r: any) => (
          <div
            key={r.username}
            onClick={() => router.push(`/page/${encodeURIComponent(r.username)}`)}
            style={{ background: "#fff", border: "1px solid #a2a9b1", padding: "14px 18px", marginBottom: 8, cursor: "pointer", borderRadius: 2 }}
          >
            <p style={{ color: "#3366cc", fontSize: 16, marginBottom: 4, fontFamily: "sans-serif" }}>{r.username}</p>
            <p style={{ fontSize: 12, color: "#54595d", fontFamily: "sans-serif" }}>
              {r.platform} · {r.view_count} view{r.view_count !== 1 ? "s" : ""} · {new Date(r.created_at).toLocaleDateString()}
            </p>
          </div>
        ))}
      </div>
    </main>
  );
}

export default function SearchPage() {
  return <Suspense><SearchResults /></Suspense>;
}