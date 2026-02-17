import { useState, useEffect, useCallback } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";
import { Textarea } from "@/components/ui/textarea";
import { toast } from "sonner";
import api from "@/lib/api";
import { 
  Newspaper, TrendingUp, TrendingDown, Minus, RefreshCw, 
  Sparkles, Clock, ExternalLink, Search, BarChart3
} from "lucide-react";

const SentimentGauge = ({ score, size = "large" }) => {
  // Convert -1 to 1 score to 0-180 degrees
  const angle = ((score + 1) / 2) * 180;
  const isLarge = size === "large";
  
  const getColor = () => {
    if (score >= 0.5) return "#00E396";
    if (score >= 0.2) return "#4ADE80";
    if (score >= -0.2) return "#A1A1AA";
    if (score >= -0.5) return "#F87171";
    return "#FF0055";
  };

  return (
    <div className={`relative ${isLarge ? "w-32 h-16" : "w-20 h-10"}`}>
      <svg viewBox="0 0 100 50" className="w-full h-full">
        {/* Background arc */}
        <path
          d="M 5 50 A 45 45 0 0 1 95 50"
          fill="none"
          stroke="#222"
          strokeWidth="8"
        />
        {/* Colored arc */}
        <path
          d="M 5 50 A 45 45 0 0 1 95 50"
          fill="none"
          stroke={getColor()}
          strokeWidth="8"
          strokeDasharray={`${(angle / 180) * 141.37} 141.37`}
        />
        {/* Needle */}
        <line
          x1="50"
          y1="50"
          x2={50 + 35 * Math.cos((Math.PI * (180 - angle)) / 180)}
          y2={50 - 35 * Math.sin((Math.PI * (180 - angle)) / 180)}
          stroke="white"
          strokeWidth="2"
          strokeLinecap="round"
        />
        <circle cx="50" cy="50" r="4" fill="white" />
      </svg>
      <div className="absolute bottom-0 w-full text-center">
        <span className={`font-mono font-bold ${isLarge ? "text-lg" : "text-xs"}`} style={{ color: getColor() }}>
          {score > 0 ? "+" : ""}{score.toFixed(2)}
        </span>
      </div>
    </div>
  );
};

const SentimentLabel = ({ label, confidence }) => {
  const colors = {
    "Strong Bullish": "#00E396",
    "Bullish": "#4ADE80",
    "Neutral": "#A1A1AA",
    "Bearish": "#F87171",
    "Strong Bearish": "#FF0055"
  };
  
  const icons = {
    "Strong Bullish": <TrendingUp className="w-3 h-3" />,
    "Bullish": <TrendingUp className="w-3 h-3" />,
    "Neutral": <Minus className="w-3 h-3" />,
    "Bearish": <TrendingDown className="w-3 h-3" />,
    "Strong Bearish": <TrendingDown className="w-3 h-3" />
  };

  return (
    <div className="flex items-center gap-2">
      <Badge 
        className="text-[9px] gap-1"
        style={{ 
          backgroundColor: `${colors[label]}20`,
          color: colors[label],
          borderColor: `${colors[label]}40`
        }}
      >
        {icons[label]}
        {label}
      </Badge>
      {confidence && (
        <span className="text-[9px] text-[#52525B] font-mono">{confidence}%</span>
      )}
    </div>
  );
};

