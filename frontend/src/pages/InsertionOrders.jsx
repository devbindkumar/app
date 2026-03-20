import { useState, useEffect } from "react";
import { 
  FileText, Plus, Trash2, Edit2, ChevronDown, ChevronRight, DollarSign, 
  Calendar, Target, Layers, Play, Pause, RefreshCw, TrendingUp, 
  BarChart3, Settings, ArrowRight, Clock, Users, Zap
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "../components/ui/card";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Label } from "../components/ui/label";
import { Badge } from "../components/ui/badge";
import { Progress } from "../components/ui/progress";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "../components/ui/tabs";
import { 
  Select, SelectContent, SelectItem, SelectTrigger, SelectValue 
} from "../components/ui/select";
import {
  Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogFooter
} from "../components/ui/dialog";
import { toast } from "sonner";
import { 
  getInsertionOrders, createInsertionOrder, updateInsertionOrder, deleteInsertionOrder,
  getLineItems, createLineItem, updateLineItem, deleteLineItem, recommendLineItems,
  getCampaigns
} from "../lib/api";

const STATUS_COLORS = {
  draft: { bg: "bg-[#64748B]/20", text: "text-slate-600" },
  active: { bg: "bg-[#10B981]/20", text: "text-[#10B981]" },
  paused: { bg: "bg-[#F59E0B]/20", text: "text-[#F59E0B]" },
  completed: { bg: "bg-[#3B82F6]/20", text: "text-[#3B82F6]" },
  pending_approval: { bg: "bg-[#8B5CF6]/20", text: "text-[#8B5CF6]" },
  cancelled: { bg: "bg-[#EF4444]/20", text: "text-[#EF4444]" },
};

const LINE_ITEM_TYPES = [
  { value: "prospecting", label: "Prospecting", color: "#3B82F6" },
  { value: "retargeting", label: "Retargeting", color: "#10B981" },
  { value: "contextual", label: "Contextual", color: "#F59E0B" },
  { value: "audience", label: "Audience", color: "#8B5CF6" },
  { value: "lookalike", label: "Lookalike", color: "#EC4899" },
];

const INVENTORY_SOURCES = [
  { value: "open_exchange", label: "Open Exchange" },
  { value: "pmp", label: "Private Marketplace" },
  { value: "pg", label: "Programmatic Guaranteed" },
  { value: "youtube", label: "YouTube" },
  { value: "gdn", label: "Google Display Network" },
];

const BID_STRATEGIES = [
  { value: "manual_cpm", label: "Manual CPM" },
  { value: "manual_cpc", label: "Manual CPC" },
  { value: "target_cpa", label: "Target CPA" },
  { value: "maximize_conversions", label: "Maximize Conversions" },
  { value: "maximize_clicks", label: "Maximize Clicks" },
];

