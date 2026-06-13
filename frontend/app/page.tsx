'use client'
import Link from 'next/link'
import { useAuth } from '@/lib/auth-context'
import { useEffect, useRef, useState } from 'react'
import styles from './page.module.css'

function useInView(threshold = 0.15) {
  const ref = useRef<HTMLDivElement>(null)
  const [inView, setInView] = useState(false)
  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => { setInView(entry.isIntersecting) },
      { threshold }
    )
    if (ref.current) observer.observe(ref.current)
    return () => observer.disconnect()
  }, [threshold])
  return { ref, inView }
}

export default function Home() {
  const { user, loading, logout } = useAuth()
  const sourcesSection = useInView()
  const featuresSection = useInView()
  const ctaSection = useInView()

  return (
    <main className={styles.main}>

      {/* Hero */}
      <section className={styles.hero}>
        <div className={styles.heroImage} />
        <div className={styles.heroOverlay} />
        <div className={styles.heroFade} />

        {/* Nav */}
        <div className={styles.heroNav}>
          <span className={styles.heroNavLogo}>Sathya</span>
          <div className={styles.heroNavRight}>
            {loading ? null : user ? (
              <>
                <Link href="/ask" className={styles.heroNavLink}>Ask</Link>
                <Link href="/library" className={styles.heroNavLink}>Library</Link>
                <button
                  onClick={logout}
                  className={styles.heroNavLink}
                  style={{ background: 'none', border: 'none', cursor: 'pointer' }}
                >
                  Sign out
                </button>
              </>
            ) : (
              <>
                <Link href="/auth/login" className={styles.heroNavLink}>Sign in</Link>
                <Link href="/auth/register" className={styles.heroNavLinkBtn}>Begin</Link>
              </>
            )}
          </div>
        </div>

        <div className={styles.heroContent}>
          <p className={`${styles.eyebrow} animate-fade-up`}>
            The Pali Canon · Theravāda Teachings · 500 BCE
          </p>
          <h1 className={`${styles.title} animate-fade-up-delay-1`}>Sathya</h1>
          <p className={`${styles.meaning} animate-fade-up-delay-2`}>
            <em>sathya</em> — Sanskrit for truth, reality, that which is
          </p>
          <p className={`${styles.subtitle} animate-fade-up-delay-3`}>
            Traverse thousands of pages of ancient Buddhist scripture —
            the direct recorded words of the Buddha, preserved for 2,500 years —
            with a single question.
          </p>

          {loading ? (
            <div className={`${styles.actions} animate-fade-up-delay-4`}>
              <span style={{ color: 'rgba(245,240,232,0.3)', fontSize: 13 }}>·</span>
            </div>
          ) : user ? (
            <div className={`${styles.actions} animate-fade-up-delay-4`}>
              <Link href="/ask" className={styles.btnLight}>Continue asking</Link>
            </div>
          ) : (
            <div className={`${styles.actions} animate-fade-up-delay-4`}>
              <Link href="/auth/register" className={styles.btnLight}>Begin</Link>
              <Link href="/auth/login" className={styles.btnGhost}>Sign in</Link>
            </div>
          )}

          <div className={`${styles.heroMeta} animate-fade-up-delay-5`}>
            <span>88 suttas indexed</span>
            <span className={styles.heroDot}>·</span>
            <span>Bhikkhu Sujato translations</span>
            <span className={styles.heroDot}>·</span>
            <span>Semantic vector search</span>
          </div>
        </div>
      </section>

      {/* Ornamental divider */}
      <div className={styles.ornaDivider}>
        <span className={styles.ornaLine} />
        <span className={styles.ornaGlyph}>❧</span>
        <span className={styles.ornaLine} />
      </div>

      {/* Sources */}
      <section
        ref={sourcesSection.ref}
        className={`${styles.sources} ${sourcesSection.inView ? styles.sectionVisible : ''}`}
      >
        <div className={styles.sectionHeader}>
          <p className={styles.sectionEyebrow}>The knowledge base</p>
          <h2 className={styles.sectionTitle}>Where the wisdom comes from</h2>
          <p className={styles.sectionSub}>
            Every response is grounded in authenticated translations of original
            Buddhist scripture — not paraphrased, not invented, always cited.
          </p>
        </div>

        <div className={styles.sourceCards}>
          <div className={styles.sourceCard}>
            <div className={styles.sourceCardAccent} />
            <span className={styles.sourceCardGlyph}>☸</span>
            <h3 className={styles.sourceCardTitle}>The Pali Canon</h3>
            <p className={styles.sourceCardText}>
              The oldest surviving complete collection of Buddhist scriptures,
              preserved in Pali — the ancient language closest to what the Buddha
              actually spoke. Compiled immediately after the Buddha's passing by
              councils of senior monks. At roughly 40 volumes, it is three times
              the length of the Bible.
            </p>
          </div>
          <div className={styles.sourceCard}>
            <div className={styles.sourceCardAccent} />
            <span className={styles.sourceCardGlyph}>◎</span>
            <h3 className={styles.sourceCardTitle}>Five Major Nikāyas</h3>
            <p className={styles.sourceCardText}>
              Sathya draws from the Dhammapada, the Majjhima Nikāya,
              the Samyutta Nikāya, the Anguttara Nikāya, and the Sutta Nipāta —
              covering meditation, daily life, dependent origination, ethics,
              and some of the oldest recorded words of the Buddha.
            </p>
          </div>
          <div className={styles.sourceCard}>
            <div className={styles.sourceCardAccent} />
            <span className={styles.sourceCardGlyph}>✦</span>
            <h3 className={styles.sourceCardTitle}>Bhikkhu Sujato</h3>
            <p className={styles.sourceCardText}>
              All translations are by Bhikkhu Sujato — an Australian-born
              Buddhist monk and one of the most respected Pali scholars alive.
              His modern English translations are considered the gold standard
              for accuracy and fidelity to the original meaning, published freely
              through SuttaCentral under Creative Commons.
            </p>
          </div>
        </div>
      </section>

      {/* Pull quote */}
      <div className={styles.pullQuote}>
        <span className={styles.pullQuoteMark}>"</span>
        <p className={styles.pullQuoteText}>
          Just as the great ocean has one taste — the taste of salt —
          so this teaching has one taste: the taste of liberation.
        </p>
        <p className={styles.pullQuoteSource}>Udāna 5.5</p>
      </div>

      {/* Ornamental divider */}
      <div className={styles.ornaDivider}>
        <span className={styles.ornaLine} />
        <span className={styles.ornaGlyph}>❧</span>
        <span className={styles.ornaLine} />
      </div>

      {/* How it works */}
      <section
        ref={featuresSection.ref}
        className={`${styles.features} ${featuresSection.inView ? styles.sectionVisible : ''}`}
      >
        <div className={styles.sectionHeader}>
          <p className={styles.sectionEyebrow}>How it works</p>
          <h2 className={styles.sectionTitle}>Ancient wisdom, modern retrieval</h2>
        </div>

        <div className={styles.featureGrid}>
          <div className={styles.featureItem}>
            <span className={styles.featureNum}>01</span>
            <h3 className={styles.featureName}>You ask anything</h3>
            <p className={styles.featureDesc}>
              Type any question in plain language — about anxiety, grief,
              relationships, purpose, or the nature of mind. No keywords needed.
            </p>
          </div>
          <div className={styles.featureItem}>
            <span className={styles.featureNum}>02</span>
            <h3 className={styles.featureName}>Semantic search</h3>
            <p className={styles.featureDesc}>
              Your question is converted into a mathematical vector and matched
              against every indexed sutta by meaning — not keywords. The most
              relevant teachings surface in milliseconds.
            </p>
          </div>
          <div className={styles.featureItem}>
            <span className={styles.featureNum}>03</span>
            <h3 className={styles.featureName}>Grounded response</h3>
            <p className={styles.featureDesc}>
              An AI synthesizes the retrieved teachings into a clear, compassionate
              response — citing the exact sutta, collection, and verse. Nothing invented.
            </p>
          </div>
          <div className={styles.featureItem}>
            <span className={styles.featureNum}>04</span>
            <h3 className={styles.featureName}>Your library</h3>
            <p className={styles.featureDesc}>
              Every question and its teachings are saved to your personal library —
              a growing record of the wisdom most relevant to your life.
            </p>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section
        ref={ctaSection.ref}
        className={`${styles.cta} ${ctaSection.inView ? styles.sectionVisible : ''}`}
      >
        <div className={styles.ctaInner}>
          <h2 className={styles.ctaTitle}>Begin your inquiry</h2>
          <p className={styles.ctaSub}>
            2,500 years of wisdom. One question at a time.
          </p>
          <div className={styles.ctaActions}>
            {loading ? null : user ? (
              <Link href="/ask" className={styles.btnDark}>Continue asking</Link>
            ) : (
              <>
                <Link href="/auth/register" className={styles.btnDark}>Create account</Link>
                <Link href="/auth/login" className={styles.btnGhostDark}>Sign in</Link>
              </>
            )}
          </div>
        </div>
      </section>

      <footer className={styles.footer}>
        <div className={styles.footerInner}>
          <span className={styles.footerLogo}>Sathya</span>
          <p className={styles.footerText}>
            Teachings from the Pali Canon · Translations by Bhikkhu Sujato · SuttaCentral
          </p>
        </div>
      </footer>

    </main>
  )
}