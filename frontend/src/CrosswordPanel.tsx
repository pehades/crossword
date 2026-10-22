import { useContext, useRef, useState, type RefObject } from 'react'
import {
  CrosswordContext,
  CrosswordGrid,
  CrosswordProvider,
  DirectionClues,
  type CluesInput,
  type CrosswordProviderImperative,
} from '@jaredreisinger/react-crossword'
import type { Crossword } from './types'

function toCluesInput(crossword: Crossword): CluesInput {
  const data: CluesInput = { across: {}, down: {} }
  for (const word of crossword.words) {
    data[word.direction][String(word.number)] = {
      clue: word.clue,
      answer: word.answer,
      row: word.row,
      col: word.col,
    }
  }
  return data
}

// lives inside the provider, so it can read the selected clue (from cell or clue clicks)
// and its counts reset when a new crossword remounts the provider
function RevealLetterButton({
  crossword,
  providerRef,
}: {
  crossword: Crossword
  providerRef: RefObject<CrosswordProviderImperative | null>
}) {
  const { selectedDirection, selectedNumber } = useContext(CrosswordContext)
  const [revealed, setRevealed] = useState<Record<string, number>>({})

  function revealLetter() {
    const word = crossword.words.find(
      (w) => w.direction === selectedDirection && String(w.number) === selectedNumber,
    )
    if (!word) return
    const key = `${word.direction}-${word.number}`
    // each click reveals the next letter of the selected word
    const k = revealed[key] ?? 0
    if (k >= word.answer.length) return
    const row = word.direction === 'across' ? word.row : word.row + k
    const col = word.direction === 'across' ? word.col + k : word.col
    providerRef.current?.setGuess(row, col, word.answer[k])
    setRevealed({ ...revealed, [key]: k + 1 })
  }

  return (
    <button onClick={revealLetter} disabled={!selectedNumber}>
      Reveal letter
    </button>
  )
}

export default function CrosswordPanel({ crossword }: { crossword: Crossword }) {
  const ref = useRef<CrosswordProviderImperative>(null)

  return (
    <CrosswordProvider
      ref={ref}
      // remount and skip localStorage so a new crossword starts empty
      key={JSON.stringify(crossword.words)}
      useStorage={false}
      data={toCluesInput(crossword)}
      theme={{
        allowNonSquare: true,
        gridBackground: '#e5e7eb',
        cellBackground: '#ffffff',
        cellBorder: '#1f2937',
        textColor: '#111827',
        numberColor: '#6b7280',
        focusBackground: '#fde68a',
        highlightBackground: '#dbeafe',
      }}
    >
      <div className="puzzle-actions">
        <RevealLetterButton crossword={crossword} providerRef={ref} />
      </div>
      <div className="puzzle">
        <div className="puzzle-grid">
          <CrosswordGrid />
        </div>
        <div className="puzzle-clues">
          <DirectionClues direction="across" />
          <DirectionClues direction="down" />
        </div>
      </div>
    </CrosswordProvider>
  )
}
