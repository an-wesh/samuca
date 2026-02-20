import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { 
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  BarChart, Bar, ComposedChart, Line, ReferenceLine
} from "recharts";
import { toast } from "sonner";
import api from "@/lib/api";
import { 
  Play, TrendingUp, TrendingDown, Activity, DollarSign, Target, 
  Clock, ArrowUpRight, ArrowDownRight, BarChart3, Percent, Shield,
  Award, AlertTriangle
} from "lucide-react";

const MetricCard = ({ label, value, subValue, icon: Icon, color, trend }) => (
  <div className="bg-[#111] border border-[#1A1A1A] rounded-sm p-3" data-testid={`metric-${label.toLowerCase().replace(/\s/g, '-')}`}>
    <div className="flex items-center justify-between mb-1">
      <span className="text-[9px] text-[#52525B] uppercase tracking-wider">{label}</span>
      {Icon && <Icon className="w-3.5 h-3.5" style={{ color }} />}
    </div>
    <p className="text-lg font-mono font-semibold" style={{ color }}>{value}</p>
    {subValue && (
      <div className="flex items-center gap-1 mt-0.5">
        {trend === "up" && <ArrowUpRight className="w-3 h-3 text-[#00E396]" />}
        {trend === "down" && <ArrowDownRight className="w-3 h-3 text-[#FF0055]" />}
        <span className="text-[10px] text-[#52525B] font-mono">{subValue}</span>
      </div>
    )}
  </div>
);

