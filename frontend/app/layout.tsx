import type { Metadata } from "next";
import "./globals.css";
import { SiteHeader } from "@/components/museum/SiteHeader";
import { SiteFooter } from "@/components/museum/SiteFooter";

export const metadata: Metadata = {
  title: "Digital Museum | AI Museum Guide",
  description: "Explore curated art and artifacts with visual recognition and knowledge-based conversational QA.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen font-sans antialiased">
        <SiteHeader />
        <main>{children}</main>
        <SiteFooter />
      </body>
    </html>
  );
}
