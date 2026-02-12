import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import api from "@/lib/api";
import { useAuthStore } from "@/lib/store";
import { TrendingUp, TrendingDown, Bot, DollarSign, Percent, ArrowUpRight, ArrowDownRight, Plus } from "lucide-react";

export default function DashboardPage() {
  const [portfolio, setPortfolio] = useState(null);
  const [bots, setBots] = useState([]);
  const [prices, setPrices] = useState({});
  const [orders, setOrders] = useState([]);
  const navigate = useNavigate();

  useEffect(() => {
    fetchData();
    const iv = setInterval(() => api.get("/market/latest_prices").then((r) => setPrices(r.data)).catch(() => {}), 10000);
    return () => clearInterval(iv);
  }, []);

  const fetchData = async () => {
    try {
      const [p, b, pr, o] = await Promise.all([
        api.get("/paper/portfolio"), api.get("/bots"),
        api.get("/market/latest_prices"), api.get("/paper/orders"),
      ]);
      setPortfolio(p.data); setBots(b.data); setPrices(pr.data); setOrders(o.data.slice(0, 10));
    } catch (err) { console.error(err); }
  };

  const kpis = [
    { label: "Portfolio Value", value: portfolio ? `$${portfolio.total_value.toLocaleString()}` : "$100,000", icon: DollarSign, color: "#3B82F6" },
    { label: "Total P&L", value: portfolio ? `${portfolio.total_pnl >= 0 ? "+" : ""}$${portfolio.total_pnl.toLocaleString()}` : "$0", icon: portfolio?.total_pnl >= 0 ? TrendingUp : TrendingDown, color: (portfolio?.total_pnl || 0) >= 0 ? "#00E396" : "#FF0055" },
    { label: "Active Bots", value: bots.filter((b) => b.status === "running").length, icon: Bot, color: "#F59E0B" },
    { label: "Win Rate", value: `${bots.length ? (bots.reduce((s, b) => s + (b.win_rate || 0), 0) / bots.length).toFixed(1) : 0}%`, icon: Percent, color: "#8B5CF6" },
  ];

  return (
    <div className="space-y-4" data-testid="dashboard-page">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold tracking-tight">Dashboard</h1>
        <Button data-testid="create-bot-btn" onClick={() => navigate("/builder")} className="bg-[#00E396] text-[#050505] hover:bg-[#00C27F] rounded-sm h-8 text-xs">
          <Plus className="w-3.5 h-3.5 mr-1" /> New Bot
        </Button>
      </div>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-2">
        {kpis.map((kpi, i) => (
          <Card key={i} className="bg-[#0A0A0A] border-[#222] rounded-sm" data-testid={`kpi-card-${i}`}>
            <CardContent className="p-4">
              <div className="flex items-center justify-between mb-2">
                <span className="text-[10px] text-[#52525B] uppercase tracking-wider">{kpi.label}</span>
                <kpi.icon className="w-4 h-4" style={{ color: kpi.color }} />
              </div>
              <p className="text-2xl font-mono font-semibold" style={{ color: kpi.color }}>{kpi.value}</p>
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-2">
        <Card className="lg:col-span-2 bg-[#0A0A0A] border-[#222] rounded-sm">
          <CardHeader className="pb-2"><CardTitle className="text-sm font-semibold">Market Overview</CardTitle></CardHeader>
          <CardContent className="p-3">
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-2">
              {Object.entries(prices).map(([sym, d]) => (
                <div key={sym} className="bg-[#111] border border-[#1A1A1A] rounded-sm p-3 cursor-pointer hover:border-[#333] transition-colors duration-100" onClick={() => navigate("/chart")} data-testid={`market-card-${sym}`}>
                  <p className="text-[10px] text-[#52525B] mb-1">{sym}</p>
                  <p className="font-mono font-semibold text-sm">${typeof d.price === 'number' ? d.price.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2}) : d.price}</p>
                  <div className={`flex items-center gap-0.5 text-[10px] font-mono mt-0.5 ${d.change_pct >= 0 ? "text-[#00E396]" : "text-[#FF0055]"}`}>
                    {d.change_pct >= 0 ? <ArrowUpRight className="w-3 h-3" /> : <ArrowDownRight className="w-3 h-3" />}
                    {d.change_pct >= 0 ? "+" : ""}{d.change_pct}%
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card className="bg-[#0A0A0A] border-[#222] rounded-sm">
          <CardHeader className="pb-2">
            <div className="flex items-center justify-between">
              <CardTitle className="text-sm font-semibold">Active Bots</CardTitle>
              <Button variant="ghost" size="sm" className="text-[10px] text-[#3B82F6] h-6" onClick={() => navigate("/bots")}>View All</Button>
            </div>
          </CardHeader>
          <CardContent className="p-3">
            <ScrollArea className="h-[200px]">
              {bots.length === 0 ? (
                <div className="text-center py-8 text-[#333]">
                  <Bot className="w-8 h-8 mx-auto mb-2" />
                  <p className="text-xs">No bots yet</p>
                  <Button variant="ghost" size="sm" className="mt-2 text-[#00E396] text-xs" onClick={() => navigate("/builder")}>Create One</Button>
                </div>
              ) : (
                <div className="space-y-1.5">
                  {bots.slice(0, 6).map((bot) => (
                    <div key={bot.id} className="flex items-center justify-between p-2 bg-[#111] rounded-sm border border-[#1A1A1A]" data-testid={`bot-item-${bot.id}`}>
                      <div>
                        <p className="text-xs font-medium">{bot.name}</p>
                        <p className="text-[10px] text-[#52525B] font-mono">{bot.symbol}</p>
                      </div>
                      <div className="text-right">
                        <Badge className={`text-[8px] px-1.5 py-0 ${bot.status === "running" ? "bg-[#00E396]/15 text-[#00E396] border-[#00E396]/30" : "bg-[#222] text-[#52525B] border-[#333]"}`}>
                          {bot.status}
                        </Badge>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </ScrollArea>
          </CardContent>
        </Card>
      </div>

      <Card className="bg-[#0A0A0A] border-[#222] rounded-sm">
        <CardHeader className="pb-2"><CardTitle className="text-sm font-semibold">Recent Trades</CardTitle></CardHeader>
        <CardContent className="p-3">
          {orders.length === 0 ? (
            <p className="text-xs text-[#333] text-center py-4">No trades yet. Start paper trading!</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-xs">
                <thead>
                  <tr className="text-[#52525B] text-[10px] border-b border-[#222]">
                    <th className="text-left p-2">Symbol</th><th className="text-left p-2">Side</th>
                    <th className="text-right p-2">Qty</th><th className="text-right p-2">Price</th><th className="text-right p-2">Time</th>
                  </tr>
                </thead>
                <tbody>
                  {orders.map((o) => (
                    <tr key={o.id} className="border-b border-[#111] hover:bg-[#111]/50">
                      <td className="p-2 font-mono">{o.symbol}</td>
                      <td className={`p-2 font-mono font-medium ${o.side === "buy" ? "text-[#00E396]" : "text-[#FF0055]"}`}>{o.side.toUpperCase()}</td>
                      <td className="p-2 text-right font-mono">{o.quantity}</td>
                      <td className="p-2 text-right font-mono">${o.price?.toLocaleString()}</td>
                      <td className="p-2 text-right text-[#52525B]">{new Date(o.filled_at).toLocaleString()}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
