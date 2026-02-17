import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { Slider } from "@/components/ui/slider";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion";
import { toast } from "sonner";
import api from "@/lib/api";
import { 
  Plus, Save, X, TrendingUp, Activity, BarChart3, Shield, 
  Zap, Layers, ChevronRight, Play, Rocket, Sparkles
} from "lucide-react";

// All Zerodha Kite Indicators organized by category
const INDICATOR_CATEGORIES = {
  trend: {
    label: "Trend",
    icon: TrendingUp,
    color: "#00E396",
    indicators: [
      { type: "SMA", label: "SMA", tip: "Simple Moving Average - trend identification", params: { period: 20 }, conditions: [
        { value: "above", label: "Price Above SMA" },
        { value: "below", label: "Price Below SMA" },
        { value: "crossover_up", label: "Price Crosses Above" },
        { value: "crossover_down", label: "Price Crosses Below" }
      ]},
      { type: "EMA", label: "EMA", tip: "Exponential Moving Average - faster response to price", params: { period: 20 }, conditions: [
        { value: "above", label: "Price Above EMA" },
        { value: "below", label: "Price Below EMA" },
        { value: "crossover_up", label: "Price Crosses Above" },
        { value: "crossover_down", label: "Price Crosses Below" }
      ]},
      { type: "SUPERTREND", label: "SuperTrend", tip: "Trend following indicator using ATR", params: { period: 10, multiplier: 3 }, conditions: [
        { value: "uptrend", label: "Uptrend (Green)" },
        { value: "downtrend", label: "Downtrend (Red)" },
        { value: "crossover_up", label: "Flip to Uptrend" },
        { value: "crossover_down", label: "Flip to Downtrend" }
      ]},
      { type: "ICHIMOKU", label: "Ichimoku", tip: "Ichimoku Cloud - comprehensive trend system", params: {}, conditions: [
        { value: "above_cloud", label: "Price Above Cloud" },
        { value: "below_cloud", label: "Price Below Cloud" },
        { value: "tk_cross_up", label: "TK Bullish Cross" },
        { value: "tk_cross_down", label: "TK Bearish Cross" }
      ]},
      { type: "PARABOLIC_SAR", label: "Parabolic SAR", tip: "Stop and Reverse - trend direction", params: {}, conditions: [
        { value: "bullish", label: "SAR Below Price (Bullish)" },
        { value: "bearish", label: "SAR Above Price (Bearish)" },
        { value: "reversal_up", label: "SAR Reversal to Bullish" },
        { value: "reversal_down", label: "SAR Reversal to Bearish" }
      ]},
      { type: "ALLIGATOR", label: "Alligator", tip: "Williams Alligator - trend sleeping/waking", params: {}, conditions: [
        { value: "bullish", label: "Lips > Teeth > Jaw (Bullish)" },
        { value: "bearish", label: "Jaw > Teeth > Lips (Bearish)" },
        { value: "sleeping", label: "Lines Intertwined (Sleeping)" }
      ]},
    ]
  },
  momentum: {
    label: "Momentum",
    icon: Activity,
    color: "#3B82F6",
    indicators: [
      { type: "RSI", label: "RSI", tip: "Relative Strength Index - overbought/oversold", params: { period: 14, value: 30 }, conditions: [
        { value: "oversold", label: "Oversold (< 30)" },
        { value: "overbought", label: "Overbought (> 70)" },
        { value: "custom_below", label: "Below Custom Value" },
        { value: "custom_above", label: "Above Custom Value" }
      ]},
      { type: "MACD", label: "MACD", tip: "Moving Average Convergence Divergence", params: { fast: 12, slow: 26, signal: 9 }, conditions: [
        { value: "bullish_crossover", label: "Bullish Crossover" },
        { value: "bearish_crossover", label: "Bearish Crossover" },
        { value: "positive", label: "Histogram Positive" },
        { value: "negative", label: "Histogram Negative" },
        { value: "divergence_bull", label: "Bullish Divergence" },
        { value: "divergence_bear", label: "Bearish Divergence" }
      ]},
      { type: "STOCHASTIC", label: "Stochastic", tip: "Stochastic Oscillator - momentum comparison", params: { k_period: 14, d_period: 3 }, conditions: [
        { value: "oversold", label: "Oversold (< 20)" },
        { value: "overbought", label: "Overbought (> 80)" },
        { value: "bullish_crossover", label: "%K Crosses Above %D" },
        { value: "bearish_crossover", label: "%K Crosses Below %D" }
      ]},
      { type: "CCI", label: "CCI", tip: "Commodity Channel Index - cyclical trends", params: { period: 20 }, conditions: [
        { value: "oversold", label: "Oversold (< -100)" },
        { value: "overbought", label: "Overbought (> 100)" },
        { value: "zero_cross_up", label: "Crosses Above Zero" },
        { value: "zero_cross_down", label: "Crosses Below Zero" }
      ]},
      { type: "WILLIAMS_R", label: "Williams %R", tip: "Williams Percent Range", params: { period: 14 }, conditions: [
        { value: "oversold", label: "Oversold (< -80)" },
        { value: "overbought", label: "Overbought (> -20)" }
      ]},
      { type: "MFI", label: "MFI", tip: "Money Flow Index - volume-weighted RSI", params: { period: 14 }, conditions: [
        { value: "oversold", label: "Oversold (< 20)" },
        { value: "overbought", label: "Overbought (> 80)" }
      ]},
      { type: "AROON", label: "Aroon", tip: "Aroon Indicator - trend strength/direction", params: { period: 25 }, conditions: [
        { value: "bullish", label: "Aroon Up > Aroon Down" },
        { value: "bearish", label: "Aroon Down > Aroon Up" },
        { value: "strong_up", label: "Strong Uptrend (Up > 70)" },
        { value: "strong_down", label: "Strong Downtrend (Down > 70)" }
      ]},
    ]
  },
  volatility: {
    label: "Volatility",
    icon: BarChart3,
    color: "#F59E0B",
    indicators: [
      { type: "BB", label: "Bollinger Bands", tip: "Volatility-based price envelope", params: { period: 20, std_dev: 2 }, conditions: [
        { value: "below_lower", label: "Price Below Lower Band" },
        { value: "above_upper", label: "Price Above Upper Band" },
        { value: "squeeze", label: "Band Squeeze" },
        { value: "expansion", label: "Band Expansion" }
      ]},
      { type: "KELTNER", label: "Keltner Channels", tip: "ATR-based price channels", params: { period: 20, multiplier: 2 }, conditions: [
        { value: "below_lower", label: "Price Below Lower" },
        { value: "above_upper", label: "Price Above Upper" }
      ]},
      { type: "DONCHIAN", label: "Donchian Channels", tip: "High/Low price channels", params: { period: 20 }, conditions: [
        { value: "breakout_up", label: "Breakout Above Upper" },
        { value: "breakout_down", label: "Breakout Below Lower" }
      ]},
      { type: "ATR", label: "ATR", tip: "Average True Range - volatility measure", params: { period: 14 }, conditions: [
        { value: "expanding", label: "ATR Increasing" },
        { value: "contracting", label: "ATR Decreasing" },
        { value: "above_threshold", label: "Above Threshold" }
      ]},
    ]
  },
  volume: {
    label: "Volume",
    icon: Layers,
    color: "#8B5CF6",
    indicators: [
      { type: "VWAP", label: "VWAP", tip: "Volume Weighted Average Price", params: {}, conditions: [
        { value: "above", label: "Price Above VWAP" },
        { value: "below", label: "Price Below VWAP" },
        { value: "crossover_up", label: "Cross Above VWAP" },
        { value: "crossover_down", label: "Cross Below VWAP" }
      ]},
      { type: "OBV", label: "OBV", tip: "On Balance Volume - volume trend", params: {}, conditions: [
        { value: "rising", label: "OBV Rising" },
        { value: "falling", label: "OBV Falling" },
        { value: "divergence_bull", label: "Bullish Divergence" },
        { value: "divergence_bear", label: "Bearish Divergence" }
      ]},
      { type: "CMF", label: "Chaikin MF", tip: "Chaikin Money Flow", params: { period: 20 }, conditions: [
        { value: "positive", label: "CMF Positive (Buying)" },
        { value: "negative", label: "CMF Negative (Selling)" }
      ]},
      { type: "VOLUME_MA", label: "Volume MA", tip: "Volume Moving Average", params: { period: 20 }, conditions: [
        { value: "above_avg", label: "Volume Above Average" },
        { value: "below_avg", label: "Volume Below Average" },
        { value: "spike", label: "Volume Spike (2x Avg)" }
      ]},
    ]
  },
  trend_strength: {
    label: "Trend Strength",
    icon: Zap,
    color: "#EC4899",
    indicators: [
      { type: "ADX", label: "ADX", tip: "Average Directional Index - trend strength", params: { period: 14, threshold: 25 }, conditions: [
        { value: "strong_trend", label: "Strong Trend (ADX > 25)" },
        { value: "weak_trend", label: "Weak/No Trend (ADX < 20)" },
        { value: "bullish", label: "+DI > -DI (Bullish)" },
        { value: "bearish", label: "-DI > +DI (Bearish)" }
      ]},
      { type: "TRIX", label: "TRIX", tip: "Triple smoothed EMA rate of change", params: { period: 15 }, conditions: [
        { value: "positive", label: "TRIX Positive" },
        { value: "negative", label: "TRIX Negative" },
        { value: "zero_cross_up", label: "Cross Above Zero" },
        { value: "zero_cross_down", label: "Cross Below Zero" }
      ]},
    ]
  }
};

