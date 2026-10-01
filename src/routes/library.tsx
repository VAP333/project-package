import { createFileRoute, Link } from "@tanstack/react-router";
import {
  BookOpen,
  Headphones,
  CheckCircle2,
  Layers,
  ArrowRight,
  Archive,
  Sparkles,
  FileText,
  Activity,
  ShieldCheck,
  ChevronRight
} from "lucide-react";
import { useState } from "react";
import { Page, Card, CorpusChip } from "@/components/app-shell";
import { HISTORY_CHAPTERS, SCIENCE_CHAPTERS, BOOKS, RECENT_PAGES } from "@/lib/mock-data";
import { cn } from "@/lib/utils";

export const Route = createFileRoute("/library")({
  head: () => ({
    meta: [
      { title: "Library — AksharSetu" },
      { name: "description", content: "Active reference textbooks and curriculum collection for AksharSetu." },
      { property: "og:title", content: "Library — AksharSetu" },
      { property: "og:description", content: "Class 8 History & Science Active Reference Textbooks." },
      { property: "og:type", content: "website" },
      { name: "twitter:card", content: "summary" },
    ],
  }),
  component: Library,
});

function ProgressBar({ v }: { v: number }) {
  return (
    <div className="h-2 rounded-full bg-muted" role="progressbar" aria-valuenow={v} aria-valuemin={0} aria-valuemax={100}>
      <div className="h-full rounded-full bg-primary transition-all duration-300" style={{ width: `${v}%` }} />
    </div>
  );
}

