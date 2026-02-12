import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { toast } from "sonner";
import api from "@/lib/api";
import { useAuthStore } from "@/lib/store";
import { Activity, Lock, Mail, User } from "lucide-react";

export default function LoginPage() {
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [name, setName] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const setAuth = useAuthStore((s) => s.setAuth);
  const token = useAuthStore((s) => s.token);

  if (token) { navigate("/dashboard"); return null; }

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const endpoint = isLogin ? "/auth/login" : "/auth/signup";
      const payload = isLogin ? { email, password } : { email, password, name };
      const { data } = await api.post(endpoint, payload);
      setAuth(data.user, data.token);
      toast.success(isLogin ? "Welcome back!" : "Account created!");
      navigate("/dashboard");
    } catch (err) {
      toast.error(err.response?.data?.detail || "Authentication failed");
    } finally {
      setLoading(false);
    }
  };

  const getStrength = () => {
    if (!password) return { w: "0%", c: "#333", l: "" };
    let s = 0;
    if (password.length >= 8) s++;
    if (/[A-Z]/.test(password)) s++;
    if (/[0-9]/.test(password)) s++;
    if (/[^A-Za-z0-9]/.test(password)) s++;
    return [
      { w: "25%", c: "#FF0055", l: "Weak" },
      { w: "50%", c: "#F59E0B", l: "Fair" },
      { w: "75%", c: "#3B82F6", l: "Good" },
      { w: "100%", c: "#00E396", l: "Strong" },
    ][Math.min(s, 3)] || { w: "25%", c: "#FF0055", l: "Weak" };
  };
  const strength = getStrength();

  return (
    <div className="min-h-screen flex" data-testid="login-page">
      <div className="flex-1 flex items-center justify-center p-8 bg-[#050505]">
        <div className="w-full max-w-md">
          <div className="flex items-center gap-3 mb-8">
            <Activity className="w-8 h-8 text-[#00E396]" />
            <h1 className="text-3xl font-bold tracking-tight">TradeForge</h1>
          </div>
          <Card className="bg-[#0A0A0A] border-[#222] rounded-sm">
            <CardHeader className="pb-4">
              <CardTitle className="text-xl">{isLogin ? "Sign In" : "Create Account"}</CardTitle>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleSubmit} className="space-y-4">
                {!isLogin && (
                  <div className="space-y-1.5">
                    <Label className="text-xs text-[#A1A1AA]">Name</Label>
                    <div className="relative">
                      <User className="absolute left-3 top-2.5 w-4 h-4 text-[#52525B]" />
                      <Input data-testid="signup-name-input" className="pl-9 h-10 bg-[#111] border-[#222] focus:border-[#444] rounded-sm" value={name} onChange={(e) => setName(e.target.value)} placeholder="Your name" />
                    </div>
                  </div>
                )}
                <div className="space-y-1.5">
                  <Label className="text-xs text-[#A1A1AA]">Email</Label>
                  <div className="relative">
                    <Mail className="absolute left-3 top-2.5 w-4 h-4 text-[#52525B]" />
                    <Input data-testid="email-input" type="email" className="pl-9 h-10 bg-[#111] border-[#222] focus:border-[#444] rounded-sm" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="you@example.com" required />
                  </div>
                </div>
                <div className="space-y-1.5">
                  <Label className="text-xs text-[#A1A1AA]">Password</Label>
                  <div className="relative">
                    <Lock className="absolute left-3 top-2.5 w-4 h-4 text-[#52525B]" />
                    <Input data-testid="password-input" type="password" className="pl-9 h-10 bg-[#111] border-[#222] focus:border-[#444] rounded-sm" value={password} onChange={(e) => setPassword(e.target.value)} placeholder="Min. 6 characters" required />
                  </div>
                  {!isLogin && password && (
                    <div className="space-y-1 pt-1">
                      <div className="h-1 bg-[#222] rounded-full overflow-hidden">
                        <div className="h-full transition-all duration-300" style={{ width: strength.w, backgroundColor: strength.c }} />
                      </div>
                      <p className="text-[10px]" style={{ color: strength.c }}>{strength.l}</p>
                    </div>
                  )}
                </div>
                <Button data-testid="auth-submit-btn" type="submit" className="w-full h-10 bg-[#00E396] text-[#050505] font-semibold hover:bg-[#00C27F] rounded-sm" disabled={loading}>
                  {loading ? "Processing..." : isLogin ? "Sign In" : "Create Account"}
                </Button>
              </form>
              <p className="text-center text-sm text-[#52525B] mt-4">
                {isLogin ? "Don't have an account?" : "Already have an account?"}
                <button data-testid="toggle-auth-mode" className="text-[#3B82F6] ml-1 hover:underline" onClick={() => setIsLogin(!isLogin)}>
                  {isLogin ? "Sign up" : "Sign in"}
                </button>
              </p>
            </CardContent>
          </Card>
        </div>
      </div>
      <div className="hidden lg:block flex-1 relative">
        <img src="https://images.unsplash.com/photo-1647067517631-aa36cda58a17?crop=entropy&cs=srgb&fm=jpg&q=85" alt="Trading" className="absolute inset-0 w-full h-full object-cover" />
        <div className="absolute inset-0 bg-black/80" />
        <div className="absolute inset-0 flex items-center justify-center p-12">
          <div className="text-center max-w-lg">
            <h2 className="text-4xl font-bold tracking-tight mb-4">AI-Powered Trading Bots</h2>
            <p className="text-lg text-[#A1A1AA]">Build, backtest, and deploy intelligent trading strategies with our no-code platform.</p>
          </div>
        </div>
      </div>
    </div>
  );
}