// Condition Block Component
function CondBlock({ c, onRemove, onUpdate }) {
  const allIndicators = Object.values(INDICATOR_CATEGORIES).flatMap(cat => cat.indicators);
  const indicator = allIndicators.find((x) => x.type === c.type);
  const category = Object.values(INDICATOR_CATEGORIES).find(cat => cat.indicators.some(i => i.type === c.type));
  
  return (
    <div className="bg-[#111] border border-[#1A1A1A] rounded-sm p-2.5 relative group" data-testid={`cond-${c.id}`}>
      <button onClick={onRemove} className="absolute top-1 right-1 opacity-0 group-hover:opacity-100 transition-opacity text-[#333] hover:text-[#FF0055]" data-testid={`rm-${c.id}`}>
        <X className="w-3 h-3" />
      </button>
      <div className="flex items-center gap-1.5 mb-2">
        <div className="w-1.5 h-1.5 rounded-full" style={{ backgroundColor: category?.color }} />
        <span className="text-[10px] font-semibold" style={{ color: category?.color }}>{indicator?.label || c.type}</span>
      </div>
      
      {/* Condition Selector */}
      <Select value={c.condition || c.operator || ""} onValueChange={(v) => onUpdate({ ...c, condition: v, operator: v })}>
        <SelectTrigger className="h-6 bg-[#0A0A0A] border-[#222] text-[10px] mb-1.5">
          <SelectValue placeholder="Select condition..." />
        </SelectTrigger>
        <SelectContent className="bg-[#0A0A0A] border-[#333]">
          {indicator?.conditions?.map(cond => (
            <SelectItem key={cond.value} value={cond.value}>{cond.label}</SelectItem>
          ))}
        </SelectContent>
      </Select>
      
      {/* Custom Value Input for RSI */}
      {c.type === "RSI" && (c.condition === "custom_below" || c.condition === "custom_above") && (
        <Input 
          type="number" 
          className="h-6 bg-[#0A0A0A] border-[#222] text-[10px] font-mono" 
          placeholder="Value (0-100)"
          value={c.value || ""} 
          onChange={(e) => onUpdate({ ...c, value: Number(e.target.value) })} 
        />
      )}
      
      {/* Period Input for indicators that support it */}
      {indicator?.params?.period !== undefined && (
        <div className="flex items-center gap-1 mt-1.5">
          <Label className="text-[8px] text-[#52525B]">Period:</Label>
          <Input 
            type="number" 
            className="h-5 w-12 bg-[#0A0A0A] border-[#222] text-[9px] font-mono" 
            value={c.period || indicator.params.period} 
            onChange={(e) => onUpdate({ ...c, period: Number(e.target.value) })} 
          />
        </div>
      )}
    </div>
  );
}

