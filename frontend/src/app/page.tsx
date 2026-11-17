"use client";

import * as React from "react";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { cn } from "@/lib/utils";
import {
  Zap,
  Shield,
  Brain,
  Wrench,
  Monitor,
  TestTube2,
  FileText,
  Users,
  BarChart3,
  ArrowRight,
  CheckCircle,
  Github,
  FileCode,
  Terminal,
  Database,
  Globe,
  Lock,
  Clock,
  Rocket,
  Target,
  Sparkles,
} from "lucide-react";

const features = [
  {
    icon: Search,
    title: "Codebase Scanner",
    description: "Deep static analysis of your entire project. Detect languages, frameworks, dependencies, broken imports, secrets, and configuration issues.",
    href: "/scanner",
  },
  {
    icon: Brain,
    title: "AI Demo Intelligence",
    description: "Get a Demo Survival Score (0-100), feature-wise reliability, failure predictions, and AI-powered stabilization recommendations.",
    href: "/intelligence",
  },
  {
    icon: Wrench,
    title: "Automated Stabilization",
    description: "AI-generated patches with diff views, mock data injection, API fallbacks, and human approval workflow. Never modifies original code.",
    href: "/stabilization",
  },
  {
    icon: Monitor,
    title: "One-Click Demo Mode",
    description: "Isolated demo environment with mocked APIs, stable datasets, feature flags, and safe rollback. Network-independent demonstrations.",
    href: "/demo-mode",
  },
  {
    icon: Shield,
    title: "Live Risk Monitor",
    description: "Git commit risk analysis, demo path protection, dependency alerts, and Demo Freeze Mode to lock down your approved version.",
    href: "/risk-monitor",
  },
  {
    icon: TestTube2,
    title: "Automated Testing",
    description: "Smoke tests, happy path validation, API health checks, UI flow testing, and regression detection with detailed reports.",
    href: "/testing",
  },
];

const techStack = [
  { icon: Github, name: "GitHub Integration", description: "Direct repository cloning and branch selection" },
  { icon: FileCode, name: "Multi-Language Support", description: "JavaScript, TypeScript, Python, Go, Rust, Java, and more" },
  { icon: Terminal, name: "Framework Detection", description: "React, Next.js, Vue, Django, FastAPI, Express, Spring, etc." },
  { icon: Database, name: "Database Analysis", description: "PostgreSQL, MySQL, MongoDB, Redis, SQLite detection" },
  { icon: Globe, name: "API Discovery", description: "REST, GraphQL, gRPC endpoint mapping" },
  { icon: Lock, name: "Secret Detection", description: "API keys, tokens, passwords, certificates scanning" },
];

