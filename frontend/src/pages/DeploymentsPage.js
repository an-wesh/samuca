import { useState, useEffect, useCallback } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Slider } from "@/components/ui/slider";
import { Switch } from "@/components/ui/switch";
import { Separator } from "@/components/ui/separator";
import { toast } from "sonner";
import api from "@/lib/api";
import { 
  Rocket, Play, Pause, Square, Trash2, RefreshCw, 
  TrendingUp, TrendingDown, DollarSign, Activity,
  Clock, Target, AlertTriangle, CheckCircle, Zap
} from "lucide-react";

const StatusBadge = ({ status }) => {
  const styles = {
    active: "bg-[#00E396]/15 text-[#00E396] border-[#00E396]/30",
    paused: "bg-[#F59E0B]/15 text-[#F59E0B] border-[#F59E0B]/30",
    stopped: "bg-[#52525B]/15 text-[#52525B] border-[#52525B]/30",
    error: "bg-[#FF0055]/15 text-[#FF0055] border-[#FF0055]/30"
  };
  return <Badge className={`text-[9px] ${styles[status] || styles.stopped}`}>{status?.toUpperCase()}</Badge>;
};

export default function DeploymentsPage() {
  const [deployments, setDeployments] = useState([]);
  const [strategies, setStrategies] = useState([]);
  const [selectedDeployment, setSelectedDeployment] = useState(null);
  const [trades, setTrades] = useState([]);
  const [signal, setSignal] = useState(null);
  const [loading, setLoading] = useState(false);
  const [showCreate, setShowCreate] = useState(false);
  
  // Create form state
  const [newDeploy, setNewDeploy] = useState({
    strategy_id: "",
    symbol: "BTCUSD",
    timeframe: "1h",
    initial_capital: 10000,
    max_position_size_pct: 10,
    auto_trade: false
  });

  const fetchDeployments = useCallback(async () => {
    try {
      const { data } = await api.get("/deploy/list");
      setDeployments(data);
    } catch (err) {
      console.error(err);
    }
  }, []);

  const fetchStrategies = useCallback(async () => {
    try {
      const { data } = await api.get("/strategies");
      setStrategies(data);
    } catch (err) {
      console.error(err);
    }
  }, []);

  useEffect(() => {
    fetchDeployments();
    fetchStrategies();
    const interval = setInterval(fetchDeployments, 30000);
    return () => clearInterval(interval);
  }, [fetchDeployments, fetchStrategies]);

  const selectDeployment = async (d) => {
    setSelectedDeployment(d);
    setSignal(null);
    try {
      const { data } = await api.get(`/deploy/${d.id}/trades`);
      setTrades(data);
    } catch (err) {
      console.error(err);
    }
  };

  const createDeployment = async () => {
    if (!newDeploy.strategy_id) {
      toast.error("Select a strategy");
      return;
    }
    setLoading(true);
    try {
      const { data } = await api.post("/deploy/create", newDeploy);
      toast.success("Strategy deployed!");
      setShowCreate(false);
      fetchDeployments();
    } catch (err) {
      toast.error(err.response?.data?.detail || "Deployment failed");
    }
    setLoading(false);
  };

  const controlDeployment = async (id, action) => {
    setLoading(true);
    try {
      await api.post(`/deploy/${id}/${action}`);
      toast.success(`Deployment ${action}ed`);
      fetchDeployments();
      if (selectedDeployment?.id === id) {
        const { data } = await api.get(`/deploy/${id}`);
        setSelectedDeployment(data);
      }
    } catch (err) {
      toast.error(err.response?.data?.detail || `Failed to ${action}`);
    }
    setLoading(false);
  };

  const deleteDeployment = async (id) => {
    if (!confirm("Delete this deployment?")) return;
    try {
      await api.delete(`/deploy/${id}`);
      toast.success("Deployment deleted");
      fetchDeployments();
      if (selectedDeployment?.id === id) {
        setSelectedDeployment(null);
      }
    } catch (err) {
      toast.error(err.response?.data?.detail || "Delete failed");
    }
  };

  const checkSignals = async (id) => {
    setLoading(true);
    try {
      const { data } = await api.get(`/deploy/${id}/signals`);
      setSignal(data);
      toast.success("Signals checked");
    } catch (err) {
      toast.error(err.response?.data?.detail || "Signal check failed");
    }
    setLoading(false);
  };

  const executeTrade = async (id, action) => {
    if (!confirm(`Execute ${action} order?`)) return;
    setLoading(true);
    try {
      const { data } = await api.post(`/deploy/${id}/execute?action=${action}`);
      toast.success(data.message);
      fetchDeployments();
      if (selectedDeployment?.id === id) {
        const { data: updated } = await api.get(`/deploy/${id}`);
        setSelectedDeployment(updated);
        const { data: newTrades } = await api.get(`/deploy/${id}/trades`);
        setTrades(newTrades);
      }
    } catch (err) {
      toast.error(err.response?.data?.detail || "Trade failed");
    }
    setLoading(false);
  };

  const d = selectedDeployment;

  return (
    <div className="space-y-3" data-testid="deployments-page">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold tracking-tight">Live Deployments</h1>
        <div className="flex items-center gap-2">
          <Button 
            variant="outline" 
            size="sm" 
            onClick={fetchDeployments}
            className="h-8 text-xs border-[#222]"
          >
            <RefreshCw className="w-3 h-3 mr-1" /> Refresh
          </Button>
          <Button 
            onClick={() => setShowCreate(true)}
            className="h-8 bg-[#00E396] text-[#050505] hover:bg-[#00C27F] text-xs"
            data-testid="new-deployment-btn"
          >
            <Rocket className="w-3 h-3 mr-1" /> Deploy Strategy
          </Button>
        </div>
      </div>

      {/* Create Deployment Modal */}
      {showCreate && (
        <Card className="bg-[#0A0A0A] border-[#222] rounded-sm">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm flex items-center gap-2">
              <Rocket className="w-4 h-4 text-[#00E396]" />
              Deploy New Strategy
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
              <div className="col-span-2">
                <Label className="text-[9px] text-[#52525B]">Strategy</Label>
                <Select value={newDeploy.strategy_id} onValueChange={(v) => setNewDeploy({...newDeploy, strategy_id: v})}>
                  <SelectTrigger className="h-8 bg-[#111] border-[#222] text-xs" data-testid="deploy-strategy-select">
                    <SelectValue placeholder="Select strategy..." />
                  </SelectTrigger>
                  <SelectContent className="bg-[#0A0A0A] border-[#333]">
                    {strategies.map(s => <SelectItem key={s.id} value={s.id}>{s.name}</SelectItem>)}
                  </SelectContent>
                </Select>
              </div>
              <div>
                <Label className="text-[9px] text-[#52525B]">Symbol</Label>
                <Select value={newDeploy.symbol} onValueChange={(v) => setNewDeploy({...newDeploy, symbol: v})}>
                  <SelectTrigger className="h-8 bg-[#111] border-[#222] text-xs">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent className="bg-[#0A0A0A] border-[#333]">
                    {["BTCUSD","ETHUSD","AAPL","TSLA","SPY"].map(s => <SelectItem key={s} value={s}>{s}</SelectItem>)}
                  </SelectContent>
                </Select>
              </div>
              <div>
                <Label className="text-[9px] text-[#52525B]">Timeframe</Label>
                <Select value={newDeploy.timeframe} onValueChange={(v) => setNewDeploy({...newDeploy, timeframe: v})}>
                  <SelectTrigger className="h-8 bg-[#111] border-[#222] text-xs">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent className="bg-[#0A0A0A] border-[#333]">
                    {["5m","15m","1h","1d"].map(t => <SelectItem key={t} value={t}>{t}</SelectItem>)}
                  </SelectContent>
                </Select>
              </div>
            </div>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
              <div>
                <Label className="text-[9px] text-[#52525B]">Initial Capital ($)</Label>
                <Input 
                  type="number" 
                  className="h-8 bg-[#111] border-[#222] text-xs font-mono" 
                  value={newDeploy.initial_capital}
                  onChange={(e) => setNewDeploy({...newDeploy, initial_capital: Number(e.target.value)})}
                />
              </div>
              <div>
                <Label className="text-[9px] text-[#52525B]">Max Position %</Label>
                <Input 
                  type="number" 
                  className="h-8 bg-[#111] border-[#222] text-xs font-mono" 
                  value={newDeploy.max_position_size_pct}
                  onChange={(e) => setNewDeploy({...newDeploy, max_position_size_pct: Number(e.target.value)})}
                />
              </div>
              <div className="flex items-center gap-2 pt-4">
                <Switch 
                  checked={newDeploy.auto_trade}
                  onCheckedChange={(v) => setNewDeploy({...newDeploy, auto_trade: v})}
                />
                <Label className="text-xs text-[#A1A1AA]">Auto Trade</Label>
              </div>
            </div>
            <div className="flex justify-end gap-2 pt-2">
              <Button variant="outline" size="sm" onClick={() => setShowCreate(false)} className="h-8 text-xs border-[#222]">
                Cancel
              </Button>
              <Button onClick={createDeployment} disabled={loading} className="h-8 bg-[#00E396] text-[#050505] hover:bg-[#00C27F] text-xs">
                <Rocket className="w-3 h-3 mr-1" /> {loading ? "Deploying..." : "Deploy"}
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-2">
        {/* Deployments List */}
        <Card className="bg-[#0A0A0A] border-[#222] rounded-sm">
          <CardHeader className="pb-2">
            <CardTitle className="text-xs text-[#52525B] uppercase tracking-wider">Active Deployments</CardTitle>
          </CardHeader>
          <CardContent className="p-2">
            <ScrollArea className="h-[500px]">
              {deployments.length === 0 ? (
                <div className="text-center py-8">
                  <Rocket className="w-8 h-8 mx-auto mb-2 text-[#222]" />
                  <p className="text-xs text-[#52525B]">No deployments yet</p>
                  <Button 
                    variant="ghost" 
                    size="sm" 
                    onClick={() => setShowCreate(true)}
                    className="mt-2 text-[#00E396] text-xs"
                  >
                    Deploy your first strategy
                  </Button>
                </div>
              ) : (
                <div className="space-y-1.5">
                  {deployments.map(dep => (
                    <div 
                      key={dep.id}
                      onClick={() => selectDeployment(dep)}
                      className={`p-3 rounded-sm border cursor-pointer transition-colors ${
                        selectedDeployment?.id === dep.id 
                          ? "bg-[#111] border-[#333]" 
                          : "bg-[#0A0A0A] border-[#1A1A1A] hover:border-[#222]"
                      }`}
                      data-testid={`deployment-${dep.id}`}
                    >
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-xs font-medium">{dep.strategy_name}</span>
                        <StatusBadge status={dep.status} />
                      </div>
                      <div className="flex items-center justify-between text-[10px] text-[#52525B]">
                        <span className="font-mono">{dep.symbol} / {dep.timeframe}</span>
                        <span className={`font-mono ${dep.total_pnl >= 0 ? "text-[#00E396]" : "text-[#FF0055]"}`}>
                          {dep.total_pnl >= 0 ? "+" : ""}${dep.total_pnl?.toFixed(2) || 0}
                        </span>
                      </div>
                      {dep.position && (
                        <div className="mt-1.5 px-2 py-1 bg-[#00E396]/10 rounded-sm">
                          <span className="text-[9px] text-[#00E396]">POSITION OPEN</span>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </ScrollArea>
          </CardContent>
        </Card>

        {/* Deployment Details */}
        <div className="lg:col-span-2 space-y-2">
          {d ? (
            <>
              {/* Controls & Status */}
              <Card className="bg-[#0A0A0A] border-[#222] rounded-sm">
                <CardContent className="p-3">
                  <div className="flex items-center justify-between mb-3">
                    <div>
                      <h2 className="text-lg font-semibold">{d.strategy_name}</h2>
                      <p className="text-xs text-[#52525B] font-mono">{d.symbol} • {d.timeframe} • {d.mode?.toUpperCase()}</p>
                    </div>
                    <StatusBadge status={d.status} />
                  </div>
                  
                  <div className="flex flex-wrap gap-2">
                    {d.status === "active" && (
                      <Button size="sm" variant="outline" onClick={() => controlDeployment(d.id, "pause")} className="h-7 text-[10px] border-[#222]">
                        <Pause className="w-3 h-3 mr-1" /> Pause
                      </Button>
                    )}
                    {d.status === "paused" && (
                      <Button size="sm" onClick={() => controlDeployment(d.id, "start")} className="h-7 text-[10px] bg-[#00E396] text-[#050505]">
                        <Play className="w-3 h-3 mr-1" /> Resume
                      </Button>
                    )}
                    {d.status !== "stopped" && (
                      <Button size="sm" variant="outline" onClick={() => controlDeployment(d.id, "stop")} className="h-7 text-[10px] border-[#FF0055] text-[#FF0055]">
                        <Square className="w-3 h-3 mr-1" /> Stop
                      </Button>
                    )}
                    {(d.status === "stopped" || d.status === "error") && (
                      <Button size="sm" variant="outline" onClick={() => deleteDeployment(d.id)} className="h-7 text-[10px] border-[#333]">
                        <Trash2 className="w-3 h-3 mr-1" /> Delete
                      </Button>
                    )}
                    <div className="ml-auto flex gap-2">
                      <Button size="sm" variant="outline" onClick={() => checkSignals(d.id)} disabled={d.status !== "active"} className="h-7 text-[10px] border-[#222]">
                        <Zap className="w-3 h-3 mr-1" /> Check Signals
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Stats */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
                <Card className="bg-[#0A0A0A] border-[#222] rounded-sm">
                  <CardContent className="p-3">
                    <p className="text-[9px] text-[#52525B] uppercase">Capital</p>
                    <p className="text-lg font-mono font-semibold text-[#3B82F6]">${d.current_capital?.toLocaleString()}</p>
                    <p className="text-[10px] text-[#52525B]">of ${d.initial_capital?.toLocaleString()}</p>
                  </CardContent>
                </Card>
                <Card className="bg-[#0A0A0A] border-[#222] rounded-sm">
                  <CardContent className="p-3">
                    <p className="text-[9px] text-[#52525B] uppercase">Total P&L</p>
                    <p className={`text-lg font-mono font-semibold ${d.total_pnl >= 0 ? "text-[#00E396]" : "text-[#FF0055]"}`}>
                      {d.total_pnl >= 0 ? "+" : ""}${d.total_pnl?.toFixed(2) || 0}
                    </p>
                  </CardContent>
                </Card>
                <Card className="bg-[#0A0A0A] border-[#222] rounded-sm">
                  <CardContent className="p-3">
                    <p className="text-[9px] text-[#52525B] uppercase">Win Rate</p>
                    <p className={`text-lg font-mono font-semibold ${d.win_rate >= 50 ? "text-[#00E396]" : "text-[#FF0055]"}`}>
                      {d.win_rate?.toFixed(1) || 0}%
                    </p>
                  </CardContent>
                </Card>
                <Card className="bg-[#0A0A0A] border-[#222] rounded-sm">
                  <CardContent className="p-3">
                    <p className="text-[9px] text-[#52525B] uppercase">Trades</p>
                    <p className="text-lg font-mono font-semibold text-[#A1A1AA]">{d.total_trades || 0}</p>
                  </CardContent>
                </Card>
              </div>

              {/* Position & Signal */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                {/* Current Position */}
                <Card className="bg-[#0A0A0A] border-[#222] rounded-sm">
                  <CardHeader className="pb-1">
                    <CardTitle className="text-xs">Current Position</CardTitle>
                  </CardHeader>
                  <CardContent className="p-3">
                    {d.position ? (
                      <div className="space-y-2">
                        <div className="flex justify-between text-xs">
                          <span className="text-[#52525B]">Entry Price</span>
                          <span className="font-mono">${d.position.entry_price?.toFixed(2)}</span>
                        </div>
                        <div className="flex justify-between text-xs">
                          <span className="text-[#52525B]">Quantity</span>
                          <span className="font-mono">{d.position.quantity?.toFixed(4)}</span>
                        </div>
                        <div className="flex justify-between text-xs">
                          <span className="text-[#52525B]">Value</span>
                          <span className="font-mono">${d.position.value?.toFixed(2)}</span>
                        </div>
                        <Separator className="bg-[#222]" />
                        <Button 
                          onClick={() => executeTrade(d.id, "SELL")} 
                          disabled={loading || d.status !== "active"}
                          className="w-full h-8 bg-[#FF0055] text-white hover:bg-[#CC0044] text-xs"
                        >
                          Close Position
                        </Button>
                      </div>
                    ) : (
                      <div className="text-center py-4">
                        <p className="text-xs text-[#52525B]">No open position</p>
                        <Button 
                          onClick={() => executeTrade(d.id, "BUY")} 
                          disabled={loading || d.status !== "active"}
                          className="mt-2 h-8 bg-[#00E396] text-[#050505] hover:bg-[#00C27F] text-xs"
                        >
                          Open Position
                        </Button>
                      </div>
                    )}
                  </CardContent>
                </Card>

                {/* Signal Status */}
                <Card className="bg-[#0A0A0A] border-[#222] rounded-sm">
                  <CardHeader className="pb-1">
                    <CardTitle className="text-xs">Latest Signal</CardTitle>
                  </CardHeader>
                  <CardContent className="p-3">
                    {signal ? (
                      <div className="space-y-2">
                        <div className="flex justify-between text-xs">
                          <span className="text-[#52525B]">Price</span>
                          <span className="font-mono">${signal.current_price?.toFixed(2)}</span>
                        </div>
                        <div className="flex justify-between text-xs">
                          <span className="text-[#52525B]">Entry Signal</span>
                          <Badge className={signal.entry_signal ? "bg-[#00E396]/15 text-[#00E396]" : "bg-[#333] text-[#52525B]"}>
                            {signal.entry_signal ? "YES" : "NO"}
                          </Badge>
                        </div>
                        <div className="flex justify-between text-xs">
                          <span className="text-[#52525B]">Exit Signal</span>
                          <Badge className={signal.exit_signal ? "bg-[#FF0055]/15 text-[#FF0055]" : "bg-[#333] text-[#52525B]"}>
                            {signal.exit_signal ? "YES" : "NO"}
                          </Badge>
                        </div>
                        {signal.recommended_action && (
                          <div className="mt-2 p-2 bg-[#111] rounded-sm">
                            <p className="text-[10px] text-[#52525B] mb-1">Recommended</p>
                            <p className={`text-sm font-semibold ${signal.recommended_action.includes("BUY") ? "text-[#00E396]" : "text-[#FF0055]"}`}>
                              {signal.recommended_action}
                            </p>
                          </div>
                        )}
                        {signal.position_pnl_pct !== undefined && (
                          <div className="flex justify-between text-xs">
                            <span className="text-[#52525B]">Position P&L</span>
                            <span className={`font-mono ${signal.position_pnl_pct >= 0 ? "text-[#00E396]" : "text-[#FF0055]"}`}>
                              {signal.position_pnl_pct >= 0 ? "+" : ""}{signal.position_pnl_pct}%
                            </span>
                          </div>
                        )}
                      </div>
                    ) : (
                      <div className="text-center py-4">
                        <Zap className="w-6 h-6 mx-auto mb-2 text-[#222]" />
                        <p className="text-xs text-[#52525B]">Click "Check Signals" to analyze</p>
                      </div>
                    )}
                  </CardContent>
                </Card>
              </div>

              {/* Trade History */}
              <Card className="bg-[#0A0A0A] border-[#222] rounded-sm">
                <CardHeader className="pb-1">
                  <CardTitle className="text-xs">Trade History</CardTitle>
                </CardHeader>
                <CardContent className="p-2">
                  <ScrollArea className="h-[200px]">
                    {trades.length === 0 ? (
                      <p className="text-xs text-[#52525B] text-center py-4">No trades yet</p>
                    ) : (
                      <table className="w-full text-[10px] font-mono">
                        <thead>
                          <tr className="text-[#52525B] border-b border-[#111]">
                            <th className="text-left p-1.5">Type</th>
                            <th className="text-right p-1.5">Price</th>
                            <th className="text-right p-1.5">Qty</th>
                            <th className="text-right p-1.5">P&L</th>
                            <th className="text-right p-1.5">Reason</th>
                          </tr>
                        </thead>
                        <tbody>
                          {trades.map(t => (
                            <tr key={t.id} className="border-b border-[#0A0A0A]">
                              <td className={`p-1.5 ${t.type === "BUY" ? "text-[#00E396]" : "text-[#FF0055]"}`}>{t.type}</td>
                              <td className="p-1.5 text-right">${t.price?.toFixed(2)}</td>
                              <td className="p-1.5 text-right">{t.quantity?.toFixed(4)}</td>
                              <td className={`p-1.5 text-right ${(t.pnl || 0) >= 0 ? "text-[#00E396]" : "text-[#FF0055]"}`}>
                                {t.pnl ? `$${t.pnl.toFixed(2)}` : "-"}
                              </td>
                              <td className="p-1.5 text-right text-[#52525B]">{t.reason || "-"}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    )}
                  </ScrollArea>
                </CardContent>
              </Card>
            </>
          ) : (
            <Card className="bg-[#0A0A0A] border-[#222] rounded-sm h-[400px] flex items-center justify-center">
              <div className="text-center">
                <Activity className="w-12 h-12 mx-auto mb-3 text-[#222]" />
                <p className="text-sm text-[#52525B]">Select a deployment to view details</p>
              </div>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}
