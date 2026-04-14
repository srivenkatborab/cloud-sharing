"use client";

/**
 * Dashboard page — requires authentication.
 *
 * Lists all files belonging to the current user fetched from DynamoDB
 * via GET /api/files/. Each file is rendered with a FileCard component
 * that supports download, share, and delete actions.
 */

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import api from "@/lib/api";
import { isAuthenticated } from "@/lib/auth";
import FileCard from "@/components/FileCard";
import { Upload, Loader2, FolderOpen } from "lucide-react";

interface FileRecord {
  file_id: string;
  filename: string;
  size: number;
  content_type: string;
  upload_time: string;
  shared_with: string[];
}

export default function DashboardPage() {
  const router = useRouter();
  const [files, setFiles] = useState<FileRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!isAuthenticated()) {
      router.replace("/login");
      return;
    }

    api
      .get("/files/")
      .then((res) => setFiles(res.data.files ?? []))
      .catch(() => setError("Failed to load files. Please refresh."))
      .finally(() => setLoading(false));
  }, [router]);

  const handleDeleted = (fileId: string) => {
    setFiles((prev) => prev.filter((f) => f.file_id !== fileId));
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20 text-gray-500">
        <Loader2 className="w-6 h-6 animate-spin mr-2" /> Loading your files...
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">My Files</h1>
        <Link
          href="/upload"
          className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white font-semibold px-4 py-2 rounded-lg transition text-sm"
        >
          <Upload className="w-4 h-4" />
          Upload File
        </Link>
      </div>

      {error && (
        <p className="text-sm text-red-600 bg-red-50 border border-red-200 rounded p-3">{error}</p>
      )}

      {files.length === 0 && !error ? (
        <div className="text-center py-20 text-gray-400 space-y-3">
          <FolderOpen className="w-12 h-12 mx-auto" />
          <p>No files yet. Upload your first file to get started.</p>
          <Link
            href="/upload"
            className="inline-block bg-blue-600 hover:bg-blue-700 text-white font-semibold px-5 py-2 rounded-lg transition text-sm mt-2"
          >
            Upload a File
          </Link>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {files.map((file) => (
            <FileCard key={file.file_id} file={file} onDeleted={handleDeleted} />
          ))}
        </div>
      )}
    </div>
  );
}
