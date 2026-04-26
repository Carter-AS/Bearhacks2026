"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

export default function BrowsePage() {
  const router = useRouter();
  const [results, setResults] = useState<any[]>([]);
  const [sort, setSort] = useState("recent");
  const [total, setTotal] = useState(0);

  useEffect(() => {
    fetch(`http://localhost:5000/api/pages?sort=${sort}`)
      .then(r => r.json())
      .then(data => { setResults(data.results || []); setTotal(data.total || 0); });
  }, [sort]);

  return (
    <main style={{ minHeight: "100vh", background: "#f8f9fa", fontFamily: "Georgia, serif" }}>
      <div style={{ background: "#fff", borderBottom: "1px solid #a2a9b1", padding: "8px 24px", display: "flex", alignItems: "center", gap: 16 }}>
        <span onClick={() => router.push("/")} style={{ fontSize: 18, fontWeight: 700, fontFamily: "sans-serif", color: "#202122", cursor: "pointer" }}>Gamerpedia</span>
      </div>
      <div style={{ maxWidth: 780, margin: "32px auto", padding: "0 24px" }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline", marginBottom: 20 }}>
          <div>
            <h1 style={{ fontSize: 26, fontWeight: 400, marginBottom: 2, color: "#202122" }}>All articles</h1>
            <p style={{ fontSize: 13, color: "#54595d", fontFamily: "sans-serif" }}>{total} article{total !== 1 ? "s" : ""} documented</p>
          </div>
          <div style={{ display: "flex", gap: 6, fontFamily: "sans-serif", fontSize: 12 }}>
            {["recent", "views"].map(s => (
              <button
                key={s}
                onClick={() => setSort(s)}
                style={{ padding: "4px 10px", cursor: "pointer", background: sort === s ? "#eaecf0" : "#fff", border: "1px solid #a2a9b1", borderRadius: 2, fontWeight: sort === s ? 600 : 400 , color : "#202122"}}
              >
                {s === "recent" ? "Most recent" : "Most viewed"}
              </button>
            ))}
          </div>
        </div>

        {results.length === 0 && (
          <div style={{ background: "#fff", border: "1px solid #a2a9b1", padding: 24, borderRadius: 2, fontFamily: "sans-serif", fontSize: 14, color: "#54595d" }}>
            No articles yet. <span style={{ color: "#3366cc", cursor: "pointer" }} onClick={() => router.push("/")}>Generate the first one →</span>
          </div>
        )}

        {results.map((r: any) => (
          <div
            key={r.username}
            onClick={() => router.push(`/page/${encodeURIComponent(r.username)}`)}
            style={{ background: "#fff", border: "1px solid #a2a9b1", padding: "14px 18px", marginBottom: 8, cursor: "pointer", borderRadius: 2, display: "flex", justifyContent: "space-between", alignItems: "center" }}
          >
            <div>
              <p style={{ color: "#3366cc", fontSize: 15, marginBottom: 3, fontFamily: "sans-serif" }}>{r.username}</p>
              <p style={{ fontSize: 12, color: "#54595d", fontFamily: "sans-serif" }}>
                Created {new Date(r.created_at).toLocaleDateString()}
              </p>
            </div>
            <p style={{ fontSize: 12, color: "#72777d", fontFamily: "sans-serif" }}>{r.view_count} views</p>
          </div>
        ))}
      </div>
    </main>
  );
}