export default function BacktestLabPage() {
  const [strategies, setStrategies] = useState([]);
  const [selStrat, setSelStrat] = useState("");
  const [symbol, setSymbol] = useState("RELIANCE.NS");
  const [symbols, setSymbols] = useState([]);
  const [tf, setTf] = useState("1h");
  const [capital, setCapital] = useState(100000);
  const [comm, setComm] = useState(0.1);
  const [slippage, setSlippage] = useState(0.05);
  const [running, setRunning] = useState(false);
  const [result, setResult] = useState(null);
  const [history, setHistory] = useState([]);
  const [activeTab, setActiveTab] = useState("overview");

  useEffect(() => {
    api.get("/strategies").then((r) => setStrategies(r.data)).catch(() => {});
    api.get("/backtests").then((r) => setHistory(r.data)).catch(() => {});
    api.get("/market/symbols").then((r) => {
      const symbolList = r.data.symbols.map(s => typeof s === 'object' ? s.symbol : s);
      setSymbols(symbolList.slice(0, 50)); // Top 50 symbols for backtest
    }).catch(() => {});
  }, []);

  const run = async () => {
    if (!selStrat) { toast.error("Select a strategy"); return; }
    setRunning(true);
    setResult(null);
    try {
      const { data } = await api.post("/backtest/run", { 
        strategy_id: selStrat, 
        symbol, 
        timeframe: tf, 
        initial_capital: capital, 
        commission_pct: comm,
        slippage_pct: slippage
      });
      setResult(data);
      toast.success("Backtest complete!");
      api.get("/backtests").then((r) => setHistory(r.data)).catch(() => {});
    } catch (err) { 
      toast.error(err.response?.data?.detail || "Backtest failed"); 
    }
    setRunning(false);
  };

  const m = result?.metrics;
  
  // Prepare drawdown chart data
  const drawdownData = result?.equity_curve?.filter((_, i) => i % Math.max(1, Math.floor(result.equity_curve.length / 200)) === 0).map(e => ({
    timestamp: e.timestamp,
    drawdown: e.drawdown_pct
  })) || [];

  // Prepare monthly returns data (mock for visualization)
  const monthlyReturns = result?.trades?.filter(t => t.type === "SELL").map(t => ({
    date: t.timestamp.slice(0, 7),
    pnl: t.pnl || 0,
    pnl_pct: t.pnl_pct || 0
  })) || [];

  return (
    <div className="space-y-3" data-testid="backtest-lab-page">
      <div className="flex items-center justify-between flex-wrap gap-2">
        <h1 className="text-2xl font-bold tracking-tight">Backtest Lab</h1>
        <Badge className="bg-[#3B82F6]/10 text-[#3B82F6] border-[#3B82F6]/20 text-[10px]">
          Institutional Grade Engine
        </Badge>
      </div>
      
      {/* Configuration Panel */}
      <Card className="bg-[#0A0A0A] border-[#222] rounded-sm">
        <CardContent className="p-3">
          <div className="grid grid-cols-2 md:grid-cols-7 gap-2 items-end">
            <div className="col-span-2">
              <Label className="text-[9px] text-[#52525B]">Strategy</Label>
              <Select value={selStrat} onValueChange={setSelStrat}>
                <SelectTrigger className="h-8 bg-[#111] border-[#222] text-xs" data-testid="strategy-select">
                  <SelectValue placeholder="Select strategy..." />
                </SelectTrigger>
                <SelectContent className="bg-[#0A0A0A] border-[#333]">
                  {strategies.map((s) => <SelectItem key={s.id} value={s.id}>{s.name}</SelectItem>)}
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label className="text-[9px] text-[#52525B]">Symbol</Label>
              <Select value={symbol} onValueChange={setSymbol}>
                <SelectTrigger className="h-8 bg-[#111] border-[#222] text-xs" data-testid="bt-symbol">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent className="bg-[#0A0A0A] border-[#333] max-h-[250px]">
                  {symbols.map((s) => <SelectItem key={s} value={s}>{s.replace(".NS", "")}</SelectItem>)}
                </SelectContent>
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
            <div>
              <Label className="text-[9px] text-[#52525B]">Slippage %</Label>
              <Input type="number" step="0.01" className="h-8 bg-[#111] border-[#222] font-mono text-xs" value={slippage} onChange={(e) => setSlippage(Number(e.target.value))} data-testid="bt-slippage" />
            </div>
            <Button onClick={run} disabled={running} className="h-8 bg-[#00E396] text-[#050505] hover:bg-[#00C27F] rounded-sm text-xs font-medium" data-testid="run-backtest-btn">
              <Play className="w-3 h-3 mr-1" />{running ? "Running..." : "Run Backtest"}
            </Button>
          </div>
        </CardContent>
      </Card>

      {result && m && (
        <>
          {/* Key Metrics Grid */}
          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-2">
            <MetricCard 
              label="Total Return" 
              value={`${m.total_return_pct >= 0 ? '+' : ''}${m.total_return_pct}%`}
              subValue={`$${m.total_return?.toLocaleString()}`}
              icon={m.total_return_pct >= 0 ? TrendingUp : TrendingDown}
              color={m.total_return_pct >= 0 ? "#00E396" : "#FF0055"}
              trend={m.total_return_pct >= 0 ? "up" : "down"}
            />
            <MetricCard 
              label="CAGR" 
              value={`${m.cagr}%`}
              icon={Activity}
              color="#3B82F6"
            />
            <MetricCard 
              label="Sharpe Ratio" 
              value={m.sharpe_ratio}
              subValue={m.sharpe_ratio >= 1 ? "Good" : m.sharpe_ratio >= 2 ? "Excellent" : "Fair"}
              icon={Award}
              color={m.sharpe_ratio >= 1 ? "#00E396" : "#F59E0B"}
            />
            <MetricCard 
              label="Sortino Ratio" 
              value={m.sortino_ratio}
              icon={Shield}
              color="#8B5CF6"
            />
            <MetricCard 
              label="Max Drawdown" 
              value={`${m.max_drawdown}%`}
              subValue={`${m.max_drawdown_duration}h duration`}
              icon={AlertTriangle}
              color="#FF0055"
            />
            <MetricCard 
              label="Win Rate" 
              value={`${m.win_rate}%`}
              subValue={`${m.winning_trades}W / ${m.losing_trades}L`}
              icon={Target}
              color={m.win_rate >= 50 ? "#00E396" : "#FF0055"}
            />
          </div>

          {/* Detailed Tabs */}
          <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-2">
            <TabsList className="bg-[#111] border border-[#222] p-0.5 h-8">
              <TabsTrigger value="overview" className="text-xs h-7 data-[state=active]:bg-[#1A1A1A]">Overview</TabsTrigger>
              <TabsTrigger value="performance" className="text-xs h-7 data-[state=active]:bg-[#1A1A1A]">Performance</TabsTrigger>
              <TabsTrigger value="risk" className="text-xs h-7 data-[state=active]:bg-[#1A1A1A]">Risk Analysis</TabsTrigger>
              <TabsTrigger value="trades" className="text-xs h-7 data-[state=active]:bg-[#1A1A1A]">Trades</TabsTrigger>
            </TabsList>

            <TabsContent value="overview" className="space-y-2">
              {/* Equity Curve */}
              <Card className="bg-[#0A0A0A] border-[#222] rounded-sm">
                <CardHeader className="pb-1 flex-row items-center justify-between">
                  <CardTitle className="text-xs">Equity Curve</CardTitle>
                  <div className="flex items-center gap-2 text-[10px] font-mono">
                    <span className="text-[#52525B]">Initial:</span>
                    <span className="text-white">${m.initial_capital?.toLocaleString()}</span>
                    <span className="text-[#52525B]">→</span>
                    <span className="text-[#52525B]">Final:</span>
                    <span style={{ color: m.total_return >= 0 ? "#00E396" : "#FF0055" }}>
                      ${m.final_equity?.toLocaleString()}
                    </span>
                  </div>
                </CardHeader>
                <CardContent className="p-2">
                  <ResponsiveContainer width="100%" height={280}>
                    <ComposedChart data={result.equity_curve.filter((_, i) => i % Math.max(1, Math.floor(result.equity_curve.length / 300)) === 0)}>
                      <defs>
                        <linearGradient id="equityGradient" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="5%" stopColor="#3B82F6" stopOpacity={0.2}/>
                          <stop offset="95%" stopColor="#3B82F6" stopOpacity={0}/>
                        </linearGradient>
                      </defs>
                      <CartesianGrid strokeDasharray="3 3" stroke="#111" />
                      <XAxis dataKey="timestamp" tick={false} stroke="#222" />
                      <YAxis stroke="#222" tickFormatter={(v) => `$${(v / 1000).toFixed(0)}k`} style={{ fontSize: 9, fontFamily: "JetBrains Mono" }} />
                      <Tooltip 
                        contentStyle={{ background: "#0A0A0A", border: "1px solid #222", fontFamily: "JetBrains Mono", fontSize: 11 }} 
                        formatter={(v, name) => [
                          name === "equity" ? `$${Number(v).toLocaleString()}` : `${v}%`,
                          name === "equity" ? "Equity" : "Drawdown"
                        ]} 
                      />
                      <ReferenceLine y={m.initial_capital} stroke="#333" strokeDasharray="3 3" />
                      <Area type="monotone" dataKey="equity" stroke="#3B82F6" fill="url(#equityGradient)" strokeWidth={1.5} />
                    </ComposedChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>

              {/* Trade P&L Distribution */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-2">
                <Card className="bg-[#0A0A0A] border-[#222] rounded-sm">
                  <CardHeader className="pb-1"><CardTitle className="text-xs">Trade P&L Distribution</CardTitle></CardHeader>
                  <CardContent className="p-2">
                    <ResponsiveContainer width="100%" height={200}>
                      <BarChart data={result.trades.filter(t => t.type === "SELL").slice(-50)}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#111" />
                        <XAxis dataKey="id" tick={false} stroke="#222" />
                        <YAxis stroke="#222" tickFormatter={(v) => `$${v}`} style={{ fontSize: 9, fontFamily: "JetBrains Mono" }} />
                        <Tooltip 
                          contentStyle={{ background: "#0A0A0A", border: "1px solid #222", fontFamily: "JetBrains Mono", fontSize: 11 }}
                          formatter={(v) => [`$${Number(v).toLocaleString()}`, "P&L"]}
                        />
                        <Bar 
                          dataKey="pnl" 
                          fill="#3B82F6"
                          radius={[2, 2, 0, 0]}
                        />
                      </BarChart>
                    </ResponsiveContainer>
                  </CardContent>
                </Card>

                <Card className="bg-[#0A0A0A] border-[#222] rounded-sm">
                  <CardHeader className="pb-1"><CardTitle className="text-xs">Drawdown Chart</CardTitle></CardHeader>
                  <CardContent className="p-2">
                    <ResponsiveContainer width="100%" height={200}>
                      <AreaChart data={drawdownData}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#111" />
                        <XAxis dataKey="timestamp" tick={false} stroke="#222" />
                        <YAxis stroke="#222" tickFormatter={(v) => `${v}%`} style={{ fontSize: 9, fontFamily: "JetBrains Mono" }} />
                        <Tooltip 
                          contentStyle={{ background: "#0A0A0A", border: "1px solid #222", fontFamily: "JetBrains Mono", fontSize: 11 }}
                          formatter={(v) => [`${v}%`, "Drawdown"]}
                        />
                        <Area type="monotone" dataKey="drawdown" stroke="#FF0055" fill="rgba(255,0,85,0.1)" strokeWidth={1} />
                      </AreaChart>
                    </ResponsiveContainer>
                  </CardContent>
                </Card>
              </div>
            </TabsContent>

            <TabsContent value="performance" className="space-y-2">
              <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
                <MetricCard label="Profit Factor" value={m.profit_factor} icon={BarChart3} color="#F59E0B" />
                <MetricCard label="Expectancy" value={`$${m.expectancy}`} icon={DollarSign} color={m.expectancy > 0 ? "#00E396" : "#FF0055"} />
                <MetricCard label="Payoff Ratio" value={m.payoff_ratio} icon={Percent} color="#8B5CF6" />
                <MetricCard label="Recovery Factor" value={m.recovery_factor} icon={TrendingUp} color="#3B82F6" />
                <MetricCard label="Gross Profit" value={`$${m.gross_profit?.toLocaleString()}`} icon={TrendingUp} color="#00E396" />
                <MetricCard label="Gross Loss" value={`$${m.gross_loss?.toLocaleString()}`} icon={TrendingDown} color="#FF0055" />
                <MetricCard label="Average Win" value={`$${m.avg_win?.toLocaleString()}`} icon={ArrowUpRight} color="#00E396" />
                <MetricCard label="Average Loss" value={`$${m.avg_loss?.toLocaleString()}`} icon={ArrowDownRight} color="#FF0055" />
                <MetricCard label="Largest Win" value={`$${m.largest_win?.toLocaleString()}`} icon={Award} color="#00E396" />
                <MetricCard label="Largest Loss" value={`$${m.largest_loss?.toLocaleString()}`} icon={AlertTriangle} color="#FF0055" />
                <MetricCard label="Avg Trade" value={`$${m.avg_trade?.toLocaleString()}`} icon={Activity} color="#3B82F6" />
                <MetricCard label="Net Profit" value={`$${m.net_profit?.toLocaleString()}`} icon={DollarSign} color={m.net_profit >= 0 ? "#00E396" : "#FF0055"} />
              </div>
            </TabsContent>

            <TabsContent value="risk" className="space-y-2">
              <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
                <MetricCard label="Calmar Ratio" value={m.calmar_ratio} icon={Shield} color="#8B5CF6" />
                <MetricCard label="Max Drawdown" value={`${m.max_drawdown}%`} icon={AlertTriangle} color="#FF0055" />
                <MetricCard label="DD Duration" value={`${m.max_drawdown_duration}h`} icon={Clock} color="#F59E0B" />
                <MetricCard label="Avg Drawdown" value={`${m.avg_drawdown}%`} icon={TrendingDown} color="#FF0055" />
                <MetricCard label="Total Trades" value={m.total_trades} icon={Activity} color="#3B82F6" />
                <MetricCard label="Avg Holding" value={`${m.avg_holding_period}h`} icon={Clock} color="#52525B" />
                <MetricCard label="Max Holding" value={`${m.max_holding_period}h`} icon={Clock} color="#52525B" />
                <MetricCard label="Total Costs" value={`$${m.total_costs?.toLocaleString()}`} subValue={`Comm: $${m.total_commission} | Slip: $${m.total_slippage}`} icon={DollarSign} color="#F59E0B" />
              </div>
            </TabsContent>

            <TabsContent value="trades">
              <Card className="bg-[#0A0A0A] border-[#222] rounded-sm">
                <CardHeader className="pb-1 flex-row items-center justify-between">
                  <CardTitle className="text-xs">Trade History ({result.trades.length} trades)</CardTitle>
                  <div className="flex gap-2">
                    <Badge className="bg-[#00E396]/15 text-[#00E396] border-0 text-[9px]">{m.winning_trades} Wins</Badge>
                    <Badge className="bg-[#FF0055]/15 text-[#FF0055] border-0 text-[9px]">{m.losing_trades} Losses</Badge>
                  </div>
                </CardHeader>
                <CardContent className="p-2">
                  <ScrollArea className="h-[400px]">
                    <table className="w-full text-[10px] font-mono">
                      <thead>
                        <tr className="text-[#52525B] border-b border-[#111] sticky top-0 bg-[#0A0A0A]">
                          <th className="text-left p-1.5">ID</th>
                          <th className="text-left p-1.5">Type</th>
                          <th className="text-right p-1.5">Price</th>
                          <th className="text-right p-1.5">Qty</th>
                          <th className="text-right p-1.5">Value</th>
                          <th className="text-right p-1.5">P&L</th>
                          <th className="text-right p-1.5">P&L %</th>
                          <th className="text-right p-1.5">Hold</th>
                          <th className="text-right p-1.5">Reason</th>
                        </tr>
                      </thead>
                      <tbody>
                        {result.trades.map((t) => (
                          <tr key={t.id} className="border-b border-[#0A0A0A] hover:bg-[#111]/50">
                            <td className="p-1.5 text-[#52525B]">{t.id}</td>
                            <td className={`p-1.5 font-medium ${t.type === "BUY" ? "text-[#00E396]" : "text-[#FF0055]"}`}>{t.type}</td>
                            <td className="p-1.5 text-right">${t.price?.toLocaleString()}</td>
                            <td className="p-1.5 text-right">{t.quantity?.toFixed(4)}</td>
                            <td className="p-1.5 text-right">${t.value?.toLocaleString()}</td>
                            <td className={`p-1.5 text-right ${(t.pnl || 0) >= 0 ? "text-[#00E396]" : "text-[#FF0055]"}`}>
                              {t.pnl != null ? `$${t.pnl?.toLocaleString()}` : "-"}
                            </td>
                            <td className={`p-1.5 text-right ${(t.pnl_pct || 0) >= 0 ? "text-[#00E396]" : "text-[#FF0055]"}`}>
                              {t.pnl_pct != null ? `${t.pnl_pct}%` : "-"}
                            </td>
                            <td className="p-1.5 text-right text-[#52525B]">{t.holding_period ? `${t.holding_period}h` : "-"}</td>
                            <td className="p-1.5 text-right text-[#52525B]">{t.reason || "-"}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </ScrollArea>
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </>
      )}

      {!result && history.length > 0 && (
        <Card className="bg-[#0A0A0A] border-[#222] rounded-sm">
          <CardHeader className="pb-1"><CardTitle className="text-xs">Previous Backtests</CardTitle></CardHeader>
          <CardContent className="p-2">
            <ScrollArea className="h-[300px]">
              {history.map((bt) => (
                <div key={bt.id} className="flex items-center justify-between p-3 border-b border-[#111] hover:bg-[#111]/50 transition-colors">
                  <div>
                    <p className="text-xs font-medium">{bt.strategy_name}</p>
                    <p className="text-[10px] text-[#52525B] font-mono">{bt.symbol} / {bt.timeframe} • ${bt.initial_capital?.toLocaleString()}</p>
                  </div>
                  <div className="text-right">
                    <p className={`text-sm font-mono font-medium ${(bt.metrics?.total_return_pct || 0) >= 0 ? "text-[#00E396]" : "text-[#FF0055]"}`}>
                      {(bt.metrics?.total_return_pct || 0) >= 0 ? '+' : ''}{bt.metrics?.total_return_pct || 0}%
                    </p>
                    <div className="flex items-center gap-2 text-[10px] text-[#52525B]">
                      <span>{bt.trades_count} trades</span>
                      <span>•</span>
                      <span>SR: {bt.metrics?.sharpe_ratio || 0}</span>
                    </div>
                  </div>
                </div>
              ))}
            </ScrollArea>
          </CardContent>
        </Card>
      )}

      {!result && history.length === 0 && (
        <Card className="bg-[#0A0A0A] border-[#222] rounded-sm">
          <CardContent className="p-8 text-center">
            <BarChart3 className="w-12 h-12 mx-auto mb-3 text-[#222]" />
            <p className="text-sm text-[#52525B]">No backtests yet</p>
            <p className="text-xs text-[#333] mt-1">Select a strategy and run your first backtest</p>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
