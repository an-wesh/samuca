import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { Slider } from "@/components/ui/slider";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";
import { toast } from "sonner";
import api from "@/lib/api";
import { Plus, Save, X, TrendingUp, Activity, BarChart3, Shield } from "lucide-react";

const BLOCKS = [
  { type: "RSI", label: "RSI", icon: Activity, color: "#3B82F6", tip: "Relative Strength Index - overbought/oversold", def: { operator: "<", value: 30 } },
  { type: "MACD", label: "MACD", icon: TrendingUp, color: "#00E396", tip: "Moving Average Convergence Divergence", def: { condition: "bullish_crossover" } },
  { type: "SMA", label: "SMA", icon: TrendingUp, color: "#F59E0B", tip: "Simple Moving Average crossover", def: { operator: "above" } },
  { type: "EMA", label: "EMA", icon: TrendingUp, color: "#8B5CF6", tip: "Exponential Moving Average crossover", def: { operator: "above" } },
  { type: "BB", label: "Bollinger Bands", icon: BarChart3, color: "#EC4899", tip: "Volatility-based price envelope", def: { condition: "below_lower" } },
];

function CondBlock({ c, onRemove, onUpdate }) {
  const b = BLOCKS.find((x) => x.type === c.type);
  return (
    <div className="bg-[#111] border border-[#1A1A1A] rounded-sm p-2.5 relative group" data-testid={`cond-${c.id}`}>
      <button onClick={onRemove} className="absolute top-1 right-1 opacity-0 group-hover:opacity-100 transition-opacity text-[#333] hover:text-[#FF0055]" data-testid={`rm-${c.id}`}><X className="w-3 h-3" /></button>
      <div className="flex items-center gap-1.5 mb-1.5">
        <div className="w-1.5 h-1.5 rounded-full" style={{ backgroundColor: b?.color }} />
        <span className="text-[10px] font-semibold" style={{ color: b?.color }}>{c.type}</span>
      </div>
      {c.type === "RSI" && (
        <div className="flex items-center gap-1.5">
          <Select value={c.operator} onValueChange={(v) => onUpdate({ ...c, operator: v })}>
            <SelectTrigger className="h-6 w-14 bg-[#0A0A0A] border-[#222] text-[10px]"><SelectValue /></SelectTrigger>
            <SelectContent className="bg-[#0A0A0A] border-[#333]"><SelectItem value="<">&lt;</SelectItem><SelectItem value=">">&gt;</SelectItem></SelectContent>
          </Select>
          <Input type="number" className="h-6 w-14 bg-[#0A0A0A] border-[#222] text-[10px] font-mono" value={c.value} onChange={(e) => onUpdate({ ...c, value: Number(e.target.value) })} />
        </div>
      )}
      {c.type === "MACD" && (
        <Select value={c.condition} onValueChange={(v) => onUpdate({ ...c, condition: v })}>
          <SelectTrigger className="h-6 bg-[#0A0A0A] border-[#222] text-[10px]"><SelectValue /></SelectTrigger>
          <SelectContent className="bg-[#0A0A0A] border-[#333]">
            <SelectItem value="bullish_crossover">Bullish Cross</SelectItem><SelectItem value="bearish_crossover">Bearish Cross</SelectItem>
            <SelectItem value="positive">Positive</SelectItem><SelectItem value="negative">Negative</SelectItem>
          </SelectContent>
        </Select>
      )}
      {(c.type === "SMA" || c.type === "EMA") && (
        <Select value={c.operator} onValueChange={(v) => onUpdate({ ...c, operator: v })}>
          <SelectTrigger className="h-6 bg-[#0A0A0A] border-[#222] text-[10px]"><SelectValue /></SelectTrigger>
          <SelectContent className="bg-[#0A0A0A] border-[#333]"><SelectItem value="above">Price Above</SelectItem><SelectItem value="below">Price Below</SelectItem></SelectContent>
        </Select>
      )}
      {c.type === "BB" && (
        <Select value={c.condition} onValueChange={(v) => onUpdate({ ...c, condition: v })}>
          <SelectTrigger className="h-6 bg-[#0A0A0A] border-[#222] text-[10px]"><SelectValue /></SelectTrigger>
          <SelectContent className="bg-[#0A0A0A] border-[#333]"><SelectItem value="below_lower">Below Lower</SelectItem><SelectItem value="above_upper">Above Upper</SelectItem></SelectContent>
        </Select>
      )}
    </div>
  );
}

