import { ComposerPrimitive, MessagePrimitive, ThreadPrimitive } from '@assistant-ui/react'
import { MarkdownTextPrimitive } from '@assistant-ui/react-markdown'

function MarkdownText() {
  return <MarkdownTextPrimitive className="markdown" />
}

function UserMessage() {
  return (
    <MessagePrimitive.Root className="message user">
      <MessagePrimitive.Parts />
    </MessagePrimitive.Root>
  )
}

function AssistantMessage() {
  return (
    <MessagePrimitive.Root className="message assistant">
      <MessagePrimitive.Parts components={{ Text: MarkdownText }} />
      <MessagePrimitive.Error>
        <div className="error">Something went wrong.</div>
      </MessagePrimitive.Error>
    </MessagePrimitive.Root>
  )
}

export default function Thread() {
  return (
    <ThreadPrimitive.Root className="thread">
      <ThreadPrimitive.Viewport className="viewport">
        <ThreadPrimitive.Empty>
          <div className="empty">
            <h2>What should your crossword be about?</h2>
            <p>Try "make me a crossword about the Roman Empire".</p>
          </div>
        </ThreadPrimitive.Empty>
        <ThreadPrimitive.Messages components={{ UserMessage, AssistantMessage }} />
      </ThreadPrimitive.Viewport>
      <ComposerPrimitive.Root className="composer">
        <ComposerPrimitive.Input className="composer-input" placeholder="Write a message..." rows={1} />
        <ComposerPrimitive.Send className="composer-send">Send</ComposerPrimitive.Send>
      </ComposerPrimitive.Root>
    </ThreadPrimitive.Root>
  )
}
