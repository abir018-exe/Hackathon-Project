"use client";

import * as React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { SidebarNavItem, navItems, bottomNavItems } from "./sidebar-nav";
import { Toaster } from "@/components/ui/toaster";
import {
  LayoutDashboard,
  FolderKanban,
  Search,
  Brain,
  Wrench,
  Monitor,
  Shield,
  TestTube2,
  FileText,
  Users,
  BarChart3,
  Settings,
  BookOpen,
  HelpCircle,
  User,
  ChevronLeft,
  ChevronRight,
  Github,
  Zap,
} from "lucide-react";
import { useAppStore } from "@/store";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuLabel, DropdownMenuSeparator, DropdownMenuTrigger } from "@/components/ui/dropdown-menu";

const navigation = [
  { name: "Overview", href: "/dashboard", icon: LayoutDashboard, key: "overview" },
  { name: "Projects", href: "/projects", icon: FolderKanban, key: "projects" },
  { name: "Codebase Scanner", href: "/scanner", icon: Search, key: "scanner" },
  { name: "AI Intelligence", href: "/intelligence", icon: Brain, key: "intelligence" },
  { name: "Stabilization", href: "/stabilization", icon: Wrench, key: "stabilization" },
  { name: "Demo Mode", href: "/demo-mode", icon: Monitor, key: "demo-mode" },
  { name: "Risk Monitor", href: "/risk-monitor", icon: Shield, key: "risk-monitor" },
  { name: "Testing & Validation", href: "/testing", icon: TestTube2, key: "testing" },
  { name: "Demo Script", href: "/demo-script", icon: FileText, key: "demo-script" },
  { name: "Team Workspace", href: "/team", icon: Users, key: "team" },
  { name: "Reports", href: "/reports", icon: BarChart3, key: "reports" },
];

const bottomNavigation = [
  { name: "Settings", href: "/settings", icon: Settings, key: "settings" },
  { name: "Documentation", href: "/docs", icon: BookOpen, key: "docs" },
  { name: "Help & Support", href: "/help", icon: HelpCircle, key: "help" },
];

interface SidebarProps {
  onClose?: () => void;
}

