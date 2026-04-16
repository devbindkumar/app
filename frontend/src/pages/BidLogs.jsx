import { useEffect, useState } from "react";
import { 
  RefreshCw, 
  CheckCircle, 
  XCircle,
  Clock,
  Zap,
  Filter,
  Calendar
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { Button } from "../components/ui/button";
import { Badge } from "../components/ui/badge";
import { ScrollArea } from "../components/ui/scroll-area";
import { Label } from "../components/ui/label";
import {
  Select, SelectContent, SelectItem, SelectTrigger, SelectValue,
} from "../components/ui/select";
import { toast } from "sonner";
import { getBidLogs, getBidLog } from "../lib/api";

// Simple JSON display component without recursion
function SimpleJsonViewer({ data }) {
  if (!data || typeof data !== 'object') {
    return <span className="text-slate-600 font-mono text-xs">{String(data)}</span>;
  }
  
  return (
    <pre className="text-xs font-mono text-slate-600 whitespace-pre-wrap overflow-auto max-h-64">
      {JSON.stringify(data, null, 2)}
    </pre>
  );
}

function BidLogEntry({ log, onSelect, isSelected }) {
  // Format timestamp to show date and time
  const formatDateTime = (timestamp) => {
    if (!timestamp) return "-";
    const date = new Date(timestamp);
    return date.toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      hour12: false
    });
  };

  return (
    <div 
      className={`log-entry p-3 border-b border-slate-200 cursor-pointer transition-colors duration-150 ${
        isSelected ? 'bg-[#3B82F6]/10 border-l-2 border-l-[#3B82F6]' : 'hover:bg-slate-100/50'
      }`}
      onClick={() => onSelect(log)}
      data-testid={`bid-log-${log.id}`}
    >
      {/* Date/Time Row */}
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-2 text-xs text-slate-500">
          <Calendar className="w-3 h-3" />
          <span className="font-medium">{formatDateTime(log.timestamp)}</span>
        </div>
        <div className="flex items-center gap-2 text-xs text-slate-500">
          <Clock className="w-3 h-3" />
          {log.processing_time_ms?.toFixed(1)}ms
        </div>
      </div>

      {/* Status Row */}
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-2">
          {log.bid_made ? (
            <CheckCircle className="w-4 h-4 text-[#10B981]" />
          ) : (
            <XCircle className="w-4 h-4 text-[#EF4444]" />
          )}
          <span className="text-sm font-medium text-slate-900">
            {log.bid_made ? 'Bid Made' : 'No Bid'}
          </span>
          <Badge 
            variant="outline" 
            className={log.openrtb_version === "2.6" 
              ? "version-badge version-2-6" 
              : "version-badge version-2-5"
            }
          >
            v{log.openrtb_version}
          </Badge>
        </div>
        {log.bid_made && log.bid_price && (
          <span className="text-sm font-mono text-[#10B981] font-medium">${log.bid_price.toFixed(2)}</span>
        )}
      </div>
      
      <div className="text-xs mb-2">
        <span className="text-slate-500">Request: </span>
        <span className="text-slate-600 font-mono">{log.request_id?.substring(0, 20)}...</span>
      </div>
      
      {log.request_summary && (
        <div className="flex flex-wrap gap-1">
          {log.request_summary.inventory_type && (
            <Badge variant="outline" className="text-[10px] bg-slate-100 text-slate-600 border-slate-200">
              {log.request_summary.inventory_type}
            </Badge>
          )}
          {log.request_summary.country && (
            <Badge variant="outline" className="text-[10px] bg-slate-100 text-slate-600 border-slate-200">
              {log.request_summary.country}
            </Badge>
          )}
          {log.request_summary.os && (
            <Badge variant="outline" className="text-[10px] bg-slate-100 text-slate-600 border-slate-200">
              {log.request_summary.os}
            </Badge>
          )}
          {(log.request_summary.make || log.request_summary.model) && (
            <Badge variant="outline" className="text-[10px] bg-[#F59E0B]/20 text-[#F59E0B] border-[#F59E0B]/30">
              {log.request_summary.make}{log.request_summary.model ? ` ${log.request_summary.model}` : ''}
            </Badge>
          )}
          {log.request_summary.has_video && (
            <Badge variant="outline" className="text-[10px] bg-[#10B981]/20 text-[#10B981] border-[#10B981]/30">
              video
            </Badge>
          )}
          {log.request_summary.has_banner && (
            <Badge variant="outline" className="text-[10px] bg-[#3B82F6]/20 text-[#3B82F6] border-[#3B82F6]/30">
              banner
            </Badge>
          )}
        </div>
      )}
    </div>
  );
}

