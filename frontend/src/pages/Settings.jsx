import { useState, useEffect } from "react";
import { useAuth } from "../context/AuthContext";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "../components/ui/card";
import { Button } from "../components/ui/button";
import { Label } from "../components/ui/label";
import { Switch } from "../components/ui/switch";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "../components/ui/select";
import { Slider } from "../components/ui/slider";
import { toast } from "sonner";
import { 
  Mail, 
  Bell, 
  Shield, 
  DollarSign, 
  Key, 
  Megaphone,
  Calendar,
  Moon,
  RotateCcw,
  Save,
  Loader2
} from "lucide-react";

const API_URL = process.env.REACT_APP_BACKEND_URL;

export default function Settings() {
  const { token, user } = useAuth();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [preferences, setPreferences] = useState(null);
  const [defaults, setDefaults] = useState(null);
  const [hasChanges, setHasChanges] = useState(false);

  useEffect(() => {
    fetchPreferences();
  }, []);

  const fetchPreferences = async () => {
    try {
      const response = await fetch(`${API_URL}/api/auth/email-preferences`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (response.ok) {
        const data = await response.json();
        setPreferences(data.preferences);
        setDefaults(data.defaults);
      }
    } catch (error) {
      toast.error("Failed to load preferences");
    } finally {
      setLoading(false);
    }
  };

  const updatePreference = (key, value) => {
    setPreferences(prev => ({ ...prev, [key]: value }));
    setHasChanges(true);
  };

  const savePreferences = async () => {
    setSaving(true);
    try {
      const response = await fetch(`${API_URL}/api/auth/email-preferences`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify(preferences)
      });
      
      if (!response.ok) {
        const err = await response.json();
        throw new Error(err.detail);
      }
      
      const data = await response.json();
      setPreferences(data.preferences);
      setHasChanges(false);
      toast.success("Preferences saved successfully");
    } catch (error) {
      toast.error(error.message);
    } finally {
      setSaving(false);
    }
  };

  const resetPreferences = async () => {
    if (!confirm("Reset all email preferences to defaults?")) return;
    
    setSaving(true);
    try {
      const response = await fetch(`${API_URL}/api/auth/email-preferences/reset`, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` }
      });
      
      if (response.ok) {
        const data = await response.json();
        setPreferences(data.preferences);
        setHasChanges(false);
        toast.success("Preferences reset to defaults");
      }
    } catch (error) {
      toast.error("Failed to reset preferences");
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-[#3B82F6]"></div>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-4xl mx-auto space-y-6" data-testid="settings-page">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-[#F8FAFC]">Email Preferences</h1>
          <p className="text-[#64748B]">Manage your email notification settings</p>
        </div>
        <div className="flex gap-2">
          <Button
            variant="outline"
            onClick={resetPreferences}
            disabled={saving}
            className="border-[#2D3B55] text-[#64748B]"
          >
            <RotateCcw className="w-4 h-4 mr-2" />
            Reset
          </Button>
          <Button
            onClick={savePreferences}
            disabled={!hasChanges || saving}
            className={hasChanges ? "bg-[#10B981]" : "bg-[#3B82F6] opacity-50"}
          >
            {saving ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Save className="w-4 h-4 mr-2" />}
            Save Changes
          </Button>
        </div>
      </div>

      {/* Notification Types */}
      <Card className="surface-primary border-panel">
        <CardHeader>
          <CardTitle className="text-[#F8FAFC] flex items-center gap-2">
            <Bell className="w-5 h-5 text-[#3B82F6]" />
            Notification Types
          </CardTitle>
          <CardDescription className="text-[#64748B]">
            Choose which notifications you want to receive
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Security Alerts */}
          <div className="flex items-center justify-between p-4 rounded-lg bg-[#0B1221] border border-[#2D3B55]">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-[#EF4444]/10 flex items-center justify-center">
                <Shield className="w-5 h-5 text-[#EF4444]" />
              </div>
              <div>
                <Label className="text-[#F8FAFC] font-medium">Security Alerts</Label>
                <p className="text-sm text-[#64748B]">New sign-in from unknown device/location</p>
              </div>
            </div>
            <Switch
              checked={preferences?.security_alerts ?? true}
              onCheckedChange={(checked) => updatePreference("security_alerts", checked)}
              className="data-[state=checked]:bg-[#10B981]"
            />
          </div>

          {/* Budget Alerts */}
          <div className="flex items-center justify-between p-4 rounded-lg bg-[#0B1221] border border-[#2D3B55]">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-[#F59E0B]/10 flex items-center justify-center">
                <DollarSign className="w-5 h-5 text-[#F59E0B]" />
              </div>
              <div>
                <Label className="text-[#F8FAFC] font-medium">Budget Alerts</Label>
                <p className="text-sm text-[#64748B]">When campaign budget reaches threshold</p>
              </div>
            </div>
            <Switch
              checked={preferences?.budget_alerts ?? true}
              onCheckedChange={(checked) => updatePreference("budget_alerts", checked)}
              className="data-[state=checked]:bg-[#10B981]"
            />
          </div>

          {/* New User Notifications (Admin/Super Admin only) */}
          {(user?.role === "admin" || user?.role === "super_admin") && (
            <div className="flex items-center justify-between p-4 rounded-lg bg-[#0B1221] border border-[#2D3B55]">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-lg bg-[#3B82F6]/10 flex items-center justify-center">
                  <Mail className="w-5 h-5 text-[#3B82F6]" />
                </div>
                <div>
                  <Label className="text-[#F8FAFC] font-medium">New User Notifications</Label>
                  <p className="text-sm text-[#64748B]">When a new user is created under your account</p>
                </div>
              </div>
              <Switch
                checked={preferences?.new_user_notifications ?? true}
                onCheckedChange={(checked) => updatePreference("new_user_notifications", checked)}
                className="data-[state=checked]:bg-[#10B981]"
              />
            </div>
          )}

          {/* Password Reset */}
          <div className="flex items-center justify-between p-4 rounded-lg bg-[#0B1221] border border-[#2D3B55]">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-[#8B5CF6]/10 flex items-center justify-center">
                <Key className="w-5 h-5 text-[#8B5CF6]" />
              </div>
              <div>
                <Label className="text-[#F8FAFC] font-medium">Password Reset</Label>
                <p className="text-sm text-[#64748B]">Password reset confirmation emails</p>
              </div>
            </div>
            <Switch
              checked={preferences?.password_reset_notifications ?? true}
              onCheckedChange={(checked) => updatePreference("password_reset_notifications", checked)}
              className="data-[state=checked]:bg-[#10B981]"
            />
          </div>

          {/* System Announcements */}
          <div className="flex items-center justify-between p-4 rounded-lg bg-[#0B1221] border border-[#2D3B55]">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-[#10B981]/10 flex items-center justify-center">
                <Megaphone className="w-5 h-5 text-[#10B981]" />
              </div>
              <div>
                <Label className="text-[#F8FAFC] font-medium">System Announcements</Label>
                <p className="text-sm text-[#64748B]">Platform updates and announcements</p>
              </div>
            </div>
            <Switch
              checked={preferences?.system_announcements ?? true}
              onCheckedChange={(checked) => updatePreference("system_announcements", checked)}
              className="data-[state=checked]:bg-[#10B981]"
            />
          </div>
        </CardContent>
      </Card>

      {/* Budget Alert Thresholds */}
      <Card className="surface-primary border-panel">
        <CardHeader>
          <CardTitle className="text-[#F8FAFC] flex items-center gap-2">
            <DollarSign className="w-5 h-5 text-[#F59E0B]" />
            Budget Alert Thresholds
          </CardTitle>
          <CardDescription className="text-[#64748B]">
            Customize when you receive budget alerts
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Warning Threshold */}
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <Label className="text-[#F8FAFC]">Warning Threshold</Label>
              <span className="text-lg font-bold text-[#F59E0B]">{preferences?.budget_warning_threshold ?? 75}%</span>
            </div>
            <Slider
              value={[preferences?.budget_warning_threshold ?? 75]}
              onValueChange={([value]) => updatePreference("budget_warning_threshold", value)}
              min={10}
              max={95}
              step={5}
              className="w-full"
              disabled={!preferences?.budget_alerts}
            />
            <p className="text-xs text-[#64748B]">
              Receive a warning when budget usage reaches this percentage
            </p>
          </div>

          {/* Critical Threshold */}
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <Label className="text-[#F8FAFC]">Critical Threshold</Label>
              <span className="text-lg font-bold text-[#EF4444]">{preferences?.budget_critical_threshold ?? 90}%</span>
            </div>
            <Slider
              value={[preferences?.budget_critical_threshold ?? 90]}
              onValueChange={([value]) => updatePreference("budget_critical_threshold", value)}
              min={50}
              max={100}
              step={5}
              className="w-full"
              disabled={!preferences?.budget_alerts}
            />
            <p className="text-xs text-[#64748B]">
              Receive a critical alert when budget usage reaches this percentage
            </p>
          </div>
        </CardContent>
      </Card>

      {/* Delivery Preferences */}
      <Card className="surface-primary border-panel">
        <CardHeader>
          <CardTitle className="text-[#F8FAFC] flex items-center gap-2">
            <Calendar className="w-5 h-5 text-[#3B82F6]" />
            Delivery Preferences
          </CardTitle>
          <CardDescription className="text-[#64748B]">
            Control how and when you receive notifications
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Weekly Digest */}
          <div className="flex items-center justify-between p-4 rounded-lg bg-[#0B1221] border border-[#2D3B55]">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-[#3B82F6]/10 flex items-center justify-center">
                <Calendar className="w-5 h-5 text-[#3B82F6]" />
              </div>
              <div>
                <Label className="text-[#F8FAFC] font-medium">Weekly Digest</Label>
                <p className="text-sm text-[#64748B]">Receive a summary instead of individual emails</p>
              </div>
            </div>
            <Switch
              checked={preferences?.weekly_digest ?? false}
              onCheckedChange={(checked) => updatePreference("weekly_digest", checked)}
              className="data-[state=checked]:bg-[#10B981]"
            />
          </div>

          {/* Digest Day */}
          {preferences?.weekly_digest && (
            <div className="flex items-center justify-between p-4 rounded-lg bg-[#0B1221] border border-[#2D3B55]">
              <div>
                <Label className="text-[#F8FAFC] font-medium">Digest Day</Label>
                <p className="text-sm text-[#64748B]">When to receive your weekly digest</p>
              </div>
              <Select
                value={preferences?.digest_day ?? "monday"}
                onValueChange={(value) => updatePreference("digest_day", value)}
              >
                <SelectTrigger className="w-36 surface-secondary border-[#2D3B55]">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent className="surface-primary border-[#2D3B55]">
                  <SelectItem value="monday">Monday</SelectItem>
                  <SelectItem value="tuesday">Tuesday</SelectItem>
                  <SelectItem value="wednesday">Wednesday</SelectItem>
                  <SelectItem value="thursday">Thursday</SelectItem>
                  <SelectItem value="friday">Friday</SelectItem>
                  <SelectItem value="saturday">Saturday</SelectItem>
                  <SelectItem value="sunday">Sunday</SelectItem>
                </SelectContent>
              </Select>
            </div>
          )}

          {/* Quiet Hours */}
          <div className="flex items-center justify-between p-4 rounded-lg bg-[#0B1221] border border-[#2D3B55]">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-[#8B5CF6]/10 flex items-center justify-center">
                <Moon className="w-5 h-5 text-[#8B5CF6]" />
              </div>
              <div>
                <Label className="text-[#F8FAFC] font-medium">Quiet Hours</Label>
                <p className="text-sm text-[#64748B]">Pause non-critical notifications during set hours</p>
              </div>
            </div>
            <Switch
              checked={preferences?.quiet_hours_enabled ?? false}
              onCheckedChange={(checked) => updatePreference("quiet_hours_enabled", checked)}
              className="data-[state=checked]:bg-[#10B981]"
            />
          </div>

          {/* Quiet Hours Time */}
          {preferences?.quiet_hours_enabled && (
            <div className="flex items-center justify-between p-4 rounded-lg bg-[#0B1221] border border-[#2D3B55]">
              <div>
                <Label className="text-[#F8FAFC] font-medium">Quiet Hours Period</Label>
                <p className="text-sm text-[#64748B]">
                  {preferences?.quiet_hours_start ?? 22}:00 - {preferences?.quiet_hours_end ?? 8}:00
                </p>
              </div>
              <div className="flex gap-2">
                <Select
                  value={String(preferences?.quiet_hours_start ?? 22)}
                  onValueChange={(value) => updatePreference("quiet_hours_start", parseInt(value))}
                >
                  <SelectTrigger className="w-20 surface-secondary border-[#2D3B55]">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent className="surface-primary border-[#2D3B55] max-h-48">
                    {Array.from({ length: 24 }, (_, i) => (
                      <SelectItem key={i} value={String(i)}>{String(i).padStart(2, '0')}:00</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                <span className="text-[#64748B] self-center">to</span>
                <Select
                  value={String(preferences?.quiet_hours_end ?? 8)}
                  onValueChange={(value) => updatePreference("quiet_hours_end", parseInt(value))}
                >
                  <SelectTrigger className="w-20 surface-secondary border-[#2D3B55]">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent className="surface-primary border-[#2D3B55] max-h-48">
                    {Array.from({ length: 24 }, (_, i) => (
                      <SelectItem key={i} value={String(i)}>{String(i).padStart(2, '0')}:00</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Save reminder */}
      {hasChanges && (
        <div className="fixed bottom-6 right-6 p-4 rounded-lg bg-[#F59E0B]/10 border border-[#F59E0B]/30 shadow-lg">
          <p className="text-sm text-[#F59E0B]">You have unsaved changes</p>
        </div>
      )}
    </div>
  );
}
