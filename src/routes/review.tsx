import { createFileRoute } from "@tanstack/react-router";
import { Check, Pencil, X, Plus, Trash2 } from "lucide-react";
import { useState } from "react";
import { toast } from "sonner";
import { Page, Card } from "@/components/app-shell";
import { GLOSSARY_INITIAL, REVIEW_QUEUE, SUBJECTS } from "@/lib/mock-data";
import { cn } from "@/lib/utils";

export const Route = createFileRoute("/review")({
  head: () => ({
    meta: [
      { title: "Reviewer dashboard — AksharSetu" },
      { name: "description", content: "Verify flagged Marathi pages and manage the subject correction dictionary." },
      { property: "og:title", content: "Reviewer dashboard — AksharSetu" },
      { property: "og:description", content: "Teacher verification queue and glossary." },
      { property: "og:type", content: "website" },
      { name: "twitter:card", content: "summary" },
    ],
  }),
  component: Review,
});

function Highlight({ text, flagged }: { text: string; flagged: string[] }) {
  return (
    <>
      {text.split(" ").map((w, i) => (
        <span key={i}>
          {flagged.some((f) => w.startsWith(f)) ? <mark className="rounded bg-warn-soft px-0.5 text-warn underline decoration-wavy">{w}</mark> : w}{" "}
        </span>
      ))}
    </>
  );
}

