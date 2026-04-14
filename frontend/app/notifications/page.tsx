"use client";

/**
 * Notifications page — requires authentication.
 *
 * Lists all file-share notifications from DynamoDB, ordered newest first.
 * Unread notifications are highlighted. Clicking "Mark as read" calls
 * PATCH /api/notifications/{id}/read.
 */

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import api from "@/lib/api";
import { isAuthenticated } from "@/lib/auth";
import { Bell, Loader2, CheckCheck } from "lucide-react";

interface Notification {
  notification_id: string;
  message: string;
  sharer_email: string;
  filename: string;
  timestamp: string;
  read: boolean;
}

export default function NotificationsPage() {
  const router = useRouter();
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!isAuthenticated()) {
      router.replace("/login");
      return;
    }
    api
      .get("/notifications/")
      .then((res) => setNotifications(res.data.notifications ?? []))
      .finally(() => setLoading(false));
  }, [router]);

  const markRead = async (id: string) => {
    await api.patch(`/notifications/${id}/read`);
    setNotifications((prev) =>
      prev.map((n) => (n.notification_id === id ? { ...n, read: true } : n))
    );
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20 text-gray-500">
        <Loader2 className="w-6 h-6 animate-spin mr-2" /> Loading notifications...
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
        <Bell className="w-6 h-6 text-blue-600" />
        Notifications
      </h1>

      {notifications.length === 0 ? (
        <div className="text-center py-20 text-gray-400 space-y-2">
          <Bell className="w-10 h-10 mx-auto" />
          <p>No notifications yet.</p>
        </div>
      ) : (
        <div className="space-y-3">
          {notifications.map((n) => (
            <div
              key={n.notification_id}
              className={`bg-white border rounded-lg p-4 flex items-start justify-between gap-3 shadow-sm ${
                n.read ? "border-gray-200 opacity-70" : "border-blue-300 bg-blue-50"
              }`}
            >
              <div className="space-y-0.5">
                <p className="text-sm text-gray-800 font-medium">{n.message}</p>
                <p className="text-xs text-gray-500">
                  {new Date(n.timestamp).toLocaleString()}
                </p>
              </div>
              {!n.read && (
                <button
                  onClick={() => markRead(n.notification_id)}
                  className="shrink-0 flex items-center gap-1 text-xs text-blue-600 hover:text-blue-800 transition"
                >
                  <CheckCheck className="w-4 h-4" />
                  Mark read
                </button>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
