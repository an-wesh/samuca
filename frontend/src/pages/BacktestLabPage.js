import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { ScrollArea } from "@/components/ui/scroll-area";
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";
import { toast } from "sonner";
import api from "@/lib/api";
import { Play } from "lucide-react";

export default function BacktestLabPage() {
  const [strategies, setStrategies] = useState([]);
  const [selStrat, setSelStrat] = useState("");
  const [symbol, setSymbol] = useState("BTCUSD");
  const [tf, setTf] = useState("1h");
  const [capital, setCapital] = useState(100000);
  const [comm, setComm] = useState(0.1);
  const [running, setRunning] = useState(false);
  const [result, setResult] = useState(null);
  const [history, setHistory] = useState([]);

  useEffect(() => {
    api.get("/strategies").then((r) => setStrategies(r.data)).catch(() => {});
    api.get("/backtests").then((r) => setHistory(r.data)).catch(() => {});
  }, []);

  const run = async () => {
    if (!selStrat) { toast.error("Select a strategy"); return; }
    setRunning(true);
    try {
      const { data } = await api.post("/backtest/run", { strategy_id: selStrat, symbol, timeframe: tf, initial_capital: capital, commission_pct: comm });
      setResult(data);
      toast.success("Backtest complete!");
    } catch (err) { toast.error(err.response?.data?.detail || "Failed"); }
    setRunning(false);
  };

  const m = result?.metrics;

  return (
    <div className="space-y-3" data-testid="backtest-lab-page">
      <h1 className="text-2xl font-bold tracking-tight">Backtest Lab</h1>
      <Card className="bg-[#0A0A0A] border-[#222] rounded-sm">
        <CardContent className="p-3">
          <div className="grid grid-cols-2 md:grid-cols-6 gap-2 items-end">
            <div className="col-span-2">
              <Label className="text-[9px] text-[#52525B]">Strategy</Label>
              <Select value={selStrat} onValueChange={setSelStrat}>
                <SelectTrigger className="h-8 bg-[#111] border-[#222] text-xs" data-testid="strategy-select"><SelectValue placeholder="Select..." /></SelectTrigger>
                <SelectContent className="bg-[#0A0A0A] border-[#333]">{strategies.map((s) => <SelectItem key={s.id} value={s.id}>{s.name}</SelectItem>)}</SelectContent>
              </Select>
            </div>
            <div>
              <Label className="text-[9px] text-[#52525B]">Symbol</Label>
              <Select value={symbol} onValueChange={setSymbol}>
                <SelectTrigger className="h-8 bg-[#111] border-[#222] text-xs" data-testid="bt-symbol"><SelectValue /></SelectTrigger>
                <SelectContent className="bg-[#0A0A0A] border-[#333]">{["BTCUSD","ETHUSD","AAPL","TSLA","SPY"].map((s) => <SelectItem key={s} value={s}>{s}</SelectItem>)}</SelectContent>
              </Select>
            </div>
            <div>
              <Label className="text-[9px] text-[#52525B]">Capital</Label>
              <Input type="number" className="h-8 bg-[#111] border-[#222] font-mono text-xs" value={capital} onChange={(e) => setCapital(Number(e.target.value))} data-testid="bt-capital" />
            </div>
            <div>
              <Label className="text-[9px] text-[#52525B]">Fee %</Label>
              <Input type="number" step="0.01" className="h-8 bg-[#111] border-[#222] font-mono text-xs" value={comm} onChange={(e) => setComm(Number(e.target.value))} data-testid="bt-comm" />
            </div>
            <Button onClick={run} disabled={running} className="h-8 bg-[#00E396] text-[#050505] hover:bg-[#00C27F] rounded-sm text-xs" data-testid="run-backtest-btn">
              <Play className="w-3 h-3 mr-1" />{running ? "Running..." : "Run"}
            </Button>
          </div>
        </CardContent>
      </Card>

      {result && m && (
        <>
          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-8 gap-1.5">
            {[
              { l: "Return", v: `${m.total_return}%`, c: m.total_return >= 0 ? "#00E396" : "#FF0055" },
              { l: "CAGR", v: `${m.cagr}%`, c: m.cagr >= 0 ? "#00E396" : "#FF0055" },
              { l: "Sharpe", v: m.sharpe_ratio, c: "#3B82F6" },
              { l: "Sortino", v: m.sortino_ratio, c: "#3B82F6" },
              { l: "Max DD", v: `${m.max_drawdown}%`, c: "#FF0055" },
              { l: "Win Rate", v: `${m.win_rate}%`, c: m.win_rate >= 50 ? "#00E396" : "#FF0055" },
              { l: "PF", v: m.profit_factor, c: "#F59E0B" },
              { l: "Trades", v: m.total_trades, c: "#A1A1AA" },
            ].map((x, i) => (
              <Card key={i} className="bg-[#0A0A0A] border-[#222] rounded-sm" data-testid={`metric-${i}`}>
                <CardContent className="p-2.5">
                  <p className="text-[8px] text-[#333] uppercase">{x.l}</p>
                  <p className="text-base font-mono font-semibold" style={{ color: x.c }}>{x.v}</p>
                </CardContent>
              </Card>
            ))}
          </div>

          <Card className="bg-[#0A0A0A] border-[#222] rounded-sm">
            <CardHeader className="pb-1"><CardTitle className="text-xs">Equity Curve</CardTitle></CardHeader>
            <CardContent className="p-2">
              <ResponsiveContainer width="100%" height={280}>
                <AreaChart data={result.equity_curve.filter((_, i) => i % Math.max(1, Math.floor(result.equity_curve.length / 300)) === 0)}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#111" />
                  <XAxis dataKey="timestamp" tick={false} stroke="#222" />
                  <YAxis stroke="#222" tickFormatter={(v) => `$${(v / 1000).toFixed(0)}k`} style={{ fontSize: 9, fontFamily: "JetBrains Mono" }} />
                  <Tooltip contentStyle={{ background: "#0A0A0A", border: "1px solid #222", fontFamily: "JetBrains Mono", fontSize: 11 }} formatter={(v) => [`$${Number(v).toLocaleString()}`, "Equity"]} />
                  <Area type="monotone" dataKey="equity" stroke="#3B82F6" fill="rgba(59,130,246,0.08)" strokeWidth={1.5} />
                </AreaChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          <Card className="bg-[#0A0A0A] border-[#222] rounded-sm">
            <CardHeader className="pb-1"><CardTitle className="text-xs">Trades ({result.trades.length})</CardTitle></CardHeader>
            <CardContent className="p-2">
              <ScrollArea className="h-[220px]">
                <table className="w-full text-[10px] font-mono">
                  <thead><tr className="text-[#333] border-b border-[#111]"><th className="text-left p-1.5">Type</th><th className="text-right p-1.5">Price</th><th className="text-right p-1.5">Qty</th><th className="text-right p-1.5">P&L</th><th className="text-right p-1.5">Reason</th></tr></thead>
                  <tbody>
                    {result.trades.map((t, i) => (
                      <tr key={i} className="border-b border-[#0A0A0A]">
                        <td className={`p-1.5 ${t.type === "BUY" ? "text-[#00E396]" : "text-[#FF0055]"}`}>{t.type}</td>
                        <td className="p-1.5 text-right">${t.price}</td>
                        <td className="p-1.5 text-right">{t.quantity?.toFixed(4)}</td>
                        <td className={`p-1.5 text-right ${(t.pnl || 0) >= 0 ? "text-[#00E396]" : "text-[#FF0055]"}`}>{t.pnl ? `$${t.pnl}` : "-"}</td>
                        <td className="p-1.5 text-right text-[#52525B]">{t.reason || "-"}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </ScrollArea>
            </CardContent>
          </Card>
        </>
      )}

      {!result && history.length > 0 && (
        <Card className="bg-[#0A0A0A] border-[#222] rounded-sm">
          <CardHeader className="pb-1"><CardTitle className="text-xs">Previous Backtests</CardTitle></CardHeader>
          <CardContent className="p-2">
            {history.map((bt) => (
              <div key={bt.id} className="flex items-center justify-between p-2 border-b border-[#111]">
                <div><p className="text-xs">{bt.strategy_name}</p><p className="text-[10px] text-[#333] font-mono">{bt.symbol} / {bt.timeframe}</p></div>
                <div className="text-right">
                  <p className={`text-xs font-mono ${(bt.metrics?.total_return || 0) >= 0 ? "text-[#00E396]" : "text-[#FF0055]"}`}>{bt.metrics?.total_return}%</p>
                  <p className="text-[10px] text-[#333]">{bt.trades_count} trades</p>
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      )}
    </div>
  );
}
