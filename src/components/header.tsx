"use client";

import { Monitor } from "lucide-react";

export function Header() {
  return (
    <header className="bg-white border-b border-gray-200 px-4 py-3">
      <div className="max-w-4xl mx-auto flex items-center gap-3">
        <div className="w-10 h-10 rounded-lg bg-blue-600 flex items-center justify-center">
          <Monitor className="w-6 h-6 text-white" />
        </div>
        <div>
          <h1 className="font-semibold text-gray-900">TechCorp Support</h1>
          <p className="text-xs text-gray-500">Computers, Monitors & Accessories</p>
        </div>
      </div>
    </header>
  );
}