export default function NewsSentimentPage() {
  const [news, setNews] = useState([]);
  const [selectedSymbol, setSelectedSymbol] = useState("");
  const [loading, setLoading] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [customHeadlines, setCustomHeadlines] = useState("");
  const [analysisResults, setAnalysisResults] = useState(null);
  const [symbolSentiment, setSymbolSentiment] = useState({});

  const fetchNews = useCallback(async () => {
    setLoading(true);
    try {
      const url = selectedSymbol ? `/news/feed/${selectedSymbol}` : "/news/feed";
      const { data } = await api.get(url);
      setNews(data);
    } catch (err) {
      console.error(err);
    }
    setLoading(false);
  }, [selectedSymbol]);

  const fetchSymbolSentiments = useCallback(async () => {
    const symbols = ["BTCUSD", "ETHUSD", "AAPL", "TSLA", "SPY"];
    const sentiments = {};
    
    for (const sym of symbols) {
      try {
        const { data } = await api.get(`/news/sentiment/aggregate/${sym}`);
        sentiments[sym] = data;
      } catch (err) {
        sentiments[sym] = { avg_score: 0, label: "Neutral" };
      }
    }
    setSymbolSentiment(sentiments);
  }, []);

  useEffect(() => {
    fetchNews();
    fetchSymbolSentiments();
  }, [fetchNews, fetchSymbolSentiments]);

  const analyzeHeadlines = async (headlines) => {
    if (!headlines.length) {
      toast.error("No headlines to analyze");
      return;
    }
    
    setAnalyzing(true);
    try {
      const { data } = await api.post("/news/analyze", { 
        headlines,
        symbols: selectedSymbol ? [selectedSymbol] : undefined
      });
      setAnalysisResults(data);
      toast.success(`Analyzed ${data.results.length} headlines`);
      fetchSymbolSentiments();
    } catch (err) {
      toast.error(err.response?.data?.detail || "Analysis failed");
    }
    setAnalyzing(false);
  };

  const analyzeCustom = () => {
    const lines = customHeadlines.split("\n").filter(l => l.trim());
    analyzeHeadlines(lines);
  };

  const analyzeNewsItem = (item) => {
    analyzeHeadlines([item.headline]);
  };

  return (
    <div className="space-y-3" data-testid="news-sentiment-page">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold tracking-tight">News & Sentiment</h1>
        <div className="flex items-center gap-2">
          <Select value={selectedSymbol || "all"} onValueChange={(v) => setSelectedSymbol(v === "all" ? "" : v)}>
            <SelectTrigger className="h-8 w-28 bg-[#111] border-[#222] text-xs">
              <SelectValue placeholder="All Symbols" />
            </SelectTrigger>
            <SelectContent className="bg-[#0A0A0A] border-[#333]">
              <SelectItem value="all">All</SelectItem>
              {["BTCUSD", "ETHUSD", "AAPL", "TSLA", "SPY"].map(s => (
                <SelectItem key={s} value={s}>{s}</SelectItem>
              ))}
            </SelectContent>
          </Select>
          <Button 
            variant="outline" 
            size="sm" 
            onClick={fetchNews}
            disabled={loading}
            className="h-8 text-xs border-[#222]"
          >
            <RefreshCw className={`w-3 h-3 mr-1 ${loading ? "animate-spin" : ""}`} /> Refresh
          </Button>
        </div>
      </div>

      {/* Symbol Sentiment Overview */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-2">
        {["BTCUSD", "ETHUSD", "AAPL", "TSLA", "SPY"].map(sym => {
          const sent = symbolSentiment[sym] || { avg_score: 0, label: "Neutral" };
          return (
            <Card 
              key={sym} 
              className={`bg-[#0A0A0A] border-[#222] rounded-sm cursor-pointer transition-all ${selectedSymbol === sym ? "border-[#333]" : ""}`}
              onClick={() => setSelectedSymbol(selectedSymbol === sym ? "" : sym)}
            >
              <CardContent className="p-3 flex items-center justify-between">
                <div>
                  <p className="text-xs font-medium">{sym}</p>
                  <SentimentLabel label={sent.label} />
                </div>
                <SentimentGauge score={sent.avg_score} size="small" />
              </CardContent>
            </Card>
          );
        })}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-2">
        {/* News Feed */}
        <Card className="lg:col-span-2 bg-[#0A0A0A] border-[#222] rounded-sm">
          <CardHeader className="pb-2">
            <CardTitle className="text-xs text-[#52525B] uppercase tracking-wider flex items-center gap-2">
              <Newspaper className="w-4 h-4" />
              {selectedSymbol ? `${selectedSymbol} News` : "Latest News"}
            </CardTitle>
          </CardHeader>
          <CardContent className="p-2">
            <ScrollArea className="h-[500px]">
              {news.length === 0 ? (
                <div className="text-center py-8">
                  <Newspaper className="w-8 h-8 mx-auto mb-2 text-[#222]" />
                  <p className="text-xs text-[#52525B]">No news available</p>
                </div>
              ) : (
                <div className="space-y-2">
                  {news.map(item => (
                    <div 
                      key={item.id}
                      className="p-3 bg-[#111] border border-[#1A1A1A] rounded-sm hover:border-[#222] transition-colors"
                    >
                      <div className="flex items-start justify-between gap-2">
                        <div className="flex-1">
                          <p className="text-xs font-medium leading-tight mb-1">{item.headline}</p>
                          <div className="flex items-center gap-2 text-[10px] text-[#52525B]">
                            <span className="font-mono">{item.symbol}</span>
                            <span>•</span>
                            <span>{item.source}</span>
                            <span>•</span>
                            <Clock className="w-3 h-3" />
                            <span>{new Date(item.timestamp).toLocaleTimeString()}</span>
                          </div>
                        </div>
                        <div className="flex flex-col items-end gap-1">
                          <Badge 
                            className={`text-[8px] ${
                              item.sentiment_hint === "bullish" ? "bg-[#00E396]/15 text-[#00E396]" :
                              item.sentiment_hint === "bearish" ? "bg-[#FF0055]/15 text-[#FF0055]" :
                              "bg-[#333] text-[#A1A1AA]"
                            }`}
                          >
                            {item.sentiment_hint}
                          </Badge>
                          <Button 
                            size="sm" 
                            variant="ghost" 
                            className="h-6 text-[9px] text-[#3B82F6]"
                            onClick={() => analyzeNewsItem(item)}
                            disabled={analyzing}
                          >
                            <Sparkles className="w-3 h-3 mr-1" /> Analyze
                          </Button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </ScrollArea>
          </CardContent>
        </Card>

        {/* Analysis Panel */}
        <div className="space-y-2">
          {/* Custom Analysis */}
          <Card className="bg-[#0A0A0A] border-[#222] rounded-sm">
            <CardHeader className="pb-2">
              <CardTitle className="text-xs text-[#52525B] uppercase tracking-wider flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-[#F59E0B]" />
                AI Sentiment Analysis
              </CardTitle>
            </CardHeader>
            <CardContent className="p-3 space-y-2">
              <Label className="text-[9px] text-[#52525B]">Enter headlines (one per line)</Label>
              <Textarea 
                className="h-24 bg-[#111] border-[#222] text-xs resize-none"
                placeholder="Bitcoin surges past $100K...
Tesla announces new factory...
Fed signals rate cuts..."
                value={customHeadlines}
                onChange={(e) => setCustomHeadlines(e.target.value)}
              />
              <Button 
                onClick={analyzeCustom}
                disabled={analyzing || !customHeadlines.trim()}
                className="w-full h-8 bg-[#3B82F6] hover:bg-[#2563EB] text-xs"
              >
                <Sparkles className="w-3 h-3 mr-1" />
                {analyzing ? "Analyzing..." : "Analyze Sentiment"}
              </Button>
            </CardContent>
          </Card>

          {/* Analysis Results */}
          {analysisResults && (
            <Card className="bg-[#0A0A0A] border-[#222] rounded-sm">
              <CardHeader className="pb-2">
                <CardTitle className="text-xs flex items-center justify-between">
                  <span className="flex items-center gap-2">
                    <BarChart3 className="w-4 h-4 text-[#00E396]" />
                    Analysis Results
                  </span>
                  <Badge className={`text-[9px] ${analysisResults.results[0]?.ai_analyzed ? "bg-[#00E396]/15 text-[#00E396]" : "bg-[#F59E0B]/15 text-[#F59E0B]"}`}>
                    {analysisResults.results[0]?.ai_analyzed ? "AI" : "Keyword"}
                  </Badge>
                </CardTitle>
              </CardHeader>
              <CardContent className="p-3">
                {/* Aggregate */}
                <div className="flex items-center justify-between mb-3 p-2 bg-[#111] rounded-sm">
                  <div>
                    <p className="text-[9px] text-[#52525B] uppercase">Overall Sentiment</p>
                    <SentimentLabel label={analysisResults.aggregate.label} />
                  </div>
                  <SentimentGauge score={analysisResults.aggregate.avg_score} />
                </div>
                
                <div className="grid grid-cols-3 gap-2 mb-3">
                  <div className="text-center p-2 bg-[#00E396]/10 rounded-sm">
                    <p className="text-lg font-mono font-bold text-[#00E396]">{analysisResults.aggregate.bullish_count}</p>
                    <p className="text-[8px] text-[#52525B]">Bullish</p>
                  </div>
                  <div className="text-center p-2 bg-[#333]/30 rounded-sm">
                    <p className="text-lg font-mono font-bold text-[#A1A1AA]">{analysisResults.aggregate.neutral_count}</p>
                    <p className="text-[8px] text-[#52525B]">Neutral</p>
                  </div>
                  <div className="text-center p-2 bg-[#FF0055]/10 rounded-sm">
                    <p className="text-lg font-mono font-bold text-[#FF0055]">{analysisResults.aggregate.bearish_count}</p>
                    <p className="text-[8px] text-[#52525B]">Bearish</p>
                  </div>
                </div>

                <Separator className="bg-[#222] my-2" />
                
                {/* Individual Results */}
                <ScrollArea className="h-[200px]">
                  <div className="space-y-2">
                    {analysisResults.results.map((r, i) => (
                      <div key={i} className="p-2 bg-[#111] border border-[#1A1A1A] rounded-sm">
                        <p className="text-[10px] text-[#A1A1AA] mb-1 line-clamp-2">{r.headline}</p>
                        <div className="flex items-center justify-between">
                          <SentimentLabel label={r.label} confidence={r.confidence} />
                          <span className={`text-xs font-mono ${r.score >= 0 ? "text-[#00E396]" : "text-[#FF0055]"}`}>
                            {r.score >= 0 ? "+" : ""}{r.score.toFixed(2)}
                          </span>
                        </div>
                        {r.key_factors?.length > 0 && (
                          <div className="flex flex-wrap gap-1 mt-1">
                            {r.key_factors.map((f, j) => (
                              <Badge key={j} className="text-[7px] bg-[#222] text-[#52525B] border-0">{f}</Badge>
                            ))}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </ScrollArea>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}
