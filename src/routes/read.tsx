import { createFileRoute } from "@tanstack/react-router";
import { Play, Pause, Repeat, SkipBack, SkipForward, Sparkles, BookOpenCheck, Mic, ChevronDown } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { Page, CorpusChip } from "@/components/app-shell";
import { READING_PAGE, VOICE_COMMANDS } from "@/lib/mock-data";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import { cn } from "@/lib/utils";

export const Route = createFileRoute("/read")({
  head: () => ({
    meta: [
      { title: "Reading — AksharSetu" },
      { name: "description", content: "Listen to a verified Marathi textbook page with sentence highlighting and optional AI Tutor Mode." },
      { property: "og:title", content: "Reading — AksharSetu" },
      { property: "og:description", content: "Verified Marathi read aloud, sentence by sentence." },
      { property: "og:type", content: "website" },
      { name: "twitter:card", content: "summary" },
    ],
  }),
  component: Reader,
});

const SPEEDS = [0.75, 1, 1.25, 1.5];

function Reader() {
  const data = READING_PAGE;
  const allSentences = useMemo(() => data.paragraphs.flatMap((p) => p.sentences.map((s) => ({ ...s, para: p.id }))), [data]);
  const [idx, setIdx] = useState(0);
  const [playing, setPlaying] = useState(false);
  const [speed, setSpeed] = useState(1);
  const [tutor, setTutor] = useState(false);
  const [cmdOpen, setCmdOpen] = useState(false);
  const current = allSentences[idx];

  // Mock playback: advance one sentence every ~3s / speed
  useEffect(() => {
    if (!playing) return;
    const t = setTimeout(() => {
      if (idx < allSentences.length - 1) setIdx(idx + 1);
      else setPlaying(false);
    }, 3000 / speed);
    return () => clearTimeout(t);
  }, [playing, idx, speed, allSentences.length]);

  const jumpPara = (d: 1 | -1) => {
    const pIds = data.paragraphs.map((p) => p.id);
    const next = pIds[Math.min(pIds.length - 1, Math.max(0, pIds.indexOf(current.para) + d))];
    setIdx(allSentences.findIndex((s) => s.para === next));
  };

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if ((e.target as HTMLElement).closest("input,select,textarea")) return;
      if (e.key === " ") { e.preventDefault(); setPlaying((p) => !p); }
      if (e.key === "ArrowRight") jumpPara(1);
      if (e.key === "ArrowLeft") jumpPara(-1);
      if (e.key.toLowerCase() === "t") setTutor((v) => !v);
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  });

  const ctrl = "grid h-12 w-12 place-items-center rounded-full transition hover:bg-accent";

  return (
    <TooltipProvider delayDuration={150}>
      <Page title={data.chapter} intro={`${data.bookEn} · Page ${data.page}`}>
        <div className="-mt-4 mb-6 flex flex-wrap items-center gap-3">
          <CorpusChip status={data.status} />
          <span className="text-sm text-muted-foreground">Confirmed by {data.confirmations} readers</span>
          <div role="radiogroup" aria-label="Mode" className="ml-auto flex rounded-xl border bg-card p-1">
            <button role="radio" aria-checked={!tutor} onClick={() => setTutor(false)} className={cn("flex items-center gap-1.5 rounded-lg px-3 py-2 text-sm font-semibold transition", !tutor && "bg-primary text-primary-foreground")}>
              <BookOpenCheck className="h-4 w-4" aria-hidden /> Reading
            </button>
            <button role="radio" aria-checked={tutor} onClick={() => setTutor(true)} className={cn("flex items-center gap-1.5 rounded-lg px-3 py-2 text-sm font-semibold transition", tutor && "bg-tutor text-primary-foreground")}>
              <Sparkles className="h-4 w-4" aria-hidden /> Tutor
            </button>
          </div>
        </div>

        <article className="space-y-6" aria-label="Page transcript">
          {data.paragraphs.map((p) => (
            <section key={p.id} className="space-y-3">
              <p className={cn("deva rounded-2xl border bg-card p-5 text-xl shadow-soft transition", current.para === p.id && "border-primary/40")}>
                {p.sentences.map((s) => {
                  const active = allSentences[idx].id === s.id;
                  return (
                    <span key={s.id} aria-current={active ? "true" : undefined} onClick={() => setIdx(allSentences.findIndex((x) => x.id === s.id))} className={cn("cursor-pointer rounded-md px-0.5 transition-colors", active && "bg-highlight")}>
                      {s.tokens.map((tk, i) =>
                        tk.flagged ? (
                          <Tooltip key={i}>
                            <TooltipTrigger asChild>
                              <span tabIndex={0} className="underline decoration-warn decoration-wavy decoration-2 underline-offset-[6px]" aria-label={`${tk.text} — couldn't be read with confidence`}>{tk.text}</span>
                            </TooltipTrigger>
                            <TooltipContent>Couldn't be read with confidence</TooltipContent>
                          </Tooltip>
                        ) : (
                          <span key={i}>{tk.text}</span>
                        )
                      ).reduce<React.ReactNode[]>((a, el, i) => (i ? [...a, " ", el] : [el]), [])}{" "}
                    </span>
                  );
                })}
              </p>
              {tutor && (
                <aside className="ml-4 rounded-2xl border-2 border-dashed border-tutor/50 bg-tutor-soft p-4 sm:ml-10" aria-label="AI-generated explanation">
                  <span className="inline-flex items-center gap-1.5 rounded-full bg-tutor px-2.5 py-0.5 text-xs font-semibold text-primary-foreground"><Sparkles className="h-3 w-3" aria-hidden /> AI-generated explanation · not from the textbook</span>
                  <p className="deva mt-2 text-lg text-tutor-foreground">{p.tutor}</p>
                </aside>
              )}
            </section>
          ))}
        </article>

        <section className="mt-8 rounded-2xl border bg-card">
          <button className="flex w-full items-center justify-between p-4 font-semibold" aria-expanded={cmdOpen} onClick={() => setCmdOpen(!cmdOpen)}>
            <span className="flex items-center gap-2"><Mic className="h-5 w-5 text-primary" aria-hidden /> Voice commands</span>
            <ChevronDown className={cn("h-5 w-5 transition", cmdOpen && "rotate-180")} aria-hidden />
          </button>
          {cmdOpen && (
            <ul className="grid gap-2 border-t p-4 sm:grid-cols-2">
              {VOICE_COMMANDS.map((c) => (
                <li key={c.say} className="flex justify-between gap-3 rounded-xl bg-muted px-3 py-2 text-sm">
                  <span className="deva font-semibold">“{c.say}”</span><span className="text-muted-foreground">{c.does}</span>
                </li>
              ))}
              <li className="text-sm text-muted-foreground sm:col-span-2">Keyboard: Space play/pause · ← → paragraph · T toggle Tutor</li>
            </ul>
          )}
        </section>
      </Page>

      <div className="fixed inset-x-0 bottom-4 z-40 px-3">
        <div className="glass mx-auto flex max-w-2xl items-center gap-1 rounded-3xl px-3 py-2" role="region" aria-label="Audio player">
          <button className={ctrl} onClick={() => jumpPara(-1)} aria-label="Previous paragraph"><SkipBack className="h-5 w-5" /></button>
          <button className="grid h-14 w-14 place-items-center rounded-full bg-primary text-primary-foreground shadow-soft transition hover:opacity-90" onClick={() => setPlaying(!playing)} aria-label={playing ? "Pause" : "Play"}>
            {playing ? <Pause className="h-6 w-6" /> : <Play className="ml-0.5 h-6 w-6" />}
          </button>
          <button className={ctrl} onClick={() => jumpPara(1)} aria-label="Next paragraph"><SkipForward className="h-5 w-5" /></button>
          <button className={ctrl} onClick={() => setPlaying(true)} aria-label="Repeat sentence"><Repeat className="h-5 w-5" /></button>
          <div className="mx-2 hidden flex-1 sm:block" aria-hidden>
            <div className="h-1.5 rounded-full bg-muted"><div className="h-full rounded-full bg-primary transition-all" style={{ width: `${((idx + 1) / allSentences.length) * 100}%` }} /></div>
            <p className="mt-1 text-xs text-muted-foreground">Sentence {idx + 1} of {allSentences.length}</p>
          </div>
          <button className="ml-auto rounded-full border px-3 py-2 text-sm font-bold hover:bg-accent sm:ml-0" onClick={() => setSpeed(SPEEDS[(SPEEDS.indexOf(speed) + 1) % SPEEDS.length])} aria-label={`Playback speed ${speed}x, change`}>
            {speed}×
          </button>
        </div>
      </div>
    </TooltipProvider>
  );
}
