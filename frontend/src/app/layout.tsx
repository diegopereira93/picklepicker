import type { Metadata } from "next";
import { Inter } from "next/font/google";
import dynamic from "next/dynamic";
import Script from "next/script";
import "./globals.css";
import { ClerkProvider } from "@clerk/nextjs";
import { ThemeProvider } from "@/components/theme-provider";
import { Header } from "@/components/layout/header";
import { Footer } from "@/components/layout/footer";
import { ClerkAvailableProvider } from "@/components/layout/header";

// Dynamic import for SpeedInsights to defer loading until after interactive
const SpeedInsights = dynamic(
  () => import("@vercel/speed-insights/next").then((mod) => mod.SpeedInsights),
  { ssr: false }
);

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-sans",
  preload: true,
  display: "swap",
  adjustFontFallback: true,
  fallback: ["system-ui", "sans-serif"],
});

export const metadata: Metadata = {
  title: "PickleIQ — AI Pickleball Paddle Advisor",
  description:
    "Encontre a raquete de pickleball perfeita com ajuda de IA. Comparador de precos, especificacoes tecnicas e recomendacoes personalizadas para jogadores brasileiros.",
  other: {
    preconnect: [
      { rel: "preconnect", href: "https://fonts.googleapis.com" },
      { rel: "preconnect", href: "https://fonts.gstatic.com", crossOrigin: "anonymous" },
    ],
  },
};

// Check if Clerk keys are available
const hasClerkKeys = process.env.CLERK_SECRET_KEY && process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY;

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  const content = (
    <html lang="pt-BR" className={inter.variable} suppressHydrationWarning>
      <body className="min-h-screen bg-background font-sans antialiased flex flex-col">
        <a
          href="#main-content"
          className="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 focus:z-50 focus:px-4 focus:py-2 focus:bg-primary focus:text-primary-foreground focus:rounded-md"
        >
          Pular para o conteúdo principal
        </a>
        <ThemeProvider
          attribute="class"
          defaultTheme="system"
          enableSystem
          disableTransitionOnChange
        >
          <ClerkAvailableProvider available={hasClerkKeys}>
            <Header />
            <main id="main-content" className="flex-1">{children}</main>
            <Footer />
          </ClerkAvailableProvider>
          <SpeedInsights sampleRate={1.0} />
        </ThemeProvider>
      </body>
    </html>
  );

  // Only wrap with ClerkProvider if keys are available
  return hasClerkKeys ? <ClerkProvider>{content}</ClerkProvider> : content;
}
