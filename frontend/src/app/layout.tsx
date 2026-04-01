import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { ClerkProvider } from "@clerk/nextjs";
import { ThemeProvider } from "@/components/theme-provider";
import { Header } from "@/components/layout/header";
import { Footer } from "@/components/layout/footer";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-sans",
  preload: true,
  display: "swap",
});

export const metadata: Metadata = {
  title: "PickleIQ — AI Pickleball Paddle Advisor",
  description:
    "Encontre a raquete de pickleball perfeita com ajuda de IA. Comparador de precos, especificacoes tecnicas e recomendacoes personalizadas para jogadores brasileiros.",
  preload: [
    {
      rel: "preload",
      href: "/_next/static/css/app/layout.css",
      as: "style",
    },
  ],
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <ClerkProvider>
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
            <Header />
            <main id="main-content" className="flex-1">{children}</main>
            <Footer />
          </ThemeProvider>
        </body>
      </html>
    </ClerkProvider>
  );
}
