import { useState, useCallback } from "react";
import { toast } from "sonner";
import { useAuth } from "../../context/AuthContext";

const API_URL = process.env.REACT_APP_BACKEND_URL;

/**
 * Custom hook for managing Admin Panel state and operations
 */
export function useAdminPanel() {
  const { user, token, hasRole, refreshUser } = useAuth();
  
  // View state for breadcrumb navigation
  const [viewMode, setViewMode] = useState("overview");
  const [viewingAdmin, setViewingAdmin] = useState(null);
  const [viewingAdvertiser, setViewingAdvertiser] = useState(null);
  
  // Core data
  const [users, setUsers] = useState([]);
  const [hierarchy, setHierarchy] = useState(null);
  const [roleConfigs, setRoleConfigs] = useState({});
  const [sidebarItems, setSidebarItems] = useState([]);
  const [permissions, setPermissions] = useState([]);
  const [stats, setStats] = useState(null);
  const [activityTimeline, setActivityTimeline] = useState([]);
  
  // UI state
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [showCreateUser, setShowCreateUser] = useState(false);
  const [newUser, setNewUser] = useState({ name: "", email: "", password: "", role: "" });
  const [searchQuery, setSearchQuery] = useState("");
  const [roleFilter, setRoleFilter] = useState("");
  
  // Bulk selection state
  const [selectedUsers, setSelectedUsers] = useState([]);
  const [showBulkDeleteConfirm, setShowBulkDeleteConfirm] = useState(false);
  
  // Audit logs
  const [auditLogs, setAuditLogs] = useState([]);
  const [auditLoading, setAuditLoading] = useState(false);
  
  // 2FA
  const [twoFAStatus, setTwoFAStatus] = useState({ enabled: false, can_enable: false });
  const [twoFASetup, setTwoFASetup] = useState(null);
  const [show2FASetup, setShow2FASetup] = useState(false);
  const [verificationCode, setVerificationCode] = useState("");
  const [copiedSecret, setCopiedSecret] = useState(false);
  
  // Access control
  const [selectedRole, setSelectedRole] = useState("advertiser");
  const [expandedAdmins, setExpandedAdmins] = useState({});
  const [editedSidebarAccess, setEditedSidebarAccess] = useState([]);
  const [editedPermissions, setEditedPermissions] = useState([]);
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false);

  const isSuperAdmin = hasRole("super_admin");
  const isAdmin = hasRole("admin");

  // Get allowed roles for user creation - 3 tier hierarchy
  const getAllowedRoles = useCallback(() => {
    if (isSuperAdmin) {
      return ["admin"];
    } else if (isAdmin) {
      return ["advertiser"];
    }
    return [];
  }, [isSuperAdmin, isAdmin]);

  // Fetch all data
  const fetchData = useCallback(async () => {
    try {
      setLoading(true);
      
      // Fetch users
      const usersRes = await fetch(`${API_URL}/api/admin/users`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (usersRes.ok) {
        const usersData = await usersRes.json();
        setUsers(usersData);
      }
      
      // Fetch hierarchy
      const hierarchyRes = await fetch(`${API_URL}/api/admin/users/hierarchy`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (hierarchyRes.ok) {
        const hierarchyData = await hierarchyRes.json();
        setHierarchy(hierarchyData);
      }
      
      // Fetch role configs
      const configsRes = await fetch(`${API_URL}/api/admin/roles/configs`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (configsRes.ok) {
        const configsData = await configsRes.json();
        setRoleConfigs(configsData);
        
        // Set sidebar items and permissions from config
        if (configsData.sidebar_items) {
          setSidebarItems(configsData.sidebar_items);
        }
        if (configsData.permissions) {
          setPermissions(configsData.permissions);
        }
      }
      
      // Fetch stats
      const statsRes = await fetch(`${API_URL}/api/admin/stats`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (statsRes.ok) {
        const statsData = await statsRes.json();
        setStats(statsData);
        
        // Set activity timeline if available
        if (statsData.activity_timeline) {
          setActivityTimeline(statsData.activity_timeline);
        }
      }
      
      // Fetch 2FA status
      const twoFARes = await fetch(`${API_URL}/api/auth/2fa/status`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (twoFARes.ok) {
        const twoFAData = await twoFARes.json();
        setTwoFAStatus(twoFAData);
      }
    } catch (error) {
      toast.error("Failed to load admin data");
    } finally {
      setLoading(false);
    }
  }, [token]);

  // Create user
  const createUser = useCallback(async () => {
    try {
      const response = await fetch(`${API_URL}/api/admin/users`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(newUser),
      });

      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.detail || "Failed to create user");
      }

      toast.success("User created successfully");
      setShowCreateUser(false);
      setNewUser({ name: "", email: "", password: "", role: getAllowedRoles()[0] || "advertiser" });
      fetchData();
    } catch (error) {
      toast.error(error.message || "Failed to create user");
    }
  }, [token, newUser, fetchData, getAllowedRoles]);

  // Toggle user status
  const toggleUserStatus = useCallback(async (userId, currentStatus) => {
    try {
      const response = await fetch(`${API_URL}/api/admin/users/${userId}/status?is_active=${!currentStatus}`, {
        method: "PUT",
        headers: { Authorization: `Bearer ${token}` },
      });

      const data = await response.json().catch(() => ({}));
      if (!response.ok) {
        throw new Error(data.detail || "Failed to update user status");
      }

      toast.success(`User ${!currentStatus ? "activated" : "deactivated"}`);
      fetchData();
    } catch (error) {
      toast.error(error.message || "Failed to update user status");
    }
  }, [token, fetchData]);

  // Delete user
  const deleteUser = useCallback(async (userId) => {
    if (!confirm("Are you sure you want to delete this user?")) return;
    
    try {
      const response = await fetch(`${API_URL}/api/admin/users/${userId}`, {
        method: "DELETE",
        headers: { Authorization: `Bearer ${token}` },
      });

      const data = await response.json().catch(() => ({}));
      if (!response.ok) {
        throw new Error(data.detail || "Failed to delete user");
      }

      toast.success("User deleted");
      fetchData();
    } catch (error) {
      toast.error(error.message || "Failed to delete user");
    }
  }, [token, fetchData]);

  // Bulk delete users
  const bulkDeleteUsers = useCallback(async () => {
    try {
      const response = await fetch(`${API_URL}/api/admin/users/bulk-delete`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ user_ids: selectedUsers }),
      });

      const result = await response.json();
      if (!response.ok) {
        throw new Error(result.detail || "Failed to delete users");
      }

      toast.success(`Successfully deleted ${result.deleted_count} user(s)`);
      setSelectedUsers([]);
      setShowBulkDeleteConfirm(false);
      fetchData();
    } catch (error) {
      toast.error(error.message || "Failed to delete users");
    }
  }, [token, selectedUsers, fetchData]);

  // 2FA operations
  const setup2FA = useCallback(async () => {
    try {
      const response = await fetch(`${API_URL}/api/auth/2fa/setup`, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
      });
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || "Failed to setup 2FA");
      }
      setTwoFASetup(data);
      setShow2FASetup(true);
    } catch (error) {
      toast.error(error.message || "Failed to setup 2FA");
    }
  }, [token]);

  const enable2FA = useCallback(async () => {
    try {
      const response = await fetch(`${API_URL}/api/auth/2fa/enable`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ code: verificationCode }),
      });
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || "Failed to enable 2FA");
      }
      toast.success("2FA enabled successfully!");
      setShow2FASetup(false);
      setTwoFASetup(null);
      setVerificationCode("");
      fetchData();
    } catch (error) {
      toast.error(error.message || "Failed to enable 2FA");
    }
  }, [token, verificationCode, fetchData]);

  const disable2FA = useCallback(async () => {
    const code = prompt("Enter your 2FA code to disable:");
    if (!code) return;
    
    try {
      const response = await fetch(`${API_URL}/api/auth/2fa/disable`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ code }),
      });
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || "Failed to disable 2FA");
      }
      toast.success("2FA disabled successfully");
      fetchData();
    } catch (error) {
      toast.error(error.message || "Failed to disable 2FA");
    }
  }, [token, fetchData]);

  // Save access changes
  const saveAccessChanges = useCallback(async () => {
    setSaving(true);
    try {
      const response = await fetch(`${API_URL}/api/admin/roles/bulk-update`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          role: selectedRole,
          sidebar_access: editedSidebarAccess,
          permissions: editedPermissions,
        }),
      });

      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || "Failed to update access");
      }

      toast.success(`Access updated for ${selectedRole} role (${data.users_updated} users updated)`);
      setHasUnsavedChanges(false);
      fetchData();
      refreshUser();
    } catch (error) {
      toast.error(error.message || "Failed to update access");
    } finally {
      setSaving(false);
    }
  }, [token, selectedRole, editedSidebarAccess, editedPermissions, fetchData, refreshUser]);

  // Fetch audit logs
  const fetchAuditLogs = useCallback(async () => {
    setAuditLoading(true);
    try {
      const response = await fetch(`${API_URL}/api/admin/audit-logs`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (response.ok) {
        const logsData = await response.json();
        setAuditLogs(logsData);
      }
    } catch {
      toast.error("Failed to load audit logs");
    } finally {
      setAuditLoading(false);
    }
  }, [token]);

  // Export users
  const exportUsers = useCallback(async () => {
    try {
      const response = await fetch(`${API_URL}/api/admin/users/export`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = `users_export_${new Date().toISOString().split("T")[0]}.csv`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
        toast.success("Users exported successfully");
      }
    } catch {
      toast.error("Failed to export users");
    }
  }, [token]);

  return {
    // Auth state
    user,
    token,
    isSuperAdmin,
    isAdmin,
    getAllowedRoles,
    
    // View state
    viewMode,
    setViewMode,
    viewingAdmin,
    setViewingAdmin,
    viewingAdvertiser,
    setViewingAdvertiser,
    
    // Core data
    users,
    hierarchy,
    roleConfigs,
    sidebarItems,
    permissions,
    stats,
    activityTimeline,
    
    // UI state
    loading,
    saving,
    showCreateUser,
    setShowCreateUser,
    newUser,
    setNewUser,
    searchQuery,
    setSearchQuery,
    roleFilter,
    setRoleFilter,
    
    // Bulk selection
    selectedUsers,
    setSelectedUsers,
    showBulkDeleteConfirm,
    setShowBulkDeleteConfirm,
    
    // Audit logs
    auditLogs,
    auditLoading,
    fetchAuditLogs,
    
    // 2FA
    twoFAStatus,
    twoFASetup,
    show2FASetup,
    setShow2FASetup,
    verificationCode,
    setVerificationCode,
    copiedSecret,
    setCopiedSecret,
    
    // Access control
    selectedRole,
    setSelectedRole,
    expandedAdmins,
    setExpandedAdmins,
    editedSidebarAccess,
    setEditedSidebarAccess,
    editedPermissions,
    setEditedPermissions,
    hasUnsavedChanges,
    setHasUnsavedChanges,
    
    // Actions
    fetchData,
    createUser,
    toggleUserStatus,
    deleteUser,
    bulkDeleteUsers,
    setup2FA,
    enable2FA,
    disable2FA,
    saveAccessChanges,
    exportUsers,
    refreshUser,
  };
}

export default useAdminPanel;
