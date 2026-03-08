import { useEffect, useState } from "react";
import { 
  TrendingUp, Play, Pause, Settings, History, Target,
  RefreshCw, Zap, DollarSign, AlertTriangle, CheckCircle,
  ArrowUp, ArrowDown, Activity, BarChart3, Lightbulb
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "../components/ui/card";
import { Button } from "../components/ui/button";
import { Badge } from "../components/ui/badge";
import { Input } from "../components/ui/input";
import { Label } from "../components/ui/label";
import { Switch } from "../components/ui/switch";
import { Progress } from "../components/ui/progress";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "../components/ui/tabs";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "../components/ui/dialog";
import { toast } from "sonner";
import { 
  getBidOptimizationStatus, 
  enableBidOptimization, 
  disableBidOptimization,
  runBidOptimization,
  getBidOptimizationHistory
} from "../lib/api";
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  LineChart, Line, Legend, AreaChart, Area, Cell
} from "recharts";

const COLORS = ["#3B82F6", "#10B981", "#F59E0B", "#EF4444", "#8B5CF6", "#EC4899"];

export default function BidOptimization() {
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selectedCampaign, setSelectedCampaign] = useState(null);
  const [showConfig, setShowConfig] = useState(false);
  const [configForm, setConfigForm] = useState({
    targetWinRate: 30,
    autoAdjust: true
  });
  const [history, setHistory] = useState([]);
  const [historyLoading, setHistoryLoading] = useState(false);
  const [activeTab, setActiveTab] = useState("all");

  useEffect(() => {
    fetchStatus();
  }, []);

  const fetchStatus = async () => {
    try {
      setLoading(true);
      const res = await getBidOptimizationStatus();
      setStatus(res.data);
    } catch (error) {
      toast.error("Failed to load optimization status");
    } finally {
      setLoading(false);
    }
  };

  const handleEnable = async (campaignId) => {
    try {
      await enableBidOptimization(campaignId, configForm.targetWinRate, configForm.autoAdjust);
      toast.success("Bid optimization enabled");
      setShowConfig(false);
      setSelectedCampaign(null);
      fetchStatus();
    } catch (error) {
      toast.error("Failed to enable optimization");
    }
  };

  const handleDisable = async (campaignId) => {
    try {
      await disableBidOptimization(campaignId);
      toast.success("Bid optimization disabled");
      fetchStatus();
    } catch (error) {
      toast.error("Failed to disable optimization");
    }
  };

  const handleRunOptimization = async (campaignId) => {
    try {
      const res = await runBidOptimization(campaignId);
      if (res.data.status === "adjusted") {
        toast.success(`Bid adjusted: $${res.data.old_bid} → $${res.data.new_bid}`);
      } else if (res.data.status === "no_change") {
        toast.info(res.data.reason);
      } else if (res.data.status === "skipped") {
        toast.warning(res.data.reason);
      } else {
        toast.info(`Recommendation: $${res.data.recommended_bid}`);
      }
      fetchStatus();
    } catch (error) {
      toast.error("Failed to run optimization");
    }
  };

  const fetchHistory = async (campaignId) => {
    try {
      setHistoryLoading(true);
      setSelectedCampaign(campaignId);
      const res = await getBidOptimizationHistory(campaignId);
      setHistory(res.data.history || []);
    } catch (error) {
      toast.error("Failed to load history");
    } finally {
      setHistoryLoading(false);
    }
  };

  // Filter campaigns based on tab
  const filteredCampaigns = status?.campaigns?.filter(c => {
    if (activeTab === "all") return true;
    if (activeTab === "enabled") return c.optimization_enabled;
    if (activeTab === "disabled") return !c.optimization_enabled;
    if (activeTab === "below") return c.optimization_enabled && c.current_win_rate < c.target_win_rate - 5;
    return true;
  }) || [];

  // Prepare chart data
  const bidComparisonData = status?.campaigns?.slice(0, 6).map(c => ({
    name: c.campaign_name.length > 12 ? c.campaign_name.slice(0, 12) + "..." : c.campaign_name,
    bid: c.bid_price,
    winRate: c.current_win_rate,
    target: c.target_win_rate
  })) || [];

  const getWinRateStatus = (current, target) => {
    const diff = current - target;
    if (Math.abs(diff) <= 5) return { status: "on-target", color: "#10B981", icon: CheckCircle };
    if (diff < -5) return { status: "below", color: "#EF4444", icon: ArrowDown };
    return { status: "above", color: "#F59E0B", icon: ArrowUp };
  };

  const getRecommendation = (campaign) => {
    if (!campaign.optimization_enabled) return null;
    const diff = campaign.current_win_rate - campaign.target_win_rate;
    if (Math.abs(diff) <= 5) return { type: "optimal", text: "Bid is optimal", color: "#10B981" };
    if (diff < -5) return { type: "increase", text: `Consider increasing bid by ~${Math.ceil(Math.abs(diff) * 2)}%`, color: "#3B82F6" };
    return { type: "decrease", text: `Consider decreasing bid by ~${Math.ceil(diff * 1.5)}%`, color: "#F59E0B" };
  };

  if (loading) {
    return (
      <div className="p-6 flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-[#3B82F6] mx-auto mb-4"></div>
          <div className="text-[#64748B]">Loading optimization status...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6" data-testid="bid-optimization-page">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-[#F8FAFC]">Automated Bid Optimization</h1>
          <p className="text-sm text-[#94A3B8] mt-1">
            Auto-adjust bid prices based on win rate targets
          </p>
        </div>
        <Button 
          onClick={fetchStatus}
          className="bg-[#3B82F6] hover:bg-[#60A5FA]"
          data-testid="refresh-btn"
        >
          <RefreshCw className="w-4 h-4 mr-2" />
          Refresh
        </Button>
      </div>

      {/* Overview Stats */}
      <div className="grid grid-cols-4 gap-4">
        <Card className="surface-primary border-panel">
          <CardContent className="p-4 flex items-center gap-3">
            <div className="p-2 rounded-lg bg-[#3B82F6]/20">
              <Target className="w-5 h-5 text-[#3B82F6]" />
            </div>
            <div>
              <p className="text-xs text-[#64748B]">Total Campaigns</p>
              <p className="text-2xl font-bold text-[#F8FAFC]">{status?.total_campaigns}</p>
            </div>
          </CardContent>
        </Card>
        <Card className="surface-primary border-panel">
          <CardContent className="p-4 flex items-center gap-3">
            <div className="p-2 rounded-lg bg-[#10B981]/20">
              <Zap className="w-5 h-5 text-[#10B981]" />
            </div>
            <div>
              <p className="text-xs text-[#64748B]">Optimization Enabled</p>
              <p className="text-2xl font-bold text-[#10B981]">{status?.optimization_enabled_count}</p>
            </div>
          </CardContent>
        </Card>
        <Card className="surface-primary border-panel">
          <CardContent className="p-4 flex items-center gap-3">
            <div className="p-2 rounded-lg bg-[#EF4444]/20">
              <AlertTriangle className="w-5 h-5 text-[#EF4444]" />
            </div>
            <div>
              <p className="text-xs text-[#64748B]">Below Target</p>
              <p className="text-2xl font-bold text-[#EF4444]">
                {status?.campaigns?.filter(c => c.optimization_enabled && c.current_win_rate < c.target_win_rate - 5).length || 0}
              </p>
            </div>
          </CardContent>
        </Card>
        <Card className="surface-primary border-panel">
          <CardContent className="p-4 flex items-center gap-3">
            <div className="p-2 rounded-lg bg-[#10B981]/20">
              <CheckCircle className="w-5 h-5 text-[#10B981]" />
            </div>
            <div>
              <p className="text-xs text-[#64748B]">On Target</p>
              <p className="text-2xl font-bold text-[#10B981]">
                {status?.campaigns?.filter(c => c.optimization_enabled && Math.abs(c.current_win_rate - c.target_win_rate) <= 5).length || 0}
              </p>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-3 gap-6">
        {/* Bid vs Win Rate Chart */}
        <Card className="col-span-2 surface-primary border-panel">
          <CardHeader className="pb-0">
            <CardTitle className="text-lg text-[#F8FAFC] flex items-center gap-2">
              <BarChart3 className="w-5 h-5 text-[#3B82F6]" />
              Campaign Bid & Win Rate Comparison
            </CardTitle>
            <CardDescription className="text-[#64748B]">
              Current bids and win rates vs target
            </CardDescription>
          </CardHeader>
          <CardContent className="pt-4">
            <div className="h-[250px]">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={bidComparisonData} margin={{ top: 20, right: 30, left: 0, bottom: 5 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1E293B" />
                  <XAxis dataKey="name" tick={{ fill: '#94A3B8', fontSize: 11 }} axisLine={{ stroke: '#1E293B' }} />
                  <YAxis yAxisId="left" tick={{ fill: '#94A3B8', fontSize: 11 }} axisLine={{ stroke: '#1E293B' }} />
                  <YAxis yAxisId="right" orientation="right" tick={{ fill: '#94A3B8', fontSize: 11 }} axisLine={{ stroke: '#1E293B' }} />
                  <Tooltip 
                    contentStyle={{ 
                      backgroundColor: '#0A0F1C', 
                      border: '1px solid #2D3B55',
                      borderRadius: '8px',
                      color: '#F8FAFC'
                    }}
                    formatter={(value, name) => {
                      if (name === 'bid') return [`$${value.toFixed(2)}`, 'Bid Price'];
                      if (name === 'winRate') return [`${value.toFixed(1)}%`, 'Win Rate'];
                      return [`${value}%`, 'Target'];
                    }}
                  />
                  <Legend 
                    wrapperStyle={{ paddingTop: '10px' }}
                    formatter={(value) => {
                      const labels = { bid: 'Bid Price', winRate: 'Win Rate', target: 'Target' };
                      return <span className="text-[#94A3B8]">{labels[value] || value}</span>;
                    }}
                  />
                  <Bar yAxisId="left" dataKey="bid" fill="#3B82F6" radius={[4, 4, 0, 0]} />
                  <Bar yAxisId="right" dataKey="winRate" fill="#10B981" radius={[4, 4, 0, 0]} />
                  <Bar yAxisId="right" dataKey="target" fill="#F59E0B" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        {/* Quick Actions & Recommendations */}
        <Card className="surface-primary border-panel">
          <CardHeader className="pb-2">
            <CardTitle className="text-lg text-[#F8FAFC] flex items-center gap-2">
              <Lightbulb className="w-5 h-5 text-[#F59E0B]" />
              Recommendations
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {status?.campaigns?.filter(c => c.optimization_enabled).slice(0, 4).map((campaign) => {
              const rec = getRecommendation(campaign);
              if (!rec) return null;
              return (
                <div 
                  key={campaign.campaign_id}
                  className="p-3 surface-secondary rounded-lg border-l-2"
                  style={{ borderLeftColor: rec.color }}
                >
                  <p className="text-sm text-[#F8FAFC] font-medium truncate">{campaign.campaign_name}</p>
                  <div className="flex items-center justify-between mt-1">
                    <p className="text-xs" style={{ color: rec.color }}>{rec.text}</p>
                    {rec.type !== "optimal" && (
                      <Button 
                        size="sm" 
                        variant="ghost"
                        onClick={() => handleRunOptimization(campaign.campaign_id)}
                        className="h-6 px-2 text-xs text-[#3B82F6] hover:bg-[#3B82F6]/10"
                      >
                        Optimize
                      </Button>
                    )}
                  </div>
                </div>
              );
            })}
            
            {status?.campaigns?.filter(c => c.optimization_enabled).length === 0 && (
              <div className="text-center py-6">
                <Zap className="w-10 h-10 mx-auto text-[#64748B] mb-2" />
                <p className="text-sm text-[#94A3B8]">Enable optimization on campaigns to see recommendations</p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Campaign Table with Tabs */}
      <Card className="surface-primary border-panel">
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="text-lg text-[#F8FAFC]">Campaign Optimization Status</CardTitle>
            <Tabs value={activeTab} onValueChange={setActiveTab}>
              <TabsList className="h-8 bg-[#0A0F1C]">
                <TabsTrigger value="all" className="text-xs data-[state=active]:bg-[#3B82F6] data-[state=active]:text-white">
                  All ({status?.campaigns?.length || 0})
                </TabsTrigger>
                <TabsTrigger value="enabled" className="text-xs data-[state=active]:bg-[#10B981] data-[state=active]:text-white">
                  Enabled ({status?.optimization_enabled_count || 0})
                </TabsTrigger>
                <TabsTrigger value="below" className="text-xs data-[state=active]:bg-[#EF4444] data-[state=active]:text-white">
                  Below Target
                </TabsTrigger>
              </TabsList>
            </Tabs>
          </div>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-[#2D3B55]">
                  <th className="text-left py-2 px-3 text-xs text-[#64748B] font-medium">Campaign</th>
                  <th className="text-center py-2 px-3 text-xs text-[#64748B] font-medium">Optimization</th>
                  <th className="text-right py-2 px-3 text-xs text-[#64748B] font-medium">Current Bid</th>
                  <th className="text-center py-2 px-3 text-xs text-[#64748B] font-medium">Win Rate</th>
                  <th className="text-right py-2 px-3 text-xs text-[#64748B] font-medium">Target</th>
                  <th className="text-center py-2 px-3 text-xs text-[#64748B] font-medium">Mode</th>
                  <th className="text-center py-2 px-3 text-xs text-[#64748B] font-medium">Actions</th>
                </tr>
              </thead>
              <tbody>
                {filteredCampaigns.map((campaign) => {
                  const winRateInfo = getWinRateStatus(campaign.current_win_rate, campaign.target_win_rate);
                  const StatusIcon = winRateInfo.icon;
                  
                  return (
                    <tr 
                      key={campaign.campaign_id} 
                      className={`border-b border-[#2D3B55]/30 transition-colors hover:bg-[#151F32] ${
                        selectedCampaign === campaign.campaign_id ? "bg-[#3B82F6]/10" : ""
                      }`}
                      data-testid={`campaign-row-${campaign.campaign_id}`}
                    >
                      <td className="py-3 px-3">
                        <div>
                          <p className="text-sm text-[#F8FAFC] font-medium">{campaign.campaign_name}</p>
                          <Badge 
                            variant="outline" 
                            className={`text-[9px] mt-1 ${
                              campaign.status === "active" 
                                ? "bg-[#10B981]/10 text-[#10B981] border-[#10B981]/30" 
                                : campaign.status === "paused"
                                ? "bg-[#F59E0B]/10 text-[#F59E0B] border-[#F59E0B]/30"
                                : "bg-[#64748B]/10 text-[#64748B] border-[#64748B]/30"
                            }`}
                          >
                            {campaign.status}
                          </Badge>
                        </div>
                      </td>
                      <td className="py-3 px-3 text-center">
                        <Badge 
                          variant="outline"
                          className={campaign.optimization_enabled 
                            ? "bg-[#10B981]/20 text-[#10B981] border-[#10B981]/30" 
                            : "bg-[#64748B]/20 text-[#64748B] border-[#64748B]/30"
                          }
                        >
                          {campaign.optimization_enabled ? "Enabled" : "Disabled"}
                        </Badge>
                      </td>
                      <td className="py-3 px-3 text-right">
                        <span className="text-sm font-mono text-[#F8FAFC]">
                          ${campaign.bid_price?.toFixed(2)}
                        </span>
                      </td>
                      <td className="py-3 px-3">
                        <div className="flex items-center justify-center gap-2">
                          {campaign.optimization_enabled && (
                            <StatusIcon className="w-4 h-4" style={{ color: winRateInfo.color }} />
                          )}
                          <span className="text-sm font-mono" style={{ color: campaign.optimization_enabled ? winRateInfo.color : '#94A3B8' }}>
                            {campaign.current_win_rate?.toFixed(1)}%
                          </span>
                        </div>
                        {campaign.optimization_enabled && (
                          <Progress 
                            value={Math.min((campaign.current_win_rate / campaign.target_win_rate) * 100, 100)} 
                            className="h-1 mt-1"
                          />
                        )}
                      </td>
                      <td className="py-3 px-3 text-right">
                        <span className="text-sm font-mono text-[#94A3B8]">
                          {campaign.target_win_rate || 30}%
                        </span>
                      </td>
                      <td className="py-3 px-3 text-center">
                        {campaign.optimization_enabled ? (
                          campaign.auto_adjust ? (
                            <Badge className="bg-[#10B981]/20 text-[#10B981] border-0">Auto</Badge>
                          ) : (
                            <Badge className="bg-[#F59E0B]/20 text-[#F59E0B] border-0">Manual</Badge>
                          )
                        ) : (
                          <span className="text-[#64748B]">-</span>
                        )}
                      </td>
                      <td className="py-3 px-3">
                        <div className="flex items-center justify-center gap-1">
                          {campaign.optimization_enabled ? (
                            <>
                              <Button 
                                size="sm" 
                                variant="ghost"
                                onClick={() => handleRunOptimization(campaign.campaign_id)}
                                className="text-[#3B82F6] hover:bg-[#3B82F6]/10 p-1.5 h-auto"
                                title="Run Optimization"
                                data-testid={`run-opt-${campaign.campaign_id}`}
                              >
                                <Play className="w-4 h-4" />
                              </Button>
                              <Button 
                                size="sm" 
                                variant="ghost"
                                onClick={() => fetchHistory(campaign.campaign_id)}
                                className="text-[#94A3B8] hover:bg-[#94A3B8]/10 p-1.5 h-auto"
                                title="View History"
                                data-testid={`history-${campaign.campaign_id}`}
                              >
                                <History className="w-4 h-4" />
                              </Button>
                              <Button 
                                size="sm" 
                                variant="ghost"
                                onClick={() => handleDisable(campaign.campaign_id)}
                                className="text-[#EF4444] hover:bg-[#EF4444]/10 p-1.5 h-auto"
                                title="Disable Optimization"
                                data-testid={`disable-${campaign.campaign_id}`}
                              >
                                <Pause className="w-4 h-4" />
                              </Button>
                            </>
                          ) : (
                            <Button 
                              size="sm" 
                              variant="outline"
                              onClick={() => {
                                setSelectedCampaign(campaign.campaign_id);
                                setShowConfig(true);
                              }}
                              className="text-[#10B981] border-[#10B981]/50 hover:bg-[#10B981]/10"
                              data-testid={`enable-${campaign.campaign_id}`}
                            >
                              Enable
                            </Button>
                          )}
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
            
            {filteredCampaigns.length === 0 && (
              <div className="text-center py-8">
                <Target className="w-10 h-10 mx-auto text-[#64748B] mb-2" />
                <p className="text-sm text-[#94A3B8]">No campaigns match the selected filter</p>
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* History Panel */}
      {selectedCampaign && (
        <Card className="surface-primary border-panel border-[#3B82F6]/30">
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="text-lg text-[#F8FAFC] flex items-center gap-2">
                <History className="w-5 h-5 text-[#3B82F6]" />
                Optimization History
              </CardTitle>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => {
                  setSelectedCampaign(null);
                  setHistory([]);
                }}
                className="text-[#64748B] hover:text-[#F8FAFC]"
              >
                Close
              </Button>
            </div>
            <CardDescription className="text-[#64748B]">
              {status?.campaigns?.find(c => c.campaign_id === selectedCampaign)?.campaign_name}
            </CardDescription>
          </CardHeader>
          <CardContent>
            {historyLoading ? (
              <div className="text-center py-8">
                <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-[#3B82F6] mx-auto"></div>
                <p className="text-sm text-[#64748B] mt-2">Loading history...</p>
              </div>
            ) : history.length > 0 ? (
              <div className="space-y-3">
                {history.map((entry, idx) => (
                  <div key={idx} className="p-3 surface-secondary rounded-lg flex items-center justify-between">
                    <div className="flex items-center gap-4">
                      <div className={`p-2 rounded-lg ${
                        entry.new_bid > entry.old_bid 
                          ? "bg-[#10B981]/20" 
                          : "bg-[#EF4444]/20"
                      }`}>
                        {entry.new_bid > entry.old_bid 
                          ? <ArrowUp className="w-4 h-4 text-[#10B981]" />
                          : <ArrowDown className="w-4 h-4 text-[#EF4444]" />
                        }
                      </div>
                      <div>
                        <div className="flex items-center gap-2">
                          <span className="text-sm text-[#94A3B8]">${entry.old_bid?.toFixed(2)}</span>
                          <span className="text-[#64748B]">→</span>
                          <span className="text-sm font-medium text-[#F8FAFC]">${entry.new_bid?.toFixed(2)}</span>
                          <Badge className={entry.new_bid > entry.old_bid 
                            ? "bg-[#10B981]/20 text-[#10B981] border-0" 
                            : "bg-[#EF4444]/20 text-[#EF4444] border-0"
                          }>
                            {entry.new_bid > entry.old_bid ? "+" : ""}
                            {((entry.new_bid - entry.old_bid) / entry.old_bid * 100).toFixed(1)}%
                          </Badge>
                        </div>
                        <p className="text-xs text-[#64748B] mt-1">{entry.reason}</p>
                      </div>
                    </div>
                    <span className="text-xs text-[#64748B]">
                      {new Date(entry.timestamp).toLocaleString()}
                    </span>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8">
                <History className="w-10 h-10 mx-auto text-[#64748B] mb-2" />
                <p className="text-sm text-[#94A3B8]">No optimization history yet</p>
                <p className="text-xs text-[#64748B] mt-1">Run optimization to generate adjustments</p>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Enable Configuration Dialog */}
      <Dialog open={showConfig} onOpenChange={setShowConfig}>
        <DialogContent className="surface-primary border-panel">
          <DialogHeader>
            <DialogTitle className="text-[#F8FAFC]">Configure Bid Optimization</DialogTitle>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label className="text-[#94A3B8]">Target Win Rate (%)</Label>
              <Input
                type="number"
                min={5}
                max={80}
                value={configForm.targetWinRate}
                onChange={(e) => setConfigForm(prev => ({ ...prev, targetWinRate: parseInt(e.target.value) || 30 }))}
                className="surface-secondary border-[#2D3B55] text-[#F8FAFC]"
              />
              <p className="text-xs text-[#64748B]">Bid prices will be adjusted to achieve this win rate</p>
            </div>
            <div className="flex items-center justify-between p-3 surface-secondary rounded-lg">
              <div>
                <Label className="text-[#F8FAFC]">Auto-Adjust Mode</Label>
                <p className="text-xs text-[#64748B]">Automatically apply bid changes</p>
              </div>
              <Switch
                checked={configForm.autoAdjust}
                onCheckedChange={(checked) => setConfigForm(prev => ({ ...prev, autoAdjust: checked }))}
              />
            </div>
            <div className="p-3 surface-secondary rounded-lg border-l-2 border-[#3B82F6]">
              <p className="text-xs text-[#94A3B8]">
                <strong className="text-[#F8FAFC]">How it works:</strong> The optimizer analyzes win rate performance and adjusts bid prices to reach your target. In Auto mode, changes apply immediately. In Manual mode, you'll receive recommendations.
              </p>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowConfig(false)} className="border-[#2D3B55] text-[#94A3B8]">
              Cancel
            </Button>
            <Button 
              onClick={() => handleEnable(selectedCampaign)}
              className="bg-[#10B981] hover:bg-[#10B981]/90"
            >
              Enable Optimization
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
