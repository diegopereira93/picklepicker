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
  title: "PickleIQ — Recomendações Inteligentes de Raquetes de Pickleball",
  description:
    "Encontre a raquete de pickleball perfeita com IA. Compare preços, veja especificações técnicas e receba recomendações personalizadas em português.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="pt-BR" suppressHydrationWarning className={`${bebasNeue.variable} ${sourceSans3.variable} ${jetbrainsMono.variable}`}>
      <body className="min-h-screen antialiased flex flex-col font-sans bg-base text-text-primary" suppressHydrationWarning>
        <ThemeProvider attribute="data-theme" defaultTheme="dark" enableSystem={false}>
          <ClerkWrapper>
              <a
                href="#main-content"
                className="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 focus:z-50 focus:px-4 focus:py-2 focus:bg-brand-primary focus:text-base focus:rounded focus:font-semibold"
              >
                Pular para o conteúdo
              </a>
            <Header />
            <main id="main-content" className="flex-1">{children}</main>
            <Footer />
            <Toaster richColors position="top-right" theme="dark" />
          </ClerkWrapper>
        </ThemeProvider>
      </body>
    </html>
  );
}
