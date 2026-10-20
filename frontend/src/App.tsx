import { useMemo, useState } from 'react'
import { AssistantRuntimeProvider, useLocalRuntime } from '@assistant-ui/react'
import { createAdapter } from './adapter'
import CrosswordPanel from './CrosswordPanel'
import Thread from './Thread'
import type { Crossword } from './types'

export default function App() {
  const [crossword, setCrossword] = useState<Crossword | null>(null)
  const adapter = useMemo(() => createAdapter(setCrossword), [])
  const runtime = useLocalRuntime(adapter)

  return (
    <AssistantRuntimeProvider runtime={runtime}>
      <div className="app">
        <header className="app-header">Crossword</header>
        <main className={crossword ? 'layout split' : 'layout'}>
          <section className="chat-pane">
            <Thread />
          </section>
          {crossword && (
            <section className="crossword-pane">
              <button className="close" onClick={() => setCrossword(null)} aria-label="Close crossword">
                ×
              </button>
              <CrosswordPanel crossword={crossword} />
            </section>
          )}
        </main>
      </div>
    </AssistantRuntimeProvider>
  )
}
