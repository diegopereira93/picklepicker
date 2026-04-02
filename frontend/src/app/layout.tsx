import type { Metadata } from "next";
import "./globals.css";
import { ClerkProvider } from "@clerk/nextjs";
import { Header } from "@/components/layout/header";
import { Footer } from "@/components/layout/footer";

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
      <html lang="pt-BR" style={{ fontFamily: "'NVIDIA-EMEA', Arial, Helvetica, sans-serif" }}>
        <head>
          <link
            rel="stylesheet"
            href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css"
            crossOrigin="anonymous"
          />
        </head>
        <body className="min-h-screen bg-background text-foreground antialiased flex flex-col">
          <Header />
          <main className="flex-1">{children}</main>
          <Footer />
        </body>
      </html>
    </ClerkProvider>
  );
}