export default function BotBuilderPage() {
  const [name, setName] = useState("");
  const [symbol, setSymbol] = useState("BTCUSD");
  const [tf, setTf] = useState("1h");
  const [entry, setEntry] = useState([]);
  const [exit, setExit] = useState([]);
  const [entryLogic, setEntryLogic] = useState("AND");
  const [exitLogic, setExitLogic] = useState("OR");
  const [risk, setRisk] = useState({ stop_loss_pct: 2, take_profit_pct: 5, max_position_size_pct: 10, max_capital_per_trade: 5000, max_daily_loss: 1000, max_concurrent_trades: 3 });
  const [strategies, setStrategies] = useState([]);
  const [saving, setSaving] = useState(false);

  useEffect(() => { api.get("/strategies").then((r) => setStrategies(r.data)).catch(() => {}); }, []);

  const add = (sec, block) => {
    const c = { id: Date.now().toString(), type: block.type, ...block.def };
    sec === "entry" ? setEntry((p) => [...p, c]) : setExit((p) => [...p, c]);
  };

  const save = async () => {
    if (!name) { toast.error("Name your strategy"); return; }
    if (!entry.length) { toast.error("Add entry conditions"); return; }
    setSaving(true);
    try {
      await api.post("/strategies", { name, symbol, timeframe: tf, entry: { logic: entryLogic, conditions: entry }, exit: { logic: exitLogic, conditions: exit }, risk });
      toast.success("Strategy saved!");
      api.get("/strategies").then((r) => setStrategies(r.data));
    } catch { toast.error("Save failed"); }
    setSaving(false);
  };

  const load = (s) => {
    setName(s.name); setSymbol(s.symbol); setTf(s.timeframe);
    setEntry(s.entry?.conditions || []); setExit(s.exit?.conditions || []);
    setEntryLogic(s.entry?.logic || "AND"); setExitLogic(s.exit?.logic || "OR");
    if (s.risk) setRisk(s.risk);
    toast.success("Strategy loaded");
  };

  return (
    <TooltipProvider>
      <div className="space-y-3" data-testid="bot-builder-page">
        <div className="flex items-center gap-2 flex-wrap">
          <h1 className="text-2xl font-bold tracking-tight">Strategy Builder</h1>
          <div className="ml-auto flex items-center gap-2">
            <Input className="h-8 w-44 bg-[#111] border-[#222] text-xs rounded-sm" placeholder="Strategy Name" value={name} onChange={(e) => setName(e.target.value)} data-testid="strategy-name-input" />
            <Select value={symbol} onValueChange={setSymbol}>
              <SelectTrigger className="h-8 w-28 bg-[#111] border-[#222] text-xs" data-testid="builder-symbol"><SelectValue /></SelectTrigger>
              <SelectContent className="bg-[#0A0A0A] border-[#333]">{["BTCUSD","ETHUSD","AAPL","TSLA","SPY"].map((s) => <SelectItem key={s} value={s}>{s}</SelectItem>)}</SelectContent>
            </Select>
            <Select value={tf} onValueChange={setTf}>
              <SelectTrigger className="h-8 w-20 bg-[#111] border-[#222] text-xs" data-testid="builder-timeframe"><SelectValue /></SelectTrigger>
              <SelectContent className="bg-[#0A0A0A] border-[#333]">{["5m","15m","1h","1d"].map((t) => <SelectItem key={t} value={t}>{t}</SelectItem>)}</SelectContent>
            </Select>
            <Button onClick={save} disabled={saving} className="h-8 bg-[#00E396] text-[#050505] hover:bg-[#00C27F] rounded-sm text-xs" data-testid="save-strategy-btn">
              <Save className="w-3 h-3 mr-1" />{saving ? "Saving..." : "Save"}
            </Button>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-2">
          <Card className="bg-[#0A0A0A] border-[#222] rounded-sm">
            <CardHeader className="pb-2"><CardTitle className="text-xs uppercase tracking-wider text-[#52525B]">Blocks</CardTitle></CardHeader>
            <CardContent className="p-3 space-y-1">
              {BLOCKS.map((b) => (
                <Tooltip key={b.type}>
                  <TooltipTrigger asChild>
                    <div className="flex items-center gap-1">
                      <Button size="sm" variant="ghost" className="flex-1 justify-start h-7 text-[10px] text-[#A1A1AA] hover:text-white hover:bg-[#111] rounded-sm" onClick={() => add("entry", b)} data-testid={`add-entry-${b.type}`}>
                        <b.icon className="w-3 h-3 mr-1.5" style={{ color: b.color }} />{b.label}
                        <Badge className="ml-auto text-[7px] bg-[#00E396]/15 text-[#00E396] border-0 px-1">+E</Badge>
                      </Button>
                      <Button size="sm" variant="ghost" className="h-7 w-7 p-0 text-[#333] hover:text-[#FF0055] rounded-sm" onClick={() => add("exit", b)} data-testid={`add-exit-${b.type}`}>
                        <Plus className="w-3 h-3" />
                      </Button>
                    </div>
                  </TooltipTrigger>
                  <TooltipContent side="right" className="bg-[#111] border-[#333] text-[10px] max-w-[180px]">{b.tip}</TooltipContent>
                </Tooltip>
              ))}
              <Separator className="bg-[#1A1A1A] my-2" />
              <p className="text-[9px] text-[#333] uppercase tracking-wider">Saved</p>
              <ScrollArea className="h-[100px]">
                {strategies.map((s) => (
                  <Button key={s.id} variant="ghost" size="sm" className="w-full justify-start h-6 text-[10px] text-[#52525B] hover:text-white rounded-sm" onClick={() => load(s)} data-testid={`load-${s.id}`}>{s.name}</Button>
                ))}
              </ScrollArea>
            </CardContent>
          </Card>

          <div className="lg:col-span-2 space-y-2">
            <Card className="bg-[#0A0A0A] border-[#222] rounded-sm">
              <CardHeader className="pb-1 flex-row items-center justify-between">
                <CardTitle className="text-xs text-[#00E396] uppercase tracking-wider">Entry</CardTitle>
                <Select value={entryLogic} onValueChange={setEntryLogic}>
                  <SelectTrigger className="h-5 w-16 bg-[#111] border-[#222] text-[9px]" data-testid="entry-logic"><SelectValue /></SelectTrigger>
                  <SelectContent className="bg-[#0A0A0A] border-[#333]"><SelectItem value="AND">AND</SelectItem><SelectItem value="OR">OR</SelectItem></SelectContent>
                </Select>
              </CardHeader>
              <CardContent className="p-3">
                {!entry.length ? <p className="text-[10px] text-[#222] text-center py-6">Click blocks to add entry conditions</p> : (
                  <div className="space-y-1.5">
                    {entry.map((c, i) => (
                      <div key={c.id}>
                        <CondBlock c={c} onRemove={() => setEntry((p) => p.filter((x) => x.id !== c.id))} onUpdate={(u) => setEntry((p) => p.map((x) => x.id === c.id ? u : x))} />
                        {i < entry.length - 1 && <div className="flex justify-center py-0.5"><Badge className="text-[7px] bg-[#111] text-[#52525B] border-[#222]">{entryLogic}</Badge></div>}
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
            <Card className="bg-[#0A0A0A] border-[#222] rounded-sm">
              <CardHeader className="pb-1 flex-row items-center justify-between">
                <CardTitle className="text-xs text-[#FF0055] uppercase tracking-wider">Exit</CardTitle>
                <Select value={exitLogic} onValueChange={setExitLogic}>
                  <SelectTrigger className="h-5 w-16 bg-[#111] border-[#222] text-[9px]" data-testid="exit-logic"><SelectValue /></SelectTrigger>
                  <SelectContent className="bg-[#0A0A0A] border-[#333]"><SelectItem value="AND">AND</SelectItem><SelectItem value="OR">OR</SelectItem></SelectContent>
                </Select>
              </CardHeader>
              <CardContent className="p-3">
                {!exit.length ? <p className="text-[10px] text-[#222] text-center py-6">Add exit conditions via + button</p> : (
                  <div className="space-y-1.5">
                    {exit.map((c, i) => (
                      <div key={c.id}>
                        <CondBlock c={c} onRemove={() => setExit((p) => p.filter((x) => x.id !== c.id))} onUpdate={(u) => setExit((p) => p.map((x) => x.id === c.id ? u : x))} />
                        {i < exit.length - 1 && <div className="flex justify-center py-0.5"><Badge className="text-[7px] bg-[#111] text-[#52525B] border-[#222]">{exitLogic}</Badge></div>}
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </div>

          <Card className="bg-[#0A0A0A] border-[#222] rounded-sm">
            <CardHeader className="pb-2"><CardTitle className="text-xs flex items-center gap-1 uppercase tracking-wider text-[#F59E0B]"><Shield className="w-3.5 h-3.5" /> Risk</CardTitle></CardHeader>
            <CardContent className="p-3 space-y-3">
              {[{ k: "stop_loss_pct", l: "Stop Loss %", mn: 0.5, mx: 20, s: 0.5 }, { k: "take_profit_pct", l: "Take Profit %", mn: 1, mx: 50, s: 0.5 }, { k: "max_position_size_pct", l: "Max Position %", mn: 1, mx: 100, s: 1 }].map(({ k, l, mn, mx, s }) => (
                <div key={k}>
                  <div className="flex justify-between mb-1"><Label className="text-[9px] text-[#52525B]">{l}</Label><span className="text-[9px] font-mono text-[#A1A1AA]">{risk[k]}%</span></div>
                  <Slider min={mn} max={mx} step={s} value={[risk[k]]} onValueChange={([v]) => setRisk((p) => ({ ...p, [k]: v }))} data-testid={`risk-${k}`} />
                </div>
              ))}
              <Separator className="bg-[#1A1A1A]" />
              {[{ k: "max_capital_per_trade", l: "Max Capital/Trade ($)" }, { k: "max_daily_loss", l: "Max Daily Loss ($)" }, { k: "max_concurrent_trades", l: "Max Concurrent Trades" }].map(({ k, l }) => (
                <div key={k}>
                  <Label className="text-[9px] text-[#52525B]">{l}</Label>
                  <Input type="number" className="h-6 bg-[#111] border-[#222] font-mono text-[10px] mt-0.5 rounded-sm" value={risk[k]} onChange={(e) => setRisk((p) => ({ ...p, [k]: Number(e.target.value) }))} data-testid={`risk-${k}`} />
                </div>
              ))}
            </CardContent>
          </Card>
        </div>
      </div>
    </TooltipProvider>
  );
}
