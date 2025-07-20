import "./globals.css";
import * as React from "react";
import { Toaster } from "@/components/ui/sonner";
import { Metadata } from "next";

export const metadata: Metadata = {
  title: "Semantic Chunking",
  icons: {
    icon: "/logo.png",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <head />
      <body>
        <main>{children}</main>
        <Toaster />
      </body>
    </html>
  );
}
