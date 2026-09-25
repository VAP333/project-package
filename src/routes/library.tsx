import { createFileRoute, Link } from "@tanstack/react-router";
import { LayoutGrid, List, Headphones } from "lucide-react";
import { useState } from "react";
import { Page, Card, CorpusChip } from "@/components/app-shell";
import { BOOKS, RECENT_PAGES } from "@/lib/mock-data";
import { cn } from "@/lib/utils";

export const Route = createFileRoute("/library")({
  head: () => ({
    meta: [
      { title: "Library — AksharSetu" },
      { name: "description", content: "Your Marathi textbooks and recently read pages, with progress and verification status." },
      { property: "og:title", content: "Library — AksharSetu" },
      { property: "og:description", content: "Books, pages and reading progress." },
      { property: "og:type", content: "website" },
      { name: "twitter:card", content: "summary" },
    ],
  }),
  component: Library,
});

function Bar({ v }: { v: number }) {
  return (
    <div className="h-2 rounded-full bg-muted" role="progressbar" aria-valuenow={v} aria-valuemin={0} aria-valuemax={100}>
      <div className="h-full rounded-full bg-primary" style={{ width: `${v}%` }} />
    </div>
  );
}

function Library() {
  const [view, setView] = useState<"grid" | "list">("grid");
  return (
    <Page title="Library" deva="माझे ग्रंथालय">
      <h2 className="mb-4 text-xl font-semibold">Books</h2>
      <div className="grid gap-4 sm:grid-cols-2">
        {BOOKS.map((b) => {
          const pct = Math.round((b.read / b.pages) * 100);
          return (
            <Card key={b.id} className="transition hover:-translate-y-0.5">
              <p className="deva text-xl font-semibold">{b.title}</p>
              <p className="text-sm text-muted-foreground">{b.titleEn} · {b.std} · {b.edition}</p>
              <div className="mt-4"><Bar v={pct} /></div>
              <p className="mt-2 text-sm text-muted-foreground">{b.read} of {b.pages} pages read ({pct}%)</p>
            </Card>
          );
        })}
      </div>

      <div className="mb-4 mt-12 flex items-center justify-between">
        <h2 className="text-xl font-semibold">Recent pages</h2>
        <div className="flex rounded-xl border bg-card p-1" role="group" aria-label="View">
          <button aria-pressed={view === "grid"} aria-label="Grid view" onClick={() => setView("grid")} className={cn("rounded-lg p-2", view === "grid" && "bg-accent")}><LayoutGrid className="h-4 w-4" /></button>
          <button aria-pressed={view === "list"} aria-label="List view" onClick={() => setView("list")} className={cn("rounded-lg p-2", view === "list" && "bg-accent")}><List className="h-4 w-4" /></button>
        </div>
      </div>
      <ul className={cn("gap-3", view === "grid" ? "grid sm:grid-cols-2 lg:grid-cols-3" : "flex flex-col")}>
        {RECENT_PAGES.map((p) => {
          const book = BOOKS.find((b) => b.id === p.bookId)!;
          return (
            <li key={p.id}>
              <Link to="/read" className={cn("flex gap-4 rounded-2xl border bg-card p-4 shadow-soft transition hover:border-primary/40", view === "grid" ? "flex-col" : "items-center")}>
                <div className="min-w-0 flex-1">
                  <p className="deva truncate text-lg font-semibold">{p.title}</p>
                  <p className="text-sm text-muted-foreground">{book.titleEn} · p. {p.page} · {p.when}</p>
                </div>
                <CorpusChip status={p.status} small />
                <div className={cn(view === "grid" ? "w-full" : "w-32")}><Bar v={p.progress} /></div>
                <Headphones className="hidden h-5 w-5 text-primary sm:block" aria-hidden />
              </Link>
            </li>
          );
        })}
      </ul>
    </Page>
  );
}
