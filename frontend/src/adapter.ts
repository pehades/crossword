import type { ChatModelAdapter } from '@assistant-ui/react'
import { fetchEventSource } from '@microsoft/fetch-event-source'
import type { ChatStreamEvent, Crossword } from './types'

const API_URL = 'http://localhost:8000/chat'

export function createAdapter(onCrossword: (crossword: Crossword) => void): ChatModelAdapter {
  let threadId: string | null = null

  return {
    async *run({ messages, abortSignal }) {
      const last = messages[messages.length - 1]
      const message = last.content.map((part) => (part.type === 'text' ? part.text : '')).join('')

      // fetchEventSource uses callbacks, so we push events into a queue and the generator pulls from it
      const queue: ChatStreamEvent[] = []
      let done = false
      let failure: unknown = null
      let wake: () => void = () => {}

      fetchEventSource(API_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message, thread_id: threadId }),
        signal: abortSignal,
        openWhenHidden: true,
        onmessage(ev) {
          if (!ev.data) return
          queue.push(JSON.parse(ev.data))
          wake()
        },
        onclose() {
          done = true
          wake()
        },
        onerror(err) {
          failure = err
          done = true
          wake()
          throw err // stop fetchEventSource from retrying
        },
      }).catch(() => {})

      let text = ''
      let status = 'Thinking...'
      // show the status until the first real token arrives
      yield { content: [{ type: 'text', text: `_${status}_` }] }
      while (true) {
        while (queue.length) {
          const event = queue.shift()!
          if (event.thread_id) threadId = event.thread_id
          if (event.crossword) onCrossword(event.crossword)
          if (event.error) throw new Error(event.error)
          if (event.status) status = event.status
          if (event.message) text += event.message
          yield { content: [{ type: 'text', text: text || `_${status}_` }] }
        }
        if (failure) throw failure
        if (done) return
        await new Promise<void>((resolve) => (wake = resolve))
      }
    },
  }
}
