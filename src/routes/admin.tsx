import { createFileRoute } from "@tanstack/react-router";
import { Area, AreaChart, Bar, BarChart, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { Page, Card } from "@/components/app-shell";
import { METRICS } from "@/lib/mock-data";
import { cn } from "@/lib/utils";

export const Route = createFileRoute("/admin")({
  head: () => ({
    meta: [
      { title: "Metrics — AksharSetu" },
      { name: "description", content: "Accuracy, Golden Corpus coverage and system health for AksharSetu." },
      { property: "og:title", content: "Metrics — AksharSetu" },
      { property: "og:description", content: "Admin accuracy and coverage dashboard." },
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

function Admin() {
  const m = METRICS;
  const kpis = [
    { l: "Pages processed", v: m.pagesProcessed.toLocaleString(), sub: `${m.pagesDelta} this week`, k: "pages" as const },
    { l: "Golden Corpus coverage", v: `${m.coverage}%`, sub: "of catalogue pages", k: null },
    { l: "Correction accuracy", v: `${m.correctionAccuracy}%`, sub: "reviewer agreement", k: null },
    { l: "Unresolved-word rate", v: `${m.unresolvedRate}%`, sub: "↓ from 3.4%", k: "unresolved" as const },
  ];
  return (
    <Page title="Metrics" deva="आकडेवारी" wide>
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {kpis.map((x) => (
          <Card key={x.l}>
            <p className="text-sm text-muted-foreground">{x.l}</p>
            <p className="mt-1 text-3xl font-bold">{x.v}</p>
            <p className="text-xs text-muted-foreground">{x.sub}</p>
            {x.k ? <Spark k={x.k} color="var(--chart-1)" /> : (
              <div className="mt-6 h-2 rounded-full bg-muted"><div className="h-full rounded-full bg-primary" style={{ width: x.v }} /></div>
            )}
          </Card>
        ))}
      </div>

      <div className="mt-4 grid gap-4 lg:grid-cols-3">
        <Card>
          <h2 className="font-semibold">CER trend</h2>
          <p className="text-xs text-muted-foreground">Character error rate, %</p>
          <div className="mt-3 h-40"><ResponsiveContainer><LineChart data={m.trend}><XAxis dataKey="week" fontSize={11} tickLine={false} axisLine={false} /><YAxis fontSize={11} width={28} tickLine={false} axisLine={false} /><Tooltip {...tip} /><Line type="monotone" dataKey="cer" stroke="var(--chart-1)" strokeWidth={2} dot={false} /></LineChart></ResponsiveContainer></div>
        </Card>
        <Card>
          <h2 className="font-semibold">WER trend</h2>
          <p className="text-xs text-muted-foreground">Word error rate, %</p>
          <div className="mt-3 h-40"><ResponsiveContainer><LineChart data={m.trend}><XAxis dataKey="week" fontSize={11} tickLine={false} axisLine={false} /><YAxis fontSize={11} width={28} tickLine={false} axisLine={false} /><Tooltip {...tip} /><Line type="monotone" dataKey="wer" stroke="var(--chart-5)" strokeWidth={2} dot={false} /></LineChart></ResponsiveContainer></div>
        </Card>
        <Card>
          <h2 className="font-semibold">Coverage by subject</h2>
          <p className="text-xs text-muted-foreground">Golden Corpus, %</p>
          <div className="mt-3 h-40"><ResponsiveContainer><BarChart data={m.bySubject} layout="vertical"><XAxis type="number" hide domain={[0, 100]} /><YAxis type="category" dataKey="subject" fontSize={11} width={70} tickLine={false} axisLine={false} /><Tooltip {...tip} /><Bar dataKey="coverage" fill="var(--chart-2)" radius={[0, 6, 6, 0]} /></BarChart></ResponsiveContainer></div>
        </Card>
      </div>

      <Card className="mt-4">
        <h2 className="font-semibold">System health</h2>
        <ul className="mt-3 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
          {m.health.map((h) => (
            <li key={h.name} className="flex items-center gap-3 rounded-xl bg-muted/60 p-3">
              <span className={cn("h-2.5 w-2.5 rounded-full", h.ok ? "bg-primary" : "bg-warn")} aria-hidden />
              <div><p className="text-sm font-semibold">{h.name} <span className="sr-only">{h.ok ? "healthy" : "needs attention"}</span></p><p className="text-xs text-muted-foreground">{h.detail}</p></div>
            </li>
          ))}
        </ul>
      </Card>
    </Page>
  );
}