export default function InsertionOrders() {
  const [insertionOrders, setInsertionOrders] = useState([]);
  const [lineItems, setLineItems] = useState({});
  const [campaigns, setCampaigns] = useState([]);
  const [loading, setLoading] = useState(true);
  const [expandedIO, setExpandedIO] = useState(null);
  const [recommendations, setRecommendations] = useState(null);
  
  // Dialogs
  const [showIODialog, setShowIODialog] = useState(false);
  const [showLineItemDialog, setShowLineItemDialog] = useState(false);
  const [editingIO, setEditingIO] = useState(null);
  const [editingLineItem, setEditingLineItem] = useState(null);
  const [selectedIOForLineItem, setSelectedIOForLineItem] = useState(null);
  
  // Form states
  const [ioForm, setIOForm] = useState({
    name: "",
    advertiser_id: "",
    campaign_id: "",
    total_budget: 10000,
    currency: "USD",
    structure_type: "audience",
    start_date: "",
    end_date: "",
  });
  
  const [lineItemForm, setLineItemForm] = useState({
    name: "",
    line_item_type: "prospecting",
    budget: 1000,
    bid_strategy: "manual_cpm",
    bid_price: 2.0,
    inventory_source: "open_exchange",
  });

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      const [iosRes, campaignsRes] = await Promise.all([
        getInsertionOrders(),
        getCampaigns()
      ]);
      setInsertionOrders(iosRes.data || []);
      setCampaigns(campaignsRes.data || []);
      
      // Load line items for each IO
      const lineItemsMap = {};
      for (const io of (iosRes.data || [])) {
        const liRes = await getLineItems(io.id);
        lineItemsMap[io.id] = liRes.data || [];
      }
      setLineItems(lineItemsMap);
    } catch (err) {
      toast.error("Failed to load data");
    } finally {
      setLoading(false);
    }
  };

  const handleCreateIO = async () => {
    try {
      const payload = {
        ...ioForm,
        campaign_id: ioForm.campaign_id === "none" ? "" : ioForm.campaign_id,
        start_date: ioForm.start_date || null,
        end_date: ioForm.end_date || null,
      };
      await createInsertionOrder(payload);
      toast.success("Insertion order created");
      setShowIODialog(false);
      resetIOForm();
      loadData();
    } catch (err) {
      toast.error("Failed to create insertion order");
    }
  };

  const handleUpdateIO = async () => {
    try {
      await updateInsertionOrder(editingIO.id, ioForm);
      toast.success("Insertion order updated");
      setShowIODialog(false);
      setEditingIO(null);
      resetIOForm();
      loadData();
    } catch (err) {
      toast.error("Failed to update insertion order");
    }
  };

  const handleDeleteIO = async (ioId) => {
    if (!window.confirm("Delete this insertion order and all its line items?")) return;
    try {
      await deleteInsertionOrder(ioId);
      toast.success("Insertion order deleted");
      loadData();
    } catch (err) {
      toast.error("Failed to delete insertion order");
    }
  };

  const handleCreateLineItem = async () => {
    try {
      await createLineItem({
        ...lineItemForm,
        io_id: selectedIOForLineItem,
      });
      toast.success("Line item created");
      setShowLineItemDialog(false);
      resetLineItemForm();
      loadData();
    } catch (err) {
      toast.error("Failed to create line item");
    }
  };

  const handleUpdateLineItem = async () => {
    try {
      await updateLineItem(editingLineItem.id, lineItemForm);
      toast.success("Line item updated");
      setShowLineItemDialog(false);
      setEditingLineItem(null);
      resetLineItemForm();
      loadData();
    } catch (err) {
      toast.error("Failed to update line item");
    }
  };

  const handleDeleteLineItem = async (itemId) => {
    if (!window.confirm("Delete this line item?")) return;
    try {
      await deleteLineItem(itemId);
      toast.success("Line item deleted");
      loadData();
    } catch (err) {
      toast.error("Failed to delete line item");
    }
  };

  const handleStatusChange = async (ioId, newStatus) => {
    try {
      await updateInsertionOrder(ioId, { status: newStatus });
      toast.success(`Status updated to ${newStatus}`);
      loadData();
    } catch (err) {
      toast.error("Failed to update status");
    }
  };

  const getRecommendations = async (goal, budget) => {
    try {
      const res = await recommendLineItems(goal, budget, "prospecting");
      setRecommendations(res.data);
    } catch (err) {
      toast.error("Failed to get recommendations");
    }
  };

  const applyRecommendation = (rec) => {
    setLineItemForm({
      name: rec.name,
      line_item_type: rec.type,
      budget: rec.budget,
      bid_strategy: rec.bid_strategy,
      bid_price: 2.0,
      inventory_source: rec.inventory_source,
    });
    setRecommendations(null);
  };

  const resetIOForm = () => {
    setIOForm({
      name: "",
      advertiser_id: "",
      campaign_id: "",
      total_budget: 10000,
      currency: "USD",
      structure_type: "audience",
      start_date: "",
      end_date: "",
    });
  };

  const resetLineItemForm = () => {
    setLineItemForm({
      name: "",
      line_item_type: "prospecting",
      budget: 1000,
      bid_strategy: "manual_cpm",
      bid_price: 2.0,
      inventory_source: "open_exchange",
    });
  };

  const openEditIO = (io) => {
    setEditingIO(io);
    setIOForm({
      name: io.name,
      advertiser_id: io.advertiser_id || "",
      campaign_id: io.campaign_id || "",
      total_budget: io.total_budget,
      currency: io.currency,
      structure_type: io.structure_type,
      start_date: io.start_date?.split('T')[0] || "",
      end_date: io.end_date?.split('T')[0] || "",
    });
    setShowIODialog(true);
  };

  const openEditLineItem = (item, ioId) => {
    setEditingLineItem(item);
    setSelectedIOForLineItem(ioId);
    setLineItemForm({
      name: item.name,
      line_item_type: item.line_item_type,
      budget: item.budget,
      bid_strategy: item.bid_strategy,
      bid_price: item.bid_price,
      inventory_source: item.inventory_source,
    });
    setShowLineItemDialog(true);
  };

  const openAddLineItem = (ioId, io) => {
    setSelectedIOForLineItem(ioId);
    resetLineItemForm();
    setShowLineItemDialog(true);
    // Get recommendations based on IO
    getRecommendations("conversions", io.total_budget);
  };

  const formatCurrency = (amount, currency = "USD") => {
    return new Intl.NumberFormat('en-US', { style: 'currency', currency }).format(amount);
  };

  const getLineItemTypeColor = (type) => {
    return LINE_ITEM_TYPES.find(t => t.value === type)?.color || "#64748B";
  };

  const calcIOSpent = (ioId) => {
    const items = lineItems[ioId] || [];
    return items.reduce((sum, item) => sum + (item.spent || 0), 0);
  };

  const calcIOImpressions = (ioId) => {
    const items = lineItems[ioId] || [];
    return items.reduce((sum, item) => sum + (item.impressions || 0), 0);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <RefreshCw className="w-8 h-8 animate-spin text-[#3B82F6]" />
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6" data-testid="insertion-orders-page">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-slate-900">Insertion Orders</h1>
          <p className="text-sm text-slate-600 mt-1">
            Manage insertion orders and line items for structured campaign delivery
          </p>
        </div>
        <Button 
          onClick={() => { resetIOForm(); setEditingIO(null); setShowIODialog(true); }}
          className="bg-[#3B82F6] hover:bg-[#2563EB]"
          data-testid="create-io-btn"
        >
          <Plus className="w-4 h-4 mr-2" />
          New Insertion Order
        </Button>
      </div>

      {/* Stats Overview */}
      <div className="grid grid-cols-4 gap-4">
        <Card className="surface-primary border-panel">
          <CardContent className="p-4">
            <div className="flex items-center gap-2 mb-1">
              <FileText className="w-4 h-4 text-[#3B82F6]" />
              <span className="text-xs text-slate-500">Total IOs</span>
            </div>
            <p className="text-2xl font-bold text-slate-900">{insertionOrders.length}</p>
          </CardContent>
        </Card>
        <Card className="surface-primary border-panel">
          <CardContent className="p-4">
            <div className="flex items-center gap-2 mb-1">
              <Layers className="w-4 h-4 text-[#10B981]" />
              <span className="text-xs text-slate-500">Total Line Items</span>
            </div>
            <p className="text-2xl font-bold text-slate-900">
              {Object.values(lineItems).flat().length}
            </p>
          </CardContent>
        </Card>
        <Card className="surface-primary border-panel">
          <CardContent className="p-4">
            <div className="flex items-center gap-2 mb-1">
              <DollarSign className="w-4 h-4 text-[#F59E0B]" />
              <span className="text-xs text-slate-500">Total Budget</span>
            </div>
            <p className="text-2xl font-bold text-slate-900">
              {formatCurrency(insertionOrders.reduce((sum, io) => sum + io.total_budget, 0))}
            </p>
          </CardContent>
        </Card>
        <Card className="surface-primary border-panel">
          <CardContent className="p-4">
            <div className="flex items-center gap-2 mb-1">
              <Play className="w-4 h-4 text-[#8B5CF6]" />
              <span className="text-xs text-slate-500">Active IOs</span>
            </div>
            <p className="text-2xl font-bold text-slate-900">
              {insertionOrders.filter(io => io.status === 'active').length}
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Insertion Orders List */}
      {insertionOrders.length === 0 ? (
        <Card className="surface-primary border-panel">
          <CardContent className="py-12 text-center">
            <FileText className="w-16 h-16 mx-auto text-slate-500 mb-4" />
            <h3 className="text-lg font-medium text-slate-900 mb-2">No Insertion Orders</h3>
            <p className="text-sm text-slate-600 mb-4">
              Create your first insertion order to start structuring campaigns
            </p>
            <Button 
              onClick={() => { resetIOForm(); setShowIODialog(true); }}
              className="bg-[#3B82F6] hover:bg-[#2563EB]"
            >
              <Plus className="w-4 h-4 mr-2" />
              Create Insertion Order
            </Button>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-4">
          {insertionOrders.map((io) => {
            const isExpanded = expandedIO === io.id;
            const ioLineItems = lineItems[io.id] || [];
            const spent = calcIOSpent(io.id);
            const budgetPercent = io.total_budget > 0 ? (spent / io.total_budget) * 100 : 0;
            
            return (
              <Card key={io.id} className="surface-primary border-panel">
                {/* IO Header */}
                <div 
                  className="p-4 cursor-pointer hover:bg-slate-100/30 transition-colors"
                  onClick={() => setExpandedIO(isExpanded ? null : io.id)}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-4">
                      <div className="p-2 rounded-lg bg-[#3B82F6]/20">
                        {isExpanded ? (
                          <ChevronDown className="w-5 h-5 text-[#3B82F6]" />
                        ) : (
                          <ChevronRight className="w-5 h-5 text-[#3B82F6]" />
                        )}
                      </div>
                      <div>
                        <div className="flex items-center gap-2">
                          <h3 className="text-lg font-semibold text-slate-900">{io.name}</h3>
                          <Badge className={`${STATUS_COLORS[io.status]?.bg} ${STATUS_COLORS[io.status]?.text}`}>
                            {io.status}
                          </Badge>
                        </div>
                        <p className="text-sm text-slate-500 mt-1">
                          {ioLineItems.length} line items • {io.structure_type} structure
                        </p>
                      </div>
                    </div>
                    
                    <div className="flex items-center gap-6">
                      {/* Budget Progress */}
                      <div className="w-48">
                        <div className="flex justify-between text-xs mb-1">
                          <span className="text-slate-500">Budget</span>
                          <span className="text-slate-900">
                            {formatCurrency(spent)} / {formatCurrency(io.total_budget)}
                          </span>
                        </div>
                        <Progress value={budgetPercent} className="h-2" />
                      </div>
                      
                      {/* Performance */}
                      <div className="text-right">
                        <p className="text-lg font-semibold text-slate-900">
                          {calcIOImpressions(io.id).toLocaleString()}
                        </p>
                        <p className="text-xs text-slate-500">Impressions</p>
                      </div>
                      
                      {/* Actions */}
                      <div className="flex items-center gap-2" onClick={(e) => e.stopPropagation()}>
                        {io.status === 'active' ? (
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => handleStatusChange(io.id, 'paused')}
                            className="border-[#F59E0B] text-[#F59E0B] hover:bg-[#F59E0B]/10"
                          >
                            <Pause className="w-3 h-3 mr-1" />
                            Pause
                          </Button>
                        ) : io.status !== 'completed' && (
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => handleStatusChange(io.id, 'active')}
                            className="border-[#10B981] text-[#10B981] hover:bg-[#10B981]/10"
                          >
                            <Play className="w-3 h-3 mr-1" />
                            Activate
                          </Button>
                        )}
                        <Button
                          size="icon"
                          variant="ghost"
                          onClick={() => openEditIO(io)}
                          className="text-slate-600 hover:text-slate-900"
                        >
                          <Edit2 className="w-4 h-4" />
                        </Button>
                        <Button
                          size="icon"
                          variant="ghost"
                          onClick={() => handleDeleteIO(io.id)}
                          className="text-[#EF4444] hover:text-[#EF4444] hover:bg-[#EF4444]/10"
                        >
                          <Trash2 className="w-4 h-4" />
                        </Button>
                      </div>
                    </div>
                  </div>
                </div>
                
                {/* Expanded Line Items */}
                {isExpanded && (
                  <div className="border-t border-slate-200 p-4 bg-slate-50/50">
                    <div className="flex items-center justify-between mb-4">
                      <h4 className="text-sm font-medium text-slate-600">Line Items</h4>
                      <Button
                        size="sm"
                        onClick={() => openAddLineItem(io.id, io)}
                        className="bg-[#10B981] hover:bg-[#059669]"
                      >
                        <Plus className="w-3 h-3 mr-1" />
                        Add Line Item
                      </Button>
                    </div>
                    
                    {ioLineItems.length === 0 ? (
                      <div className="text-center py-8">
                        <Layers className="w-10 h-10 mx-auto text-slate-500 mb-2" />
                        <p className="text-sm text-slate-500">No line items yet</p>
                      </div>
                    ) : (
                      <div className="space-y-3">
                        {ioLineItems.map((item) => {
                          const itemBudgetPercent = item.budget > 0 ? (item.spent / item.budget) * 100 : 0;
                          return (
                            <div 
                              key={item.id} 
                              className="p-3 surface-secondary rounded-lg border-l-4"
                              style={{ borderLeftColor: getLineItemTypeColor(item.line_item_type) }}
                            >
                              <div className="flex items-center justify-between">
                                <div className="flex items-center gap-3">
                                  <div>
                                    <div className="flex items-center gap-2">
                                      <span className="text-sm font-medium text-slate-900">{item.name}</span>
                                      <Badge 
                                        className="text-xs capitalize"
                                        style={{ 
                                          backgroundColor: getLineItemTypeColor(item.line_item_type) + '20',
                                          color: getLineItemTypeColor(item.line_item_type)
                                        }}
                                      >
                                        {item.line_item_type}
                                      </Badge>
                                      <Badge className="bg-slate-200 text-slate-600 text-xs">
                                        {item.inventory_source}
                                      </Badge>
                                    </div>
                                    <div className="flex items-center gap-4 mt-1 text-xs text-slate-500">
                                      <span>Strategy: {item.bid_strategy?.replace(/_/g, ' ')}</span>
                                      <span>Bid: ${item.bid_price?.toFixed(2)}</span>
                                    </div>
                                  </div>
                                </div>
                                
                                <div className="flex items-center gap-6">
                                  {/* Line Item Budget */}
                                  <div className="w-32">
                                    <div className="flex justify-between text-xs mb-1">
                                      <span className="text-slate-500">Budget</span>
                                      <span className="text-slate-900">{formatCurrency(item.budget)}</span>
                                    </div>
                                    <Progress value={itemBudgetPercent} className="h-1.5" />
                                  </div>
                                  
                                  {/* Stats */}
                                  <div className="flex gap-4 text-xs">
                                    <div className="text-right">
                                      <p className="text-slate-900 font-medium">{item.impressions?.toLocaleString() || 0}</p>
                                      <p className="text-slate-500">Impr.</p>
                                    </div>
                                    <div className="text-right">
                                      <p className="text-slate-900 font-medium">{item.clicks?.toLocaleString() || 0}</p>
                                      <p className="text-slate-500">Clicks</p>
                                    </div>
                                  </div>
                                  
                                  {/* Actions */}
                                  <div className="flex gap-1">
                                    <Button
                                      size="icon"
                                      variant="ghost"
                                      onClick={() => openEditLineItem(item, io.id)}
                                      className="h-8 w-8 text-slate-600 hover:text-slate-900"
                                    >
                                      <Edit2 className="w-3 h-3" />
                                    </Button>
                                    <Button
                                      size="icon"
                                      variant="ghost"
                                      onClick={() => handleDeleteLineItem(item.id)}
                                      className="h-8 w-8 text-[#EF4444] hover:bg-[#EF4444]/10"
                                    >
                                      <Trash2 className="w-3 h-3" />
                                    </Button>
                                  </div>
                                </div>
                              </div>
                            </div>
                          );
                        })}
                      </div>
                    )}
                  </div>
                )}
              </Card>
            );
          })}
        </div>
      )}

      {/* Create/Edit IO Dialog */}
      <Dialog open={showIODialog} onOpenChange={setShowIODialog}>
        <DialogContent className="surface-primary border-panel max-w-lg">
          <DialogHeader>
            <DialogTitle className="text-slate-900">
              {editingIO ? "Edit Insertion Order" : "Create Insertion Order"}
            </DialogTitle>
            <DialogDescription className="text-slate-500">
              Configure your insertion order settings
            </DialogDescription>
          </DialogHeader>
          
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label className="text-slate-600">Name *</Label>
              <Input
                value={ioForm.name}
                onChange={(e) => setIOForm(prev => ({ ...prev, name: e.target.value }))}
                placeholder="e.g., Q1 Brand Campaign"
                className="surface-secondary border-slate-200 text-slate-900"
                data-testid="io-name-input"
              />
            </div>
            
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label className="text-slate-600">Total Budget</Label>
                <Input
                  type="number"
                  value={ioForm.total_budget}
                  onChange={(e) => setIOForm(prev => ({ ...prev, total_budget: parseFloat(e.target.value) || 0 }))}
                  className="surface-secondary border-slate-200 text-slate-900"
                />
              </div>
              <div className="space-y-2">
                <Label className="text-slate-600">Currency</Label>
                <Select 
                  value={ioForm.currency} 
                  onValueChange={(v) => setIOForm(prev => ({ ...prev, currency: v }))}
                >
                  <SelectTrigger className="surface-secondary border-slate-200 text-slate-900">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent className="surface-primary border-slate-200">
                    {["USD", "EUR", "GBP", "CAD", "AUD"].map(c => (
                      <SelectItem key={c} value={c} className="text-slate-900">{c}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>
            
            <div className="space-y-2">
              <Label className="text-slate-600">Structure Type</Label>
              <Select 
                value={ioForm.structure_type} 
                onValueChange={(v) => setIOForm(prev => ({ ...prev, structure_type: v }))}
              >
                <SelectTrigger className="surface-secondary border-slate-200 text-slate-900">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent className="surface-primary border-slate-200">
                  <SelectItem value="audience" className="text-slate-900">By Audience</SelectItem>
                  <SelectItem value="tactic" className="text-slate-900">By Tactic</SelectItem>
                  <SelectItem value="goal" className="text-slate-900">By Goal</SelectItem>
                </SelectContent>
              </Select>
            </div>
            
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label className="text-slate-600">Start Date</Label>
                <Input
                  type="date"
                  value={ioForm.start_date}
                  onChange={(e) => setIOForm(prev => ({ ...prev, start_date: e.target.value }))}
                  className="surface-secondary border-slate-200 text-slate-900"
                />
              </div>
              <div className="space-y-2">
                <Label className="text-slate-600">End Date</Label>
                <Input
                  type="date"
                  value={ioForm.end_date}
                  onChange={(e) => setIOForm(prev => ({ ...prev, end_date: e.target.value }))}
                  className="surface-secondary border-slate-200 text-slate-900"
                />
              </div>
            </div>
            
            <div className="space-y-2">
              <Label className="text-slate-600">Link to Campaign (optional)</Label>
              <Select 
                value={ioForm.campaign_id} 
                onValueChange={(v) => setIOForm(prev => ({ ...prev, campaign_id: v }))}
              >
                <SelectTrigger className="surface-secondary border-slate-200 text-slate-900">
                  <SelectValue placeholder="Select campaign" />
                </SelectTrigger>
                <SelectContent className="surface-primary border-slate-200">
                  <SelectItem value="none" className="text-slate-900">None</SelectItem>
                  {campaigns.map(c => (
                    <SelectItem key={c.id} value={c.id} className="text-slate-900">{c.name}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>
          
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowIODialog(false)} className="border-slate-200 text-slate-600">
              Cancel
            </Button>
            <Button 
              onClick={editingIO ? handleUpdateIO : handleCreateIO}
              className="bg-[#3B82F6] hover:bg-[#2563EB]"
              disabled={!ioForm.name}
              data-testid="save-io-btn"
            >
              {editingIO ? "Update" : "Create"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Create/Edit Line Item Dialog */}
      <Dialog open={showLineItemDialog} onOpenChange={setShowLineItemDialog}>
        <DialogContent className="surface-primary border-panel max-w-2xl">
          <DialogHeader>
            <DialogTitle className="text-slate-900">
              {editingLineItem ? "Edit Line Item" : "Create Line Item"}
            </DialogTitle>
            <DialogDescription className="text-slate-500">
              Configure line item targeting and bidding
            </DialogDescription>
          </DialogHeader>
          
          <div className="grid grid-cols-2 gap-6 py-4">
            <div className="space-y-4">
              <div className="space-y-2">
                <Label className="text-slate-600">Name *</Label>
                <Input
                  value={lineItemForm.name}
                  onChange={(e) => setLineItemForm(prev => ({ ...prev, name: e.target.value }))}
                  placeholder="e.g., Retargeting - High Intent"
                  className="surface-secondary border-slate-200 text-slate-900"
                  data-testid="line-item-name-input"
                />
              </div>
              
              <div className="space-y-2">
                <Label className="text-slate-600">Line Item Type</Label>
                <Select 
                  value={lineItemForm.line_item_type} 
                  onValueChange={(v) => setLineItemForm(prev => ({ ...prev, line_item_type: v }))}
                >
                  <SelectTrigger className="surface-secondary border-slate-200 text-slate-900">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent className="surface-primary border-slate-200">
                    {LINE_ITEM_TYPES.map(type => (
                      <SelectItem key={type.value} value={type.value} className="text-slate-900">
                        {type.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              
              <div className="space-y-2">
                <Label className="text-slate-600">Budget</Label>
                <Input
                  type="number"
                  value={lineItemForm.budget}
                  onChange={(e) => setLineItemForm(prev => ({ ...prev, budget: parseFloat(e.target.value) || 0 }))}
                  className="surface-secondary border-slate-200 text-slate-900"
                />
              </div>
              
              <div className="space-y-2">
                <Label className="text-slate-600">Bid Strategy</Label>
                <Select 
                  value={lineItemForm.bid_strategy} 
                  onValueChange={(v) => setLineItemForm(prev => ({ ...prev, bid_strategy: v }))}
                >
                  <SelectTrigger className="surface-secondary border-slate-200 text-slate-900">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent className="surface-primary border-slate-200">
                    {BID_STRATEGIES.map(s => (
                      <SelectItem key={s.value} value={s.value} className="text-slate-900">
                        {s.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label className="text-slate-600">Bid Price</Label>
                  <Input
                    type="number"
                    step="0.01"
                    value={lineItemForm.bid_price}
                    onChange={(e) => setLineItemForm(prev => ({ ...prev, bid_price: parseFloat(e.target.value) || 0 }))}
                    className="surface-secondary border-slate-200 text-slate-900"
                  />
                </div>
                <div className="space-y-2">
                  <Label className="text-slate-600">Inventory Source</Label>
                  <Select 
                    value={lineItemForm.inventory_source} 
                    onValueChange={(v) => setLineItemForm(prev => ({ ...prev, inventory_source: v }))}
                  >
                    <SelectTrigger className="surface-secondary border-slate-200 text-slate-900">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent className="surface-primary border-slate-200">
                      {INVENTORY_SOURCES.map(s => (
                        <SelectItem key={s.value} value={s.value} className="text-slate-900">
                          {s.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>
            </div>
            
            {/* Recommendations Panel */}
            {recommendations && !editingLineItem && (
              <div className="space-y-3">
                <div className="flex items-center gap-2 mb-2">
                  <Zap className="w-4 h-4 text-[#F59E0B]" />
                  <Label className="text-[#F59E0B]">Recommended Line Items</Label>
                </div>
                {recommendations.recommendations?.slice(0, 3).map((rec, idx) => (
                  <div 
                    key={idx} 
                    onClick={() => applyRecommendation(rec)}
                    className="p-3 surface-secondary rounded-lg cursor-pointer hover:bg-slate-200 transition-colors border-l-2"
                    style={{ borderLeftColor: getLineItemTypeColor(rec.type) }}
                  >
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-sm font-medium text-slate-900">{rec.name}</span>
                      <Badge 
                        className="text-xs"
                        style={{ 
                          backgroundColor: getLineItemTypeColor(rec.type) + '20',
                          color: getLineItemTypeColor(rec.type)
                        }}
                      >
                        {rec.type}
                      </Badge>
                    </div>
                    <p className="text-xs text-slate-500">{rec.description}</p>
                    <div className="flex gap-3 mt-2 text-xs text-slate-600">
                      <span>Budget: ${rec.budget}</span>
                      <span>{rec.inventory_source}</span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
          
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowLineItemDialog(false)} className="border-slate-200 text-slate-600">
              Cancel
            </Button>
            <Button 
              onClick={editingLineItem ? handleUpdateLineItem : handleCreateLineItem}
              className="bg-[#10B981] hover:bg-[#059669]"
              disabled={!lineItemForm.name}
              data-testid="save-line-item-btn"
            >
              {editingLineItem ? "Update" : "Create"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
