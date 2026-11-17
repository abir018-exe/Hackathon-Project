import type { Metadata, Viewport } from "next";
import { Inter, Geist_Mono } from "next/font/google";
import "./globals.css";

const inter = Inter({
  subsets: ["latin"],
  display: "swap",
  variable: "--font-inter",
});

const geistMono = Geist_Mono({
  subsets: ["latin"],
  display: "swap",
  variable: "--font-geist-mono",
});

export const metadata: Metadata = {
  title: "Last Mile Stabilizer - AI-Powered Hackathon Project Stabilization",
  description: "Analyse, stabilize and validate your software before the moment that matters. Transform unstable projects into demo-ready applications.",
  keywords: ["hackathon", "stabilization", "demo", "testing", "AI", "developer tools", "code analysis"],
  authors: [{ name: "Last Mile Stabilizer Team" }],
  creator: "Last Mile Stabilizer",
  publisher: "Last Mile Stabilizer",
  robots: "index, follow",
  openGraph: {
    type: "website",
    locale: "en_US",
    url: "https://lastmilestabilizer.com",
    title: "Last Mile Stabilizer - Make Your Demo Survive",
    description: "Stop building. Start stabilizing. Transform unstable projects into tested, demo-ready applications.",
    siteName: "Last Mile Stabilizer",
  },
  twitter: {
    card: "summary_large_image",
    title: "Last Mile Stabilizer",
    description: "Your project deserves a demo that doesn't fail.",
  },
  verification: {
    google: "google-site-verification-code",
  },
};

export const viewport: Viewport = {
  themeColor: "#090B10",
  width: "device-width",
  initialScale: 1,
  maximumScale: 5,
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
      </head>
      <body className={`${inter.variable} ${geistMono.variable} antialiased`}>
        {children}
      </body>
    </html>
  );
}