import { useState, useEffect } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Label } from "@/components/ui/label";
import { toast } from "sonner";
import api from "@/lib/api";
import { Bot, Play, Square, Copy, Trash2, Plus } from "lucide-react";

export default function BotManagementPage() {
  const [bots, setBots] = useState([]);
  const [open, setOpen] = useState(false);
  const [nb, setNb] = useState({ name: "", symbol: "BTCUSD", timeframe: "1h", strategy_id: "" });
  const [strategies, setStrategies] = useState([]);

  useEffect(() => { fetch(); api.get("/strategies").then((r) => setStrategies(r.data)).catch(() => {}); }, []);
  const fetch = () => api.get("/bots").then((r) => setBots(r.data)).catch(() => {});

  const create = async () => {
    if (!nb.name) { toast.error("Name required"); return; }
    try { await api.post("/bots", nb); toast.success("Bot created!"); setOpen(false); setNb({ name: "", symbol: "BTCUSD", timeframe: "1h", strategy_id: "" }); fetch(); }
    catch (err) { toast.error(err.response?.data?.detail || "Failed"); }
  };

  const toggle = async (b) => {
    const a = b.status === "running" ? "stop" : "start";
    await api.post(`/bots/${b.id}/${a}`); toast.success(`Bot ${a}ed`); fetch();
  };

  return (
    <div className="space-y-3" data-testid="bot-management-page">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold tracking-tight">Bot Management</h1>
        <Dialog open={open} onOpenChange={setOpen}>
          <DialogTrigger asChild>
            <Button className="bg-[#00E396] text-[#050505] hover:bg-[#00C27F] rounded-sm h-8 text-xs" data-testid="create-bot-dialog-btn"><Plus className="w-3.5 h-3.5 mr-1" />New Bot</Button>
          </DialogTrigger>
          <DialogContent className="bg-[#0A0A0A] border-[#333] rounded-sm">
            <DialogHeader><DialogTitle className="text-base">Create Bot</DialogTitle></DialogHeader>
            <div className="space-y-3">
              <div><Label className="text-[10px] text-[#52525B]">Name</Label><Input className="h-8 bg-[#111] border-[#222] rounded-sm" value={nb.name} onChange={(e) => setNb((p) => ({ ...p, name: e.target.value }))} placeholder="My Bot" data-testid="new-bot-name" /></div>
              <div><Label className="text-[10px] text-[#52525B]">Symbol</Label>
                <Select value={nb.symbol} onValueChange={(v) => setNb((p) => ({ ...p, symbol: v }))}>
                  <SelectTrigger className="h-8 bg-[#111] border-[#222]" data-testid="new-bot-symbol"><SelectValue /></SelectTrigger>
                  <SelectContent className="bg-[#0A0A0A] border-[#333]">{["BTCUSD","ETHUSD","AAPL","TSLA","SPY"].map((s) => <SelectItem key={s} value={s}>{s}</SelectItem>)}</SelectContent>
                </Select>
              </div>
              <div><Label className="text-[10px] text-[#52525B]">Strategy</Label>
                <Select value={nb.strategy_id} onValueChange={(v) => setNb((p) => ({ ...p, strategy_id: v }))}>
                  <SelectTrigger className="h-8 bg-[#111] border-[#222]" data-testid="new-bot-strategy"><SelectValue placeholder="Optional" /></SelectTrigger>
                  <SelectContent className="bg-[#0A0A0A] border-[#333]">{strategies.map((s) => <SelectItem key={s.id} value={s.id}>{s.name}</SelectItem>)}</SelectContent>
                </Select>
              </div>
              <Button onClick={create} className="w-full h-8 bg-[#00E396] text-[#050505] rounded-sm text-xs" data-testid="confirm-create-bot">Create</Button>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      {!bots.length ? (
        <Card className="bg-[#0A0A0A] border-[#222] rounded-sm">
          <CardContent className="flex flex-col items-center py-16">
            <Bot className="w-12 h-12 text-[#222] mb-3" />
            <p className="text-[#333] text-sm mb-2">No bots yet</p>
            <Button onClick={() => setOpen(true)} variant="ghost" className="text-[#00E396] text-xs">Create your first bot</Button>
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-2">
          {bots.map((b) => (
            <Card key={b.id} className="bg-[#0A0A0A] border-[#222] rounded-sm hover:border-[#333] transition-colors duration-100" data-testid={`bot-card-${b.id}`}>
              <CardContent className="p-3">
                <div className="flex items-start justify-between mb-2">
                  <div><p className="text-sm font-medium">{b.name}</p><p className="text-[10px] text-[#333] font-mono">{b.symbol} / {b.timeframe}</p></div>
                  <Badge className={`text-[8px] ${b.status === "running" ? "bg-[#00E396]/15 text-[#00E396] border-[#00E396]/30" : "bg-[#111] text-[#333] border-[#222]"}`}>{b.status}</Badge>
                </div>
                <div className="grid grid-cols-3 gap-1 mb-2 text-center">
                  <div><p className="text-[8px] text-[#333]">P&L</p><p className={`text-xs font-mono ${(b.pnl || 0) >= 0 ? "text-[#00E396]" : "text-[#FF0055]"}`}>${(b.pnl || 0).toFixed(2)}</p></div>
                  <div><p className="text-[8px] text-[#333]">Win Rate</p><p className="text-xs font-mono">{b.win_rate || 0}%</p></div>
                  <div><p className="text-[8px] text-[#333]">Trades</p><p className="text-xs font-mono">{b.total_trades || 0}</p></div>
                </div>
                <div className="flex gap-1">
                  <Button size="sm" onClick={() => toggle(b)} className={`flex-1 h-6 text-[10px] rounded-sm ${b.status === "running" ? "bg-[#FF0055]/15 text-[#FF0055] hover:bg-[#FF0055]/25" : "bg-[#00E396]/15 text-[#00E396] hover:bg-[#00E396]/25"}`} data-testid={`toggle-${b.id}`}>
                    {b.status === "running" ? <><Square className="w-2.5 h-2.5 mr-1" />Stop</> : <><Play className="w-2.5 h-2.5 mr-1" />Start</>}
                  </Button>
                  <Button size="sm" variant="ghost" className="h-6 w-6 p-0 text-[#333] hover:text-white" onClick={() => { api.post(`/bots/${b.id}/clone`); toast.success("Cloned"); fetch(); }} data-testid={`clone-${b.id}`}><Copy className="w-3 h-3" /></Button>
                  <Button size="sm" variant="ghost" className="h-6 w-6 p-0 text-[#333] hover:text-[#FF0055]" onClick={() => { api.delete(`/bots/${b.id}`); toast.success("Deleted"); fetch(); }} data-testid={`delete-${b.id}`}><Trash2 className="w-3 h-3" /></Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
