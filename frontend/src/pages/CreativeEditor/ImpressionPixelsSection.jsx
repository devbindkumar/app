import { Plus, Trash2, ToggleLeft, ToggleRight, Code } from "lucide-react";
import { Input } from "../../components/ui/input";
import { Label } from "../../components/ui/label";
import { Button } from "../../components/ui/button";
import { 
  Select, 
  SelectContent, 
  SelectItem, 
  SelectTrigger, 
  SelectValue 
} from "../../components/ui/select";
import { Badge } from "../../components/ui/badge";

/**
 * Impression Pixels Section Component
 */
export function ImpressionPixelsSection({
  impressionPixels,
  onAdd,
  onUpdate,
  onRemove,
  onToggle,
  onShowMacros,
  macrosLoading
}) {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <Label className="text-slate-900">Impression Tracking Pixels</Label>
          <p className="text-xs text-slate-500 mt-1">
            Add third-party pixels to track impressions. Use macros for dynamic values.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button
            type="button"
            variant="outline"
            size="sm"
            onClick={onShowMacros}
            disabled={macrosLoading}
            className="text-xs"
          >
            <Code className="w-3 h-3 mr-1" />
            {macrosLoading ? "Loading..." : "View Macros"}
          </Button>
          <Button
            type="button"
            variant="outline"
            size="sm"
            onClick={onAdd}
            className="text-[#3B82F6] border-[#3B82F6]/30 hover:bg-[#3B82F6]/10"
          >
            <Plus className="w-4 h-4 mr-1" />
            Add Pixel
          </Button>
        </div>
      </div>
      
      {impressionPixels.length === 0 ? (
        <div className="border-2 border-dashed border-slate-200 rounded-lg p-6 text-center">
          <p className="text-sm text-slate-500">No impression pixels configured</p>
          <p className="text-xs text-slate-400 mt-1">
            Click "Add Pixel" to add third-party tracking
          </p>
        </div>
      ) : (
        <div className="space-y-3">
          {impressionPixels.map((pixel, index) => (
            <ImpressionPixelRow
              key={pixel.id || index}
              pixel={pixel}
              index={index}
              onUpdate={onUpdate}
              onRemove={onRemove}
              onToggle={onToggle}
            />
          ))}
        </div>
      )}
    </div>
  );
}

function ImpressionPixelRow({ pixel, index, onUpdate, onRemove, onToggle }) {
  return (
    <div className={`p-4 rounded-lg border ${pixel.enabled ? 'border-slate-200 bg-white' : 'border-slate-100 bg-slate-50 opacity-60'}`}>
      <div className="flex items-start gap-4">
        <div className="flex-1 space-y-3">
          <div className="grid grid-cols-2 gap-3">
            <div>
              <Label className="text-xs text-slate-600">Pixel Name</Label>
              <Input
                placeholder="e.g., DV360 Impression"
                value={pixel.name}
                onChange={(e) => onUpdate(index, 'name', e.target.value)}
                className="mt-1 h-9"
              />
            </div>
            <div>
              <Label className="text-xs text-slate-600">Event Type</Label>
              <Select
                value={pixel.event}
                onValueChange={(value) => onUpdate(index, 'event', value)}
              >
                <SelectTrigger className="mt-1 h-9">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="impression">Impression</SelectItem>
                  <SelectItem value="viewable">Viewable Impression</SelectItem>
                  <SelectItem value="start">Video Start</SelectItem>
                  <SelectItem value="firstQuartile">First Quartile</SelectItem>
                  <SelectItem value="midpoint">Midpoint</SelectItem>
                  <SelectItem value="thirdQuartile">Third Quartile</SelectItem>
                  <SelectItem value="complete">Complete</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
          <div>
            <Label className="text-xs text-slate-600">Pixel URL</Label>
            <Input
              placeholder="https://pixel.example.com/track?auction=${AUCTION_ID}&price=${AUCTION_PRICE}"
              value={pixel.url}
              onChange={(e) => onUpdate(index, 'url', e.target.value)}
              className="mt-1 h-9 font-mono text-xs"
            />
            <p className="text-[10px] text-slate-400 mt-1">
              Supports macros: {"${AUCTION_ID}"}, {"${AUCTION_PRICE}"}, {"${CREATIVE_ID}"}, etc.
            </p>
          </div>
        </div>
        <div className="flex flex-col items-center gap-2">
          <button
            type="button"
            onClick={() => onToggle(index)}
            className="text-slate-400 hover:text-slate-600"
            title={pixel.enabled ? "Disable" : "Enable"}
          >
            {pixel.enabled ? (
              <ToggleRight className="w-6 h-6 text-[#10B981]" />
            ) : (
              <ToggleLeft className="w-6 h-6" />
            )}
          </button>
          <button
            type="button"
            onClick={() => onRemove(index)}
            className="text-slate-400 hover:text-red-500"
            title="Remove pixel"
          >
            <Trash2 className="w-4 h-4" />
          </button>
        </div>
      </div>
      {pixel.enabled && pixel.name && pixel.url && (
        <Badge className="mt-3 bg-[#10B981]/10 text-[#10B981] text-xs">
          Active
        </Badge>
      )}
    </div>
  );
}

export default ImpressionPixelsSection;
