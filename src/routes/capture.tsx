import { createFileRoute, Link } from "@tanstack/react-router";
import { Camera, Upload, CheckCircle2, AlertTriangle, Loader2, ArrowRight } from "lucide-react";
import { useRef, useState } from "react";
import { Page, Card } from "@/components/app-shell";
import { BOOKS, EDITIONS, SUBJECTS } from "@/lib/mock-data";
import { cn } from "@/lib/utils";

export const Route = createFileRoute("/capture")({
  head: () => ({
    meta: [
      { title: "Capture a page — AksharSetu" },
      { name: "description", content: "Select your textbook and page, then photograph it for verified Marathi audio." },
      { property: "og:title", content: "Capture a page — AksharSetu" },
      { property: "og:description", content: "Photograph a Marathi textbook page to hear it read aloud." },
      { property: "og:type", content: "website" },
      { name: "twitter:card", content: "summary" },
    ],
  }),
  component: Capture,
});

type Quality = "idle" | "checking" | "good" | "blurry";

function Capture() {
  const [book, setBook] = useState(BOOKS[0].id);
  const [edition, setEdition] = useState(EDITIONS[0]);
  const [subject, setSubject] = useState(BOOKS[0].subject);
  const [page, setPage] = useState("34");
  const [quality, setQuality] = useState<Quality>("idle");
  const [preview, setPreview] = useState<string | null>(null);
  const fileRef = useRef<HTMLInputElement>(null);
  const ready = book && edition && subject && page;

  const onFile = (f?: File) => {
    if (!f) return;
    setPreview(URL.createObjectURL(f));
    setQuality("checking");
    // Mock quality check — swap for real API later
    setTimeout(() => setQuality(Math.random() > 0.35 ? "good" : "blurry"), 1200);
  };

  const field = "mt-1.5 w-full rounded-xl border bg-card px-3 py-3 text-base focus-visible:border-primary";

  return (
    <Page title="Capture a page" deva="पान फोटो काढा" intro="First tell us which page this is — then take the photo.">
      <div className="grid gap-6 md:grid-cols-5">
        <Card className="md:col-span-2">
          <h2 className="flex items-center gap-2 font-semibold"><span className="grid h-7 w-7 place-items-center rounded-full bg-primary text-sm text-primary-foreground">1</span> Choose the page</h2>
          <div className="mt-5 space-y-4">
            <label className="block text-sm font-medium">Book
              <select className={field} value={book} onChange={(e) => { setBook(e.target.value); const b = BOOKS.find((x) => x.id === e.target.value); if (b) setSubject(b.subject); }}>
                {BOOKS.map((b) => <option key={b.id} value={b.id}>{b.title} · {b.titleEn}</option>)}
              </select>
            </label>
            <label className="block text-sm font-medium">Edition
              <select className={field} value={edition} onChange={(e) => setEdition(e.target.value)}>
                {EDITIONS.map((x) => <option key={x}>{x}</option>)}
              </select>
            </label>
            <label className="block text-sm font-medium">Subject
              <select className={field} value={subject} onChange={(e) => setSubject(e.target.value)}>
                {SUBJECTS.map((x) => <option key={x}>{x}</option>)}
              </select>
            </label>
            <label className="block text-sm font-medium">Page number
              <input className={field} inputMode="numeric" value={page} onChange={(e) => setPage(e.target.value.replace(/\D/g, ""))} />
            </label>
          </div>
        </Card>

        <Card className={cn("md:col-span-3", !ready && "opacity-60")}>
          <h2 className="flex items-center gap-2 font-semibold"><span className="grid h-7 w-7 place-items-center rounded-full bg-primary text-sm text-primary-foreground">2</span> Photograph it</h2>
          <input ref={fileRef} type="file" accept="image/*" capture="environment" className="sr-only" onChange={(e) => onFile(e.target.files?.[0])} aria-label="Photo of the page" />
          <button
            type="button"
            disabled={!ready}
            onClick={() => fileRef.current?.click()}
            onDragOver={(e) => e.preventDefault()}
            onDrop={(e) => { e.preventDefault(); onFile(e.dataTransfer.files[0]); }}
            className="mt-5 flex aspect-[4/3] w-full flex-col items-center justify-center gap-3 overflow-hidden rounded-2xl border-2 border-dashed border-primary/40 bg-accent/40 transition hover:bg-accent"
          >
            {preview ? (
              <img src={preview} alt="Captured page preview" className="h-full w-full object-contain" />
            ) : (
              <>
                <span className="grid h-16 w-16 place-items-center rounded-2xl bg-primary text-primary-foreground"><Camera className="h-8 w-8" aria-hidden /></span>
                <span className="text-lg font-semibold">Tap to open camera</span>
                <span className="flex items-center gap-1.5 text-sm text-muted-foreground"><Upload className="h-4 w-4" aria-hidden /> or drop an image here</span>
              </>
            )}
          </button>

          <div role="status" aria-live="polite" className="mt-4">
            {quality === "checking" && <p className="flex items-center gap-2 rounded-xl bg-muted p-3"><Loader2 className="h-5 w-5 animate-spin" aria-hidden /> Checking photo quality…</p>}
            {quality === "good" && (
              <div className="flex flex-wrap items-center justify-between gap-3 rounded-xl bg-accent p-3 text-accent-foreground">
                <p className="flex items-center gap-2 font-semibold"><CheckCircle2 className="h-5 w-5 text-primary" aria-hidden /> Looks good — text is sharp and well lit.</p>
                <Link to="/read" className="inline-flex items-center gap-1.5 rounded-lg bg-primary px-4 py-2 font-semibold text-primary-foreground">Read page <ArrowRight className="h-4 w-4" aria-hidden /></Link>
              </div>
            )}
            {quality === "blurry" && (
              <div className="flex flex-wrap items-center justify-between gap-3 rounded-xl bg-warn-soft p-3 text-warn">
                <p className="flex items-center gap-2 font-semibold"><AlertTriangle className="h-5 w-5" aria-hidden /> Too blurry — hold steady and try again.</p>
                <button onClick={() => fileRef.current?.click()} className="rounded-lg border border-warn/40 bg-card px-4 py-2 font-semibold">Retake</button>
              </div>
            )}
            {quality !== "idle" && (
              <div className="mt-3 flex gap-1" aria-hidden>
                {[0, 1, 2, 3, 4].map((i) => (
                  <span key={i} className={cn("h-2 flex-1 rounded-full bg-muted transition-colors", quality === "good" && "bg-primary", quality === "blurry" && i < 2 && "bg-warn")} />
                ))}
              </div>
            )}
          </div>
        </Card>
      </div>
    </Page>
  );
}
