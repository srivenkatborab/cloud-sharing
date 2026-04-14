"use client";

/**
 * FileCard component.
 *
 * Displays a single file's metadata with Download, Share, and Delete actions.
 */

import { useState } from "react";
import api from "@/lib/api";
import { Download, Trash2, Share2, FileText, Loader2 } from "lucide-react";

interface FileRecord {
  file_id: string;
  filename: string;
  size: number;
  content_type: string;
  upload_time: string;
  shared_with: string[];
}

interface FileCardProps {
  file: FileRecord;
  onDeleted: (fileId: string) => void;
}

function formatBytes(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

export default function FileCard({ file, onDeleted }: FileCardProps) {
  const [sharing, setSharing] = useState(false);
  const [shareEmail, setShareEmail] = useState("");
  const [deleting, setDeleting] = useState(false);
  const [downloading, setDownloading] = useState(false);
  const [message, setMessage] = useState<{ text: string; type: "success" | "error" } | null>(null);

  const handleDownload = async () => {
    setDownloading(true);
    setMessage(null);
    try {
      const res = await api.get(`/files/${file.file_id}/download`);
      window.open(res.data.download_url, "_blank");
    } catch {
      setMessage({ text: "Failed to get download link.", type: "error" });
    } finally {
      setDownloading(false);
    }
  };

  const handleDelete = async () => {
    if (!confirm(`Delete "${file.filename}"? This cannot be undone.`)) return;
    setDeleting(true);
    try {
      await api.delete(`/files/${file.file_id}`);
      onDeleted(file.file_id);
    } catch {
      setMessage({ text: "Failed to delete file.", type: "error" });
      setDeleting(false);
    }
  };

  const handleShare = async (e: React.FormEvent) => {
    e.preventDefault();
    setMessage(null);
    try {
      await api.post("/share/", { file_id: file.file_id, recipient_email: shareEmail });
      setMessage({ text: `Shared with ${shareEmail}. They will receive an email notification.`, type: "success" });
      setShareEmail("");
      setSharing(false);
    } catch (err: unknown) {
      const detail = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
      setMessage({ text: detail || "Share failed.", type: "error" });
    }
  };

  return (
    <div className="bg-white border border-gray-200 rounded-lg shadow-sm p-4 flex flex-col gap-3">
      {/* File info */}
      <div className="flex items-start gap-3">
        <FileText className="w-8 h-8 text-blue-500 shrink-0 mt-1" />
        <div className="min-w-0">
          <p className="font-semibold text-gray-800 truncate" title={file.filename}>
            {file.filename}
          </p>
          <p className="text-xs text-gray-500">
            {formatBytes(file.size)} &bull;{" "}
            {new Date(file.upload_time).toLocaleDateString()}
          </p>
          {file.shared_with.length > 0 && (
            <p className="text-xs text-blue-600 mt-0.5">
              Shared with {file.shared_with.length} user(s)
            </p>
          )}
        </div>
      </div>

      {/* Action buttons */}
      <div className="flex gap-2 flex-wrap">
        <button
          onClick={handleDownload}
          disabled={downloading}
          className="flex items-center gap-1 text-sm bg-blue-50 hover:bg-blue-100 text-blue-700 px-3 py-1.5 rounded transition disabled:opacity-50"
        >
          {downloading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Download className="w-4 h-4" />}
          Download
        </button>
        <button
          onClick={() => { setSharing(!sharing); setMessage(null); }}
          className="flex items-center gap-1 text-sm bg-green-50 hover:bg-green-100 text-green-700 px-3 py-1.5 rounded transition"
        >
          <Share2 className="w-4 h-4" />
          Share
        </button>
        <button
          onClick={handleDelete}
          disabled={deleting}
          className="flex items-center gap-1 text-sm bg-red-50 hover:bg-red-100 text-red-700 px-3 py-1.5 rounded transition disabled:opacity-50 ml-auto"
        >
          {deleting ? <Loader2 className="w-4 h-4 animate-spin" /> : <Trash2 className="w-4 h-4" />}
          Delete
        </button>
      </div>

      {/* Share form */}
      {sharing && (
        <form onSubmit={handleShare} className="flex gap-2 mt-1">
          <input
            type="email"
            placeholder="Recipient email"
            value={shareEmail}
            onChange={(e) => setShareEmail(e.target.value)}
            required
            className="flex-1 border border-gray-300 rounded px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400"
          />
          <button
            type="submit"
            className="bg-green-600 hover:bg-green-700 text-white text-sm px-3 py-1.5 rounded transition"
          >
            Send
          </button>
        </form>
      )}

      {/* Feedback message */}
      {message && (
        <p className={`text-xs mt-1 ${message.type === "success" ? "text-green-600" : "text-red-600"}`}>
          {message.text}
        </p>
      )}
    </div>
  );
}
