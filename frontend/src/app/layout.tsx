import type { Metadata } from "next";
import Script from "next/script";
import { Inter, JetBrains_Mono } from "next/font/google";
import "./globals.css";
import { ClerkProvider } from "@clerk/nextjs";
import { Header } from "@/components/layout/header";
import { Footer } from "@/components/layout/footer";
import { ThemeProvider } from "@/components/theme-provider";

const inter = Inter({
  subsets: ["latin"],
  display: "swap",
  variable: "--font-inter",
});

const jetbrainsMono = JetBrains_Mono({
  subsets: ["latin"],
  display: "swap",
  variable: "--font-mono",
});

export const metadata: Metadata = {
  title: "PickleIQ — AI Pickleball Paddle Advisor",
  description:
    "Encontre a raquete de pickleball perfeita com ajuda de IA. Comparador de precos, especificacoes tecnicas e recomendacoes personalizadas para jogadores brasileiros.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <ClerkProvider>
      <ThemeProvider attribute="data-theme" defaultTheme="light" enableSystem>
        <html lang="pt-BR" className={`${inter.variable} ${jetbrainsMono.variable}`}>
          <head>
            <Script id="clerk-title-guard" strategy="afterInteractive">
              {`(function(){var T="PickleIQ — AI Pickleball Paddle Advisor";function r(){var t=document.querySelector("title");if(t){if(!t.textContent)t.textContent=T}else{var e=document.createElement("title");e.textContent=T;document.head.appendChild(e)}}r();var o=new MutationObserver(r);o.observe(document.head,{childList:true})})()`}
            </Script>
          </head>
          <body className="min-h-screen antialiased flex flex-col">
            <Header />
            <main className="flex-1">{children}</main>
            <Footer />
          </body>
        </html>
      </ThemeProvider>
    </ClerkProvider>
  );
}
