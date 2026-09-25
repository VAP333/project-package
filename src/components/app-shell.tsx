import { Link } from "@tanstack/react-router";
import { Contrast, Menu, X, ShieldCheck, Users, CircleAlert } from "lucide-react";
import { useState, type ReactNode } from "react";
import { useA11y, useT } from "@/lib/a11y";
import type { CorpusStatus } from "@/lib/mock-data";
import { cn } from "@/lib/utils";

export function Logo({ className }: { className?: string }) {
  return (
    <Link to="/" className={cn("flex items-baseline gap-2 rounded-lg", className)} aria-label="AksharSetu home">
      <span className="grid h-8 w-8 place-items-center self-center rounded-xl bg-primary text-primary-foreground deva text-lg leading-none" aria-hidden>
        अ
      </span>
      <span className="text-lg font-bold tracking-tight">AksharSetu</span>
      <span className="deva hidden text-base text-muted-foreground sm:inline">अक्षरसेतु</span>
    </Link>
  );
}

export function A11yControls({ compact }: { compact?: boolean }) {
  const { size, bump, setSize, contrast, setContrast } = useA11y();
  const btn = "grid h-9 min-w-9 place-items-center rounded-lg px-2 text-sm font-semibold transition-colors hover:bg-accent";
  return (
    <div className="flex items-center gap-1" role="group" aria-label="Text size and contrast">
      <button className={btn} onClick={() => bump(-1)} aria-label="Decrease text size">A−</button>
      <button className={cn(btn, size === "md" && "bg-accent")} onClick={() => setSize("md")} aria-label="Default text size">A</button>
      <button className={cn(btn, "text-base")} onClick={() => bump(1)} aria-label="Increase text size">A+</button>
      <button
        className={cn(btn, contrast && "bg-foreground text-background hover:bg-foreground")}
        onClick={() => setContrast(!contrast)}
        aria-pressed={contrast}
        aria-label="Toggle high contrast"
      >
        <Contrast className="h-4 w-4" />
        {!compact && <span className="sr-only">High contrast</span>}
      </button>
    </div>
  );
}

const NAV = [
  { to: "/capture", k: "capture" },
  { to: "/read", k: "read" },
  { to: "/library", k: "library" },
  { to: "/review", k: "review" },
  { to: "/admin", k: "admin" },
  { to: "/settings", k: "settings" },
] as const;

export function SiteHeader() {
  const t = useT();
  const [open, setOpen] = useState(false);
  return (
    <header className="fixed inset-x-0 top-3 z-50 px-3">
      <nav className="glass mx-auto flex max-w-6xl items-center justify-between gap-3 rounded-2xl px-3 py-2" aria-label="Main">
        <Logo />
        <ul className="hidden items-center gap-1 lg:flex">
          {NAV.map((n) => (
            <li key={n.to}>
              <Link
                to={n.to}
                className="rounded-lg px-3 py-2 text-sm font-medium text-muted-foreground transition-colors hover:bg-accent hover:text-foreground"
                activeProps={{ className: "bg-accent !text-foreground" }}
              >
                {t(n.k)}
              </Link>
            </li>
          ))}
        </ul>
        <div className="flex items-center gap-1">
          <A11yControls compact />
          <button className="grid h-9 w-9 place-items-center rounded-lg hover:bg-accent lg:hidden" aria-label={open ? "Close menu" : "Open menu"} aria-expanded={open} onClick={() => setOpen(!open)}>
            {open ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
          </button>
        </div>
      </nav>
      {open && (
        <ul className="glass mx-auto mt-2 grid max-w-6xl gap-1 rounded-2xl p-2 lg:hidden">
          {NAV.map((n) => (
            <li key={n.to}>
              <Link to={n.to} onClick={() => setOpen(false)} className="block rounded-lg px-3 py-3 font-medium hover:bg-accent" activeProps={{ className: "bg-accent" }}>
                {t(n.k)}
              </Link>
            </li>
          ))}
        </ul>
      )}
    </header>
  );
}

export function Page({ title, deva, intro, children, wide }: { title: string; deva?: string; intro?: string; children: ReactNode; wide?: boolean }) {
  return (
    <main className={cn("mx-auto px-4 pb-32 pt-28", wide ? "max-w-7xl" : "max-w-5xl")}>
      <header className="mb-8">
        <h1 className="text-3xl font-bold tracking-tight sm:text-4xl">{title}</h1>
        {deva && <p className="deva mt-1 text-lg text-muted-foreground">{deva}</p>}
        {intro && <p className="mt-3 max-w-2xl text-muted-foreground">{intro}</p>}
      </header>
      {children}
    </main>
  );
}

const STATUS = {
  verified: { label: "Verified", mr: "सत्यापित", icon: ShieldCheck, cls: "bg-accent text-accent-foreground border-primary/30" },
  community: { label: "Community-confirmed", mr: "समुदाय-पुष्टी", icon: Users, cls: "bg-secondary text-secondary-foreground border-border" },
  unverified: { label: "Unverified", mr: "असत्यापित", icon: CircleAlert, cls: "bg-warn-soft text-warn border-warn/30" },
};

export function CorpusChip({ status, small }: { status: CorpusStatus; small?: boolean }) {
  const s = STATUS[status];
  const Icon = s.icon;
  return (
    <span className={cn("inline-flex items-center gap-1.5 rounded-full border font-semibold", small ? "px-2 py-0.5 text-xs" : "px-3 py-1 text-sm", s.cls)} title={`Golden Corpus: ${s.label}`}>
      <Icon className={small ? "h-3 w-3" : "h-4 w-4"} aria-hidden />
      <span><span className="sr-only">Golden Corpus status: </span>{s.label}</span>
    </span>
  );
}

export function Card({ className, children }: { className?: string; children: ReactNode }) {
  return <div className={cn("rounded-2xl border bg-card p-5 shadow-soft", className)}>{children}</div>;
}
