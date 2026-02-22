import { useState, useEffect, useRef, useCallback } from "react";
import { createChart, CandlestickSeries, LineSeries, HistogramSeries } from "lightweight-charts";
import { Button } from "@/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Switch } from "@/components/ui/switch";
import { Label } from "@/components/ui/label";
import api from "@/lib/api";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

export default function ChartTerminalPage() {
  const chartContainerRef = useRef(null);
  const chartRef = useRef(null);
  const candleRef = useRef(null);
  const volumeRef = useRef(null);
  const indRefs = useRef({});
  const wsRef = useRef(null);

  const [symbol, setSymbol] = useState("RELIANCE.NS");
  const [timeframe, setTimeframe] = useState("1h");
  const [symbols, setSymbols] = useState([]);
  const [indicators, setIndicators] = useState({ sma: false, ema: false, bb: false });

  useEffect(() => { 
    api.get("/market/symbols").then((r) => {
      // Extract symbol strings from the response objects
      const symbolList = r.data.symbols.map(s => typeof s === 'object' ? s.symbol : s);
      setSymbols(symbolList);
    }); 
  }, []);

  const loadData = useCallback(async () => {
    try {
      const { data } = await api.get(`/market/ohlcv?symbol=${symbol}&timeframe=${timeframe}&limit=500`);
      const ohlcv = data.data || data;
      if (candleRef.current && ohlcv.length > 0) {
        candleRef.current.setData(ohlcv.map((c) => ({ time: c.timestamp, open: c.open, high: c.high, low: c.low, close: c.close })));
      }
      if (volumeRef.current && ohlcv.length > 0) {
        volumeRef.current.setData(ohlcv.map((c) => ({ time: c.timestamp, value: c.volume, color: c.close >= c.open ? "rgba(0,227,150,0.25)" : "rgba(255,0,85,0.25)" })));
      }
      if (chartRef.current) chartRef.current.timeScale().fitContent();
    } catch (err) { console.error("Failed to load chart data:", err); }
  }, [symbol, timeframe]);

  const updateIndicators = useCallback(async () => {
    const chart = chartRef.current;
    if (!chart) return;
    Object.values(indRefs.current).forEach((s) => { try { chart.removeSeries(s); } catch (e) { console.log(e); } });
    indRefs.current = {};
    if (!indicators.sma && !indicators.ema && !indicators.bb) return;
    try {
      const { data } = await api.get(`/indicators/${symbol}?timeframe=${timeframe}`);
      const ind = data.indicators;
      if (indicators.sma && ind.sma_20) {
        const s = chart.addSeries(LineSeries, { color: "#3B82F6", lineWidth: 1, title: "SMA 20" });
        s.setData(ind.timestamps.map((t, i) => ind.sma_20[i] != null ? { time: t, value: ind.sma_20[i] } : null).filter(Boolean));
        indRefs.current.sma = s;
      }
      if (indicators.ema && ind.ema_50) {
        const s = chart.addSeries(LineSeries, { color: "#F59E0B", lineWidth: 1, title: "EMA 50" });
        s.setData(ind.timestamps.map((t, i) => ind.ema_50[i] != null ? { time: t, value: ind.ema_50[i] } : null).filter(Boolean));
        indRefs.current.ema = s;
      }
      if (indicators.bb && ind.bb_upper && ind.bb_lower) {
        const u = chart.addSeries(LineSeries, { color: "#8B5CF6", lineWidth: 1, lineStyle: 2, title: "BB Upper" });
        const l = chart.addSeries(LineSeries, { color: "#8B5CF6", lineWidth: 1, lineStyle: 2, title: "BB Lower" });
        u.setData(ind.timestamps.map((t, i) => ind.bb_upper[i] != null ? { time: t, value: ind.bb_upper[i] } : null).filter(Boolean));
        l.setData(ind.timestamps.map((t, i) => ind.bb_lower[i] != null ? { time: t, value: ind.bb_lower[i] } : null).filter(Boolean));
        indRefs.current.bbu = u;
        indRefs.current.bbl = l;
      }
    } catch (err) { console.error("Failed to load indicators:", err); }
  }, [indicators, symbol, timeframe]);

  useEffect(() => {
    if (!chartContainerRef.current) return;
    const chart = createChart(chartContainerRef.current, {
      layout: { background: { type: "solid", color: "#050505" }, textColor: "#71717A", fontFamily: "JetBrains Mono, monospace", fontSize: 11 },
      grid: { vertLines: { color: "#111" }, horzLines: { color: "#111" } },
      crosshair: { mode: 0, vertLine: { color: "#333", labelBackgroundColor: "#222" }, horzLine: { color: "#333", labelBackgroundColor: "#222" } },
      rightPriceScale: { borderColor: "#222", scaleMargins: { top: 0.1, bottom: 0.2 } },
      timeScale: { borderColor: "#222", timeVisible: true, secondsVisible: false },
      localization: { locale: "en-US" },
    });
    chartRef.current = chart;

    const cs = chart.addSeries(CandlestickSeries, {
      upColor: "#00E396", downColor: "#FF0055",
      borderUpColor: "#00E396", borderDownColor: "#FF0055",
      wickUpColor: "#00E396", wickDownColor: "#FF0055",
    });
    candleRef.current = cs;

    const vs = chart.addSeries(HistogramSeries, { color: "#3B82F6", priceFormat: { type: "volume" }, priceScaleId: "vol" });
    vs.priceScale().applyOptions({ scaleMargins: { top: 0.85, bottom: 0 } });
    volumeRef.current = vs;

    const ro = new ResizeObserver((entries) => {
      for (const e of entries) chart.applyOptions({ width: e.contentRect.width, height: e.contentRect.height });
    });
    ro.observe(chartContainerRef.current);
    return () => { ro.disconnect(); chart.remove(); };
  }, []);

  useEffect(() => { loadData(); }, [symbol, timeframe, loadData]);

  useEffect(() => {
    if (wsRef.current) wsRef.current.close();
    const wsUrl = `${BACKEND_URL.replace("https://", "wss://").replace("http://", "ws://")}/api/market/ws/${symbol}`;
    const ws = new WebSocket(wsUrl);
    ws.onmessage = (e) => {
      const t = JSON.parse(e.data);
      if (candleRef.current) candleRef.current.update({ time: t.timestamp, open: t.open, high: t.high, low: t.low, close: t.close });
    };
    wsRef.current = ws;
    return () => ws.close();
  }, [symbol]);

  useEffect(() => { updateIndicators(); }, [indicators, symbol, timeframe, updateIndicators]);

  return (
    <div className="space-y-2" data-testid="chart-terminal-page">
      <div className="flex items-center gap-3 flex-wrap">
        <Select value={symbol} onValueChange={setSymbol}>
          <SelectTrigger className="w-[160px] h-8 bg-[#111] border-[#222] text-xs font-mono" data-testid="symbol-select"><SelectValue /></SelectTrigger>
          <SelectContent className="bg-[#0A0A0A] border-[#333] max-h-[300px]">
            {symbols.map((s) => (
              <SelectItem key={s} value={s} className="text-xs font-mono">
                {s.replace(".NS", "")}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
        <div className="flex gap-0.5">
          {["5m", "15m", "1h", "1d"].map((tf) => (
            <Button key={tf} variant="ghost" size="sm" className={`h-8 text-[10px] font-mono px-3 rounded-sm ${tf === timeframe ? "bg-[#222] text-white" : "text-[#52525B] hover:text-[#A1A1AA]"}`}
              onClick={() => setTimeframe(tf)} data-testid={`tf-btn-${tf}`}>{tf}</Button>
          ))}
        </div>
        <div className="flex items-center gap-4 ml-auto">
          {[{ k: "sma", l: "SMA 20", c: "#3B82F6" }, { k: "ema", l: "EMA 50", c: "#F59E0B" }, { k: "bb", l: "BB", c: "#8B5CF6" }].map((ind) => (
            <div key={ind.k} className="flex items-center gap-1.5">
              <Switch checked={indicators[ind.k]} onCheckedChange={(v) => setIndicators((p) => ({ ...p, [ind.k]: v }))} className="scale-75" data-testid={`indicator-${ind.k}`} />
              <Label className="text-[10px] font-mono" style={{ color: ind.c }}>{ind.l}</Label>
            </div>
          ))}
        </div>
      </div>
      <div ref={chartContainerRef} className="w-full h-[calc(100vh-130px)] bg-[#050505] border border-[#222] rounded-sm" data-testid="chart-container" />
    </div>
  );
}