export function Sidebar({ onClose }: SidebarProps) {
  const pathname = usePathname();
  const { sidebarOpen, toggleSidebar, user, currentProject } = useAppStore();
  
  const [hovered, setHovered] = React.useState(false);
  const sidebarRef = React.useRef<HTMLDivElement>(null);

  const handleMouseEnter = () => setHovered(true);
  const handleMouseLeave = () => setHovered(false);

  const isActive = (href: string) => {
    if (href === "/dashboard") return pathname === "/dashboard" || pathname === "/";
    return pathname.startsWith(href);
  };

  return (
    <>
      <div
        ref={sidebarRef}
        onMouseEnter={handleMouseEnter}
        onMouseLeave={handleMouseLeave}
        className={cn(
          "fixed left-0 top-0 z-40 h-screen border-r bg-lms-background-card transition-all duration-300 ease-in-out",
          sidebarOpen
            ? "w-64"
            : hovered
            ? "w-20"
            : "w-20"
        )}
        style={{ backgroundColor: "#141925" }}
      >
        {/* Brand Section */}
        <div className="flex h-16 items-center justify-between border-b px-4" style={{ borderColor: "hsl(var(--border))" }}>
          <Link href="/dashboard" className="flex items-center gap-2" onClick={onClose}>
            <div className="flex h-8 w-8 items-center justify-center rounded-lg" style={{ backgroundColor: "#8B7CFF" }}>
              <Zap className="h-5 w-5 text-white" />
            </div>
            <span className={cn(
              "font-semibold text-lg text-white transition-opacity duration-200",
              sidebarOpen || hovered ? "opacity-100" : "opacity-0 invisible w-0"
            )}>
              Last Mile Stabilizer
            </span>
          </Link>
          <Button
            variant="ghost"
            size="icon"
            className={cn(
              "text-muted-foreground hover:text-foreground",
              sidebarOpen || hovered ? "opacity-100" : "opacity-0 invisible"
            )}
            onClick={toggleSidebar}
            aria-label={sidebarOpen ? "Collapse sidebar" : "Expand sidebar"}
          >
            {sidebarOpen ? <ChevronLeft className="h-4 w-4" /> : <ChevronRight className="h-4 w-4" />}
          </Button>
        </div>

        {/* Workspace Selector */}
        <div className="p-4 border-b" style={{ borderColor: "hsl(var(--border))" }}>
          <div className={cn("flex items-center gap-2", sidebarOpen || hovered ? "" : "justify-center")}>
            <div className="relative flex h-8 w-8 items-center justify-center rounded-full" style={{ backgroundColor: "#191F2B" }}>
              <Github className="h-4 w-4 text-muted-foreground" />
            </div>
            <div className={cn("flex-1 min-w-0", sidebarOpen || hovered ? "" : "hidden")}>
              <p className="text-xs font-medium text-white truncate">{currentProject?.name || "No project selected"}</p>
              <p className="text-xs text-muted-foreground truncate">Select a project to begin</p>
            </div>
            <Button
              variant="ghost"
              size="icon"
              className={cn(sidebarOpen || hovered ? "" : "hidden")}
            >
              <ChevronRight className="h-4 w-4" />
            </Button>
          </div>
        </div>

        {/* Main Navigation */}
        <nav className="flex-1 overflow-y-auto p-4 space-y-1" role="navigation" aria-label="Main navigation">
          {navigation.map((item) => {
            const active = isActive(item.href);
            return (
              <Link
                key={item.key}
                href={item.href}
                onClick={onClose}
                className={cn(
                  "flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors",
                  active
                    ? "bg-lms-accent-primary text-lms-background-primary"
                    : "text-muted-foreground hover:text-foreground hover:bg-lms-background-elevated",
                  sidebarOpen || hovered ? "" : "justify-center"
                )}
                style={{ backgroundColor: active ? "#8B7CFF" : "transparent" }}
                title={sidebarOpen || hovered ? undefined : item.name}
                aria-current={active ? "page" : undefined}
              >
                <item.icon className="h-5 w-5 flex-shrink-0" aria-hidden="true" />
                <span className={cn(
                  "truncate transition-opacity duration-200",
                  sidebarOpen || hovered ? "opacity-100" : "opacity-0 invisible w-0"
                )}>
                  {item.name}
                </span>
                {active && (
                  <span className={cn(
                    "absolute right-2 h-1.5 w-1.5 rounded-full",
                    sidebarOpen || hovered ? "opacity-100" : "opacity-0"
                  )} style={{ backgroundColor: "#090B10" }} />
                )}
              </Link>
            );
          })}
        </nav>

        <Separator className="mx-4" style={{ borderColor: "hsl(var(--border))" }} />

        {/* Bottom Navigation */}
        <nav className="flex-1 overflow-y-auto p-4 space-y-1" role="navigation" aria-label="Bottom navigation">
          {bottomNavigation.map((item) => (
            <Link
              key={item.key}
              href={item.href}
              onClick={onClose}
              className={cn(
                "flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors",
                isActive(item.href)
                  ? "bg-lms-accent-primary text-lms-background-primary"
                  : "text-muted-foreground hover:text-foreground hover:bg-lms-background-elevated",
                sidebarOpen || hovered ? "" : "justify-center"
              )}
              style={{ backgroundColor: isActive(item.href) ? "#8B7CFF" : "transparent" }}
              title={sidebarOpen || hovered ? undefined : item.name}
            >
              <item.icon className="h-5 w-5 flex-shrink-0" aria-hidden="true" />
              <span className={cn(
                "truncate transition-opacity duration-200",
                sidebarOpen || hovered ? "opacity-100" : "opacity-0 invisible w-0"
              )}>
                {item.name}
              </span>
            </Link>
          ))}
        </nav>

        {/* User Profile */}
        <div className="p-4 border-t" style={{ borderColor: "hsl(var(--border))" }}>
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <button
                className={cn(
                  "flex w-full items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors text-muted-foreground hover:text-foreground hover:bg-lms-background-elevated",
                  sidebarOpen || hovered ? "" : "justify-center"
                )}
                title={sidebarOpen || hovered ? undefined : user?.name}
              >
                <Avatar className="h-8 w-8">
                  <AvatarImage src={user?.avatar || ""} alt={user?.name || "User"} />
                  <AvatarFallback>{user?.name?.charAt(0).toUpperCase() || "U"}</AvatarFallback>
                </Avatar>
                <div className={cn(
                  "flex-1 min-w-0 text-left",
                  sidebarOpen || hovered ? "" : "hidden"
                )}>
                  <p className="truncate font-medium text-white">{user?.name || "User"}</p>
                  <p className="truncate text-xs text-muted-foreground">{user?.email || "user@example.com"}</p>
                </div>
              </button>
            </DropdownMenuTrigger>
            <DropdownMenuContent className="w-56" align="end" forceMount>
              <DropdownMenuLabel className="font-normal" style={sidebarOpen || hovered ? {} : { display: "none" }}>
                <div className="flex flex-col space-y-1">
                  <p className="font-medium text-sm">{user?.name || "User"}</p>
                  <p className="text-xs text-muted-foreground">{user?.email || "user@example.com"}</p>
                </div>
              </DropdownMenuLabel>
              <DropdownMenuSeparator />
              <DropdownMenuItem asChild>
                <Link href="/profile" onClick={onClose} className="flex items-center gap-2">
                  <User className="h-4 w-4" />
                  Profile
                </Link>
              </DropdownMenuItem>
              <DropdownMenuItem asChild>
                <Link href="/settings" onClick={onClose} className="flex items-center gap-2">
                  <Settings className="h-4 w-4" />
                  Settings
                </Link>
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem className="text-destructive focus:text-destructive" onClick={() => {}}>
                <HelpCircle className="h-4 w-4" />
                Sign out
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </div>

      {/* Backdrop for mobile */}
      {!sidebarOpen && (
        <div
          className="fixed inset-0 z-30 bg-black/50 lg:hidden"
          onClick={onClose}
          aria-hidden="true"
        />
      )}

      <Toaster />
    </>
  );
}