import { useState, useEffect, useCallback } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Switch } from "@/components/ui/switch";
import { Separator } from "@/components/ui/separator";
import { Slider } from "@/components/ui/slider";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { toast } from "sonner";
import api from "@/lib/api";
import { 
  Shield, Users, DollarSign, Activity, AlertTriangle, 
  Plus, Search, RefreshCw, Edit, Trash2, Power, Eye,
  TrendingUp, TrendingDown, Ban, CheckCircle
} from "lucide-react";

const StatCard = ({ label, value, icon: Icon, color, subtext }) => (
  <Card className="bg-[#0A0A0A] border-[#222] rounded-sm">
    <CardContent className="p-4 flex items-center justify-between">
      <div>
        <p className="text-[10px] text-[#52525B] uppercase">{label}</p>
        <p className="text-2xl font-mono font-bold" style={{ color }}>{value}</p>
        {subtext && <p className="text-[10px] text-[#333]">{subtext}</p>}
      </div>
      <Icon className="w-8 h-8 text-[#222]" />
    </CardContent>
  </Card>
);

export default function AdminTerminalPage() {
  const [dashboard, setDashboard] = useState(null);
  const [users, setUsers] = useState([]);
  const [activity, setActivity] = useState(null);
  const [selectedUser, setSelectedUser] = useState(null);
  const [loading, setLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [activeTab, setActiveTab] = useState("dashboard");
  const [showCreateUser, setShowCreateUser] = useState(false);
  const [showCapitalDialog, setShowCapitalDialog] = useState(false);

  // New user form
  const [newUser, setNewUser] = useState({
    email: "", password: "", name: "", role: "user", initial_capital: 100000
  });

  // Capital allocation
  const [capitalForm, setCapitalForm] = useState({
    user_id: "", amount: 0, reason: ""
  });

  // Risk limits
  const [riskLimits, setRiskLimits] = useState({
    max_daily_loss_pct: 5, max_position_size_pct: 20, max_concurrent_positions: 5, max_leverage: 1
  });

  const fetchDashboard = useCallback(async () => {
    try {
      const { data } = await api.get("/admin/dashboard");
      setDashboard(data);
    } catch (err) {
      if (err.response?.status === 403) {
        toast.error("Admin access required");
      }
    }
  }, []);

  const fetchUsers = useCallback(async () => {
    try {
      const { data } = await api.get("/admin/users", { params: { search: searchQuery, limit: 100 } });
      setUsers(data.users || []);
    } catch (err) { console.error(err); }
  }, [searchQuery]);

  const fetchActivity = useCallback(async () => {
    try {
      const { data } = await api.get("/admin/monitoring/activity", { params: { hours: 24 } });
      setActivity(data);
    } catch (err) { console.error(err); }
  }, []);

  useEffect(() => {
    fetchDashboard();
  }, [fetchDashboard]);

  useEffect(() => {
    if (activeTab === "users") fetchUsers();
    if (activeTab === "monitoring") fetchActivity();
  }, [activeTab, fetchUsers, fetchActivity]);

  const createUser = async () => {
    try {
      await api.post("/admin/users", newUser);
      toast.success("User created!");
      setShowCreateUser(false);
      setNewUser({ email: "", password: "", name: "", role: "user", initial_capital: 100000 });
      fetchUsers();
    } catch (err) {
      toast.error(err.response?.data?.detail || "Failed to create user");
    }
  };

  const updateUser = async (userId, updates) => {
    try {
      await api.patch(`/admin/users/${userId}`, updates);
      toast.success("User updated!");
      fetchUsers();
      if (selectedUser?.id === userId) {
        setSelectedUser({ ...selectedUser, ...updates });
      }
    } catch (err) {
      toast.error(err.response?.data?.detail || "Update failed");
    }
  };

  const toggleTrading = async (userId, enable) => {
    try {
      if (enable) {
        await api.post(`/admin/risk/enable-trading/${userId}`);
      } else {
        await api.post(`/admin/risk/disable-trading/${userId}?reason=Admin disabled`);
      }
      toast.success(`Trading ${enable ? "enabled" : "disabled"}`);
      fetchUsers();
    } catch (err) {
      toast.error(err.response?.data?.detail || "Failed");
    }
  };

  const allocateCapital = async () => {
    try {
      await api.post("/admin/capital/allocate", capitalForm);
      toast.success("Capital allocated!");
      setShowCapitalDialog(false);
      setCapitalForm({ user_id: "", amount: 0, reason: "" });
      fetchUsers();
    } catch (err) {
      toast.error(err.response?.data?.detail || "Failed");
    }
  };

  const updateRiskLimits = async (userId) => {
    try {
      await api.put(`/admin/risk/limits/${userId}`, riskLimits);
      toast.success("Risk limits updated!");
    } catch (err) {
      toast.error(err.response?.data?.detail || "Failed");
    }
  };

  const emergencyStop = async () => {
    if (!confirm("EMERGENCY: Stop ALL trading platform-wide?")) return;
    try {
      const { data } = await api.post("/admin/bulk/stop-all-trading", null, {
        params: { reason: "Emergency stop by admin" }
      });
      toast.success(`Stopped ${data.deployments_stopped} deployments`);
      fetchActivity();
    } catch (err) {
      toast.error(err.response?.data?.detail || "Failed");
    }
  };

  if (!dashboard) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <Shield className="w-12 h-12 mx-auto mb-3 text-[#222]" />
          <p className="text-sm text-[#52525B]">Loading admin panel...</p>
          <p className="text-xs text-[#333] mt-1">Admin access required</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-3" data-testid="admin-terminal-page">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <h1 className="text-2xl font-bold tracking-tight">Admin Terminal</h1>
          <Badge className="bg-[#FF0055]/10 text-[#FF0055] border-[#FF0055]/20">
            <Shield className="w-3 h-3 mr-1" /> Admin
          </Badge>
        </div>
        <Button 
          variant="destructive" 
          size="sm"
          onClick={emergencyStop}
          className="h-8 bg-[#FF0055] hover:bg-[#CC0044]"
        >
          <AlertTriangle className="w-3 h-3 mr-1" /> Emergency Stop
        </Button>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="bg-[#111] border border-[#222] p-0.5 h-8">
          <TabsTrigger value="dashboard" className="text-xs h-7">Dashboard</TabsTrigger>
          <TabsTrigger value="users" className="text-xs h-7">Users</TabsTrigger>
          <TabsTrigger value="monitoring" className="text-xs h-7">Monitoring</TabsTrigger>
          <TabsTrigger value="capital" className="text-xs h-7">Capital</TabsTrigger>
        </TabsList>

        {/* Dashboard Tab */}
        <TabsContent value="dashboard" className="space-y-3">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
            <StatCard label="Total Users" value={dashboard.users?.total} icon={Users} color="#3B82F6" subtext={`${dashboard.users?.active} active`} />
            <StatCard label="New This Week" value={dashboard.users?.new_this_week} icon={TrendingUp} color="#00E396" />
            <StatCard label="Active Deployments" value={dashboard.trading?.active_deployments} icon={Activity} color="#F59E0B" />
            <StatCard label="Total Capital" value={`$${(dashboard.capital?.total_allocated || 0).toLocaleString()}`} icon={DollarSign} color="#8B5CF6" />
          </div>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
            <StatCard label="Strategies" value={dashboard.trading?.strategies} icon={Activity} color="#A1A1AA" />
            <StatCard label="Backtests" value={dashboard.trading?.backtests} icon={Activity} color="#A1A1AA" />
            <StatCard label="ML Models" value={dashboard.trading?.ml_models} icon={Activity} color="#A1A1AA" />
            <StatCard label="Avg Capital/User" value={`$${(dashboard.capital?.average_per_user || 0).toLocaleString()}`} icon={DollarSign} color="#A1A1AA" />
          </div>
        </TabsContent>

        {/* Users Tab */}
        <TabsContent value="users" className="space-y-2">
          <div className="flex items-center gap-2">
            <div className="relative flex-1">
              <Search className="absolute left-2 top-2 w-4 h-4 text-[#52525B]" />
              <Input 
                className="h-8 pl-8 bg-[#111] border-[#222] text-xs"
                placeholder="Search users..."
                value={searchQuery}
                onChange={e => setSearchQuery(e.target.value)}
              />
            </div>
            <Button size="sm" variant="outline" onClick={fetchUsers} className="h-8 border-[#222]">
              <RefreshCw className="w-3 h-3" />
            </Button>
            <Dialog open={showCreateUser} onOpenChange={setShowCreateUser}>
              <DialogTrigger asChild>
                <Button size="sm" className="h-8 bg-[#00E396] text-[#050505]">
                  <Plus className="w-3 h-3 mr-1" /> Add User
                </Button>
              </DialogTrigger>
              <DialogContent className="bg-[#0A0A0A] border-[#333]">
                <DialogHeader>
                  <DialogTitle>Create New User</DialogTitle>
                </DialogHeader>
                <div className="space-y-3">
                  <Input placeholder="Email" value={newUser.email} onChange={e => setNewUser({...newUser, email: e.target.value})} className="bg-[#111] border-[#222]" />
                  <Input placeholder="Name" value={newUser.name} onChange={e => setNewUser({...newUser, name: e.target.value})} className="bg-[#111] border-[#222]" />
                  <Input type="password" placeholder="Password" value={newUser.password} onChange={e => setNewUser({...newUser, password: e.target.value})} className="bg-[#111] border-[#222]" />
                  <Select value={newUser.role} onValueChange={v => setNewUser({...newUser, role: v})}>
                    <SelectTrigger className="bg-[#111] border-[#222]"><SelectValue /></SelectTrigger>
                    <SelectContent className="bg-[#0A0A0A] border-[#333]">
                      <SelectItem value="user">User</SelectItem>
                      <SelectItem value="admin">Admin</SelectItem>
                    </SelectContent>
                  </Select>
                  <Input type="number" placeholder="Initial Capital" value={newUser.initial_capital} onChange={e => setNewUser({...newUser, initial_capital: Number(e.target.value)})} className="bg-[#111] border-[#222]" />
                  <Button onClick={createUser} className="w-full bg-[#00E396] text-[#050505]">Create User</Button>
                </div>
              </DialogContent>
            </Dialog>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-2">
            <Card className="lg:col-span-2 bg-[#0A0A0A] border-[#222] rounded-sm">
              <CardContent className="p-2">
                <ScrollArea className="h-[400px]">
                  <table className="w-full text-xs">
                    <thead>
                      <tr className="text-[#52525B] border-b border-[#111]">
                        <th className="text-left p-2">User</th>
                        <th className="text-left p-2">Role</th>
                        <th className="text-right p-2">Capital</th>
                        <th className="text-center p-2">Status</th>
                        <th className="text-center p-2">Trading</th>
                        <th className="text-center p-2">Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {users.map(u => (
                        <tr key={u.id} className="border-b border-[#0A0A0A] hover:bg-[#111]/50">
                          <td className="p-2">
                            <p className="font-medium">{u.name}</p>
                            <p className="text-[10px] text-[#52525B]">{u.email}</p>
                          </td>
                          <td className="p-2">
                            <Badge className={`text-[8px] ${u.role === 'admin' ? 'bg-[#FF0055]/15 text-[#FF0055]' : 'bg-[#333] text-[#A1A1AA]'}`}>
                              {u.role}
                            </Badge>
                          </td>
                          <td className="p-2 text-right font-mono">${(u.virtual_capital || 0).toLocaleString()}</td>
                          <td className="p-2 text-center">
                            <Badge className={`text-[8px] ${u.is_active !== false ? 'bg-[#00E396]/15 text-[#00E396]' : 'bg-[#FF0055]/15 text-[#FF0055]'}`}>
                              {u.is_active !== false ? 'Active' : 'Inactive'}
                            </Badge>
                          </td>
                          <td className="p-2 text-center">
                            <Switch 
                              checked={u.trading_enabled !== false}
                              onCheckedChange={v => toggleTrading(u.id, v)}
                            />
                          </td>
                          <td className="p-2 text-center">
                            <Button size="sm" variant="ghost" className="h-6 w-6 p-0" onClick={() => setSelectedUser(u)}>
                              <Eye className="w-3 h-3" />
                            </Button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </ScrollArea>
              </CardContent>
            </Card>

            {/* User Details Panel */}
            <Card className="bg-[#0A0A0A] border-[#222] rounded-sm">
              <CardHeader className="pb-2">
                <CardTitle className="text-xs text-[#52525B] uppercase">User Details</CardTitle>
              </CardHeader>
              <CardContent className="p-3">
                {selectedUser ? (
                  <div className="space-y-3">
                    <div>
                      <p className="text-sm font-medium">{selectedUser.name}</p>
                      <p className="text-xs text-[#52525B]">{selectedUser.email}</p>
                    </div>
                    <Separator className="bg-[#222]" />
                    <div className="space-y-2">
                      <div className="flex justify-between text-xs">
                        <span className="text-[#52525B]">Capital</span>
                        <span className="font-mono">${(selectedUser.virtual_capital || 0).toLocaleString()}</span>
                      </div>
                      <div className="flex justify-between text-xs">
                        <span className="text-[#52525B]">Role</span>
                        <Select value={selectedUser.role} onValueChange={v => updateUser(selectedUser.id, { role: v })}>
                          <SelectTrigger className="h-6 w-24 bg-[#111] border-[#222] text-xs">
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent className="bg-[#0A0A0A] border-[#333]">
                            <SelectItem value="user">User</SelectItem>
                            <SelectItem value="admin">Admin</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>
                    </div>
                    <Separator className="bg-[#222]" />
                    <div className="space-y-2">
                      <Label className="text-[9px] text-[#52525B]">Risk Limits</Label>
                      <div className="space-y-1">
                        <div className="flex items-center gap-2">
                          <span className="text-[10px] text-[#52525B] w-28">Max Daily Loss %</span>
                          <Slider 
                            min={1} max={20} step={0.5}
                            value={[selectedUser.risk_limits?.max_daily_loss_pct || 5]}
                            onValueChange={([v]) => setRiskLimits({...riskLimits, max_daily_loss_pct: v})}
                            className="flex-1"
                          />
                          <span className="text-[10px] font-mono w-8">{riskLimits.max_daily_loss_pct}%</span>
                        </div>
                        <div className="flex items-center gap-2">
                          <span className="text-[10px] text-[#52525B] w-28">Max Position %</span>
                          <Slider 
                            min={5} max={50} step={5}
                            value={[riskLimits.max_position_size_pct]}
                            onValueChange={([v]) => setRiskLimits({...riskLimits, max_position_size_pct: v})}
                            className="flex-1"
                          />
                          <span className="text-[10px] font-mono w-8">{riskLimits.max_position_size_pct}%</span>
                        </div>
                      </div>
                      <Button size="sm" onClick={() => updateRiskLimits(selectedUser.id)} className="w-full h-7 bg-[#3B82F6]">
                        Update Limits
                      </Button>
                    </div>
                  </div>
                ) : (
                  <p className="text-xs text-[#52525B] text-center py-8">Select a user to view details</p>
                )}
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Monitoring Tab */}
        <TabsContent value="monitoring" className="space-y-2">
          {activity && (
            <>
              <div className="grid grid-cols-3 gap-2">
                <StatCard label="Backtests (24h)" value={activity.backtests?.count} icon={Activity} color="#3B82F6" />
                <StatCard label="Trades (24h)" value={activity.trades?.count} icon={TrendingUp} color="#00E396" />
                <StatCard label="Total P&L (24h)" value={`$${activity.trades?.total_pnl}`} icon={DollarSign} color={activity.trades?.total_pnl >= 0 ? "#00E396" : "#FF0055"} />
              </div>
              <Card className="bg-[#0A0A0A] border-[#222] rounded-sm">
                <CardHeader className="pb-2">
                  <CardTitle className="text-xs">Recent Trades</CardTitle>
                </CardHeader>
                <CardContent className="p-2">
                  <ScrollArea className="h-[300px]">
                    <table className="w-full text-[10px]">
                      <thead>
                        <tr className="text-[#52525B] border-b border-[#111]">
                          <th className="text-left p-1.5">Type</th>
                          <th className="text-left p-1.5">Symbol</th>
                          <th className="text-right p-1.5">Price</th>
                          <th className="text-right p-1.5">P&L</th>
                          <th className="text-right p-1.5">Time</th>
                        </tr>
                      </thead>
                      <tbody>
                        {activity.trades?.recent?.map((t, i) => (
                          <tr key={i} className="border-b border-[#0A0A0A]">
                            <td className={`p-1.5 ${t.type === 'BUY' ? 'text-[#00E396]' : 'text-[#FF0055]'}`}>{t.type}</td>
                            <td className="p-1.5">{t.symbol}</td>
                            <td className="p-1.5 text-right font-mono">${t.price?.toFixed(2)}</td>
                            <td className={`p-1.5 text-right font-mono ${(t.pnl || 0) >= 0 ? 'text-[#00E396]' : 'text-[#FF0055]'}`}>
                              {t.pnl ? `$${t.pnl.toFixed(2)}` : '-'}
                            </td>
                            <td className="p-1.5 text-right text-[#52525B]">{new Date(t.created_at).toLocaleTimeString()}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </ScrollArea>
                </CardContent>
              </Card>
            </>
          )}
        </TabsContent>

        {/* Capital Tab */}
        <TabsContent value="capital" className="space-y-2">
          <Card className="bg-[#0A0A0A] border-[#222] rounded-sm">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm">Capital Allocation</CardTitle>
            </CardHeader>
            <CardContent className="p-3 space-y-3">
              <div className="grid grid-cols-3 gap-3">
                <div>
                  <Label className="text-[9px] text-[#52525B]">Select User</Label>
                  <Select value={capitalForm.user_id} onValueChange={v => setCapitalForm({...capitalForm, user_id: v})}>
                    <SelectTrigger className="h-8 bg-[#111] border-[#222] text-xs">
                      <SelectValue placeholder="Select user..." />
                    </SelectTrigger>
                    <SelectContent className="bg-[#0A0A0A] border-[#333]">
                      {users.map(u => (
                        <SelectItem key={u.id} value={u.id}>{u.name} ({u.email})</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <Label className="text-[9px] text-[#52525B]">Amount (+ to add, - to deduct)</Label>
                  <Input 
                    type="number"
                    className="h-8 bg-[#111] border-[#222] text-xs font-mono"
                    value={capitalForm.amount}
                    onChange={e => setCapitalForm({...capitalForm, amount: Number(e.target.value)})}
                  />
                </div>
                <div>
                  <Label className="text-[9px] text-[#52525B]">Reason</Label>
                  <Input 
                    className="h-8 bg-[#111] border-[#222] text-xs"
                    value={capitalForm.reason}
                    onChange={e => setCapitalForm({...capitalForm, reason: e.target.value})}
                    placeholder="Bonus allocation..."
                  />
                </div>
              </div>
              <Button 
                onClick={allocateCapital}
                disabled={!capitalForm.user_id || !capitalForm.amount}
                className="bg-[#3B82F6]"
              >
                <DollarSign className="w-4 h-4 mr-2" /> Allocate Capital
              </Button>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