function Library() {
  const [activeSubject, setActiveSubject] = useState<"history" | "science">("science");
  const [showArchived, setShowArchived] = useState(false);

  // Active Reference Textbooks
  const historyBook = BOOKS.find((b) => b.id === "history-8") || {
    id: "history-8",
    title: "इयत्ता आठवी — इतिहास व नागरिकशास्त्र (इतिहास विभाग)",
    titleEn: "History (8th Standard, Master Reference)",
    std: "Class 8",
    edition: "2018 First Edition",
    subject: "History",
    pages: 75,
    read: 14,
  };

  const scienceBook = BOOKS.find((b) => b.id === "science-8") || {
    id: "science-8",
    title: "इयत्ता आठवी — सामान्य विज्ञान",
    titleEn: "General Science (8th Standard, Master Reference)",
    std: "Class 8",
    edition: "2018 First Edition",
    subject: "Science",
    pages: 148,
    read: 19,
  };

  // Archived Textbooks (safely preserved, inactive in this milestone)
  const archivedBooks = BOOKS.filter((b) => b.id !== "history-8" && b.id !== "science-8");

  const currentBook = activeSubject === "science" ? scienceBook : historyBook;
  const currentChapters = activeSubject === "science" ? SCIENCE_CHAPTERS : HISTORY_CHAPTERS;

  return (
    <Page title="Library" deva="माझे ग्रंथालय">
      {/* ------------------------------------------------------------- */}
      {/* SECTION 1: SUBJECT SWITCHER & ACTIVE REFERENCE TEXTBOOK       */}
      {/* ------------------------------------------------------------- */}
      <div className="mb-6 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <span className="inline-flex items-center gap-1.5 rounded-full bg-primary/10 px-3 py-1 text-xs font-bold text-primary">
            <Sparkles className="h-3.5 w-3.5" aria-hidden /> ACTIVE REFERENCE TEXTBOOKS
          </span>
          <h2 className="mt-1 text-2xl font-bold tracking-tight text-foreground">
            Class 8 Maharashtra State Board · प्राथमिक संदर्भ पाठ्यपुस्तके
          </h2>
        </div>

        {/* Subject Tab Toggle */}
        <div className="flex items-center rounded-xl border bg-muted/40 p-1">
          <button
            type="button"
            onClick={() => setActiveSubject("science")}
            className={cn(
              "flex items-center gap-1.5 rounded-lg px-3.5 py-1.5 text-xs font-bold transition",
              activeSubject === "science"
                ? "bg-card text-foreground shadow-xs"
                : "text-muted-foreground hover:text-foreground"
            )}
          >
            🔬 सामान्य विज्ञान (Science)
          </button>
          <button
            type="button"
            onClick={() => setActiveSubject("history")}
            className={cn(
              "flex items-center gap-1.5 rounded-lg px-3.5 py-1.5 text-xs font-bold transition",
              activeSubject === "history"
                ? "bg-card text-foreground shadow-xs"
                : "text-muted-foreground hover:text-foreground"
            )}
          >
            📜 इतिहास (History)
          </button>
        </div>
      </div>

      {/* Prominent Reference Textbook Card */}
      <Card className="relative overflow-hidden border-2 border-primary/40 bg-gradient-to-br from-card via-card to-primary/5 p-6 shadow-md md:p-8">
        <div className="flex flex-col gap-6 md:flex-row md:items-start md:justify-between">
          <div className="max-w-2xl space-y-3">
            <div className="flex flex-wrap items-center gap-2">
              <span className="rounded-md bg-primary px-2.5 py-1 text-xs font-bold text-primary-foreground">
                REFERENCE STANDARD
              </span>
              <span className="rounded-md bg-accent px-2.5 py-1 text-xs font-semibold text-accent-foreground">
                Maharashtra State Board
              </span>
              <span className="rounded-md bg-muted px-2.5 py-1 text-xs font-medium text-muted-foreground">
                Marathi Medium
              </span>
              <span className="rounded-md bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 px-2.5 py-1 text-xs font-bold">
                {activeSubject === "science" ? "19 Chapters" : "14 Chapters"}
              </span>
            </div>

            <h3 className="deva text-3xl font-extrabold text-foreground sm:text-4xl">
              {currentBook.title}
            </h3>
            <p className="text-sm font-medium text-muted-foreground">
              {activeSubject === "science"
                ? "General Science · 19 Chapters · 136 Content Pages (PDF pp. 11–146) · 321 Pedagogical Learning Units"
                : "Modern Indian History · 14 Chapters · 65 Content Pages (PDF pp. 10–74) · 146 Pedagogical Learning Units"}
            </p>

            <div className="grid grid-cols-2 gap-3 pt-2 sm:grid-cols-4">
              <div className="rounded-xl border bg-card/80 p-3 shadow-xs">
                <span className="text-xs text-muted-foreground">Chapters</span>
                <p className="text-lg font-bold text-foreground">
                  {activeSubject === "science" ? "19" : "14"}
                </p>
              </div>
              <div className="rounded-xl border bg-card/80 p-3 shadow-xs">
                <span className="text-xs text-muted-foreground">Content Pages</span>
                <p className="text-lg font-bold text-foreground">
                  {activeSubject === "science" ? "136" : "65"}
                </p>
              </div>
              <div className="rounded-xl border bg-card/80 p-3 shadow-xs">
                <span className="text-xs text-muted-foreground">Learning Units</span>
                <p className="text-lg font-bold text-foreground">
                  {activeSubject === "science" ? "321" : "146"}
                </p>
              </div>
              <div className="rounded-xl border bg-card/80 p-3 shadow-xs">
                <span className="text-xs text-muted-foreground">Pronunciation Risk</span>
                <p className="text-lg font-bold text-foreground">
                  {activeSubject === "science" ? "150+ Terms" : "197 Lexicon"}
                </p>
              </div>
            </div>

            <div className="pt-2">
              <div className="flex items-center justify-between text-xs text-muted-foreground mb-1.5">
                <span>Verification State: Complete Reference Ingestion</span>
                <span className="font-semibold text-primary">100% Ready</span>
              </div>
              <ProgressBar v={100} />
            </div>
          </div>

          <div className="flex flex-col gap-2.5 sm:min-w-[200px]">
            <Link
              to="/read"
              search={{ doc: activeSubject === "science" ? "science-8" : "history-8", chapter: "CH_01", page: 1 }}
              className="inline-flex items-center justify-center gap-2 rounded-xl bg-primary px-5 py-3 font-semibold text-primary-foreground shadow-soft transition hover:opacity-90"
            >
              <Headphones className="h-5 w-5" aria-hidden /> Continue Reading
            </Link>
            <Link
              to="/capture"
              className="inline-flex items-center justify-center gap-2 rounded-xl border bg-card px-5 py-2.5 font-semibold text-foreground transition hover:bg-accent"
            >
              <Activity className="h-4 w-4 text-primary" aria-hidden /> Ingestion Dashboard
            </Link>
          </div>
        </div>
      </Card>

      {/* ------------------------------------------------------------- */}
      {/* SECTION 2: CHAPTERS AT A GLANCE                               */}
      {/* ------------------------------------------------------------- */}
      <div className="mt-10 mb-4 flex items-center justify-between">
        <h3 className="text-xl font-bold tracking-tight">
          {activeSubject === "science" ? "Science Chapters Navigator (१९ पाठ)" : "History Chapters Navigator (१४ पाठ)"}
        </h3>
        <span className="text-xs font-semibold text-muted-foreground">Full Subject Inventory</span>
      </div>

      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
        {currentChapters.map((ch) => (
          <Link
            key={ch.id}
            to="/read"
            search={{ doc: activeSubject === "science" ? "science-8" : "history-8", chapter: ch.id, page: ch.page }}
            className="group flex flex-col justify-between rounded-xl border bg-card p-4 transition hover:border-primary/50 hover:shadow-xs"
          >
            <div>
              <div className="flex items-center justify-between gap-2">
                <span className="rounded-md bg-primary/10 px-2 py-0.5 text-xs font-bold text-primary font-mono">
                  {ch.id}
                </span>
                <span className="text-xs text-muted-foreground">
                  पान {ch.page} · PDF {ch.pdfStart}–{ch.pdfEnd}
                </span>
              </div>
              <p className="deva mt-2 font-bold text-foreground group-hover:text-primary transition-colors">
                {ch.title}
              </p>
              <p className="text-xs text-muted-foreground">{ch.titleEn}</p>
            </div>

            <div className="mt-3 flex items-center justify-between border-t pt-2 text-xs text-muted-foreground">
              <span className="inline-flex items-center gap-1 text-emerald-600 font-medium">
                <CheckCircle2 className="h-3.5 w-3.5" aria-hidden /> Ready to Listen
              </span>
              <span className="inline-flex items-center gap-0.5 font-semibold text-primary">
                Open <ChevronRight className="h-3 w-3" aria-hidden />
              </span>
            </div>
          </Link>
        ))}
      </div>

      {/* ------------------------------------------------------------- */}
      {/* SECTION 3: ARCHIVED / PREVIOUS TEXTBOOKS                      */}
      {/* ------------------------------------------------------------- */}
      <div className="mt-14 border-t pt-8">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Archive className="h-4 w-4 text-muted-foreground" aria-hidden />
            <h3 className="text-base font-semibold text-muted-foreground">
              Archived / Previous Textbooks (संग्रहित पाठ्यपुस्तके)
            </h3>
          </div>
          <button
            type="button"
            onClick={() => setShowArchived(!showArchived)}
            className="text-xs font-semibold text-primary hover:underline"
          >
            {showArchived ? "Hide Archived Textbooks" : "Show Archived (2 Textbooks)"}
          </button>
        </div>
        <p className="mt-1 text-xs text-muted-foreground">
          Safely preserved in database storage. Inactive during the Class 8 History reference implementation milestone.
        </p>

        {showArchived && (
          <div className="mt-4 grid gap-4 sm:grid-cols-2 opacity-80">
            {archivedBooks.map((b) => (
              <div
                key={b.id}
                className="flex flex-col rounded-xl border border-dashed border-border bg-muted/30 p-4"
              >
                <div className="flex items-start justify-between gap-2">
                  <div>
                    <span className="rounded bg-muted px-2 py-0.5 text-[10px] font-bold text-muted-foreground">
                      ARCHIVED · INACTIVE
                    </span>
                    <p className="deva mt-1 text-base font-semibold text-foreground">{b.title}</p>
                    <p className="text-xs text-muted-foreground">{b.titleEn} · {b.std}</p>
                  </div>
                  <span className="text-xs text-muted-foreground">{b.pages} pages</span>
                </div>
                <p className="mt-3 text-xs text-muted-foreground">
                  Preserved in database. Switch to Class 8 History to access active learning graphs and grounded tutor.
                </p>
              </div>
            ))}
          </div>
        )}
      </div>
    </Page>
  );
}