function Review() {
  const [tab, setTab] = useState<"queue" | "glossary">("queue");
  const [queue, setQueue] = useState(REVIEW_QUEUE);
  const [editing, setEditing] = useState<string | null>(null);
  const [draft, setDraft] = useState("");
  const [gloss, setGloss] = useState(GLOSSARY_INITIAL);
  const [filter, setFilter] = useState("All");
  const [nt, setNt] = useState({ term: "", note: "", subject: SUBJECTS[0] });

  const resolve = (id: string, action: string) => {
    setQueue((q) => q.filter((x) => x.id !== id));
    setEditing(null);
    toast.success(`Page ${action}`);
  };

  return (
    <Page title="Reviewer dashboard" deva="शिक्षक तपासणी" wide>
      <div className="mb-6 flex gap-2" role="tablist">
        {(["queue", "glossary"] as const).map((t) => (
          <button key={t} role="tab" aria-selected={tab === t} onClick={() => setTab(t)} className={cn("rounded-xl px-4 py-2 font-semibold transition", tab === t ? "bg-primary text-primary-foreground" : "border bg-card hover:bg-accent")}>
            {t === "queue" ? `Verification queue (${queue.length})` : "Dictionary"}
          </button>
        ))}
      </div>

      {tab === "queue" ? (
        <div className="space-y-4">
          {queue.length === 0 && <Card><p className="text-center text-muted-foreground">Queue is clear. Nice work.</p></Card>}
          {queue.map((r) => (
            <Card key={r.id} className="grid gap-5 lg:grid-cols-[220px_1fr]">
              <div className="grid aspect-[3/4] place-items-center rounded-xl border bg-muted p-4" role="img" aria-label={`Photo of ${r.book} page ${r.page}`}>
                <div className="deva w-full space-y-2 text-[10px] leading-tight text-muted-foreground/70" aria-hidden>
                  {Array.from({ length: 9 }).map((_, i) => <div key={i} className="h-1.5 rounded bg-foreground/15" style={{ width: `${70 + ((i * 13) % 30)}%` }} />)}
                </div>
              </div>
              <div>
                <div className="flex flex-wrap items-center gap-3">
                  <h2 className="deva text-lg font-semibold">{r.book}</h2>
                  <span className="text-sm text-muted-foreground">Page {r.page} · {r.submitted}</span>
                  <span className="ml-auto rounded-full bg-muted px-2.5 py-0.5 text-xs font-semibold">OCR confidence {Math.round(r.confidence * 100)}%</span>
                </div>
                {editing === r.id ? (
                  <textarea className="deva mt-3 w-full rounded-xl border bg-card p-3 text-lg" rows={3} value={draft} onChange={(e) => setDraft(e.target.value)} aria-label="Corrected transcript" />
                ) : (
                  <p className="deva mt-3 rounded-xl bg-muted/60 p-3 text-lg"><Highlight text={r.transcript} flagged={r.flagged} /></p>
                )}
                <p className="mt-2 text-sm text-muted-foreground">Flagged: <span className="deva">{r.flagged.join(", ")}</span></p>
                <div className="mt-4 flex flex-wrap gap-2">
                  <button onClick={() => resolve(r.id, "approved")} className="inline-flex items-center gap-1.5 rounded-xl bg-primary px-4 py-2 font-semibold text-primary-foreground"><Check className="h-4 w-4" aria-hidden /> Approve</button>
                  {editing === r.id ? (
                    <button onClick={() => resolve(r.id, "corrected")} className="inline-flex items-center gap-1.5 rounded-xl border px-4 py-2 font-semibold hover:bg-accent"><Check className="h-4 w-4" aria-hidden /> Save correction</button>
                  ) : (
                    <button onClick={() => { setEditing(r.id); setDraft(r.transcript); }} className="inline-flex items-center gap-1.5 rounded-xl border px-4 py-2 font-semibold hover:bg-accent"><Pencil className="h-4 w-4" aria-hidden /> Correct</button>
                  )}
                  <button onClick={() => resolve(r.id, "rejected")} className="inline-flex items-center gap-1.5 rounded-xl border border-destructive/40 px-4 py-2 font-semibold text-destructive hover:bg-destructive/5"><X className="h-4 w-4" aria-hidden /> Reject</button>
                </div>
              </div>
            </Card>
          ))}
        </div>
      ) : (
        <Card>
          <form className="grid gap-3 sm:grid-cols-[1fr_1fr_160px_auto]" onSubmit={(e) => { e.preventDefault(); if (!nt.term) return; setGloss([{ id: crypto.randomUUID(), ...nt }, ...gloss]); setNt({ ...nt, term: "", note: "" }); toast.success("Term added"); }}>
            <input className="deva rounded-xl border px-3 py-2" placeholder="Marathi term" aria-label="Marathi term" value={nt.term} onChange={(e) => setNt({ ...nt, term: e.target.value })} />
            <input className="rounded-xl border px-3 py-2" placeholder="Meaning / note" aria-label="Meaning" value={nt.note} onChange={(e) => setNt({ ...nt, note: e.target.value })} />
            <select className="rounded-xl border px-3 py-2" aria-label="Subject" value={nt.subject} onChange={(e) => setNt({ ...nt, subject: e.target.value })}>{SUBJECTS.map((s) => <option key={s}>{s}</option>)}</select>
            <button className="inline-flex items-center justify-center gap-1.5 rounded-xl bg-primary px-4 py-2 font-semibold text-primary-foreground"><Plus className="h-4 w-4" aria-hidden /> Add</button>
          </form>
          <div className="mt-5 flex flex-wrap gap-2">
            {["All", ...SUBJECTS].map((s) => (
              <button key={s} aria-pressed={filter === s} onClick={() => setFilter(s)} className={cn("rounded-full border px-3 py-1 text-sm", filter === s && "bg-accent font-semibold")}>{s}</button>
            ))}
          </div>
          <table className="mt-4 w-full text-left">
            <thead className="text-sm text-muted-foreground"><tr><th className="py-2">Term</th><th>Meaning</th><th>Subject</th><th className="sr-only">Actions</th></tr></thead>
            <tbody>
              {gloss.filter((g) => filter === "All" || g.subject === filter).map((g) => (
                <tr key={g.id} className="border-t">
                  <td className="deva py-2 text-lg">
                    <input className="w-full rounded-lg bg-transparent px-1 hover:bg-muted" aria-label="Edit term" value={g.term} onChange={(e) => setGloss(gloss.map((x) => x.id === g.id ? { ...x, term: e.target.value } : x))} />
                  </td>
                  <td><input className="w-full rounded-lg bg-transparent px-1 hover:bg-muted" aria-label="Edit meaning" value={g.note} onChange={(e) => setGloss(gloss.map((x) => x.id === g.id ? { ...x, note: e.target.value } : x))} /></td>
                  <td className="text-sm">{g.subject}</td>
                  <td className="text-right"><button aria-label={`Delete ${g.term}`} onClick={() => setGloss(gloss.filter((x) => x.id !== g.id))} className="rounded-lg p-2 hover:bg-muted"><Trash2 className="h-4 w-4" /></button></td>
                </tr>
              ))}
            </tbody>
          </table>
        </Card>
      )}
    </Page>
  );
}
