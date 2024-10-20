import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Calendario Cortes de Luz",
  description: "Calendario Cortes de Luz Ecuador",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
