"use client";

import { Package, Search, ShoppingCart, HelpCircle } from "lucide-react";

const QUICK_ACTIONS = [
  {
    label: "Browse Products",
    prompt: "Show me all your products",
    icon: Package,
  },
  {
    label: "Search",
    prompt: "I'm looking for a monitor",
    icon: Search,
  },
  {
    label: "My Orders",
    prompt: "I want to check my order status",
    icon: ShoppingCart,
  },
  {
    label: "Help",
    prompt: "What can you help me with?",
    icon: HelpCircle,
  },
];

interface QuickActionsProps {
  onSelect: (prompt: string) => void;
  disabled?: boolean;
}

export function QuickActions({ onSelect, disabled }: QuickActionsProps) {
  return (
    <div className="flex gap-2 flex-wrap">
      {QUICK_ACTIONS.map((action) => {
        const Icon = action.icon;
        return (
          <button
            key={action.label}
            onClick={() => onSelect(action.prompt)}
            disabled={disabled}
            className="inline-flex items-center gap-1.5 px-3 py-1.5
                       bg-white border border-gray-200 rounded-full
                       text-sm text-gray-700
                       hover:bg-gray-50 hover:border-gray-300
                       disabled:opacity-50 disabled:cursor-not-allowed
                       transition-colors"
          >
            <Icon className="w-4 h-4" />
            {action.label}
          </button>
        );
      })}
    </div>
  );
}