// Strategy Templates
const TEMPLATES = [
  {
    id: "rsi_mean_reversion",
    name: "RSI Mean Reversion",
    description: "Buy when RSI oversold, sell when overbought",
    entry: { logic: "AND", conditions: [{ type: "RSI", condition: "oversold", value: 30 }] },
    exit: { logic: "OR", conditions: [{ type: "RSI", condition: "overbought", value: 70 }] },
    risk: { stop_loss_pct: 3, take_profit_pct: 6, max_position_size_pct: 20 }
  },
  {
    id: "macd_momentum",
    name: "MACD Momentum",
    description: "Trend following with MACD crossovers",
    entry: { logic: "AND", conditions: [{ type: "MACD", condition: "bullish_crossover" }] },
    exit: { logic: "OR", conditions: [{ type: "MACD", condition: "bearish_crossover" }] },
    risk: { stop_loss_pct: 4, take_profit_pct: 8, max_position_size_pct: 25 }
  },
  {
    id: "supertrend_follow",
    name: "SuperTrend Follower",
    description: "Follow SuperTrend direction changes",
    entry: { logic: "AND", conditions: [{ type: "SUPERTREND", condition: "crossover_up" }] },
    exit: { logic: "OR", conditions: [{ type: "SUPERTREND", condition: "crossover_down" }] },
    risk: { stop_loss_pct: 5, take_profit_pct: 10, max_position_size_pct: 30 }
  },
  {
    id: "bb_squeeze",
    name: "Bollinger Squeeze",
    description: "Buy at lower band, sell at upper band",
    entry: { logic: "AND", conditions: [{ type: "BB", condition: "below_lower" }] },
    exit: { logic: "OR", conditions: [{ type: "BB", condition: "above_upper" }] },
    risk: { stop_loss_pct: 2, take_profit_pct: 4, max_position_size_pct: 15 }
  },
  {
    id: "multi_confirm",
    name: "Multi-Indicator Confirm",
    description: "RSI + MACD + ADX confirmation",
    entry: { logic: "AND", conditions: [
      { type: "RSI", condition: "oversold", value: 35 },
      { type: "MACD", condition: "bullish_crossover" },
      { type: "ADX", condition: "strong_trend", threshold: 25 }
    ]},
    exit: { logic: "OR", conditions: [
      { type: "RSI", condition: "overbought", value: 65 },
      { type: "MACD", condition: "bearish_crossover" }
    ]},
    risk: { stop_loss_pct: 3, take_profit_pct: 9, max_position_size_pct: 20 }
  }
];

