"use client";

/**
 * Navbar component.
 *
 * Shows Login / Register when unauthenticated.
 * Shows the user's email, a notification bell, and Logout when authenticated.
 */

import { useEffect, useState } from "react";
import Link from "next/link";
import { isAuthenticated, getUserEmail, logout } from "@/lib/auth";
import api from "@/lib/api";
import { Bell, Cloud, LogOut, Upload, LayoutDashboard } from "lucide-react";

export default function Navbar() {
  const [authed, setAuthed] = useState(false);
  const [email, setEmail] = useState<string | null>(null);
  const [unread, setUnread] = useState(0);

  useEffect(() => {
    const authedNow = isAuthenticated();
    setAuthed(authedNow);
    setEmail(getUserEmail());

    if (authedNow) {
      // Poll notification count every 30 seconds
      const fetchUnread = () => {
        api
          .get("/notifications/")
          .then((res) => setUnread(res.data.unread_count ?? 0))
          .catch(() => {});
      };
      fetchUnread();
      const interval = setInterval(fetchUnread, 30000);
      return () => clearInterval(interval);
    }
  }, []);

  return (
    <nav className="bg-blue-700 text-white shadow-md">
      <div className="max-w-6xl mx-auto flex items-center justify-between px-4 py-3">
        {/* Brand */}
        <Link href="/" className="flex items-center gap-2 font-bold text-xl">
          <Cloud className="w-6 h-6" />
          CloudShare
        </Link>

        {/* Nav links */}
        <div className="flex items-center gap-4 text-sm font-medium">
          {authed ? (
            <>
              <Link
                href="/dashboard"
                className="flex items-center gap-1 hover:text-blue-200 transition"
              >
                <LayoutDashboard className="w-4 h-4" />
                My Files
              </Link>
              <Link
                href="/upload"
                className="flex items-center gap-1 hover:text-blue-200 transition"
              >
                <Upload className="w-4 h-4" />
                Upload
              </Link>
              {/* Notification bell */}
              <Link
                href="/notifications"
                className="relative flex items-center gap-1 hover:text-blue-200 transition"
              >
                <Bell className="w-4 h-4" />
                {unread > 0 && (
                  <span className="absolute -top-2 -right-2 bg-red-500 text-white text-xs rounded-full w-4 h-4 flex items-center justify-center">
                    {unread}
                  </span>
                )}
              </Link>
              <span className="text-blue-200 hidden sm:block">{email}</span>
              <button
                onClick={logout}
                className="flex items-center gap-1 bg-blue-800 hover:bg-blue-900 px-3 py-1.5 rounded transition"
              >
                <LogOut className="w-4 h-4" />
                Logout
              </button>
            </>
          ) : (
            <>
              <Link href="/login" className="hover:text-blue-200 transition">
                Login
              </Link>
              <Link
                href="/register"
                className="bg-white text-blue-700 hover:bg-blue-100 px-3 py-1.5 rounded transition font-semibold"
              >
                Register
              </Link>
            </>
          )}
        </div>
      </div>
    </nav>
  );
}
