import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { ScrollArea } from "@/components/ui/scroll-area";
import { toast } from "sonner";
import api from "@/lib/api";
import { RefreshCw } from "lucide-react";

export default function PaperTradingPage() {
  const [portfolio, setPortfolio] = useState(null);
  const [positions, setPositions] = useState([]);
  const [orders, setOrders] = useState([]);
  const [symbol, setSymbol] = useState("BTCUSD");
  const [side, setSide] = useState("buy");
  const [qty, setQty] = useState("");
  const [prices, setPrices] = useState({});
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchAll();
    const iv = setInterval(fetchAll, 10000);
    return () => clearInterval(iv);
  }, []);

  const fetchAll = async () => {
    try {
      const [p, pos, o, pr] = await Promise.all([api.get("/paper/portfolio"), api.get("/paper/positions"), api.get("/paper/orders"), api.get("/market/latest_prices")]);
      setPortfolio(p.data); setPositions(pos.data); setOrders(o.data); setPrices(pr.data);
    } catch {}
  };

  const placeOrder = async () => {
    if (!qty || Number(qty) <= 0) { toast.error("Enter valid quantity"); return; }
    setLoading(true);
    try {
      await api.post("/paper/order", { symbol, side, quantity: Number(qty), order_type: "market" });
      toast.success(`${side.toUpperCase()} order filled!`);
      setQty(""); fetchAll();
    } catch (err) { toast.error(err.response?.data?.detail || "Order failed"); }
    setLoading(false);
  };

  const reset = async () => { await api.post("/paper/reset"); toast.success("Portfolio reset"); fetchAll(); };
  const cp = prices[symbol]?.price;

  return (
    <div className="space-y-3" data-testid="paper-trading-page">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold tracking-tight">Paper Trading</h1>
        <Button variant="ghost" size="sm" onClick={reset} className="text-[#FF0055] text-[10px] h-7" data-testid="reset-portfolio-btn"><RefreshCw className="w-3 h-3 mr-1" />Reset</Button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-2">
        <Card className="bg-[#0A0A0A] border-[#222] rounded-sm">
          <CardHeader className="pb-1"><CardTitle className="text-xs">Portfolio</CardTitle></CardHeader>
          <CardContent className="p-3 space-y-2">
            <div>
              <p className="text-[9px] text-[#333]">Total Value</p>
              <p className="text-xl font-mono font-bold" data-testid="portfolio-value">${portfolio?.total_value?.toLocaleString() || "100,000"}</p>
            </div>
            <div className="grid grid-cols-2 gap-2">
              <div><p className="text-[8px] text-[#333]">Cash</p><p className="text-xs font-mono">${portfolio?.cash?.toLocaleString() || "100,000"}</p></div>
              <div><p className="text-[8px] text-[#333]">P&L</p>
                <p className={`text-xs font-mono ${(portfolio?.total_pnl || 0) >= 0 ? "text-[#00E396]" : "text-[#FF0055]"}`} data-testid="portfolio-pnl">
                  {(portfolio?.total_pnl || 0) >= 0 ? "+" : ""}${portfolio?.total_pnl?.toFixed(2) || "0.00"}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-[#0A0A0A] border-[#222] rounded-sm">
          <CardHeader className="pb-1"><CardTitle className="text-xs">Place Order</CardTitle></CardHeader>
          <CardContent className="p-3 space-y-2">
            <Select value={symbol} onValueChange={setSymbol}>
              <SelectTrigger className="h-7 bg-[#111] border-[#222] text-[10px] font-mono" data-testid="order-symbol"><SelectValue /></SelectTrigger>
              <SelectContent className="bg-[#0A0A0A] border-[#333]">{["BTCUSD","ETHUSD","AAPL","TSLA","SPY"].map((s) => <SelectItem key={s} value={s}>{s}</SelectItem>)}</SelectContent>
            </Select>
            {cp && <p className="text-[10px] text-[#52525B] font-mono">Price: ${cp.toLocaleString()}</p>}
            <div className="flex gap-1">
              <Button onClick={() => setSide("buy")} size="sm" className={`flex-1 h-7 text-[10px] rounded-sm ${side === "buy" ? "bg-[#00E396] text-[#050505]" : "bg-[#111] text-[#52525B]"}`} data-testid="buy-btn">BUY</Button>
              <Button onClick={() => setSide("sell")} size="sm" className={`flex-1 h-7 text-[10px] rounded-sm ${side === "sell" ? "bg-[#FF0055] text-white" : "bg-[#111] text-[#52525B]"}`} data-testid="sell-btn">SELL</Button>
            </div>
            <Input type="number" placeholder="Quantity" className="h-7 bg-[#111] border-[#222] font-mono text-[10px] rounded-sm" value={qty} onChange={(e) => setQty(e.target.value)} data-testid="order-quantity" />
            <Button onClick={placeOrder} disabled={loading} className={`w-full h-7 text-[10px] rounded-sm ${side === "buy" ? "bg-[#00E396] text-[#050505]" : "bg-[#FF0055] text-white"}`} data-testid="place-order-btn">
              {loading ? "..." : `${side.toUpperCase()} ${symbol}`}
            </Button>
          </CardContent>
        </Card>

        <Card className="lg:col-span-2 bg-[#0A0A0A] border-[#222] rounded-sm">
          <Tabs defaultValue="positions">
            <CardHeader className="pb-0 pt-2 px-3">
              <TabsList className="bg-[#111] h-7"><TabsTrigger value="positions" className="text-[10px] h-6" data-testid="tab-positions">Positions</TabsTrigger><TabsTrigger value="orders" className="text-[10px] h-6" data-testid="tab-orders">Orders</TabsTrigger></TabsList>
            </CardHeader>
            <CardContent className="p-2">
              <TabsContent value="positions" className="mt-0">
                <ScrollArea className="h-[200px]">
                  {!positions.length ? <p className="text-[10px] text-[#222] text-center py-8">No positions</p> : (
                    <table className="w-full text-[10px] font-mono">
                      <thead><tr className="text-[#333] border-b border-[#111]"><th className="text-left p-1.5">Symbol</th><th className="text-right p-1.5">Qty</th><th className="text-right p-1.5">Avg</th><th className="text-right p-1.5">Current</th><th className="text-right p-1.5">P&L</th></tr></thead>
                      <tbody>
                        {positions.map((p) => (
                          <tr key={p.symbol} className="border-b border-[#0A0A0A]" data-testid={`position-${p.symbol}`}>
                            <td className="p-1.5">{p.symbol}</td><td className="p-1.5 text-right">{p.quantity}</td>
                            <td className="p-1.5 text-right">${p.avg_price}</td><td className="p-1.5 text-right">${p.current_price}</td>
                            <td className={`p-1.5 text-right ${p.unrealized_pnl >= 0 ? "text-[#00E396]" : "text-[#FF0055]"}`}>${p.unrealized_pnl}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  )}
                </ScrollArea>
              </TabsContent>
              <TabsContent value="orders" className="mt-0">
                <ScrollArea className="h-[200px]">
                  {!orders.length ? <p className="text-[10px] text-[#222] text-center py-8">No orders</p> : (
                    <table className="w-full text-[10px] font-mono">
                      <thead><tr className="text-[#333] border-b border-[#111]"><th className="text-left p-1.5">Symbol</th><th className="text-left p-1.5">Side</th><th className="text-right p-1.5">Qty</th><th className="text-right p-1.5">Price</th></tr></thead>
                      <tbody>
                        {orders.slice(0, 20).map((o) => (
                          <tr key={o.id} className="border-b border-[#0A0A0A]">
                            <td className="p-1.5">{o.symbol}</td>
                            <td className={`p-1.5 ${o.side === "buy" ? "text-[#00E396]" : "text-[#FF0055]"}`}>{o.side.toUpperCase()}</td>
                            <td className="p-1.5 text-right">{o.quantity}</td><td className="p-1.5 text-right">${o.price}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  )}
                </ScrollArea>
              </TabsContent>
            </CardContent>
          </Tabs>
        </Card>
      </div>
    </div>
  );
}