const stats = [
  { value: "95%+", label: "Demo Survival Rate", icon: Target },
  { value: "< 5 min", label: "Average Scan Time", icon: Clock },
  { value: "50+", label: "Supported Frameworks", icon: Sparkles },
  { value: "Zero", label: "Original Code Modified", icon: Shield },
];

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-lms-background-primary" style={{ backgroundColor: "#090B10" }}>
      {/* Navigation */}
      <nav className="fixed top-0 left-0 right-0 z-50 border-b bg-lms-background-secondary/80 backdrop-blur-sm" style={{ borderColor: "#191F2B", backgroundColor: "#10131BCC" }}>
        <div className="flex h-16 items-center justify-between px-4 lg:px-8">
          <Link href="/" className="flex items-center gap-2" style={{ color: "#8B7CFF" }}>
            <Zap className="h-6 w-6" />
            <span className="font-semibold text-xl">Last Mile Stabilizer</span>
          </Link>
          <div className="hidden md:flex items-center gap-6">
            <Link href="#features" className="text-sm font-medium text-muted-foreground hover:text-foreground transition-colors">Features</Link>
            <Link href="#how-it-works" className="text-sm font-medium text-muted-foreground hover:text-foreground transition-colors">How It Works</Link>
            <Link href="#tech-stack" className="text-sm font-medium text-muted-foreground hover:text-foreground transition-colors">Tech Stack</Link>
            <Link href="#security" className="text-sm font-medium text-muted-foreground hover:text-foreground transition-colors">Security</Link>
          </div>
          <div className="flex items-center gap-3">
            <Link href="/login">
              <Button variant="ghost" size="sm">Sign In</Button>
            </Link>
            <Link href="/register">
              <Button size="sm" style={{ backgroundColor: "#8B7CFF", color: "#090B10" }}>
                Get Started
                <ArrowRight className="ml-2 h-4 w-4" />
              </Button>
            </Link>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative pt-32 pb-20 lg:pt-48 lg:pb-32 px-4 lg:px-8 overflow-hidden">
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-lms-accent-primary/10 via-transparent to-transparent" style={{ backgroundColor: "rgba(139, 124, 255, 0.1)" }} />
        <div className="absolute inset-0 bg-[url('/grid.svg')] opacity-5" />
        
        <div className="relative max-w-5xl mx-auto text-center">
          <div className="inline-flex items-center gap-2 rounded-full border px-4 py-1.5 mb-8 text-sm font-medium" style={{ borderColor: "#191F2B", backgroundColor: "#141925", color: "#929BAA" }}>
            <span className="relative flex h-2 w-2" style={{ backgroundColor: "#35C98A" }}>
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full opacity-75" style={{ backgroundColor: "#35C98A" }} />
            </span>
            Now in Public Beta
          </div>
          
          <h1 className="mb-6 text-4xl lg:text-6xl font-bold tracking-tight text-white">
            Your project deserves a demo
            <br />
            <span style={{ color: "#8B7CFF" }} className="relative">that doesn't fail.</span>
          </h1>
          
          <p className="mx-auto mb-10 max-w-2xl text-lg lg:text-xl text-muted-foreground">
            Analyse, stabilize and validate your software before the moment that matters. 
            Transform unstable, incomplete or unreliable projects into tested, demo-ready applications.
          </p>
          
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link href="/register">
              <Button size="lg" className="gap-2 px-8 py-3 text-lg" style={{ backgroundColor: "#8B7CFF", color: "#090B10" }}>
                Stabilize Your Project
                <ArrowRight className="h-5 w-5" />
              </Button>
            </Link>
            <Link href="/demo">
              <Button size="lg" variant="outline" className="gap-2 px-8 py-3 text-lg">
                Explore Platform
                <ArrowRight className="h-5 w-5" />
              </Button>
            </Link>
          </div>

          {/* Trust indicators */}
          <div className="mt-16 flex flex-wrap items-center justify-center gap-8 text-sm text-muted-foreground">
            <div className="flex items-center gap-2">
              <CheckCircle className="h-4 w-4" style={{ color: "#35C98A" }} />
              <span>Zero original code modification</span>
            </div>
            <div className="flex items-center gap-2">
              <CheckCircle className="h-4 w-4" style={{ color: "#35C98A" }} />
              <span>Human approval required</span>
            </div>
            <div className="flex items-center gap-2">
              <CheckCircle className="h-4 w-4" style={{ color: "#35C98A" }} />
              <span>Isolated execution environments</span>
            </div>
            <div className="flex items-center gap-2">
              <CheckCircle className="h-4 w-4" style={{ color: "#35C98A" }} />
              <span>Complete audit trail</span>
            </div>
          </div>
        </div>
      </section>

      {/* Stats */}
      <section className="py-16 px-4 lg:px-8 border-y" style={{ borderColor: "#191F2B" }}>
        <div className="max-w-6xl mx-auto grid grid-cols-2 lg:grid-cols-4 gap-8">
          {stats.map((stat) => (
            <div key={stat.label} className="text-center">
              <div className="flex items-center justify-center gap-2 mb-2">
                <stat.icon className="h-5 w-5" style={{ color: "#8B7CFF" }} />
              </div>
              <div className="text-3xl lg:text-4xl font-bold text-white">{stat.value}</div>
              <div className="text-sm text-muted-foreground">{stat.label}</div>
            </div>
          ))}
        </div>
      </section>

      {/* Features */}
      <section id="features" className="py-20 lg:py-28 px-4 lg:px-8">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="mb-4 text-3xl lg:text-4xl font-bold text-white">Core Capabilities</h2>
            <p className="mx-auto max-w-2xl text-lg text-muted-foreground">
              Every module is designed to work together seamlessly, taking your project from unstable to demo-ready.
            </p>
          </div>
          
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {features.map((feature) => (
              <Link key={feature.title} href={feature.href} className="group">
                <Card className="h-full transition-all hover:shadow-lg hover:border-lms-accent-primary/50" style={{ backgroundColor: "#141925", borderColor: "#191F2B" }}>
                  <CardHeader>
                    <div className="mb-3 flex h-12 w-12 items-center justify-center rounded-lg" style={{ backgroundColor: "rgba(139, 124, 255, 0.1)" }}>
                      <feature.icon className="h-6 w-6" style={{ color: "#8B7CFF" }} />
                    </div>
                    <CardTitle className="text-lg">{feature.title}</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-sm text-muted-foreground group-hover:text-foreground transition-colors">
                      {feature.description}
                    </p>
                  </CardContent>
                </Card>
              </Link>
            ))}
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section id="how-it-works" className="py-20 lg:py-28 px-4 lg:px-8" style={{ backgroundColor: "#10131B" }}>
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="mb-4 text-3xl lg:text-4xl font-bold text-white">How It Works</h2>
            <p className="mx-auto max-w-2xl text-lg text-muted-foreground">
              From unstable code to confident demo in four steps.
            </p>
          </div>
          
          <div className="grid md:grid-cols-4 gap-8">
            {[
              { step: "01", title: "Connect Your Project", description: "Upload a ZIP or connect GitHub. We analyze structure, dependencies, and configuration without executing code.", icon: FileCode },
              { step: "02", title: "AI Risk Analysis", description: "Get a Demo Survival Score, feature reliability ratings, failure predictions, and prioritized stabilization recommendations.", icon: Brain },
              { step: "03", title: "Stabilize & Test", description: "Review AI-generated patches, approve changes, inject mocks, configure fallbacks. Run automated tests to verify.", icon: Wrench },
              { step: "04", title: "Demo with Confidence", description: "Activate Demo Mode, generate presentation scripts, freeze your version. Walk into the demo knowing it works.", icon: Rocket },
            ].map((item) => (
              <div key={item.step} className="relative">
                <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-xl" style={{ backgroundColor: "rgba(139, 124, 255, 0.1)" }}>
                  <item.icon className="h-6 w-6" style={{ color: "#8B7CFF" }} />
                </div>
                <div className="mb-2 text-2xl font-bold text-white">{item.step}</div>
                <h3 className="mb-2 text-lg font-semibold text-white">{item.title}</h3>
                <p className="text-sm text-muted-foreground">{item.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Tech Stack */}
      <section id="tech-stack" className="py-20 lg:py-28 px-4 lg:px-8">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="mb-4 text-3xl lg:text-4xl font-bold text-white">Supported Technologies</h2>
            <p className="mx-auto max-w-2xl text-lg text-muted-foreground">
              Comprehensive detection and analysis across the modern development ecosystem.
            </p>
          </div>
          
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
            {techStack.map((tech) => (
              <Card key={tech.name} className="transition-colors hover:border-lms-accent-primary/50" style={{ backgroundColor: "#141925", borderColor: "#191F2B" }}>
                <CardContent className="pt-6">
                  <div className="flex items-start gap-4">
                    <div className="flex h-10 w-10 items-center justify-center rounded-lg" style={{ backgroundColor: "rgba(139, 124, 255, 0.1)" }}>
                      <tech.icon className="h-5 w-5" style={{ color: "#8B7CFF" }} />
                    </div>
                    <div>
                      <h4 className="font-medium text-white">{tech.name}</h4>
                      <p className="text-sm text-muted-foreground">{tech.description}</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Security */}
      <section id="security" className="py-20 lg:py-28 px-4 lg:px-8" style={{ backgroundColor: "#10131B" }}>
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="mb-4 text-3xl lg:text-4xl font-bold text-white">Security & Safety First</h2>
            <p className="mx-auto max-w-2xl text-lg text-muted-foreground">
              Built with developer trust as the foundation. Every design decision prioritizes your code's safety.
            </p>
          </div>
          
          <div className="grid md:grid-cols-3 gap-6">
            {[
              { icon: Shield, title: "Original Code Preservation", description: "Never modifies your source project. All changes happen in isolated working copies with full version history." },
              { icon: Lock, title: "Isolated Execution", description: "Code runs in Docker sandboxes with CPU, memory, and time limits. No network access by default." },
              { icon: Clock, title: "Complete Audit Trail", description: "Every scan, patch, approval, and rollback logged. Full transparency for compliance and debugging." },
            ].map((item) => (
              <Card key={item.title} className="h-full" style={{ backgroundColor: "#141925", borderColor: "#191F2B" }}>
                <CardContent className="pt-6">
                  <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-lg" style={{ backgroundColor: "rgba(53, 201, 138, 0.1)" }}>
                    <item.icon className="h-6 w-6" style={{ color: "#35C98A" }} />
                  </div>
                  <h3 className="mb-2 text-lg font-semibold text-white">{item.title}</h3>
                  <p className="text-sm text-muted-foreground">{item.description}</p>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-20 lg:py-28 px-4 lg:px-8">
        <div className="max-w-3xl mx-auto text-center">
          <div className="relative rounded-2xl p-8 lg:p-16" style={{ backgroundColor: "#141925", borderColor: "#191F2B" }}>
            <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-lms-accent-primary/20 via-transparent to-transparent rounded-2xl" style={{ backgroundColor: "rgba(139, 124, 255, 0.2)" }} />
            <div className="relative">
              <h2 className="mb-4 text-3xl lg:text-4xl font-bold text-white">
                Ready to make your demo survive?
              </h2>
              <p className="mx-auto mb-8 max-w-xl text-lg text-muted-foreground">
                Join developers who ship confident demos. Start stabilizing your project today.
              </p>
              <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
                <Link href="/register">
                  <Button size="lg" className="gap-2 px-8 py-3 text-lg" style={{ backgroundColor: "#8B7CFF", color: "#090B10" }}>
                    Start Free - No Credit Card
                    <ArrowRight className="h-5 w-5" />
                  </Button>
                </Link>
                <Link href="/docs">
                  <Button size="lg" variant="outline" className="gap-2 px-8 py-3 text-lg">
                    Read Documentation
                  </Button>
                </Link>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-12 px-4 lg:px-8 border-t" style={{ borderColor: "#191F2B" }}>
        <div className="max-w-6xl mx-auto">
          <div className="grid md:grid-cols-4 gap-8 mb-8">
            <div>
              <Link href="/" className="flex items-center gap-2 mb-4" style={{ color: "#8B7CFF" }}>
                <Zap className="h-6 w-6" />
                <span className="font-semibold text-lg text-white">Last Mile Stabilizer</span>
              </Link>
              <p className="text-sm text-muted-foreground">
                Stop building. Start stabilizing. Make your demo survive.
              </p>
            </div>
            <div>
              <h4 className="mb-4 font-medium text-white">Product</h4>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li><Link href="/features" className="hover:text-foreground transition-colors">Features</Link></li>
                <li><Link href="/pricing" className="hover:text-foreground transition-colors">Pricing</Link></li>
                <li><Link href="/changelog" className="hover:text-foreground transition-colors">Changelog</Link></li>
                <li><Link href="/roadmap" className="hover:text-foreground transition-colors">Roadmap</Link></li>
              </ul>
            </div>
            <div>
              <h4 className="mb-4 font-medium text-white">Resources</h4>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li><Link href="/docs" className="hover:text-foreground transition-colors">Documentation</Link></li>
                <li><Link href="/blog" className="hover:text-foreground transition-colors">Blog</Link></li>
                <li><Link href="/community" className="hover:text-foreground transition-colors">Community</Link></li>
                <li><Link href="/api-docs" className="hover:text-foreground transition-colors">API Reference</Link></li>
              </ul>
            </div>
            <div>
              <h4 className="mb-4 font-medium text-white">Company</h4>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li><Link href="/about" className="hover:text-foreground transition-colors">About</Link></li>
                <li><Link href="/careers" className="hover:text-foreground transition-colors">Careers</Link></li>
                <li><Link href="/privacy" className="hover:text-foreground transition-colors">Privacy</Link></li>
                <li><Link href="/terms" className="hover:text-foreground transition-colors">Terms</Link></li>
              </ul>
            </div>
          </div>
          <div className="flex flex-col md:flex-row items-center justify-between gap-4 pt-8 border-t" style={{ borderColor: "#191F2B" }}>
            <p className="text-sm text-muted-foreground">© 2026 Last Mile Stabilizer. All rights reserved.</p>
            <div className="flex items-center gap-6">
              <a href="https://github.com" target="_blank" rel="noopener noreferrer" className="text-muted-foreground hover:text-foreground transition-colors">
                <Github className="h-5 w-5" />
              </a>
              <a href="https://twitter.com" target="_blank" rel="noopener noreferrer" className="text-muted-foreground hover:text-foreground transition-colors">
                <svg className="h-5 w-5" viewBox="0 0 24 24" fill="currentColor"><path d="M23 3a10.9 10.9 0 0 1-3.14 1.53 4.48 4.48 0 0 0-7.86 3v1A10.66 10.66 0 0 1 3 4s-4 9 5 13a11.64 11.64 0 0 1-7 2c9 5 20 0 20-11.5a4.5 4.5 0 0 0-.08-.83A7.72 7.72 0 0 0 23 3z"/></svg>
              </a>
              <a href="https://linkedin.com" target="_blank" rel="noopener noreferrer" className="text-muted-foreground hover:text-foreground transition-colors">
                <svg className="h-5 w-5" viewBox="0 0 24 24" fill="currentColor"><path d="M16 8a6 6 0 0 1 6 6v7h-4v-7a2 2 0 0 0-2-2 2 2 0 0 0-2 2v7h-4v-7a6 6 0 0 1 6-6z"/><rect x="2" y="9" width="4" height="12"/><circle cx="4" cy="4" r="2"/></svg>
              </a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}