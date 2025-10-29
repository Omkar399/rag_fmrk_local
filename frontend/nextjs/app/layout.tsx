import type { Metadata } from 'next'
import { Toaster } from 'sonner'
import { Inter } from 'next/font/google'
import './globals.css'

const inter = Inter({
  subsets: ['latin'],
  weight: ['400', '500', '600', '700'],
  variable: '--font-inter',
})

export const metadata: Metadata = {
  title: 'RAG Chat',
  description: 'Local RAG Pipeline with LM Studio',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className={`${inter.variable} dark`}>
      <body className="font-inter">
        {children}
        <Toaster />
      </body>
    </html>
  )
}
