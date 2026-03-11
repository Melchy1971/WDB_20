import type { PropsWithChildren } from 'react'

export function AppLayout({ children }: PropsWithChildren) {
  return (
    <main className="layout">
      <header>
        <h1>Mail Knowledge Platform</h1>
      </header>
      {children}
    </main>
  )
}
