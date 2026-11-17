"use client";

import * as React from "react";
import { Sidebar } from "./Sidebar";
import { Header } from "./Header";
import { cn } from "@/lib/utils";
import { useAppStore } from "@/store";

interface DashboardLayoutProps {
  children: React.ReactNode;
}

export function DashboardLayout({ children }: DashboardLayoutProps) {
  const { sidebarOpen } = useAppStore();
  const [mobileMenuOpen, setMobileMenuOpen] = React.useState(false);

  return (
    <div className="min-h-screen bg-lms-background-primary" style={{ backgroundColor: "#090B10" }}>
      <Sidebar onClose={() => setMobileMenuOpen(false)} />
      <Header onMenuClick={() => setMobileMenuOpen(true)} />
      
      <main
        className={cn(
          "transition-all duration-300 ease-in-out min-h-[calc(100vh-4rem)]",
          sidebarOpen ? "lg:ml-64" : "lg:ml-20"
        )}
        style={{ backgroundColor: "#090B10" }}
      >
        <div className="p-4 lg:p-6">
          {children}
        </div>
      </main>

      {/* Mobile menu backdrop */}
      {mobileMenuOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/50 lg:hidden"
          onClick={() => setMobileMenuOpen(false)}
          aria-hidden="true"
        />
      )}
    </div>
  );
}