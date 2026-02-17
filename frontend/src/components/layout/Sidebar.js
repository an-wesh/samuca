import { useNavigate, useLocation } from "react-router-dom";
import { LayoutDashboard, Blocks, LineChart, FlaskConical, Wallet, Bot, Activity, LogOut, Rocket } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import { useAuthStore } from "@/lib/store";

const NAV_ITEMS = [
  { path: "/dashboard", icon: LayoutDashboard, label: "Dashboard" },
  { path: "/builder", icon: Blocks, label: "Bot Builder" },
  { path: "/chart", icon: LineChart, label: "Chart Terminal" },
  { path: "/backtest", icon: FlaskConical, label: "Backtest Lab" },
  { path: "/deploy", icon: Rocket, label: "Live Deployments" },
  { path: "/paper-trading", icon: Wallet, label: "Paper Trading" },
  { path: "/bots", icon: Bot, label: "Bot Management" },
];

export default function Sidebar() {
  const navigate = useNavigate();
  const location = useLocation();
  const logout = useAuthStore((s) => s.logout);
  const user = useAuthStore((s) => s.user);

  return (
    <TooltipProvider delayDuration={0}>
      <div className="w-16 h-screen bg-[#0A0A0A] border-r border-[#222] flex flex-col items-center py-4 shrink-0" data-testid="sidebar">
        <div className="mb-6 cursor-pointer" onClick={() => navigate("/dashboard")}>
          <Activity className="w-7 h-7 text-[#00E396]" />
        </div>
        <nav className="flex-1 flex flex-col gap-1">
          {NAV_ITEMS.map((item) => {
            const active = location.pathname === item.path;
            return (
              <Tooltip key={item.path}>
                <TooltipTrigger asChild>
                  <Button
                    variant="ghost"
                    size="sm"
                    className={`w-10 h-10 p-0 rounded-sm ${active ? "bg-[#111] text-[#00E396]" : "text-[#52525B] hover:text-[#A1A1AA] hover:bg-[#111]"}`}
                    onClick={() => navigate(item.path)}
                    data-testid={`nav-${item.path.slice(1)}`}
                  >
                    <item.icon className="w-5 h-5" />
                  </Button>
                </TooltipTrigger>
                <TooltipContent side="right" className="bg-[#111] border-[#333] text-xs">{item.label}</TooltipContent>
              </Tooltip>
            );
          })}
        </nav>
        <div className="mt-auto flex flex-col items-center gap-2">
          {user && (
            <Tooltip>
              <TooltipTrigger asChild>
                <div className="w-8 h-8 rounded-full bg-[#222] flex items-center justify-center text-xs font-semibold text-[#A1A1AA] cursor-default">
                  {user.name?.[0]?.toUpperCase() || "U"}
                </div>
              </TooltipTrigger>
              <TooltipContent side="right" className="bg-[#111] border-[#333] text-xs">{user.name || user.email}</TooltipContent>
            </Tooltip>
          )}
          <Tooltip>
            <TooltipTrigger asChild>
              <Button variant="ghost" size="sm" onClick={() => { logout(); navigate("/login"); }} className="w-10 h-10 p-0 rounded-sm text-[#52525B] hover:text-[#FF0055]" data-testid="logout-btn">
                <LogOut className="w-5 h-5" />
              </Button>
            </TooltipTrigger>
            <TooltipContent side="right" className="bg-[#111] border-[#333] text-xs">Logout</TooltipContent>
          </Tooltip>
        </div>
      </div>
    </TooltipProvider>
  );
}
