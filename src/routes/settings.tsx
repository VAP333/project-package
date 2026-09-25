import { createFileRoute } from "@tanstack/react-router";
import { useState } from "react";
import { Page, Card } from "@/components/app-shell";
import { Switch } from "@/components/ui/switch";
import { Slider } from "@/components/ui/slider";
import { useA11y, type TextSize } from "@/lib/a11y";
import { cn } from "@/lib/utils";

export const Route = createFileRoute("/settings")({
  head: () => ({
    meta: [
      { title: "Settings & accessibility — AksharSetu" },
      { name: "description", content: "Adjust text size, contrast, voice speed, interface language and notifications." },
      { property: "og:title", content: "Settings — AksharSetu" },
      { property: "og:description", content: "Accessibility and preferences." },
      { property: "og:type", content: "website" },
      { name: "twitter:card", content: "summary" },
    ],
  }),
  component: Settings,
});

function Row({ label, hint, children }: { label: string; hint?: string; children: React.ReactNode }) {
  return (
    <div className="flex flex-wrap items-center justify-between gap-4 border-t py-5 first:border-t-0 first:pt-0">
      <div><p className="font-semibold">{label}</p>{hint && <p className="text-sm text-muted-foreground">{hint}</p>}</div>
      {children}
    </div>
  );
}

function Settings() {
  const { size, setSize, contrast, setContrast, lang, setLang } = useA11y();
  const [speed, setSpeed] = useState([1]);
  const [notif, setNotif] = useState({ reviewed: true, newPages: false, weekly: true });
  const seg = (on: boolean) => cn("rounded-lg px-4 py-2 font-semibold transition", on ? "bg-primary text-primary-foreground" : "hover:bg-accent");

  return (
    <Page title="Settings" deva="सेटिंग्ज व सुलभता">
      <Card>
        <h2 className="mb-4 text-lg font-bold">Accessibility</h2>
        <Row label="Text size" hint="Also available in the top bar (A− A A+)">
          <div className="flex rounded-xl border p-1" role="radiogroup" aria-label="Text size">
            {(["sm", "md", "lg", "xl"] as TextSize[]).map((s, i) => (
              <button key={s} role="radio" aria-checked={size === s} onClick={() => setSize(s)} className={seg(size === s)} style={{ fontSize: `${0.8 + i * 0.15}rem` }}>A</button>
            ))}
          </div>
        </Row>
        <Row label="High contrast" hint="Near-black text and stronger borders">
          <Switch checked={contrast} onCheckedChange={setContrast} aria-label="High contrast" />
        </Row>
        <Row label="Default voice speed" hint={`${speed[0].toFixed(2)}×`}>
          <Slider className="w-56" min={0.5} max={2} step={0.25} value={speed} onValueChange={setSpeed} aria-label="Default voice speed" />
        </Row>
        <Row label="Interface language" hint="Menus and buttons only — book text is always Marathi">
          <div className="flex rounded-xl border p-1" role="radiogroup" aria-label="Interface language">
            <button role="radio" aria-checked={lang === "en"} onClick={() => setLang("en")} className={seg(lang === "en")}>English</button>
            <button role="radio" aria-checked={lang === "mr"} onClick={() => setLang("mr")} className={cn(seg(lang === "mr"), "deva")}>मराठी</button>
          </div>
        </Row>
      </Card>
      <Card className="mt-6">
        <h2 className="mb-4 text-lg font-bold">Notifications</h2>
        <Row label="A page I read was verified"><Switch checked={notif.reviewed} onCheckedChange={(v) => setNotif({ ...notif, reviewed: v })} aria-label="Page verified notifications" /></Row>
        <Row label="New pages added to my books"><Switch checked={notif.newPages} onCheckedChange={(v) => setNotif({ ...notif, newPages: v })} aria-label="New pages notifications" /></Row>
        <Row label="Weekly reading summary"><Switch checked={notif.weekly} onCheckedChange={(v) => setNotif({ ...notif, weekly: v })} aria-label="Weekly summary notifications" /></Row>
      </Card>
    </Page>
  );
}
