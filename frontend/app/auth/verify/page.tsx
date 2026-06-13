'use client'
import { useEffect, useState, Suspense } from 'react'
import { useSearchParams } from 'next/navigation'
import Link from 'next/link'
import { api } from '@/lib/api'
import styles from '../auth.module.css'

function VerifyForm() {
  const searchParams = useSearchParams()
  const token = searchParams.get('token')
  const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading')
  const [message, setMessage] = useState('')

  useEffect(() => {
    if (!token) { setStatus('error'); setMessage('Invalid verification link.'); return }
    api.auth.verify(token)
      .then(() => setStatus('success'))
      .catch(err => { setStatus('error'); setMessage(err.message) })
  }, [token])

  return (
    <div className={styles.container}>
      <div className={styles.card}>
        <div className={styles.ornament}>☸</div>
        {status === 'loading' && <h1 className={styles.title}>Verifying...</h1>}
        {status === 'success' && (
          <>
            <h1 className={styles.title}>Verified</h1>
            <p className={styles.subtitle}>Your account is now active.</p>
            <Link href="/auth/login" className="btn-primary" style={{ display: 'block', textAlign: 'center', marginTop: 24 }}>
              Sign in
            </Link>
          </>
        )}
        {status === 'error' && (
          <>
            <h1 className={styles.title}>Link expired</h1>
            <p className={styles.subtitle}>{message || 'This verification link is invalid or has expired.'}</p>
            <Link href="/auth/register" className="btn-primary" style={{ display: 'block', textAlign: 'center', marginTop: 24 }}>
              Register again
            </Link>
          </>
        )}
      </div>
    </div>
  )
}

export default function VerifyPage() {
  return (
    <Suspense fallback={null}>
      <VerifyForm />
    </Suspense>
  )
}