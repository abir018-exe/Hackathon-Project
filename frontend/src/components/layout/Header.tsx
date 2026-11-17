"use client";

import * as React from "react";
import Link from "next/link";
import { usePathname, useSearchParams } from "next/navigation";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuLabel, DropdownMenuSeparator, DropdownMenuTrigger } from "@/components/ui/dropdown-menu";
import { Input } from "@/components/ui/input";
import { Search, Bell, ChevronDown, Filter, Zap } from "lucide-react";
import { useAppStore } from "@/store";
import { Badge } from "@/components/ui/badge";

interface HeaderProps {
  onMenuClick?: () => void;
}

export function Header({ onMenuClick }: HeaderProps) {
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const { user, currentProject, unreadCount, setSidebarOpen } = useAppStore();
  
  const [searchQuery, setSearchQuery] = React.useState("");
  const [showNotifications, setShowNotifications] = React.useState(false);

  const projectName = currentProject?.name || "Select a project";
  const projectStatus = currentProject?.status || "none";

  const statusColors: Record<string, string> = {
    pending: "bg-yellow-600",
    scanning: "bg-blue-600",
    analyzed: "bg-green-600",
    stabilizing: "bg-purple-600",
    ready: "bg-green-600",
    error: "bg-red-600",
    none: "bg-muted",
  };

  const statusLabels: Record<string, string> = {
    pending: "Pending",
    scanning: "Scanning",
    analyzed: "Analyzed",
    stabilizing: "Stabilizing",
    ready: "Ready",
    error: "Error",
    none: "No Project",
  };

  return (
    <header className="sticky top-0 z-30 w-full border-b bg-lms-background-secondary/80 backdrop-blur-sm" style={{ borderColor: "hsl(var(--border))", backgroundColor: "#10131BCC" }}>
      <div className="flex h-16 items-center justify-between px-4 lg:px-6">
        {/* Left side - Mobile menu + Project selector */}
        <div className="flex items-center gap-4">
          <Button
            variant="ghost"
            size="icon"
            className="lg:hidden"
            onClick={onMenuClick}
            aria-label="Open menu"
          >
            <svg className="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <line x1="3" y1="6" x2="21" y2="6" />
              <line x1="3" y1="12" x2="21" y2="12" />
              <line x1="3" y1="18" x2="21" y2="18" />
            </svg>
          </Button>

          <div className="hidden sm:flex items-center gap-2">
            <Link href="/dashboard" className="flex items-center gap-2" style={{ color: "#8B7CFF" }}>
              <Zap className="h-5 w-5" />
              <span className="font-semibold text-lg">Last Mile Stabilizer</span>
            </Link>
          </div>

          {/* Project Selector */}
          <div className="hidden md:flex items-center gap-3 px-3 py-1.5 rounded-lg border" style={{ borderColor: "hsl(var(--border))", backgroundColor: "#141925" }}>
            <div className="flex items-center gap-2">
              <div className="relative flex h-8 w-8 items-center justify-center rounded-full" style={{ backgroundColor: "#191F2B" }}>
                <Zap className="h-4 w-4" style={{ color: "#8B7CFF" }} />
              </div>
              <div>
                <p className="text-sm font-medium text-white truncate max-w-[200px]">{projectName}</p>
                <div className="flex items-center gap-1">
                  <span className={cn("h-1.5 w-1.5 rounded-full", statusColors[projectStatus])} />
                  <span className="text-xs text-muted-foreground">{statusLabels[projectStatus]}</span>
                </div>
              </div>
            </div>
            <Button variant="ghost" size="icon" className="ml-1">
              <ChevronDown className="h-4 w-4" />
            </Button>
          </div>
        </div>

        {/* Center - Global Search */}
        <div className="hidden lg:flex flex-1 max-w-xl mx-8">
          <div className="relative w-full">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
            <Input
              placeholder="Search projects, files, issues... (⌘K)"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-10 pr-10 bg-lms-background-card border-lms-background-elevated"
              style={{ backgroundColor: "#141925", borderColor: "#191F2B" }}
            />
            {searchQuery && (
              <Button
                variant="ghost"
                size="icon"
                className="absolute right-2 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
                onClick={() => setSearchQuery("")}
              >
                <svg className="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <line x1="18" y1="6" x2="6" y2="18" />
                  <line x1="6" y1="6" x2="18" y2="18" />
                </svg>
              </Button>
            )}
          </div>
        </div>

        {/* Right side - Notifications, User */}
        <div className="flex items-center gap-2">
          {/* Notifications */}
          <div className="relative">
            <Button
              variant="ghost"
              size="icon"
              className="relative"
              onClick={() => setShowNotifications(!showNotifications)}
              aria-label="Notifications"
            >
              <Bell className="h-5 w-5" />
              {unreadCount > 0 && (
                <span className="absolute -top-1 -right-1 flex h-5 w-5 items-center justify-center rounded-full bg-destructive text-xs text-destructive-foreground">
                  {unreadCount > 9 ? "9+" : unreadCount}
                </span>
              )}
            </Button>
          </div>

          {/* User Menu */}
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" className="relative h-10 w-10 rounded-full" aria-label="User menu">
                <Avatar className="h-10 w-10">
                  <AvatarImage src={user?.avatar || ""} alt={user?.name || "User"} />
                  <AvatarFallback className="text-xs" style={{ backgroundColor: "#8B7CFF", color: "#090B10" }}>
                    {user?.name?.charAt(0).toUpperCase() || "U"}
                  </AvatarFallback>
                </Avatar>
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent className="w-56" align="end" forceMount>
              <DropdownMenuLabel className="font-normal">
                <div className="flex flex-col space-y-1">
                  <p className="font-medium text-sm">{user?.name || "User"}</p>
                  <p className="text-xs text-muted-foreground">{user?.email || "user@example.com"}</p>
                </div>
              </DropdownMenuLabel>
              <DropdownMenuSeparator />
              <DropdownMenuItem asChild>
                <Link href="/profile" className="flex items-center gap-2">
                  <svg className="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
                    <circle cx="12" cy="7" r="4" />
                  </svg>
                  Profile
                </Link>
              </DropdownMenuItem>
              <DropdownMenuItem asChild>
                <Link href="/settings" className="flex items-center gap-2">
                  <svg className="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <circle cx="12" cy="12" r="3" />
                    <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z" />
                  </svg>
                  Settings
                </Link>
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem className="text-destructive focus:text-destructive" onClick={() => {}}>
                <svg className="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" />
                  <polyline points="16 17 21 12 16 7" />
                  <line x1="21" y1="12" x2="9" y2="12" />
                </svg>
                Sign out
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </div>
    </header>
  );
}