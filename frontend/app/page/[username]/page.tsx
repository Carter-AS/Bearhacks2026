"use client";
import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";

export default function WikiPage() {
  const params = useParams();
  const username = decodeURIComponent(params.username as string);
  const router = useRouter();
  const [pageData, setPageData] = useState<any>(null);
  const [notFound, setNotFound] = useState(false);
  const [narrating, setNarrating] = useState(false);
  const [audioUrl, setAudioUrl] = useState<string | null>(null);

  useEffect(() => {
    console.log("Fetching username:", username);
    fetch(`http://localhost:5000/api/page/${username}`)
      .then(r => {
        console.log("Response status:", r.status);
        return r.json();
      })
      .then(data => {
        console.log("Response data:", data);
        if (data.page) setPageData(data.page);
        else setNotFound(true);
      })
      .catch((e) => {
        console.log("Fetch error:", e);
        setNotFound(true);
      });
  }, [username]);

  if (notFound) return (
    <main style={{ maxWidth: 680, margin: "80px auto", padding: "0 24px", fontFamily: "Georgia, serif" }}>
      <h1 style={{ fontWeight: 400, fontSize: 28 }}>Article not found</h1>
      <p style={{ color: "#54595d", margin: "8px 0 20px" }}>No Gamerpedia article exists for <em>{username}</em>.</p>
      <button onClick={() => router.push("/")} style={{ cursor: "pointer", fontFamily: "sans-serif", fontSize: 13 }}>← Generate one</button>
    </main>
  );

  if (!pageData) return (
    <main style={{ maxWidth: 680, margin: "80px auto", padding: "0 24px", fontFamily: "Georgia, serif", color: "#54595d" }}>
      Loading article...
    </main>
  );

  const displayName = (pageData.display_name || username)
  .split(" ")
  .map((word: string) => word.charAt(0).toUpperCase() + word.slice(1))
  .join(" ");

  const riot = pageData.riot_data || {};
const games = riot.games || {};
const lol = games.league_of_legends || {};
const tft = games.tft || {};
const rank = lol.rank || {};
const recent = lol.recent_stats || {};
const steam = pageData.steam_data || {};
const sections = pageData.sections || [];

const profileImageUrl = steam?.avatar || riot?.profile_image_url || null;


  async function handleNarrate() {
    setNarrating(true);
    
    // Build the text to narrate from the page
    const textToRead = sections
      .map((s: any) => `${s.title}. ${s.content}`)
      .join(" ");

    const res = await fetch("http://localhost:5000/api/narrate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text: textToRead }),
    });

    const data = await res.json();
    setNarrating(false);

    if (data.audio) {
      // Convert base64 to blob and play
      const audioBytes = atob(data.audio);
      const byteArray = new Uint8Array(audioBytes.length);
      for (let i = 0; i < audioBytes.length; i++) {
        byteArray[i] = audioBytes.charCodeAt(i);
      }
      const blob = new Blob([byteArray], { type: "audio/mpeg" });
      const url = URL.createObjectURL(blob);
      setAudioUrl(url);
    }
  }


  return (
    <main style={{ minHeight: "100vh", background: "#f8f9fa", fontFamily: "Georgia, 'Linux Libertine', serif" }}>
      {/* Top bar */}
      <div style={{ background: "#fff", borderBottom: "1px solid #a2a9b1", padding: "8px 24px", display: "flex", alignItems: "center", gap: 16 }}>
        <span onClick={() => router.push("/")} style={{ fontSize: 18, fontWeight: 700, fontFamily: "sans-serif", color: "#202122", cursor: "pointer" }}>Gamerpedia</span>
        <span style={{ fontSize: 12, color: "#54595d", fontFamily: "sans-serif" }}>The free ironic encyclopedia</span>
      </div>

      <div style={{ maxWidth: 960, margin: "0 auto", padding: "24px 24px" }}>
        {/* Breadcrumb */}
        <p style={{ fontSize: 12, color: "#54595d", fontFamily: "sans-serif", marginBottom: 12 }}>
          <span onClick={() => router.push("/")} style={{ color: "#3366cc", cursor: "pointer" }}>Gamerpedia</span>
          {" › "}
          <span onClick={() => router.push("/")} style={{ color: "#3366cc", cursor: "pointer" }}>Gamers</span>
          {" › "}
          {displayName}
        </p>

        {/* Claim banner */}
        <div style={{ background: "#eaf3fb", border: "1px solid #a2a9b1", padding: "8px 14px", marginBottom: 16, display: "flex", justifyContent: "space-between", alignItems: "center", fontFamily: "sans-serif", fontSize: 12, borderRadius: 2, color: "#202122" }}>
          <span>Is this you? <b>Claim this article</b> to add your personal quote and early life blurb.</span>
          <button style={{ fontSize: 11, padding: "3px 8px", cursor: "pointer", background: "#fff", border: "1px solid #a2a9b1", borderRadius: 2 }}>Claim →</button>
        </div>


        {/* Narrate button */}
        <div style={{ marginBottom: 16, display: "flex", alignItems: "center", gap: 12 }}>
          <button
            onClick={handleNarrate}
            disabled={narrating}
            style={{
              padding: "6px 14px",
              fontSize: 12,
              fontFamily: "sans-serif",
              cursor: narrating ? "not-allowed" : "pointer",
              opacity: narrating ? 0.6 : 1,
              background: "#fff",
              border: "1px solid #a2a9b1",
              borderRadius: 2,
              display: "flex",
              alignItems: "center",
              gap: 6,
              color: "#202122",
            }}
          >
            🔊 {narrating ? "Generating narration..." : "Listen to this article"}
          </button>

          {audioUrl && (
            <audio controls autoPlay src={audioUrl} style={{ height: 32 }} />
          )}
        </div>

        {/* Nav tabs */}
        <div style={{ display: "flex", gap: 0, borderBottom: "1px solid #a2a9b1", marginBottom: 16, fontFamily: "sans-serif", fontSize: 13 }}>
          {["Article", "Talk", "History"].map((tab, i) => (
            <div key={tab} style={{
              padding: "6px 14px",
              cursor: i === 0 ? "default" : "pointer",
              borderBottom: i === 0 ? "2px solid #202122" : "none",
              color: i === 0 ? "#202122" : "#3366cc",
              fontWeight: i === 0 ? 600 : 400,
              marginBottom: -1,
            }}>{tab}</div>
          ))}
        </div>

        <div style={{ display: "grid", gridTemplateColumns: "1fr 240px", gap: 24, alignItems: "start" }}>
          {/* Main content */}
          <div>
            {/* Title */}
            <h1 style={{ fontSize: 30, fontWeight: 400, borderBottom: "1px solid #a2a9b1", paddingBottom: 4, marginBottom: 12, color: "#202122" }}>
            {displayName}
            </h1>

           {/* Lead paragraph */}
            <p style={{ color: "#202122",fontSize: 14, lineHeight: 1.8, marginBottom: 12 }}>
              <b>{pageData.display_name || username}</b> is a gamer of {rank.tier ? "notable" : "questionable"} repute
              {rank.tier ? `, currently ranked ${rank.tier} ${rank.rank} in competitive play` : ""},
              {steam && steam.total_games ? ` the owner of ${steam.total_games} Steam games (${steam.never_played_percent ?? "?"}% of which remain unplayed),` : ""}
              {" "}and a figure whose digital legacy is, at best, a work in progress.
              Scholars have yet to reach consensus on their overall contribution to the gaming community,
              though sources close to the situation describe their playstyle as <em>"{
                (recent.kda ?? 0) >= 3 ? "calculated" :
                (recent.kda ?? 0) >= 2 ? "ambitious" :
                "characterful"
              }"</em>.
              <sup style={{ color: "#202122", fontSize: 11 }}>[1]</sup>
            </p>
            {/* Table of contents */}
            <div style={{ border: "1px solid #a2a9b1", background: "#f8f9fa", display: "inline-block", padding: "10px 20px", marginBottom: 20, minWidth: 200, borderRadius: 2 }}>
              <p style={{ fontFamily: "sans-serif", fontSize: 12, fontWeight: 700, marginBottom: 6, color: "#202122" }}>Contents</p>
              <ol style={{ paddingLeft: 18, margin: 0 }}>
                {sections.map((s: any, i: number) => (
                  <li key={i} style={{ margin: "3px 0" }}>
                    <a href={`#section-${i}`} style={{ color: "#3366cc", fontSize: 12, fontFamily: "sans-serif", textDecoration: "none" }}>
                      {s.title}
                    </a>
                  </li>
                ))}
                <li style={{ margin: "3px 0" }}>
                  <a href="#stats" style={{ color: "#3366cc", fontSize: 12, fontFamily: "sans-serif", textDecoration: "none" }}>
                    Career statistics
                  </a>
                </li>
              </ol>
            </div>

            {/* Generated sections */}
{sections.map((section: any, i: number) => (
  <div key={i} id={`section-${i}`} style={{ marginBottom: 20 }}>
    <h2 style={{ fontSize: 20, fontWeight: 400, borderBottom: "1px solid #eaecf0", paddingBottom: 4, marginBottom: 8, color: "#202122" }}>
      {section.title}
    </h2>

    {/* Inject champion image into Career section */}
    {section.title === "Career" && riot?.champ_image_url && (
      <div style={{ float: "right", margin: "0 0 12px 16px", border: "1px solid #a2a9b1", background: "#f8f9fa", padding: 4, maxWidth: 120, borderRadius: 2 }}>
        <img
          src={riot.champ_image_url}
          alt="Most played champion"
          style={{ width: "100%", height: 140, objectFit: "cover", objectPosition: "top", display: "block" }}
        />
        <p style={{ fontSize: 10, fontFamily: "sans-serif", color: "#54595d", textAlign: "center", margin: "4px 2px", fontStyle: "italic" }}>
          {lol?.top_champions?.[0] || "Unknown"}<br />Most played champion
        </p>
      </div>
    )}

    {/* Inject Steam game image into Legacy section */}
    {section.title === "Legacy and statistics" && steam?.most_played?.name && (() => {
      const appid = steam?.most_played_appid;
      const steamImgUrl = appid
        ? `https://cdn.cloudflare.steamstatic.com/steam/apps/${appid}/header.jpg`
        : null;
      return steamImgUrl ? (
        <div style={{ float: "right", margin: "0 0 12px 16px", border: "1px solid #a2a9b1", background: "#f8f9fa", padding: 4, maxWidth: 160, borderRadius: 2 }}>
          <img
            src={steamImgUrl}
            alt="Most played Steam game"
            style={{ width: "100%", height: 75, objectFit: "cover", display: "block" }}
          />
          <p style={{ fontSize: 10, fontFamily: "sans-serif", color: "#54595d", textAlign: "center", margin: "4px 2px", fontStyle: "italic" }}>
            {steam.most_played.name}<br />{steam.most_played.hours}h played
          </p>
        </div>
      ) : null;
    })()}

    <p style={{ fontSize: 14, lineHeight: 1.8, color: "#202122" }}>
      {section.content}
      <sup style={{ color: "#3366cc", fontSize: 11 }}>[{i + 2}]</sup>
    </p>

    {/* Clear float after each section */}
    <div style={{ clear: "both" }} />
  </div>
))}

            {/* Stats table
            <div id="stats" style={{ marginBottom: 20 }}>
              <h2 style={{ fontSize: 20, fontWeight: 400, borderBottom: "1px solid #eaecf0", paddingBottom: 4, marginBottom: 8, color: "#202122" }}>
                Career statistics
              </h2>
              <table style={{ borderCollapse: "collapse", width: "100%", fontSize: 13, fontFamily: "sans-serif" }}>
                <thead>
                  <tr style={{ background: "#eaecf0" }}>
                    <th style={{ border: "1px solid #a2a9b1", padding: "6px 10px", textAlign: "left" }}>Statistic</th>
                    <th style={{ border: "1px solid #a2a9b1", padding: "6px 10px", textAlign: "left" }}>Value</th>
                    <th style={{ border: "1px solid #a2a9b1", padding: "6px 10px", textAlign: "left" }}>Assessment</th>
                  </tr>
                </thead>
                <tbody>
                  {[
                    { stat: "Rank", value: `${rank.tier || "?"} ${rank.rank || ""}`, note: rank.tier === "DIAMOND" ? "Genuinely impressive" : rank.tier === "GOLD" ? "Peaked in 2021, allegedly" : "A work in progress" },
                    { stat: "Win rate", value: `${rank.win_rate ?? "?"}%`, note: (rank.win_rate ?? 0) >= 55 ? "Statistically dominant" : (rank.win_rate ?? 0) >= 50 ? "Barely above water" : "Losing more than winning" },
                    { stat: "KDA (recent)", value: recent.kda ?? "?", note: (recent.kda ?? 0) >= 3 ? "Respectable" : "Room for growth" },
                    { stat: "Vision score avg", value: recent.avg_vision_score ?? "?", note: (recent.avg_vision_score ?? 0) <= 15 ? "Wards? What wards?" : "Aware of map existence" },
                    { stat: "Summoner level", value: riot.summoner_level ?? "?", note: "Time well spent, presumably" },
                    { stat: "Total games", value: rank.total_games ?? "?", note: "Each one a learning experience" },
                  ].map((row, i) => (
                    <tr key={i} style={{ background: i % 2 === 0 ? "#fff" : "#f8f9fa" }}>
                      <td style={{ border: "1px solid #a2a9b1", padding: "6px 10px", fontWeight: 600 }}>{row.stat}</td>
                      <td style={{ border: "1px solid #a2a9b1", padding: "6px 10px" }}>{row.value}</td>
                      <td style={{ border: "1px solid #a2a9b1", padding: "6px 10px", fontStyle: "italic", color: "#54595d" }}>{row.note}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div> */}

            {/* Categories */}
            <div style={{ borderTop: "1px solid #a2a9b1", paddingTop: 10, marginTop: 24, fontFamily: "sans-serif", fontSize: 12 }}>
              <b>Categories: </b>
              {[
                rank.tier ? `${rank.tier} players` : "Unranked players",
                `${(riot.top_champions || [])[0] || "Unknown"} mains`,
                "North American server",
                "People with a complicated relationship with vision score",
              ].map((cat, i) => (
                <span key={i}>
                  <span style={{ color: "#3366cc", cursor: "pointer" }}>{cat}</span>
                  {i < 3 ? " · " : ""}
                </span>
              ))}
            </div>

            {/* Footer */}
            <div style={{ marginTop: 16, fontSize: 11, color: "#72777d", fontFamily: "sans-serif", display: "flex", justifyContent: "space-between" }}>
              <span>Last edited: just now by an impartial observer</span>
              <span>Views: {pageData.view_count}</span>
            </div>
          </div>

            {/* Infobox */}
