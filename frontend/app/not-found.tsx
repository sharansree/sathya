'use client'
import Link from 'next/link'
import { useEffect, useState } from 'react'

export default function NotFound() {
  const [mounted, setMounted] = useState(false)
  useEffect(() => setMounted(true), [])
  if (!mounted) return null

  return (
    <div style={{
      minHeight: '100vh',
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      background: '#f5f0e8',
      gap: '16px',
      textAlign: 'center',
      padding: '24px'
    }}>
      <span style={{ fontSize: 32, color: '#c4922a' }}>☸</span>
      <h1 style={{
        fontFamily: 'Georgia, serif',
        fontSize: 48,
        fontWeight: 300,
        color: '#1e1c18',
        letterSpacing: -1,
        margin: 0
      }}>404</h1>
      <p style={{
        fontFamily: 'Georgia, serif',
        fontSize: 18,
        color: '#5c5a54',
        fontStyle: 'italic',
        maxWidth: 380,
        lineHeight: 1.7,
        margin: 0
      }}>
        "Do not pursue the past. Do not lose yourself in the future."
      </p>
      <p style={{
        fontSize: 11,
        color: '#9b9890',
        letterSpacing: 1,
        margin: 0
      }}>
        MN 131 · Majjhima Nikaya
      </p>
      <Link href="/" style={{
        marginTop: 16,
        background: '#1e1c18',
        color: '#f5f0e8',
        padding: '10px 24px',
        fontSize: 13,
        textDecoration: 'none',
        display: 'inline-block'
      }}>
        Return home
      </Link>
    </div>
  )
}