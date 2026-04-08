import type { Metadata } from "next";
import { Bebas_Neue, Source_Sans_3, JetBrains_Mono } from "next/font/google";
import "./globals.css";
import { Header } from "@/components/layout/header";
import { Footer } from "@/components/layout/footer";
import { ThemeProvider } from "@/components/theme-provider";
import { ClerkWrapper } from "@/components/clerk-provider";
import { Toaster } from "sonner";

const bebasNeue = Bebas_Neue({
  subsets: ["latin"],
  weight: "400",
  variable: "--font-display",
  display: "swap",
});

const sourceSans3 = Source_Sans_3({
  subsets: ["latin"],
  variable: "--font-body",
  display: "swap",
  weight: ["400", "500", "600", "700"],
});

const jetbrainsMono = JetBrains_Mono({
  subsets: ["latin"],
  variable: "--font-mono",
  display: "swap",
  weight: ["400", "500", "600", "700"],
});

export const metadata: Metadata = {
  title: "PickleIQ — AI Pickleball Paddle Advisor",
  description:
    "Find the perfect pickleball paddle with AI. Price comparisons, technical specs, and personalized recommendations.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning className={`${bebasNeue.variable} ${sourceSans3.variable} ${jetbrainsMono.variable}`}>
      <body className="min-h-screen antialiased flex flex-col font-sans bg-base text-text-primary" suppressHydrationWarning>
        <ThemeProvider attribute="data-theme" defaultTheme="dark" enableSystem={false}>
          <ClerkWrapper>
            <Header />
            <main className="flex-1">{children}</main>
            <Footer />
            <Toaster richColors position="top-right" theme="dark" />
          </ClerkWrapper>
        </ThemeProvider>
      </body>
    </html>
  );
}
