'use client'
import { useState, useRef, useEffect } from 'react'
import { useAuth } from '@/lib/auth-context'
import { useRouter } from 'next/navigation'
import { api } from '@/lib/api'
import Link from 'next/link'
import styles from './ask.module.css'

interface Source {
  title: string
  reference: string
  collection: string
  similarity: number
}

interface Response {
  answer: string
  sources: Source[]
}

const EXAMPLE_QUESTIONS = [
  "How do I stop my mind from dwelling on the past?",
  "What does the Buddha say about anger and resentment?",
  "How should I deal with a difficult person in my life?",
  "What is the nature of suffering and how do we overcome it?",
  "How do I find peace when everything feels uncertain?",
]

export default function AskPage() {
  const { user, loading, logout } = useAuth()
  const router = useRouter()
  const [question, setQuestion] = useState('')
  const [response, setResponse] = useState<Response | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')
  const textareaRef = useRef<HTMLTextAreaElement>(null)
  const responseRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (!loading && !user) router.push('/auth/login')
  }, [user, loading, router])

  useEffect(() => {
    if (response && responseRef.current) {
      responseRef.current.scrollIntoView({ behavior: 'smooth', block: 'start' })
    }
  }, [response])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!question.trim() || isLoading) return
    setError('')
    setResponse(null)
    setIsLoading(true)
    try {
      const data = await api.questions.ask(question.trim())
      setResponse(data)
    } catch (err: any) {
      setError(err.message)
    } finally {
      setIsLoading(false)
    }
  }

  const handleNew = () => {
    setQuestion('')
    setResponse(null)
    setError('')
    textareaRef.current?.focus()
  }

  if (loading) return (
    <div style={{
      minHeight: '100vh',
      background: '#f5f0e8',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center'
    }}>
      <span style={{
        fontSize: 48,
        color: '#c4922a',
        display: 'inline-block',
        animation: 'spin 3s linear infinite',
        lineHeight: 1
      }}>☸</span>
    </div>
  )

  return (
    <div className={styles.layout}>
      <nav className={styles.nav}>
        <a href="/" className={styles.navLogo}>Sathya</a>
        <div className={styles.navRight}>
          <Link href="/library" className={styles.navLink}>Library</Link>
          <span className={styles.navUser}>{user?.name}</span>
          <button onClick={logout} className={styles.navLogout}>Sign out</button>
        </div>
      </nav>

      <main className={styles.main}>
        {!response && !isLoading && (
          <div className={styles.intro}>
            <p className={styles.introEyebrow}>Ask anything</p>
            <h1 className={styles.introTitle}>What is on your mind?</h1>
            <p className={styles.introSub}>
              Bring a question — about your life, your mind, your practice —
              and receive guidance from the original teachings of the Buddha.
            </p>
          </div>
        )}

        <form onSubmit={handleSubmit} className={styles.form}>
          <div className={styles.inputWrap}>
            <textarea
              ref={textareaRef}
              className={styles.textarea}
              value={question}
              onChange={e => setQuestion(e.target.value)}
              placeholder="Ask your question here..."
              rows={3}
              onKeyDown={e => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault()
                  handleSubmit(e)
                }
              }}
            />
            <button
              type="submit"
              className={styles.submitBtn}
              disabled={!question.trim() || isLoading}
            >
              {isLoading ? '...' : '↵'}
            </button>
          </div>
          {error && <p className="error-text">{error}</p>}
        </form>

        {!response && !isLoading && (
          <div>
            <p className={styles.examplesLabel}>Some have asked</p>
            <div className={styles.exampleList}>
              {EXAMPLE_QUESTIONS.map((q, i) => (
                <button
                  key={i}
                  className={styles.exampleBtn}
                  onClick={() => {
                    setQuestion(q)
                    textareaRef.current?.focus()
                  }}
                >
                  {q}
                </button>
              ))}
            </div>
          </div>
        )}

        {isLoading && (
          <div className={styles.loading}>
            <div className={styles.loadingGlyph}>☸</div>
            <p className={styles.loadingText}>Searching the canon</p>
            <div style={{ display: 'flex', gap: 4, justifyContent: 'center', marginTop: 12 }}>
              <span className="loading-dot" />
              <span className="loading-dot" />
              <span className="loading-dot" />
            </div>
          </div>
        )}

        {response && (
          <div ref={responseRef} className={styles.response}>
            <div className={styles.questionEcho}>
              <span className={styles.questionLabel}>Your question</span>
              <p className={styles.questionText}>{question}</p>
            </div>

            <div className={styles.answerBlock}>
              <span className={styles.answerLabel}>From the teachings</span>
              <div className={styles.answerText}>
                {response.answer.split('\n').map((para, i) => (
                  para.trim()
                    ? <p key={i} className={styles.answerPara}>{para}</p>
                    : <br key={i} />
                ))}
              </div>
            </div>

            {response.sources.length > 0 && (
              <div className={styles.sourcesBlock}>
                <span className={styles.sourcesLabel}>Sources consulted</span>
                <div className={styles.sourceList}>
                  {response.sources.map((s, i) => (
                    <div key={i} className={`${styles.source} ${styles.sourceAnimated}`}>
                      <span className={styles.sourceRef}>{s.reference}</span>
                      <span className={styles.sourceTitle}>{s.title}</span>
                      <span className={styles.sourceCollection}>{s.collection}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            <div className={styles.responseActions}>
              <button onClick={handleNew} className="btn-ghost">
                Ask another question
              </button>
              <Link href="/library" className={styles.libraryLink}>
                View your library →
              </Link>
            </div>
          </div>
        )}
      </main>
    </div>
  )
}