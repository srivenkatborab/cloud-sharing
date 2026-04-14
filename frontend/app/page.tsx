/**
 * Public dashboard — accessible without login.
 *
 * Shows an overview of the application, feature highlights, and
 * calls-to-action for registration and login. This ensures examiners
 * can verify the system is running without needing an account.
 */

import Link from "next/link";
import { Cloud, Upload, Share2, Bell, Lock, Database } from "lucide-react";

const features = [
  {
    icon: <Upload className="w-6 h-6 text-blue-500" />,
    title: "Secure File Upload",
    desc: "Upload any file type directly to Amazon S3 cloud storage with private access control.",
  },
  {
    icon: <Share2 className="w-6 h-6 text-green-500" />,
    title: "File Sharing",
    desc: "Share files with other registered users. Sharing is processed asynchronously via Amazon SQS.",
  },
  {
    icon: <Bell className="w-6 h-6 text-yellow-500" />,
    title: "Email Notifications",
    desc: "Recipients receive instant email alerts via Amazon SNS when a file is shared with them.",
  },
  {
    icon: <Lock className="w-6 h-6 text-purple-500" />,
    title: "Secure Authentication",
    desc: "User accounts are managed by Amazon Cognito with JWT token-based session management.",
  },
  {
    icon: <Database className="w-6 h-6 text-orange-500" />,
    title: "Metadata Storage",
    desc: "File metadata and notifications are stored in Amazon DynamoDB for fast, scalable retrieval.",
  },
  {
    icon: <Cloud className="w-6 h-6 text-blue-400" />,
    title: "Cloud-Native Architecture",
    desc: "Built on five AWS managed services with no self-managed infrastructure, ensuring high availability.",
  },
];

const services = [
  { name: "Amazon S3", colour: "bg-orange-100 text-orange-700", role: "File Storage" },
  { name: "Amazon DynamoDB", colour: "bg-blue-100 text-blue-700", role: "Metadata & Notifications" },
  { name: "Amazon SQS", colour: "bg-yellow-100 text-yellow-700", role: "Async Queue" },
  { name: "Amazon SNS", colour: "bg-green-100 text-green-700", role: "Email Alerts" },
  { name: "Amazon Cognito", colour: "bg-purple-100 text-purple-700", role: "Authentication" },
];

export default function HomePage() {
  return (
    <div className="space-y-12">
      {/* Hero */}
      <section className="text-center py-12 space-y-4">
        <div className="flex justify-center">
          <Cloud className="w-16 h-16 text-blue-600" />
        </div>
        <h1 className="text-4xl font-bold text-gray-900">CloudShare</h1>
        <p className="text-lg text-gray-600 max-w-2xl mx-auto">
          A cloud-native file sharing platform built on Amazon Web Services.
          Upload, manage, and share files securely — powered by five AWS managed services.
        </p>
        <div className="flex gap-4 justify-center pt-2">
          <Link
            href="/register"
            className="bg-blue-600 hover:bg-blue-700 text-white font-semibold px-6 py-2.5 rounded-lg transition"
          >
            Get Started
          </Link>
          <Link
            href="/login"
            className="border border-blue-600 text-blue-600 hover:bg-blue-50 font-semibold px-6 py-2.5 rounded-lg transition"
          >
            Sign In
          </Link>
        </div>
      </section>

      {/* AWS Services badges */}
      <section className="space-y-3">
        <h2 className="text-center text-sm font-semibold text-gray-500 uppercase tracking-widest">
          Powered by AWS
        </h2>
        <div className="flex flex-wrap justify-center gap-3">
          {services.map((s) => (
            <span
              key={s.name}
              className={`px-4 py-2 rounded-full text-sm font-medium ${s.colour}`}
            >
              {s.name} — {s.role}
            </span>
          ))}
        </div>
      </section>

      {/* Features grid */}
      <section className="space-y-4">
        <h2 className="text-2xl font-bold text-gray-800 text-center">Features</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {features.map((f) => (
            <div
              key={f.title}
              className="bg-white border border-gray-200 rounded-lg p-5 shadow-sm space-y-2"
            >
              {f.icon}
              <h3 className="font-semibold text-gray-800">{f.title}</h3>
              <p className="text-sm text-gray-600">{f.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* How it works */}
      <section className="bg-blue-50 border border-blue-100 rounded-xl p-8 space-y-4">
        <h2 className="text-2xl font-bold text-gray-800">How It Works</h2>
        <ol className="space-y-2 text-gray-700 text-sm list-decimal list-inside">
          <li>Register an account — Cognito verifies your email address.</li>
          <li>Log in and upload a file — stored securely in Amazon S3.</li>
          <li>View and manage your files from the dashboard.</li>
          <li>Share a file with another user — placed on an SQS queue for async processing.</li>
          <li>The recipient receives an SNS email notification and can download the file.</li>
        </ol>
      </section>
    </div>
  );
}
