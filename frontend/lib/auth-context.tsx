'use client'
import { createContext, useContext, useEffect, useState, ReactNode } from 'react'
import { useRouter } from 'next/navigation'

interface User {
  id: string
  name: string
  email: string
}

interface AuthContextType {
  user: User | null
  loading: boolean
  login: (token: string, user: User) => void
  logout: () => void
}

const AuthContext = createContext<AuthContextType>({
  user: null,
  loading: true,
  login: () => {},
  logout: () => {},
})

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)
  const router = useRouter()

  useEffect(() => {
    try {
      const token = localStorage.getItem('sathya_token')
      const userData = localStorage.getItem('sathya_user')
      if (token && userData) {
        setUser(JSON.parse(userData))
      }
    } catch (e) {
      console.error('Auth restore error:', e)
    } finally {
      setLoading(false)
    }
  }, [])

  const login = (token: string, user: User) => {
    localStorage.setItem('sathya_token', token)
    localStorage.setItem('sathya_user', JSON.stringify(user))
    setUser(user)
    router.push('/ask')
  }

  const logout = () => {
    localStorage.removeItem('sathya_token')
    localStorage.removeItem('sathya_user')
    setUser(null)
    router.push('/')
  }

  return (
    <AuthContext.Provider value={{ user, loading, login, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => useContext(AuthContext)