<div style={{ border: "1px solid #a2a9b1", fontSize: 12, background: "#f8f9fa", borderRadius: 2, position: "sticky", top: 16 }}>
  <div style={{ background: "#a2a9b1", color: "#000", textAlign: "center", fontWeight: 700, fontSize: 13, padding: "6px 8px", fontFamily: "sans-serif" }}>
    {displayName}
  </div>

  {/* Profile image */}
  {profileImageUrl ? (
  <div style={{ textAlign: "center", padding: 12, borderBottom: "1px solid #eaecf0" }}>
    <img
      src={profileImageUrl}
      alt="Profile"
      style={{
        width: 80,
        height: 80,
        borderRadius: "50%",
        objectFit: "cover",
        border: "2px solid #a2a9b1",
        display: "block",
        margin: "0 auto",
      }}
    />
    <p style={{ fontSize: 11, color: "#54595d", fontStyle: "italic", marginTop: 6, fontFamily: "sans-serif" }}>
      {steam?.avatar ? "Steam profile photo." : "League of Legends profile icon."}
    </p>
  </div>
) : (
  <div style={{ textAlign: "center", padding: 12, borderBottom: "1px solid #eaecf0" }}>
    <div style={{ width: 72, height: 72, borderRadius: "50%", background: "linear-gradient(135deg, #36393f, #5865f2)", display: "inline-flex", alignItems: "center", justifyContent: "center", fontSize: 28, margin: "0 auto" }}>
      🎮
    </div>
    <p style={{ fontSize: 11, color: "#54595d", fontStyle: "italic", marginTop: 6, fontFamily: "sans-serif" }}>
      Profile image unavailable.<br />Artist's interpretation used.
    </p>
  </div>
)}

  <table style={{ width: "100%", borderCollapse: "collapse" }}>
  <tbody>
    {[
      // Always show
      ["Status", "Active (regrettably)"],

      // LoL stats — only if rank data exists
      ...(rank.tier ? [
        ["LoL Rank", `${rank.tier} ${rank.rank}`.trim()],
        ["LP", rank.lp ?? "—"],
        ["Win rate", rank.win_rate ? `${rank.win_rate}%` : "—"],
        ["KDA", recent.kda ?? "—"],
        ["Vision score", recent.avg_vision_score ?? "—"],
        ["Level", lol?.summoner_level ?? "—"],
        ["Main", (lol?.top_champions || [])[0] || "—"],
      ] : []),

      // TFT stats — only if TFT rank exists
      ...(tft?.rank?.tier ? [
        ["TFT Rank", `${tft.rank.tier} ${tft.rank.rank}`.trim()],
        ["TFT Win rate", tft.rank.win_rate ? `${tft.rank.win_rate}%` : "—"],
      ] : []),

      // Steam stats — only if steam data exists
      ...(steam?.total_games ? [
        ["Steam games", steam.total_games],
        ["Never played", `${steam.never_played_count} (${steam.never_played_percent}%)`],
        ["Total hours", steam.total_hours ? `${steam.total_hours}h` : "—"],
        ["Most played", steam.most_played?.name || "—"],
      ] : []),

    ].map(([label, value], i) => (
      <tr key={i} style={{ borderTop: "1px solid #eaecf0" }}>
        <td style={{ padding: "4px 8px", fontWeight: 700, color: "#54595d", fontFamily: "sans-serif", width: "45%", verticalAlign: "top" }}>{label}</td>
        <td style={{ padding: "4px 8px", fontFamily: "sans-serif", color: "#202122" }}>{String(value)}</td>
      </tr>
    ))}
      </tbody>

  </table>



          </div>
        </div>
      </div>
    </main>
  );
}