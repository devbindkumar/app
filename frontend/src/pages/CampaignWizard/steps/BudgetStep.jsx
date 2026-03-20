import { Card, CardContent, CardHeader, CardTitle } from "../../../components/ui/card";
import { Input } from "../../../components/ui/input";
import { NumberInput } from "../../../components/ui/number-input";
import { Label } from "../../../components/ui/label";
import { 
  Select, SelectContent, SelectItem, SelectTrigger, SelectValue 
} from "../../../components/ui/select";
import { 
  BIDDING_STRATEGIES, BID_PRICING_TYPES, CURRENCIES, PACING_TYPES,
  INVENTORY_SOURCES, ENVIRONMENTS
} from "../constants";

export function BudgetStep({ form, updateField, forecast }) {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-semibold text-slate-900 mb-1">Budget & Bidding</h2>
        <p className="text-sm text-slate-500">Set your budget, bidding strategy, and inventory sources</p>
      </div>

      {/* Currency & Pricing Type */}
      <div className="grid grid-cols-2 gap-4">
        <div className="space-y-2">
          <Label className="text-slate-600">Currency *</Label>
          <Select value={form.currency} onValueChange={(v) => updateField("currency", v)}>
            <SelectTrigger className="surface-secondary border-slate-200 text-slate-900">
              <SelectValue />
            </SelectTrigger>
            <SelectContent className="surface-primary border-slate-200">
              {CURRENCIES.map((c) => (
                <SelectItem key={c.value} value={c.value} className="text-slate-900">{c.label}</SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
        <div className="space-y-2">
          <Label className="text-slate-600">Bid Pricing Type *</Label>
          <Select value={form.bid_pricing_type} onValueChange={(v) => updateField("bid_pricing_type", v)}>
            <SelectTrigger className="surface-secondary border-slate-200 text-slate-900">
              <SelectValue />
            </SelectTrigger>
            <SelectContent className="surface-primary border-slate-200">
              {BID_PRICING_TYPES.map((t) => (
                <SelectItem key={t.value} value={t.value} className="text-slate-900">{t.label}</SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      </div>

      {/* Budget */}
      <div className="grid grid-cols-2 gap-4">
        <div className="space-y-2">
          <Label className="text-slate-600">Daily Budget ($) *</Label>
          <NumberInput
            value={form.daily_budget}
            onChange={(e) => updateField("daily_budget", parseFloat(e.target.value) || 0)}
            className="surface-secondary border-slate-200 text-slate-900"
            data-testid="daily-budget-input"
            min={0}
          />
        </div>
        <div className="space-y-2">
          <Label className="text-slate-600">Total Budget ($)</Label>
          <NumberInput
            value={form.total_budget}
            onChange={(e) => updateField("total_budget", parseFloat(e.target.value) || 0)}
            className="surface-secondary border-slate-200 text-slate-900"
            min={0}
          />
        </div>
      </div>

      {/* Bidding Strategy */}
      <div className="space-y-2">
        <Label className="text-slate-600">Bidding Strategy</Label>
        <Select value={form.bidding_strategy} onValueChange={(v) => updateField("bidding_strategy", v)}>
          <SelectTrigger className="surface-secondary border-slate-200 text-slate-900">
            <SelectValue />
          </SelectTrigger>
          <SelectContent className="surface-primary border-slate-200">
            {BIDDING_STRATEGIES.map((s) => (
              <SelectItem key={s.value} value={s.value} className="text-slate-900">
                {s.label} - {s.desc}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      {/* Bid Floor */}
      <div className="space-y-2">
        <Label className="text-slate-600">Bid Floor ({form.currency})</Label>
        <NumberInput
          step="0.01"
          value={form.bid_floor}
          onChange={(e) => updateField("bid_floor", parseFloat(e.target.value) || 0)}
          className="surface-secondary border-slate-200 text-slate-900"
          min={0}
        />
        <p className="text-xs text-slate-500">Minimum price to participate in auctions</p>
      </div>

      {/* Bid Price (Hidden but important for submission) */}
      <div className="space-y-2">
        <Label className="text-slate-600">Bid Price ({form.currency})</Label>
        <NumberInput
          step="0.01"
          value={form.bid_price}
          onChange={(e) => updateField("bid_price", parseFloat(e.target.value) || 0)}
          className="surface-secondary border-slate-200 text-slate-900"
          min={0}
        />
        <p className="text-xs text-slate-500">Your maximum bid for impressions</p>
      </div>

      {/* Budget Pacing */}
      <div className="space-y-2">
        <Label className="text-slate-600">Budget Pacing</Label>
        <div className="grid grid-cols-3 gap-3">
          {PACING_TYPES.map((pacing) => (
            <div
              key={pacing.value}
              onClick={() => updateField("pacing_type", pacing.value)}
              className={`p-4 rounded-lg cursor-pointer border transition-all ${
                form.pacing_type === pacing.value
                  ? "bg-[#3B82F6]/20 border-[#3B82F6]"
                  : "surface-secondary border-slate-200 hover:border-[#3B82F6]/50"
              }`}
            >
              <p className="text-sm font-medium text-slate-900">{pacing.label}</p>
              <p className="text-xs text-slate-500 mt-1">{pacing.desc}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Inventory Sources */}
      <div className="space-y-2">
        <Label className="text-slate-600">Inventory Sources</Label>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {INVENTORY_SOURCES.map((source) => {
            const Icon = source.icon;
            const isSelected = form.inventory_sources.includes(source.value);
            return (
              <div
                key={source.value}
                onClick={() => {
                  const newSources = isSelected
                    ? form.inventory_sources.filter(s => s !== source.value)
                    : [...form.inventory_sources, source.value];
                  updateField("inventory_sources", newSources);
                }}
                className={`p-4 rounded-lg cursor-pointer border transition-all ${
                  isSelected
                    ? "bg-[#10B981]/20 border-[#10B981]"
                    : "surface-secondary border-slate-200 hover:border-[#10B981]/50"
                }`}
              >
                <Icon className={`w-5 h-5 mb-2 ${isSelected ? "text-[#10B981]" : "text-slate-500"}`} />
                <p className="text-sm font-medium text-slate-900">{source.label}</p>
                <p className="text-xs text-slate-500 mt-1">{source.desc}</p>
              </div>
            );
          })}
        </div>
      </div>

      {/* Environments */}
      <div className="space-y-2">
        <Label className="text-slate-600">Environments</Label>
        <div className="grid grid-cols-4 gap-3">
          {ENVIRONMENTS.map((env) => {
            const Icon = env.icon;
            const isSelected = form.environments.includes(env.value);
            return (
              <div
                key={env.value}
                onClick={() => {
                  const newEnvs = isSelected
                    ? form.environments.filter(e => e !== env.value)
                    : [...form.environments, env.value];
                  updateField("environments", newEnvs);
                }}
                className={`p-4 rounded-lg cursor-pointer border transition-all text-center ${
                  isSelected
                    ? "bg-[#8B5CF6]/20 border-[#8B5CF6]"
                    : "surface-secondary border-slate-200 hover:border-[#8B5CF6]/50"
                }`}
              >
                <Icon className={`w-5 h-5 mx-auto mb-2 ${isSelected ? "text-[#8B5CF6]" : "text-slate-500"}`} />
                <p className="text-sm font-medium text-slate-900">{env.label}</p>
              </div>
            );
          })}
        </div>
      </div>

      {/* Performance Forecast */}
      {forecast && (
        <Card className="surface-secondary border-[#10B981]/30">
          <CardHeader className="pb-2">
            <CardTitle className="text-base text-[#10B981]">Performance Forecast</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-4 gap-4 text-center">
              <div>
                <p className="text-2xl font-bold text-slate-900">
                  {(forecast.estimated_impressions / 1000000).toFixed(1)}M
                </p>
                <p className="text-xs text-slate-500">Est. Impressions</p>
              </div>
              <div>
                <p className="text-2xl font-bold text-slate-900">
                  {(forecast.estimated_reach / 1000).toFixed(0)}K
                </p>
                <p className="text-xs text-slate-500">Est. Reach</p>
              </div>
              <div>
                <p className="text-2xl font-bold text-slate-900">
                  {(forecast.estimated_clicks / 1000).toFixed(1)}K
                </p>
                <p className="text-xs text-slate-500">Est. Clicks</p>
              </div>
              <div>
                <p className="text-2xl font-bold text-slate-900">
                  ${forecast.estimated_cpm?.toFixed(2)}
                </p>
                <p className="text-xs text-slate-500">Est. CPM</p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
