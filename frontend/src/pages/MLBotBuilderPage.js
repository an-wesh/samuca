import { useState, useEffect, useCallback } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Slider } from "@/components/ui/slider";
import { Checkbox } from "@/components/ui/checkbox";
import { Separator } from "@/components/ui/separator";
import { Progress } from "@/components/ui/progress";
import { toast } from "sonner";
import api from "@/lib/api";
import { 
  Brain, Sparkles, Target, Play, Settings, ChevronRight,
  Zap, BarChart3, CheckCircle, AlertTriangle, Cpu, TrendingUp
} from "lucide-react";

const MetricCard = ({ label, value, description, color }) => (
  <div className="bg-[#111] border border-[#1A1A1A] rounded-sm p-3">
    <p className="text-[9px] text-[#52525B] uppercase">{label}</p>
    <p className="text-lg font-mono font-semibold" style={{ color }}>{value}</p>
    {description && <p className="text-[9px] text-[#333]">{description}</p>}
  </div>
);

export default function MLBotBuilderPage() {
  const [mode, setMode] = useState("guided"); // automl, guided, advanced
  const [templates, setTemplates] = useState([]);
  const [features, setFeatures] = useState([]);
  const [targets, setTargets] = useState([]);
  const [models, setModels] = useState([]);
  const [training, setTraining] = useState(false);
  const [trainingProgress, setTrainingProgress] = useState(0);
  const [result, setResult] = useState(null);
  const [selectedModel, setSelectedModel] = useState(null);
  const [backtestResult, setBacktestResult] = useState(null);

  // Form state
  const [symbol, setSymbol] = useState("RELIANCE.NS");
  const [timeframe, setTimeframe] = useState("1h");
  const [selectedTemplate, setSelectedTemplate] = useState("");
  const [targetType, setTargetType] = useState("next_direction");
  const [modelType, setModelType] = useState("xgboost");
  const [selectedFeatures, setSelectedFeatures] = useState([]);
  const [modelName, setModelName] = useState("");
  const [params, setParams] = useState({
    n_estimators: 100,
    max_depth: 5,
    learning_rate: 0.1
  });

  useEffect(() => {
    fetchTemplates();
    fetchFeatures();
    fetchModels();
  }, []);

  const fetchTemplates = async () => {
    try {
      const { data } = await api.get("/ml/templates");
      setTemplates(data.templates || []);
    } catch (err) { console.error(err); }
  };

  const fetchFeatures = async () => {
    try {
      const { data } = await api.get("/ml/features");
      setFeatures(data.features || []);
      setTargets(data.targets || []);
    } catch (err) { console.error(err); }
  };

  const fetchModels = async () => {
    try {
      const { data } = await api.get("/ml/models");
      setModels(data || []);
    } catch (err) { console.error(err); }
  };

  const trainAutoML = async () => {
    setTraining(true);
    setTrainingProgress(0);
    setResult(null);
    
    const progressInterval = setInterval(() => {
      setTrainingProgress(p => Math.min(p + 10, 90));
    }, 500);

    try {
      const { data } = await api.post("/ml/automl/train", {
        symbol, timeframe, target_type: targetType
      });
      setResult(data);
      toast.success("AutoML training complete!");
      fetchModels();
    } catch (err) {
      toast.error(err.response?.data?.detail || "Training failed");
    }
    
    clearInterval(progressInterval);
    setTrainingProgress(100);
    setTraining(false);
  };

  const trainGuided = async () => {
    if (!selectedTemplate) {
      toast.error("Select a template");
      return;
    }
    setTraining(true);
    setTrainingProgress(0);
    setResult(null);

    const progressInterval = setInterval(() => {
      setTrainingProgress(p => Math.min(p + 15, 90));
    }, 400);

    try {
      const { data } = await api.post("/ml/guided/train", {
        symbol, timeframe, template_id: selectedTemplate
      });
      setResult(data);
      toast.success("Model trained successfully!");
      fetchModels();
    } catch (err) {
      toast.error(err.response?.data?.detail || "Training failed");
    }
    
    clearInterval(progressInterval);
    setTrainingProgress(100);
    setTraining(false);
  };

  const trainAdvanced = async () => {
    if (!modelName || selectedFeatures.length === 0) {
      toast.error("Provide model name and select features");
      return;
    }
    setTraining(true);
    setTrainingProgress(0);
    setResult(null);

    const progressInterval = setInterval(() => {
      setTrainingProgress(p => Math.min(p + 12, 90));
    }, 400);

    try {
      const { data } = await api.post("/ml/advanced/train", {
        symbol, timeframe, name: modelName, model_type: modelType,
        target_type: targetType, features: selectedFeatures, params
      });
      setResult(data);
      toast.success("Custom model trained!");
      fetchModels();
    } catch (err) {
      toast.error(err.response?.data?.detail || "Training failed");
    }
    
    clearInterval(progressInterval);
    setTrainingProgress(100);
    setTraining(false);
  };

  const backtestModel = async (modelId) => {
    try {
      const { data } = await api.get(`/ml/models/${modelId}/backtest?symbol=${symbol}&timeframe=${timeframe}`);
      setBacktestResult(data);
      toast.success("Backtest complete!");
    } catch (err) {
      toast.error(err.response?.data?.detail || "Backtest failed");
    }
  };

  const predict = async (modelId) => {
    try {
      const { data } = await api.post("/ml/predict", {
        model_id: modelId, symbol, timeframe
      });
      toast.success(`Prediction: ${data.prediction_label} (${(data.confidence * 100).toFixed(1)}% confidence)`);
    } catch (err) {
      toast.error(err.response?.data?.detail || "Prediction failed");
    }
  };

  const toggleFeature = (fname) => {
    setSelectedFeatures(prev => 
      prev.includes(fname) ? prev.filter(f => f !== fname) : [...prev, fname]
    );
  };

  return (
    <div className="space-y-3" data-testid="ml-bot-builder-page">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <h1 className="text-2xl font-bold tracking-tight">ML Bot Builder</h1>
          <Badge className="bg-[#8B5CF6]/10 text-[#8B5CF6] border-[#8B5CF6]/20">
            <Brain className="w-3 h-3 mr-1" /> Machine Learning
          </Badge>
        </div>
      </div>

      {/* Mode Selector & Config */}
      <Card className="bg-[#0A0A0A] border-[#222] rounded-sm">
        <CardContent className="p-3">
          <div className="flex flex-wrap items-end gap-3">
            <div className="flex gap-1 bg-[#111] border border-[#222] rounded-sm p-0.5">
              <Button 
                size="sm" variant={mode === "automl" ? "secondary" : "ghost"}
                onClick={() => setMode("automl")}
                className="h-7 text-[10px]"
              >
                <Sparkles className="w-3 h-3 mr-1" /> AutoML
              </Button>
              <Button 
                size="sm" variant={mode === "guided" ? "secondary" : "ghost"}
                onClick={() => setMode("guided")}
                className="h-7 text-[10px]"
              >
                <Target className="w-3 h-3 mr-1" /> Guided
              </Button>
              <Button 
                size="sm" variant={mode === "advanced" ? "secondary" : "ghost"}
                onClick={() => setMode("advanced")}
                className="h-7 text-[10px]"
              >
                <Settings className="w-3 h-3 mr-1" /> Advanced
              </Button>
            </div>
            <div>
              <Label className="text-[9px] text-[#52525B]">Symbol</Label>
              <Select value={symbol} onValueChange={setSymbol}>
                <SelectTrigger className="h-8 w-36 bg-[#111] border-[#222] text-xs">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent className="bg-[#0A0A0A] border-[#333]">
                  {["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "ICICIBANK.NS", "BTCUSD"].map(s => (
                    <SelectItem key={s} value={s}>{s.replace(".NS", "")}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label className="text-[9px] text-[#52525B]">Timeframe</Label>
              <Select value={timeframe} onValueChange={setTimeframe}>
                <SelectTrigger className="h-8 w-20 bg-[#111] border-[#222] text-xs">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent className="bg-[#0A0A0A] border-[#333]">
                  {["15m", "1h", "1d"].map(t => <SelectItem key={t} value={t}>{t}</SelectItem>)}
                </SelectContent>
              </Select>
            </div>
          </div>
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-2">
        {/* Training Panel */}
        <div className="lg:col-span-2 space-y-2">
          {/* AutoML Mode */}
          {mode === "automl" && (
            <Card className="bg-[#0A0A0A] border-[#222] rounded-sm">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm flex items-center gap-2">
                  <Sparkles className="w-4 h-4 text-[#F59E0B]" /> AutoML Mode
                </CardTitle>
              </CardHeader>
              <CardContent className="p-3 space-y-3">
                <p className="text-xs text-[#52525B]">
                  Automatically select the best model type and parameters for your data.
                </p>
                <div>
                  <Label className="text-[9px] text-[#52525B]">Prediction Target</Label>
                  <Select value={targetType} onValueChange={setTargetType}>
                    <SelectTrigger className="h-8 bg-[#111] border-[#222] text-xs">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent className="bg-[#0A0A0A] border-[#333]">
                      {targets.map(t => (
                        <SelectItem key={t.name} value={t.name}>{t.description}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <Button 
                  onClick={trainAutoML} 
                  disabled={training}
                  className="w-full h-10 bg-[#F59E0B] text-[#050505] hover:bg-[#D97706]"
                >
                  <Zap className="w-4 h-4 mr-2" />
                  {training ? "Training..." : "Start AutoML Training"}
                </Button>
                {training && <Progress value={trainingProgress} className="h-1" />}
              </CardContent>
            </Card>
          )}

          {/* Guided Mode */}
          {mode === "guided" && (
            <Card className="bg-[#0A0A0A] border-[#222] rounded-sm">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm flex items-center gap-2">
                  <Target className="w-4 h-4 text-[#3B82F6]" /> Guided Mode - Templates
                </CardTitle>
              </CardHeader>
              <CardContent className="p-3 space-y-3">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                  {templates.map(t => (
                    <div 
                      key={t.id}
                      onClick={() => setSelectedTemplate(t.id)}
                      className={`p-3 rounded-sm border cursor-pointer transition-all ${
                        selectedTemplate === t.id 
                          ? "bg-[#3B82F6]/10 border-[#3B82F6]/30" 
                          : "bg-[#111] border-[#1A1A1A] hover:border-[#222]"
                      }`}
                    >
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-xs font-medium">{t.name}</span>
                        {selectedTemplate === t.id && <CheckCircle className="w-3 h-3 text-[#3B82F6]" />}
                      </div>
                      <p className="text-[10px] text-[#52525B] mb-2">{t.description}</p>
                      <div className="flex flex-wrap gap-1">
                        <Badge className="text-[7px] bg-[#111] text-[#52525B]">{t.model_type}</Badge>
                        {t.features.slice(0, 3).map(f => (
                          <Badge key={f} className="text-[7px] bg-[#222] text-[#A1A1AA]">{f}</Badge>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
                <Button 
                  onClick={trainGuided} 
                  disabled={training || !selectedTemplate}
                  className="w-full h-10 bg-[#3B82F6] hover:bg-[#2563EB]"
                >
                  <Cpu className="w-4 h-4 mr-2" />
                  {training ? "Training..." : "Train Selected Template"}
                </Button>
                {training && <Progress value={trainingProgress} className="h-1" />}
              </CardContent>
            </Card>
          )}

          {/* Advanced Mode */}
          {mode === "advanced" && (
            <Card className="bg-[#0A0A0A] border-[#222] rounded-sm">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm flex items-center gap-2">
                  <Settings className="w-4 h-4 text-[#8B5CF6]" /> Advanced Mode - Custom Model
                </CardTitle>
              </CardHeader>
              <CardContent className="p-3 space-y-3">
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <Label className="text-[9px] text-[#52525B]">Model Name</Label>
                    <Input 
                      className="h-8 bg-[#111] border-[#222] text-xs"
                      value={modelName}
                      onChange={e => setModelName(e.target.value)}
                      placeholder="My Custom Model"
                    />
                  </div>
                  <div>
                    <Label className="text-[9px] text-[#52525B]">Model Type</Label>
                    <Select value={modelType} onValueChange={setModelType}>
                      <SelectTrigger className="h-8 bg-[#111] border-[#222] text-xs">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent className="bg-[#0A0A0A] border-[#333]">
                        <SelectItem value="xgboost">XGBoost</SelectItem>
                        <SelectItem value="random_forest">Random Forest</SelectItem>
                        <SelectItem value="gradient_boosting">Gradient Boosting</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>
                <div>
                  <Label className="text-[9px] text-[#52525B]">Prediction Target</Label>
                  <Select value={targetType} onValueChange={setTargetType}>
                    <SelectTrigger className="h-8 bg-[#111] border-[#222] text-xs">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent className="bg-[#0A0A0A] border-[#333]">
                      {targets.map(t => (
                        <SelectItem key={t.name} value={t.name}>{t.description}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <Label className="text-[9px] text-[#52525B] mb-2 block">
                    Features ({selectedFeatures.length} selected)
                  </Label>
                  <ScrollArea className="h-32 bg-[#111] border border-[#222] rounded-sm p-2">
                    <div className="grid grid-cols-2 gap-1">
                      {features.map(f => (
                        <div 
                          key={f.name}
                          className="flex items-center gap-2 p-1 hover:bg-[#1A1A1A] rounded cursor-pointer"
                          onClick={() => toggleFeature(f.name)}
                        >
                          <Checkbox checked={selectedFeatures.includes(f.name)} />
                          <span className="text-[10px]">{f.name}</span>
                        </div>
                      ))}
                    </div>
                  </ScrollArea>
                </div>
                <Separator className="bg-[#222]" />
                <div className="space-y-2">
                  <Label className="text-[9px] text-[#52525B]">Hyperparameters</Label>
                  {[
                    { key: "n_estimators", label: "N Estimators", min: 10, max: 500 },
                    { key: "max_depth", label: "Max Depth", min: 2, max: 15 },
                    { key: "learning_rate", label: "Learning Rate", min: 0.01, max: 0.5, step: 0.01 }
                  ].map(p => (
                    <div key={p.key} className="flex items-center gap-3">
                      <span className="text-[10px] text-[#52525B] w-24">{p.label}</span>
                      <Slider 
                        min={p.min} max={p.max} step={p.step || 1}
                        value={[params[p.key]]}
                        onValueChange={([v]) => setParams({...params, [p.key]: v})}
                        className="flex-1"
                      />
                      <span className="text-[10px] font-mono w-12">{params[p.key]}</span>
                    </div>
                  ))}
                </div>
                <Button 
                  onClick={trainAdvanced} 
                  disabled={training || !modelName || selectedFeatures.length === 0}
                  className="w-full h-10 bg-[#8B5CF6] hover:bg-[#7C3AED]"
                >
                  <Brain className="w-4 h-4 mr-2" />
                  {training ? "Training..." : "Train Custom Model"}
                </Button>
                {training && <Progress value={trainingProgress} className="h-1" />}
              </CardContent>
            </Card>
          )}

          {/* Training Result */}
          {result && (
            <Card className="bg-[#0A0A0A] border-[#222] rounded-sm">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm flex items-center gap-2">
                  <CheckCircle className="w-4 h-4 text-[#00E396]" /> Training Results
                </CardTitle>
              </CardHeader>
              <CardContent className="p-3">
                <div className="grid grid-cols-2 md:grid-cols-4 gap-2 mb-3">
                  <MetricCard label="Accuracy" value={`${(result.metrics?.accuracy * 100).toFixed(1)}%`} color="#00E396" />
                  <MetricCard label="Precision" value={`${(result.metrics?.precision * 100).toFixed(1)}%`} color="#3B82F6" />
                  <MetricCard label="Recall" value={`${(result.metrics?.recall * 100).toFixed(1)}%`} color="#F59E0B" />
                  <MetricCard label="F1 Score" value={`${(result.metrics?.f1_score * 100).toFixed(1)}%`} color="#8B5CF6" />
                </div>
                <div className="flex justify-between items-center text-xs text-[#52525B]">
                  <span>Model ID: {result.model_id?.slice(0, 8)}...</span>
                  <span>CV Accuracy: {(result.metrics?.cv_accuracy_mean * 100).toFixed(1)}% ± {(result.metrics?.cv_accuracy_std * 100).toFixed(1)}%</span>
                </div>
              </CardContent>
            </Card>
          )}
        </div>

        {/* Models Panel */}
        <Card className="bg-[#0A0A0A] border-[#222] rounded-sm">
          <CardHeader className="pb-2">
            <CardTitle className="text-xs text-[#52525B] uppercase tracking-wider">Trained Models</CardTitle>
          </CardHeader>
          <CardContent className="p-2">
            <ScrollArea className="h-[500px]">
              {models.length === 0 ? (
                <div className="text-center py-8">
                  <Brain className="w-8 h-8 mx-auto mb-2 text-[#222]" />
                  <p className="text-xs text-[#52525B]">No models trained yet</p>
                </div>
              ) : (
                <div className="space-y-2">
                  {models.map(m => (
                    <div 
                      key={m.id}
                      className="p-3 bg-[#111] border border-[#1A1A1A] rounded-sm"
                    >
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-xs font-medium">{m.name}</span>
                        <Badge className="text-[7px] bg-[#222] text-[#A1A1AA]">{m.mode}</Badge>
                      </div>
                      <div className="text-[10px] text-[#52525B] mb-2">
                        <span>{m.model_type}</span> • <span>Acc: {(m.metrics?.accuracy * 100).toFixed(0)}%</span>
                      </div>
                      <div className="flex gap-1">
                        <Button 
                          size="sm" variant="outline" 
                          className="h-6 text-[9px] flex-1 border-[#222]"
                          onClick={() => predict(m.id)}
                        >
                          <TrendingUp className="w-3 h-3 mr-1" /> Predict
                        </Button>
                        <Button 
                          size="sm" variant="outline" 
                          className="h-6 text-[9px] flex-1 border-[#222]"
                          onClick={() => backtestModel(m.id)}
                        >
                          <BarChart3 className="w-3 h-3 mr-1" /> Backtest
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </ScrollArea>
          </CardContent>
        </Card>
      </div>

      {/* Backtest Results */}
      {backtestResult && (
        <Card className="bg-[#0A0A0A] border-[#222] rounded-sm">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm">Backtest Results - {backtestResult.symbol}</CardTitle>
          </CardHeader>
          <CardContent className="p-3">
            <div className="grid grid-cols-2 md:grid-cols-5 gap-2">
              <MetricCard label="Total Trades" value={backtestResult.metrics?.total_trades} color="#A1A1AA" />
              <MetricCard label="Win Rate" value={`${backtestResult.metrics?.win_rate}%`} color={backtestResult.metrics?.win_rate >= 50 ? "#00E396" : "#FF0055"} />
              <MetricCard label="Total P&L" value={`$${backtestResult.metrics?.total_pnl?.toFixed(2)}`} color={backtestResult.metrics?.total_pnl >= 0 ? "#00E396" : "#FF0055"} />
              <MetricCard label="Wins" value={backtestResult.metrics?.wins} color="#00E396" />
              <MetricCard label="Losses" value={backtestResult.metrics?.losses} color="#FF0055" />
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
