import "@/App.css";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { Toaster } from "@/components/ui/sonner";
import { useAuthStore } from "@/lib/store";
import AppLayout from "@/components/layout/AppLayout";
import LoginPage from "@/pages/LoginPage";
import DashboardPage from "@/pages/DashboardPage";
import BotBuilderPage from "@/pages/BotBuilderPage";
import ChartTerminalPage from "@/pages/ChartTerminalPage";
import BacktestLabPage from "@/pages/BacktestLabPage";
import PaperTradingPage from "@/pages/PaperTradingPage";
import BotManagementPage from "@/pages/BotManagementPage";
import DeploymentsPage from "@/pages/DeploymentsPage";

function ProtectedRoute({ children }) {
  const token = useAuthStore((s) => s.token);
  if (!token) return <Navigate to="/login" replace />;
  return <AppLayout>{children}</AppLayout>;
}

function App() {
  return (
    <BrowserRouter>
      <Toaster theme="dark" position="bottom-right" richColors />
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/dashboard" element={<ProtectedRoute><DashboardPage /></ProtectedRoute>} />
        <Route path="/builder" element={<ProtectedRoute><BotBuilderPage /></ProtectedRoute>} />
        <Route path="/chart" element={<ProtectedRoute><ChartTerminalPage /></ProtectedRoute>} />
        <Route path="/backtest" element={<ProtectedRoute><BacktestLabPage /></ProtectedRoute>} />
        <Route path="/paper-trading" element={<ProtectedRoute><PaperTradingPage /></ProtectedRoute>} />
        <Route path="/bots" element={<ProtectedRoute><BotManagementPage /></ProtectedRoute>} />
        <Route path="/deploy" element={<ProtectedRoute><DeploymentsPage /></ProtectedRoute>} />
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
