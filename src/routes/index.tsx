import { createFileRoute, Link } from "@tanstack/react-router";
import { Camera, ShieldCheck, Headphones, BookOpenCheck, Sparkles, ArrowRight, Eye, Keyboard } from "lucide-react";
import { Card } from "@/components/app-shell";

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: "AksharSetu — Marathi textbooks, read aloud and verified" },
      { name: "description", content: "AksharSetu turns photographed Marathi textbook pages into verified, spoken Marathi for visually impaired students." },
      { property: "og:title", content: "AksharSetu — the bridge of letters" },
      { property: "og:description", content: "Photograph a Marathi textbook page. Hear it read back, accurately." },
      { property: "og:type", content: "website" },
      { name: "twitter:card", content: "summary_large_image" },
    ],
  }),
  component: Landing,
});

function Landing() {
  return (
    <main className="pb-24">
      <section className="relative overflow-hidden px-4 pb-20 pt-36">
        <div className="pointer-events-none absolute -top-32 left-1/2 h-[520px] w-[900px] -translate-x-1/2 rounded-full bg-mint/50 blur-3xl" aria-hidden />
        <div className="relative mx-auto max-w-4xl text-center">
          <p className="deva text-2xl text-primary">अक्षरसेतु</p>
          <h1 className="mt-3 text-4xl font-bold tracking-tight sm:text-6xl">
            Every Marathi textbook page, <span className="text-primary">heard exactly as written.</span>
          </h1>
          <p className="mx-auto mt-5 max-w-2xl text-lg text-muted-foreground">
            AksharSetu is the bridge of letters — it turns a photo of a school page into verified, spoken Marathi for visually impaired students.
          </p>
          <div className="mt-8 flex flex-wrap justify-center gap-3">
            <Link to="/capture" className="inline-flex items-center gap-2 rounded-xl bg-primary px-6 py-3 font-semibold text-primary-foreground shadow-soft transition hover:opacity-90">
              <Camera className="h-5 w-5" aria-hidden /> Try it now
            </Link>
            <Link to="/read" className="inline-flex items-center gap-2 rounded-xl border bg-card px-6 py-3 font-semibold transition hover:bg-accent">
              <Headphones className="h-5 w-5" aria-hidden /> Hear a sample page
            </Link>
          </div>
        </div>
      </section>

      <section className="mx-auto max-w-6xl px-4 py-16" aria-labelledby="how">
        <h2 id="how" className="text-center text-3xl font-bold tracking-tight">How it works</h2>
        <ol className="mt-10 grid gap-5 md:grid-cols-3">
          {[
            { icon: Camera, t: "Capture", mr: "फोटो घ्या", d: "Choose the book, edition and page, then photograph it. We tell you instantly if the photo is clear enough." },
            { icon: ShieldCheck, t: "Verify", mr: "तपासा", d: "Text is read and corrected against a subject dictionary. Words we can't read confidently are flagged — never guessed." },
            { icon: Headphones, t: "Listen", mr: "ऐका", d: "Hear the page in natural Marathi, sentence by sentence, with full voice and keyboard control." },
          ].map((s, i) => (
            <li key={s.t}>
              <Card className="h-full transition hover:-translate-y-0.5">
                <div className="flex items-center gap-3">
                  <span className="grid h-11 w-11 place-items-center rounded-xl bg-accent text-primary"><s.icon className="h-5 w-5" aria-hidden /></span>
                  <span className="text-sm font-semibold text-muted-foreground">Step {i + 1}</span>
                </div>
                <h3 className="mt-4 text-xl font-semibold">{s.t} <span className="deva font-normal text-muted-foreground">· {s.mr}</span></h3>
                <p className="mt-2 text-muted-foreground">{s.d}</p>
              </Card>
            </li>
          ))}
        </ol>
      </section>

      <section className="mx-auto max-w-6xl px-4 py-16" aria-labelledby="modes">
        <h2 id="modes" className="text-center text-3xl font-bold tracking-tight">Two modes. Never confused.</h2>
        <p className="mx-auto mt-3 max-w-2xl text-center text-muted-foreground">The textbook's words and AI explanations are always kept visually and audibly separate.</p>
        <div className="mt-10 grid gap-5 md:grid-cols-2">
          <Card className="border-primary/30">
            <span className="inline-flex items-center gap-1.5 rounded-full bg-accent px-3 py-1 text-sm font-semibold text-accent-foreground"><BookOpenCheck className="h-4 w-4" aria-hidden /> Reading Mode · canonical text</span>
            <p className="deva mt-5 text-lg">माझी शाळा गावाच्या टोकाला एका टेकडीवर आहे.</p>
            <p className="mt-4 text-muted-foreground">Exactly what's printed in the book — verified word for word. This is the default.</p>
          </Card>
          <Card className="border-2 border-dashed border-tutor/50 bg-tutor-soft">
            <span className="inline-flex items-center gap-1.5 rounded-full bg-tutor px-3 py-1 text-sm font-semibold text-primary-foreground"><Sparkles className="h-4 w-4" aria-hidden /> Tutor Mode · AI-generated</span>
            <p className="deva mt-5 text-lg text-tutor-foreground">‘टेकडी’ म्हणजे लहान डोंगर. लेखक शाळेचा परिसर वर्णन करतो.</p>
            <p className="mt-4 text-muted-foreground">Helpful explanations produced by AI. Always labelled, always spoken with an audible "explanation" cue, never mixed into the book text.</p>
          </Card>
        </div>
      </section>

      <section className="mx-auto max-w-6xl px-4 py-16" aria-labelledby="trust">
        <div className="grid gap-8 rounded-3xl bg-accent/60 p-8 md:grid-cols-2 md:p-12">
          <div>
            <h2 id="trust" className="text-3xl font-bold tracking-tight">Accuracy you can trust</h2>
            <p className="mt-3 text-muted-foreground">Every page carries a Golden Corpus status so students and teachers know exactly how reliable it is. Uncertain words are marked, not smoothed over.</p>
          </div>
          <dl className="grid grid-cols-2 gap-4">
            {[["97.8%", "correction accuracy"], ["18k+", "pages processed"], ["64%", "Golden Corpus coverage"], ["<2%", "unresolved words"]].map(([v, l]) => (
              <div key={l} className="rounded-2xl bg-card p-4 shadow-soft">
                <dt className="text-sm text-muted-foreground">{l}</dt>
                <dd className="text-2xl font-bold text-primary">{v}</dd>
              </div>
            ))}
          </dl>
        </div>
        <ul className="mt-6 flex flex-wrap justify-center gap-6 text-sm text-muted-foreground">
          <li className="flex items-center gap-2"><Eye className="h-4 w-4" aria-hidden /> High-contrast & large text</li>
          <li className="flex items-center gap-2"><Keyboard className="h-4 w-4" aria-hidden /> Full keyboard & voice control</li>
          <li className="flex items-center gap-2"><ShieldCheck className="h-4 w-4" aria-hidden /> Teacher-reviewed pages</li>
        </ul>
      </section>

      <section className="mx-auto max-w-3xl px-4 py-16 text-center">
        <h2 className="text-3xl font-bold tracking-tight">Ready to hear your first page?</h2>
        <Link to="/capture" className="mt-6 inline-flex items-center gap-2 rounded-xl bg-primary px-6 py-3 font-semibold text-primary-foreground transition hover:opacity-90">
          Start capturing <ArrowRight className="h-5 w-5" aria-hidden />
        </Link>
      </section>
    </main>
  );
}
