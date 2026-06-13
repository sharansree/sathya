'use client'
import { useState, useEffect } from 'react'
import { useAuth } from '@/lib/auth-context'
import { useRouter } from 'next/navigation'
import { api } from '@/lib/api'
import Link from 'next/link'
import styles from './library.module.css'

interface Question {
  id: string
  question: string
  answer: string
  sources: any[]
  created_at: string
}

export default function LibraryPage() {
  const { user, loading, logout } = useAuth()
  const router = useRouter()
  const [questions, setQuestions] = useState<Question[]>([])
  const [fetching, setFetching] = useState(true)
  const [expanded, setExpanded] = useState<string | null>(null)

  useEffect(() => {
    if (!loading && !user) router.push('/auth/login')
  }, [user, loading, router])

  useEffect(() => {
    if (user) {
      api.questions.history()
        .then(data => setQuestions(data.questions))
        .finally(() => setFetching(false))
    }
  }, [user])

  const handleDelete = async (id: string) => {
    await api.questions.delete(id)
    setQuestions(q => q.filter(item => item.id !== id))
    if (expanded === id) setExpanded(null)
  }

  const formatDate = (dt: string) => {
    return new Date(dt).toLocaleDateString('en-US', {
      month: 'short', day: 'numeric', year: 'numeric'
    })
  }

  if (loading || fetching) return (
    <div style={{
      minHeight: '100vh',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      background: '#f5f0e8',
      flexDirection: 'column',
      gap: 12
    }}>
      <span style={{ fontSize: 28, color: '#c4922a' }}>☸</span>
      <p style={{
        fontFamily: 'Georgia, serif',
        fontSize: 16,
        color: '#9b9890',
        fontStyle: 'italic'
      }}>
        Loading your library...
      </p>
    </div>
  )

  return (
    <div className={styles.layout}>
      <nav className={styles.nav}>
        <Link href="/" className={styles.navLogo}>Sathya</Link>
        <div className={styles.navRight}>
          <Link href="/ask" className={styles.navLink}>Ask</Link>
          <span className={styles.navUser}>{user?.name}</span>
          <button onClick={logout} className={styles.navLogout}>Sign out</button>
        </div>
      </nav>

      <main className={styles.main}>
        <div className={styles.header}>
          <h1 className={styles.title}>Your library</h1>
          <p className={styles.subtitle}>
            {questions.length === 0
              ? 'Questions you ask will be saved here.'
              : `${questions.length} question${questions.length !== 1 ? 's' : ''} saved`}
          </p>
        </div>

        {questions.length === 0 ? (
          <div className={styles.empty}>
            <span className={styles.emptyGlyph}>◎</span>
            <p className={styles.emptyText}>Your library is empty</p>
            <Link href="/ask" className="btn-primary" style={{ marginTop: 20 }}>
              Ask your first question
            </Link>
          </div>
        ) : (
          <div className={styles.list}>
            {questions.map(q => (
              <div key={q.id} className={styles.item}>
                <div
                  className={styles.itemHeader}
                  onClick={() => setExpanded(expanded === q.id ? null : q.id)}
                >
                  <div className={styles.itemLeft}>
                    <span className={styles.itemDate}>{formatDate(q.created_at)}</span>
                    <p className={styles.itemQuestion}>{q.question}</p>
                  </div>
                  <span className={styles.itemToggle}>{expanded === q.id ? '−' : '+'}</span>
                </div>

                {expanded === q.id && (
                  <div className={styles.itemBody}>
                    <div className={styles.itemAnswer}>
                      {q.answer.split('\n').map((para, i) =>
                        para.trim() ? <p key={i}>{para}</p> : <br key={i} />
                      )}
                    </div>
                    {q.sources?.length > 0 && (
                      <div className={styles.itemSources}>
                        {q.sources.map((s: any, i: number) => (
                          <span key={i} className={styles.itemSource}>
                            {s.reference} — {s.title}
                          </span>
                        ))}
                      </div>
                    )}
                    <button
                      className={styles.deleteBtn}
                      onClick={() => handleDelete(q.id)}
                    >
                      Remove from library
                    </button>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </main>
    </div>
  )
}