export default function BotBuilderPage() {
  const [mode, setMode] = useState("visual"); // visual, templates, ai
  const [name, setName] = useState("");
  const [symbol, setSymbol] = useState("BTCUSD");
  const [tf, setTf] = useState("1h");
  const [entry, setEntry] = useState([]);
  const [exit, setExit] = useState([]);
  const [entryLogic, setEntryLogic] = useState("AND");
  const [exitLogic, setExitLogic] = useState("OR");
  const [risk, setRisk] = useState({ 
    stop_loss_pct: 2, 
    take_profit_pct: 5, 
    max_position_size_pct: 10, 
    max_capital_per_trade: 5000, 
    max_daily_loss: 1000, 
    max_concurrent_trades: 3,
    trailing_stop_pct: null
  });
  const [strategies, setStrategies] = useState([]);
  const [saving, setSaving] = useState(false);
  const [expandedCategory, setExpandedCategory] = useState("trend");

  useEffect(() => { 
    api.get("/strategies").then((r) => setStrategies(r.data)).catch(() => {}); 
  }, []);

  const addCondition = (sec, indicator) => {
    const c = { 
      id: Date.now().toString(), 
      type: indicator.type, 
      condition: indicator.conditions?.[0]?.value || "",
      ...indicator.params
    };
    sec === "entry" ? setEntry((p) => [...p, c]) : setExit((p) => [...p, c]);
  };

  const save = async () => {
    if (!name) { toast.error("Name your strategy"); return; }
    if (!entry.length) { toast.error("Add entry conditions"); return; }
    setSaving(true);
    try {
      await api.post("/strategies", { 
        name, symbol, timeframe: tf, 
        entry: { logic: entryLogic, conditions: entry }, 
        exit: { logic: exitLogic, conditions: exit }, 
        risk 
      });
      toast.success("Strategy saved!");
      api.get("/strategies").then((r) => setStrategies(r.data));
    } catch { toast.error("Save failed"); }
    setSaving(false);
  };

  const loadTemplate = (template) => {
    setName(template.name);
    setEntry(template.entry.conditions.map((c, i) => ({ ...c, id: `${Date.now()}-${i}` })));
    setExit(template.exit.conditions.map((c, i) => ({ ...c, id: `${Date.now()}-e-${i}` })));
    setEntryLogic(template.entry.logic);
    setExitLogic(template.exit.logic);
    setRisk({ ...risk, ...template.risk });
    setMode("visual");
    toast.success(`Loaded: ${template.name}`);
  };

  const loadStrategy = (s) => {
    setName(s.name); 
    setSymbol(s.symbol); 
    setTf(s.timeframe);
    setEntry(s.entry?.conditions || []); 
    setExit(s.exit?.conditions || []);
    setEntryLogic(s.entry?.logic || "AND"); 
    setExitLogic(s.exit?.logic || "OR");
    if (s.risk) setRisk(s.risk);
    toast.success("Strategy loaded");
  };

  return (
    <TooltipProvider>
      <div className="space-y-3" data-testid="bot-builder-page">
        {/* Header */}
        <div className="flex items-center gap-3 flex-wrap">
          <h1 className="text-2xl font-bold tracking-tight">Strategy Builder</h1>
          <div className="flex items-center gap-1 bg-[#111] border border-[#222] rounded-sm p-0.5">
            <Button 
              size="sm" 
              variant={mode === "templates" ? "secondary" : "ghost"} 
              className="h-6 text-[10px] rounded-sm"
              onClick={() => setMode("templates")}
            >
              <Sparkles className="w-3 h-3 mr-1" />Templates
            </Button>
            <Button 
              size="sm" 
              variant={mode === "visual" ? "secondary" : "ghost"} 
              className="h-6 text-[10px] rounded-sm"
              onClick={() => setMode("visual")}
            >
              <Layers className="w-3 h-3 mr-1" />Visual
            </Button>
          </div>
          <div className="ml-auto flex items-center gap-2">
            <Input 
              className="h-8 w-44 bg-[#111] border-[#222] text-xs rounded-sm" 
              placeholder="Strategy Name" 
              value={name} 
              onChange={(e) => setName(e.target.value)} 
              data-testid="strategy-name-input" 
            />
            <Select value={symbol} onValueChange={setSymbol}>
              <SelectTrigger className="h-8 w-28 bg-[#111] border-[#222] text-xs" data-testid="builder-symbol">
                <SelectValue />
              </SelectTrigger>
              <SelectContent className="bg-[#0A0A0A] border-[#333]">
                {["BTCUSD","ETHUSD","AAPL","TSLA","SPY"].map((s) => <SelectItem key={s} value={s}>{s}</SelectItem>)}
              </SelectContent>
            </Select>
            <Select value={tf} onValueChange={setTf}>
              <SelectTrigger className="h-8 w-20 bg-[#111] border-[#222] text-xs" data-testid="builder-timeframe">
                <SelectValue />
              </SelectTrigger>
              <SelectContent className="bg-[#0A0A0A] border-[#333]">
                {["5m","15m","1h","1d"].map((t) => <SelectItem key={t} value={t}>{t}</SelectItem>)}
              </SelectContent>
            </Select>
            <Button 
              onClick={save} 
              disabled={saving} 
              className="h-8 bg-[#00E396] text-[#050505] hover:bg-[#00C27F] rounded-sm text-xs" 
              data-testid="save-strategy-btn"
            >
              <Save className="w-3 h-3 mr-1" />{saving ? "Saving..." : "Save"}
            </Button>
          </div>
        </div>

        {/* Templates Mode */}
        {mode === "templates" && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-2">
            {TEMPLATES.map((t) => (
              <Card 
                key={t.id} 
                className="bg-[#0A0A0A] border-[#222] rounded-sm hover:border-[#333] transition-colors cursor-pointer"
                onClick={() => loadTemplate(t)}
                data-testid={`template-${t.id}`}
              >
                <CardContent className="p-4">
                  <div className="flex items-center justify-between mb-2">
                    <h3 className="text-sm font-medium">{t.name}</h3>
                    <ChevronRight className="w-4 h-4 text-[#52525B]" />
                  </div>
                  <p className="text-xs text-[#52525B] mb-3">{t.description}</p>
                  <div className="flex flex-wrap gap-1">
                    {t.entry.conditions.map((c, i) => (
                      <Badge key={i} className="text-[8px] bg-[#00E396]/10 text-[#00E396] border-0">{c.type}</Badge>
                    ))}
                    {t.exit.conditions.map((c, i) => (
                      <Badge key={`e-${i}`} className="text-[8px] bg-[#FF0055]/10 text-[#FF0055] border-0">{c.type}</Badge>
                    ))}
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}

        {/* Visual Builder Mode */}
        {mode === "visual" && (
          <div className="grid grid-cols-1 lg:grid-cols-4 gap-2">
            {/* Indicator Palette */}
            <Card className="bg-[#0A0A0A] border-[#222] rounded-sm">
              <CardHeader className="pb-2">
                <CardTitle className="text-xs uppercase tracking-wider text-[#52525B]">Indicators</CardTitle>
              </CardHeader>
              <CardContent className="p-2">
                <ScrollArea className="h-[500px]">
                  <Accordion type="single" collapsible value={expandedCategory} onValueChange={setExpandedCategory}>
                    {Object.entries(INDICATOR_CATEGORIES).map(([key, category]) => (
                      <AccordionItem key={key} value={key} className="border-[#1A1A1A]">
                        <AccordionTrigger className="py-2 text-xs hover:no-underline">
                          <div className="flex items-center gap-2">
                            <category.icon className="w-3.5 h-3.5" style={{ color: category.color }} />
                            <span style={{ color: category.color }}>{category.label}</span>
                            <Badge className="text-[7px] bg-[#111] text-[#52525B] border-[#222] ml-auto">
                              {category.indicators.length}
                            </Badge>
                          </div>
                        </AccordionTrigger>
                        <AccordionContent className="space-y-1 pb-2">
                          {category.indicators.map((ind) => (
                            <Tooltip key={ind.type}>
                              <TooltipTrigger asChild>
                                <div className="flex items-center gap-1">
                                  <Button 
                                    size="sm" 
                                    variant="ghost" 
                                    className="flex-1 justify-start h-7 text-[10px] text-[#A1A1AA] hover:text-white hover:bg-[#111] rounded-sm" 
                                    onClick={() => addCondition("entry", ind)} 
                                    data-testid={`add-entry-${ind.type}`}
                                  >
                                    {ind.label}
                                    <Badge className="ml-auto text-[7px] bg-[#00E396]/15 text-[#00E396] border-0 px-1">+E</Badge>
                                  </Button>
                                  <Button 
                                    size="sm" 
                                    variant="ghost" 
                                    className="h-7 w-7 p-0 text-[#333] hover:text-[#FF0055] rounded-sm" 
                                    onClick={() => addCondition("exit", ind)} 
                                    data-testid={`add-exit-${ind.type}`}
                                  >
                                    <Plus className="w-3 h-3" />
                                  </Button>
                                </div>
                              </TooltipTrigger>
                              <TooltipContent side="right" className="bg-[#111] border-[#333] text-[10px] max-w-[200px]">
                                {ind.tip}
                              </TooltipContent>
                            </Tooltip>
                          ))}
                        </AccordionContent>
                      </AccordionItem>
                    ))}
                  </Accordion>
                  
                  <Separator className="bg-[#1A1A1A] my-3" />
                  <p className="text-[9px] text-[#333] uppercase tracking-wider mb-2 px-1">Saved Strategies</p>
                  <div className="space-y-0.5">
                    {strategies.map((s) => (
                      <Button 
                        key={s.id} 
                        variant="ghost" 
                        size="sm" 
                        className="w-full justify-start h-6 text-[10px] text-[#52525B] hover:text-white rounded-sm" 
                        onClick={() => loadStrategy(s)} 
                        data-testid={`load-${s.id}`}
                      >
                        {s.name}
                      </Button>
                    ))}
                  </div>
                </ScrollArea>
              </CardContent>
            </Card>

            {/* Entry/Exit Builder */}
            <div className="lg:col-span-2 space-y-2">
              {/* Entry Section */}
              <Card className="bg-[#0A0A0A] border-[#222] rounded-sm">
                <CardHeader className="pb-1 flex-row items-center justify-between">
                  <CardTitle className="text-xs text-[#00E396] uppercase tracking-wider flex items-center gap-1.5">
                    <Play className="w-3 h-3" /> Entry Conditions
                  </CardTitle>
                  <Select value={entryLogic} onValueChange={setEntryLogic}>
                    <SelectTrigger className="h-5 w-16 bg-[#111] border-[#222] text-[9px]" data-testid="entry-logic">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent className="bg-[#0A0A0A] border-[#333]">
                      <SelectItem value="AND">AND</SelectItem>
                      <SelectItem value="OR">OR</SelectItem>
                    </SelectContent>
                  </Select>
                </CardHeader>
                <CardContent className="p-3">
                  {!entry.length ? (
                    <p className="text-[10px] text-[#222] text-center py-8">Click indicators to add entry conditions</p>
                  ) : (
                    <div className="space-y-1.5">
                      {entry.map((c, i) => (
                        <div key={c.id}>
                          <CondBlock 
                            c={c} 
                            onRemove={() => setEntry((p) => p.filter((x) => x.id !== c.id))} 
                            onUpdate={(u) => setEntry((p) => p.map((x) => x.id === c.id ? u : x))} 
                          />
                          {i < entry.length - 1 && (
                            <div className="flex justify-center py-0.5">
                              <Badge className="text-[7px] bg-[#111] text-[#52525B] border-[#222]">{entryLogic}</Badge>
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  )}
                </CardContent>
              </Card>
              
              {/* Exit Section */}
              <Card className="bg-[#0A0A0A] border-[#222] rounded-sm">
                <CardHeader className="pb-1 flex-row items-center justify-between">
                  <CardTitle className="text-xs text-[#FF0055] uppercase tracking-wider flex items-center gap-1.5">
                    <X className="w-3 h-3" /> Exit Conditions
                  </CardTitle>
                  <Select value={exitLogic} onValueChange={setExitLogic}>
                    <SelectTrigger className="h-5 w-16 bg-[#111] border-[#222] text-[9px]" data-testid="exit-logic">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent className="bg-[#0A0A0A] border-[#333]">
                      <SelectItem value="AND">AND</SelectItem>
                      <SelectItem value="OR">OR</SelectItem>
                    </SelectContent>
                  </Select>
                </CardHeader>
                <CardContent className="p-3">
                  {!exit.length ? (
                    <p className="text-[10px] text-[#222] text-center py-8">Add exit conditions via + button</p>
                  ) : (
                    <div className="space-y-1.5">
                      {exit.map((c, i) => (
                        <div key={c.id}>
                          <CondBlock 
                            c={c} 
                            onRemove={() => setExit((p) => p.filter((x) => x.id !== c.id))} 
                            onUpdate={(u) => setExit((p) => p.map((x) => x.id === c.id ? u : x))} 
                          />
                          {i < exit.length - 1 && (
                            <div className="flex justify-center py-0.5">
                              <Badge className="text-[7px] bg-[#111] text-[#52525B] border-[#222]">{exitLogic}</Badge>
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>

            {/* Risk Management */}
            <Card className="bg-[#0A0A0A] border-[#222] rounded-sm">
              <CardHeader className="pb-2">
                <CardTitle className="text-xs flex items-center gap-1.5 uppercase tracking-wider text-[#F59E0B]">
                  <Shield className="w-3.5 h-3.5" /> Risk Management
                </CardTitle>
              </CardHeader>
              <CardContent className="p-3 space-y-4">
                {/* Sliders */}
                {[
                  { k: "stop_loss_pct", l: "Stop Loss %", mn: 0.5, mx: 20, s: 0.5, color: "#FF0055" },
                  { k: "take_profit_pct", l: "Take Profit %", mn: 1, mx: 50, s: 0.5, color: "#00E396" },
                  { k: "max_position_size_pct", l: "Max Position %", mn: 1, mx: 100, s: 1, color: "#3B82F6" }
                ].map(({ k, l, mn, mx, s, color }) => (
                  <div key={k}>
                    <div className="flex justify-between mb-1">
                      <Label className="text-[9px] text-[#52525B]">{l}</Label>
                      <span className="text-[9px] font-mono" style={{ color }}>{risk[k]}%</span>
                    </div>
                    <Slider 
                      min={mn} 
                      max={mx} 
                      step={s} 
                      value={[risk[k]]} 
                      onValueChange={([v]) => setRisk((p) => ({ ...p, [k]: v }))} 
                      data-testid={`risk-${k}`}
                    />
                  </div>
                ))}
                
                <Separator className="bg-[#1A1A1A]" />
                
                {/* Number Inputs */}
                {[
                  { k: "max_capital_per_trade", l: "Max Capital/Trade ($)" },
                  { k: "max_daily_loss", l: "Max Daily Loss ($)" },
                  { k: "max_concurrent_trades", l: "Max Concurrent Trades" },
                  { k: "trailing_stop_pct", l: "Trailing Stop % (optional)" }
                ].map(({ k, l }) => (
                  <div key={k}>
                    <Label className="text-[9px] text-[#52525B]">{l}</Label>
                    <Input 
                      type="number" 
                      className="h-6 bg-[#111] border-[#222] font-mono text-[10px] mt-0.5 rounded-sm" 
                      value={risk[k] || ""} 
                      placeholder={k === "trailing_stop_pct" ? "Disabled" : ""}
                      onChange={(e) => setRisk((p) => ({ ...p, [k]: e.target.value ? Number(e.target.value) : null }))} 
                      data-testid={`risk-${k}`} 
                    />
                  </div>
                ))}
              </CardContent>
            </Card>
          </div>
        )}
      </div>
    </TooltipProvider>
  );
}
