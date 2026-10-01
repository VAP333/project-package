import { createFileRoute } from "@tanstack/react-router";
import { Area, AreaChart, Bar, BarChart, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { useState, useEffect } from "react";
import {
  Volume2,
  CheckCircle2,
  AlertTriangle,
  Play,
  Check,
  Search,
  ShieldCheck,
  Filter
} from "lucide-react";
import { toast } from "sonner";
import { Page, Card } from "@/components/app-shell";
import { METRICS, HISTORY_CHAPTERS, SCIENCE_CHAPTERS } from "@/lib/mock-data";
import { cn } from "@/lib/utils";

export const Route = createFileRoute("/admin")({
  head: () => ({
    meta: [
      { title: "Metrics & Pronunciation — AksharSetu" },
      { name: "description", content: "System health and History pronunciation lexicon reviewer for AksharSetu." },
      { property: "og:title", content: "Metrics & Pronunciation — AksharSetu" },
      { property: "og:description", content: "Admin dashboard and pronunciation knowledge base." },
      { property: "og:type", content: "website" },
      { name: "twitter:card", content: "summary" },
    ],
  }),
  component: Admin,
});

const tip = { contentStyle: { borderRadius: 12, border: "1px solid var(--border)", fontSize: 12 } };

function Spark({ k, color }: { k: "cer" | "wer" | "unresolved" | "pages"; color: string }) {
  return (
    <div className="h-16" aria-hidden>
      <ResponsiveContainer>
        <AreaChart data={METRICS.trend}>
          <Tooltip {...tip} />
          <Area type="monotone" dataKey={k} stroke={color} fill={color} fillOpacity={0.12} strokeWidth={2} />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}

type PronunciationItem = {
  canonical_text: string;
  chapter_id: string;
  subject: string;
  risk_type: string;
  verification_status: string;
  preferred_pronunciation?: string;
};

function Admin() {
  const m = METRICS;
  const kpis = [
    { l: "Pages processed", v: m.pagesProcessed.toLocaleString(), sub: `${m.pagesDelta} this week`, k: "pages" as const },
    { l: "Golden Corpus coverage", v: `${m.coverage}%`, sub: "of catalogue pages", k: null },
    { l: "Correction accuracy", v: `${m.correctionAccuracy}%`, sub: "reviewer agreement", k: null },
    { l: "Unresolved-word rate", v: `${m.unresolvedRate}%`, sub: "↓ from 3.4%", k: "unresolved" as const },
  ];

  // Pronunciation Lexicon Review State (§14) - Science & History
  const [selectedSubject, setSelectedSubject] = useState<"science" | "history">("science");
  const [lexicon, setLexicon] = useState<PronunciationItem[]>([]);
  const [selectedChapter, setSelectedChapter] = useState<string>("ALL");
  const [searchQuery, setSearchQuery] = useState("");
  const [playingWord, setPlayingWord] = useState<string | null>(null);

  useEffect(() => {
    const apiPath = selectedSubject === "science" ? "/api/science/pronunciation" : "/api/history/pronunciation";
    fetch(apiPath)
      .then((res) => (res.ok ? res.json() : null))
      .then((data) => {
        if (data && data.lexicon) {
          setLexicon(data.lexicon);
        }
      })
      .catch((e) => console.debug("Pronunciation fetch notice:", e));
  }, [selectedSubject]);

  const handleApprove = async (word: string) => {
    try {
      const apiPath = selectedSubject === "science" ? "/api/science/pronunciation/approve" : "/api/history/pronunciation/approve";
      const res = await fetch(apiPath, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          canonical_text: word,
          preferred_pronunciation: word,
          approved_by: "Admin Reviewer",
        }),
      });

      if (res.ok) {
        setLexicon((prev) =>
          prev.map((item) =>
            item.canonical_text === word ? { ...item, verification_status: "GOLDEN_TRUTH" } : item
          )
        );
        toast.success(`'${word}' उच्चार मंजूर (GOLDEN_TRUTH)!`);
      } else {
        toast.error("मंजूर करण्यात अडचण आली.");
      }
    } catch {
      toast.error("नेटवर्क त्रुटी.");
    }
  };

  const handlePreview = (word: string) => {
    setPlayingWord(word);
    fetch("/api/tts/synthesize", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        text: word,
        speaker: "shreya",
        provider: "sarvam",
      }),
    })
      .then((r) => r.json())
      .then((d) => {
        if (d.audio_base64) {
          const a = new Audio("data:audio/wav;base64," + d.audio_base64);
          a.onended = () => setPlayingWord(null);
          a.play();
        } else {
          setPlayingWord(null);
        }
      })
      .catch(() => setPlayingWord(null));
  };

  const filteredLexicon = lexicon.filter((item) => {
    const matchChapter = selectedChapter === "ALL" || item.chapter_id === selectedChapter;
    const matchSearch =
      !searchQuery ||
      item.canonical_text.toLowerCase().includes(searchQuery.toLowerCase()) ||
      item.chapter_id.toLowerCase().includes(searchQuery.toLowerCase());
    return matchChapter && matchSearch;
  });

  return (
    <Page title="Admin & Metrics" deva="प्रशासक व आकडेवारी" wide>
      {/* KPI Cards */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {kpis.map((x) => (
          <Card key={x.l}>
            <p className="text-sm text-muted-foreground">{x.l}</p>
            <p className="mt-1 text-3xl font-bold">{x.v}</p>
            <p className="text-xs text-muted-foreground">{x.sub}</p>
            {x.k ? (
              <Spark k={x.k} color="var(--chart-1)" />
            ) : (
              <div className="mt-6 h-2 rounded-full bg-muted">
                <div className="h-full rounded-full bg-primary" style={{ width: x.v }} />
              </div>
            )}
          </Card>
        ))}
      </div>

      {/* ------------------------------------------------------------- */}
      {/* SECTION: CLASS 8 HISTORY PRONUNCIATION REVIEWER (§14)         */}
      {/* ------------------------------------------------------------- */}
      <Card className="mt-6 border-2 border-primary/20 p-6">
        <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between border-b pb-4">
          <div>
            <div className="flex items-center gap-2">
              <span className="inline-flex items-center gap-1.5 rounded-full bg-primary/10 px-2.5 py-0.5 text-xs font-bold text-primary">
                <ShieldCheck className="h-3.5 w-3.5" aria-hidden /> SECTION 14 COMPLIANCE
              </span>
              {/* Subject Selector Toggle */}
              <div className="inline-flex items-center rounded-lg border bg-muted/40 p-0.5">
                <button
                  type="button"
                  onClick={() => { setSelectedSubject("science"); setSelectedChapter("ALL"); }}
                  className={cn(
                    "rounded-md px-2.5 py-1 text-xs font-bold transition",
                    selectedSubject === "science"
                      ? "bg-card text-foreground shadow-xs"
                      : "text-muted-foreground hover:text-foreground"
                  )}
                >
                  🔬 Science (150+ terms)
                </button>
                <button
                  type="button"
                  onClick={() => { setSelectedSubject("history"); setSelectedChapter("ALL"); }}
                  className={cn(
                    "rounded-md px-2.5 py-1 text-xs font-bold transition",
                    selectedSubject === "history"
                      ? "bg-card text-foreground shadow-xs"
                      : "text-muted-foreground hover:text-foreground"
                  )}
                >
                  📜 History (197 terms)
                </button>
              </div>
            </div>
            <h2 className="text-xl font-bold tracking-tight text-foreground mt-2">
              {selectedSubject === "science"
                ? "Class 8 Science — Technical Glossary & Proper Nouns Lexicon"
                : "Class 8 History — Pronunciation Knowledge Review (197 Proper Nouns)"}
            </h2>
            <p className="text-xs text-muted-foreground">
              Proper noun candidates remain <code className="text-amber-600 font-bold">UNVERIFIED</code> until expert review. After approval, they become <code className="text-emerald-600 font-bold">GOLDEN_TRUTH</code>.
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-2">
            <div className="relative">
              <Search className="absolute left-2.5 top-2.5 h-3.5 w-3.5 text-muted-foreground" aria-hidden />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="शब्द शोधा (Search word)..."
                className="rounded-lg border bg-background pl-8 pr-3 py-1.5 text-xs text-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-primary w-44"
              />
            </div>

            <select
              value={selectedChapter}
              onChange={(e) => setSelectedChapter(e.target.value)}
              className="rounded-lg border bg-background px-2.5 py-1.5 text-xs font-semibold text-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-primary cursor-pointer"
            >
              <option value="ALL">सर्व पाठ (All Chapters)</option>
              {(selectedSubject === "science" ? SCIENCE_CHAPTERS : HISTORY_CHAPTERS).map((ch) => (
                <option key={ch.id} value={ch.id}>
                  {ch.id} — {ch.title}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Lexicon Items Table */}
        <div className="mt-4 max-h-96 overflow-y-auto rounded-xl border">
          <table className="w-full text-left text-xs">
            <thead className="bg-muted/50 sticky top-0 border-b">
              <tr>
                <th className="p-3 font-semibold text-muted-foreground">Canonical Spelling (मूळ शब्द)</th>
                <th className="p-3 font-semibold text-muted-foreground">Chapter</th>
                <th className="p-3 font-semibold text-muted-foreground">Type</th>
                <th className="p-3 font-semibold text-muted-foreground">Status</th>
                <th className="p-3 text-right font-semibold text-muted-foreground">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y">
              {filteredLexicon.length > 0 ? (
                filteredLexicon.map((item, idx) => {
                  const isVerified = item.verification_status === "GOLDEN_TRUTH";
                  return (
                    <tr key={idx} className="hover:bg-muted/20 transition-colors">
                      <td className="p-3 font-bold text-foreground deva text-base">
                        {item.canonical_text}
                      </td>
                      <td className="p-3 font-mono font-semibold text-muted-foreground">
                        {item.chapter_id}
                      </td>
                      <td className="p-3 text-muted-foreground capitalize">
                        {item.risk_type.replace(/_/g, " ")}
                      </td>
                      <td className="p-3">
                        {isVerified ? (
                          <span className="inline-flex items-center gap-1 rounded-md bg-emerald-500/10 px-2 py-0.5 text-[11px] font-bold text-emerald-600">
                            <CheckCircle2 className="h-3 w-3" /> GOLDEN_TRUTH
                          </span>
                        ) : (
                          <span className="inline-flex items-center gap-1 rounded-md bg-amber-500/10 px-2 py-0.5 text-[11px] font-bold text-amber-600">
                            <AlertTriangle className="h-3 w-3" /> UNVERIFIED
                          </span>
                        )}
                      </td>
                      <td className="p-3 text-right">
                        <div className="flex items-center justify-end gap-1.5">
                          <button
                            type="button"
                            onClick={() => handlePreview(item.canonical_text)}
                            disabled={playingWord === item.canonical_text}
                            className="inline-flex items-center gap-1 rounded-lg border bg-card px-2.5 py-1 text-xs font-semibold text-primary hover:bg-accent transition cursor-pointer"
                          >
                            <Volume2 className="h-3 w-3" /> [ Preview ]
                          </button>

                          {!isVerified && (
                            <button
                              type="button"
                              onClick={() => handleApprove(item.canonical_text)}
                              className="inline-flex items-center gap-1 rounded-lg bg-emerald-600 px-2.5 py-1 text-xs font-semibold text-white hover:bg-emerald-700 transition cursor-pointer"
                            >
                              <Check className="h-3 w-3" /> [ Approve ]
                            </button>
                          )}
                        </div>
                      </td>
                    </tr>
                  );
                })
              ) : (
                <tr>
                  <td colSpan={5} className="p-6 text-center text-muted-foreground">
                    कोणतेही उच्चार सापडले नाहीत (No pronunciation candidates found).
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </Card>

      {/* Accuracy Charts */}
      <div className="mt-6 grid gap-4 lg:grid-cols-3">
        <Card>
          <h2 className="font-semibold">CER trend</h2>
          <p className="text-xs text-muted-foreground">Character error rate, %</p>
          <div className="mt-3 h-40">
            <ResponsiveContainer>
              <LineChart data={m.trend}>
                <XAxis dataKey="week" fontSize={11} tickLine={false} axisLine={false} />
                <YAxis fontSize={11} width={28} tickLine={false} axisLine={false} />
                <Tooltip {...tip} />
                <Line type="monotone" dataKey="cer" stroke="var(--chart-1)" strokeWidth={2} dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </Card>
        <Card>
          <h2 className="font-semibold">WER trend</h2>
          <p className="text-xs text-muted-foreground">Word error rate, %</p>
          <div className="mt-3 h-40">
            <ResponsiveContainer>
              <LineChart data={m.trend}>
                <XAxis dataKey="week" fontSize={11} tickLine={false} axisLine={false} />
                <YAxis fontSize={11} width={28} tickLine={false} axisLine={false} />
                <Tooltip {...tip} />
                <Line type="monotone" dataKey="wer" stroke="var(--chart-5)" strokeWidth={2} dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </Card>
        <Card>
          <h2 className="font-semibold">Coverage by subject</h2>
          <p className="text-xs text-muted-foreground">Golden Corpus, %</p>
          <div className="mt-3 h-40">
            <ResponsiveContainer>
              <BarChart data={m.bySubject} layout="vertical">
                <XAxis type="number" hide domain={[0, 100]} />
                <YAxis type="category" dataKey="subject" fontSize={11} width={70} tickLine={false} axisLine={false} />
                <Tooltip {...tip} />
                <Bar dataKey="coverage" fill="var(--chart-2)" radius={[0, 6, 6, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Card>
      </div>

      {/* System Health */}
      <Card className="mt-4">
        <h2 className="font-semibold">System health</h2>
        <ul className="mt-3 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
          {m.health.map((h) => (
            <li key={h.name} className="flex items-center gap-3 rounded-xl bg-muted/60 p-3">
              <span className={cn("h-2.5 w-2.5 rounded-full", h.ok ? "bg-primary" : "bg-warn")} aria-hidden />
              <div>
                <p className="text-sm font-semibold">
                  {h.name} <span className="sr-only">{h.ok ? "healthy" : "needs attention"}</span>
                </p>
                <p className="text-xs text-muted-foreground">{h.detail}</p>
              </div>
            </li>
          ))}
        </ul>
      </Card>
    </Page>
  );
}
