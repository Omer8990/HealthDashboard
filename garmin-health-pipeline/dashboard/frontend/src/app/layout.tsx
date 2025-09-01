'use client';
import './globals.css'
import { Inter } from 'next/font/google'

const inter = Inter({ subsets: ['latin'] })

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className="dark">
      <head>
        <title>🧬 Garmin Longevity Matrix</title>
        <meta name="description" content="Cyberpunk-themed health dashboard for longevity optimization" />
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="" />
        <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=JetBrains+Mono:wght@300;400;700&display=swap" rel="stylesheet" />
      </head>
      <body className={`${inter.className} bg-matrix-bg text-cyber-cyan min-h-screen`}>
        <div className="bg-cyber-grid bg-grid opacity-20 fixed inset-0 pointer-events-none"></div>
        <div className="relative z-10">
          {children}
        </div>
      </body>
    </html>
  )
}