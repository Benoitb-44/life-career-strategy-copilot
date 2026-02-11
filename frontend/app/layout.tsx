import type { Metadata } from "next";
import { FlowProvider } from "@/lib/flow-store";
import "./globals.css";

export const metadata: Metadata = {
  title: "Life/Career Strategy Copilot",
  description: "Minimal frontend flow",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="fr">
      <body>
        <FlowProvider>
          <main className="container">{children}</main>
        </FlowProvider>
      </body>
    </html>
  );
}