export default function BidLogs() {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedLog, setSelectedLog] = useState(null);
  const [total, setTotal] = useState(0);
  const [stats, setStats] = useState({ bid_made: 0, no_bid: 0 });
  
  // Filter states
  const [filters, setFilters] = useState({
    bid_status: "",      // "", "bid_made", "no_bid"
  });

  const fetchLogs = async (filterParams = filters) => {
    try {
      setLoading(true);
      const params = {
        limit: 20,  // Load fewer for faster response
        offset: 0,
        ...(filterParams.bid_status && { bid_status: filterParams.bid_status }),
      };
      const response = await getBidLogs(params);
      setLogs(response.data.logs);
      setTotal(response.data.total);
      setStats(response.data.stats || { bid_made: 0, no_bid: 0 });
    } catch (error) {
      toast.error("Failed to load bid logs");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLogs();
  }, []);

  const handleSelectLog = async (log) => {
    try {
      const response = await getBidLog(log.id);
      setSelectedLog(response.data);
    } catch (error) {
      setSelectedLog(log);
    }
  };

  const handleFilterChange = (value) => {
    const newFilters = { bid_status: value === "all" ? "" : value };
    setFilters(newFilters);
    fetchLogs(newFilters);
  };

  const clearFilters = () => {
    const clearedFilters = { bid_status: "" };
    setFilters(clearedFilters);
    fetchLogs(clearedFilters);
  };

  const hasActiveFilters = !!filters.bid_status;

  return (
    <div className="p-6 h-[calc(100vh-1px)]" data-testid="bid-logs-page">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div>
          <h1 className="text-3xl font-bold text-slate-900">Bid Logs</h1>
          <p className="text-sm text-slate-600 mt-1">
            Real-time bid request and response monitoring
            {total > 0 && <span className="ml-2 text-slate-500">({total} total)</span>}
          </p>
        </div>
        <div className="flex items-center gap-3">
          {/* Bid Status Filter - Inline */}
          <div className="flex items-center gap-2">
            <Label className="text-xs text-slate-500">Status:</Label>
            <Select 
              value={filters.bid_status || "all"} 
              onValueChange={handleFilterChange}
            >
              <SelectTrigger className="w-[140px] h-9">
                <SelectValue placeholder="All statuses" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Statuses</SelectItem>
                <SelectItem value="bid_made">
                  <span className="flex items-center gap-2">
                    <CheckCircle className="w-3 h-3 text-[#10B981]" />
                    Bid Made
                  </span>
                </SelectItem>
                <SelectItem value="no_bid">
                  <span className="flex items-center gap-2">
                    <XCircle className="w-3 h-3 text-[#EF4444]" />
                    No Bid
                  </span>
                </SelectItem>
              </SelectContent>
            </Select>
          </div>
          
          <Button 
            variant="outline"
            onClick={() => fetchLogs()}
            className="border-slate-200 text-slate-600 hover:text-slate-900 hover:bg-slate-100"
            data-testid="refresh-logs-btn"
          >
            <RefreshCw className="w-4 h-4 mr-2" />
            Refresh
          </Button>
        </div>
      </div>

      {/* Stats Summary */}
      <div className="grid grid-cols-3 gap-3 mb-4">
        <Card className="surface-primary border-panel">
          <CardContent className="p-3 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Zap className="w-4 h-4 text-[#3B82F6]" />
              <span className="text-sm text-slate-600">Total</span>
            </div>
            <span className="text-lg font-bold text-slate-900">{total.toLocaleString()}</span>
          </CardContent>
        </Card>
        <Card className="surface-primary border-panel">
          <CardContent className="p-3 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <CheckCircle className="w-4 h-4 text-[#10B981]" />
              <span className="text-sm text-slate-600">Bid Made</span>
            </div>
            <span className="text-lg font-bold text-[#10B981]">{stats.bid_made.toLocaleString()}</span>
          </CardContent>
        </Card>
        <Card className="surface-primary border-panel">
          <CardContent className="p-3 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <XCircle className="w-4 h-4 text-[#EF4444]" />
              <span className="text-sm text-slate-600">No Bid</span>
            </div>
            <span className="text-lg font-bold text-[#EF4444]">{stats.no_bid.toLocaleString()}</span>
          </CardContent>
        </Card>
      </div>

      {loading ? (
        <div className="flex items-center justify-center h-64">
          <div className="text-slate-500">Loading logs...</div>
        </div>
      ) : logs.length === 0 ? (
        <Card className="surface-primary border-panel">
          <CardContent className="empty-state py-16">
            {hasActiveFilters ? (
              <>
                <Filter className="w-12 h-12 mx-auto mb-3 opacity-50 text-slate-400" />
                <h3 className="text-lg font-medium text-slate-900 mb-2">No logs match your filters</h3>
                <p className="text-sm text-slate-600 mb-4">Try adjusting your filter criteria</p>
                <Button variant="outline" onClick={clearFilters}>
                  Clear Filters
                </Button>
              </>
            ) : (
              <>
                <Zap className="empty-state-icon" />
                <h3 className="text-lg font-medium text-slate-900 mb-2">No bid logs yet</h3>
                <p className="text-sm text-slate-600">Bid requests will appear here once SSPs start sending traffic</p>
              </>
            )}
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-12 gap-4 h-[calc(100%-200px)]">
          {/* Log List */}
          <Card className="surface-primary border-panel col-span-5 flex flex-col">
            <CardHeader className="py-3 px-4 border-b border-slate-200">
              <CardTitle className="text-sm text-slate-900">Recent Requests</CardTitle>
            </CardHeader>
            <ScrollArea className="flex-1">
              {logs.map((log) => (
                <BidLogEntry 
                  key={log.id} 
                  log={log} 
                  onSelect={handleSelectLog}
                  isSelected={selectedLog?.id === log.id}
                />
              ))}
            </ScrollArea>
          </Card>

          {/* Log Detail */}
          <Card className="surface-primary border-panel col-span-7 flex flex-col">
            <CardHeader className="py-3 px-4 border-b border-slate-200">
              <CardTitle className="text-sm text-slate-900">Request Details</CardTitle>
            </CardHeader>
            <ScrollArea className="flex-1 p-4">
              {selectedLog ? (
                <div className="space-y-4">
                  {/* Summary */}
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <p className="text-[10px] text-slate-500 uppercase tracking-wider mb-1">Request ID</p>
                      <p className="text-xs font-mono text-slate-900">{selectedLog.request_id}</p>
                    </div>
                    <div>
                      <p className="text-[10px] text-slate-500 uppercase tracking-wider mb-1">OpenRTB Version</p>
                      <Badge 
                        variant="outline" 
                        className={selectedLog.openrtb_version === "2.6" 
                          ? "version-badge version-2-6" 
                          : "version-badge version-2-5"
                        }
                      >
                        v{selectedLog.openrtb_version}
                      </Badge>
                    </div>
                    <div>
                      <p className="text-[10px] text-slate-500 uppercase tracking-wider mb-1">Result</p>
                      <div className="flex items-center gap-1">
                        {selectedLog.bid_made ? (
                          <>
                            <CheckCircle className="w-3 h-3 text-[#10B981]" />
                            <span className="text-xs text-[#10B981]">Bid Made</span>
                          </>
                        ) : (
                          <>
                            <XCircle className="w-3 h-3 text-[#EF4444]" />
                            <span className="text-xs text-[#EF4444]">No Bid</span>
                          </>
                        )}
                      </div>
                    </div>
                    <div>
                      <p className="text-[10px] text-slate-500 uppercase tracking-wider mb-1">Processing Time</p>
                      <p className="text-xs font-mono text-slate-900">{selectedLog.processing_time_ms?.toFixed(2)}ms</p>
                    </div>
                  </div>

                  {/* Bid Info */}
                  {selectedLog.bid_made && (
                    <div className="p-3 surface-secondary rounded border border-slate-200">
                      <p className="text-[10px] text-slate-500 uppercase tracking-wider mb-2">Winning Bid</p>
                      <div className="grid grid-cols-3 gap-4">
                        <div>
                          <p className="text-[10px] text-slate-500">Price (CPM)</p>
                          <p className="text-sm font-mono text-[#3B82F6]">${selectedLog.bid_price?.toFixed(2)}</p>
                        </div>
                        <div>
                          <p className="text-[10px] text-slate-500">Campaign</p>
                          <p className="text-xs font-mono text-slate-900 truncate">{selectedLog.campaign_id?.substring(0, 12)}...</p>
                        </div>
                        <div>
                          <p className="text-[10px] text-slate-500">Creative</p>
                          <p className="text-xs font-mono text-slate-900 truncate">{selectedLog.creative_id?.substring(0, 12)}...</p>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Device Info */}
                  {selectedLog.request_summary && (
                    <div className="p-3 surface-secondary rounded border border-[#F59E0B]/30">
                      <p className="text-[10px] text-[#F59E0B] uppercase tracking-wider mb-2">Device Information</p>
                      <div className="grid grid-cols-4 gap-4">
                        <div>
                          <p className="text-[10px] text-slate-500">Make</p>
                          <p className="text-xs font-medium text-slate-900">{selectedLog.request_summary.make || '-'}</p>
                        </div>
                        <div>
                          <p className="text-[10px] text-slate-500">Model</p>
                          <p className="text-xs font-medium text-slate-900">{selectedLog.request_summary.model || '-'}</p>
                        </div>
                        <div>
                          <p className="text-[10px] text-slate-500">OS</p>
                          <p className="text-xs font-medium text-slate-900">{selectedLog.request_summary.os || '-'}</p>
                        </div>
                        <div>
                          <p className="text-[10px] text-slate-500">Device Type</p>
                          <p className="text-xs font-medium text-slate-900">
                            {selectedLog.request_summary.device_type === 1 ? 'Mobile' : 
                             selectedLog.request_summary.device_type === 2 ? 'Desktop' :
                             selectedLog.request_summary.device_type === 3 ? 'CTV' :
                             selectedLog.request_summary.device_type === 4 ? 'Phone' :
                             selectedLog.request_summary.device_type === 5 ? 'Tablet' :
                             selectedLog.request_summary.device_type || '-'}
                          </p>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Bid Response JSON - Only show if bid was made */}
                  {selectedLog.bid_made && selectedLog.bid_response && (
                    <div>
                      <p className="text-[10px] text-slate-500 uppercase tracking-wider mb-2">
                        Bid Response (OpenRTB)
                      </p>
                      <div className="p-3 bg-[#3B82F6]/5 rounded border border-[#3B82F6]/20 overflow-auto max-h-96">
                        <SimpleJsonViewer data={selectedLog.bid_response} />
                      </div>
                    </div>
                  )}

                  {/* Rejection Reasons */}
                  {selectedLog.rejection_reasons?.length > 0 && (
                    <div className="p-3 bg-[#EF4444]/10 rounded border border-[#EF4444]/30">
                      <p className="text-[10px] text-[#EF4444] uppercase tracking-wider mb-2">Rejection Reasons</p>
                      <ul className="space-y-1">
                        {selectedLog.rejection_reasons.map((reason, i) => (
                          <li key={i} className="text-xs text-[#EF4444]">• {reason}</li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {/* Matched Campaigns */}
                  {selectedLog.matched_campaigns?.length > 0 && (
                    <div>
                      <p className="text-[10px] text-slate-500 uppercase tracking-wider mb-2">Matched Campaigns</p>
                      <div className="flex flex-wrap gap-1">
                        {selectedLog.matched_campaigns.map((id, i) => (
                          <Badge key={i} variant="outline" className="text-[10px] bg-[#10B981]/10 text-[#10B981] border-[#10B981]/30">
                            {id.substring(0, 8)}...
                          </Badge>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Request Summary JSON */}
                  {selectedLog.request_summary && (
                    <div>
                      <p className="text-[10px] text-slate-500 uppercase tracking-wider mb-2">Request Summary</p>
                      <div className="p-3 bg-slate-50 rounded border border-slate-200 overflow-auto max-h-64">
                        <SimpleJsonViewer data={selectedLog.request_summary} />
                      </div>
                    </div>
                  )}
                </div>
              ) : (
                <div className="flex items-center justify-center h-full text-slate-500">
                  Select a log entry to view details
                </div>
              )}
            </ScrollArea>
          </Card>
        </div>
      )}
    </div>
  );
}
