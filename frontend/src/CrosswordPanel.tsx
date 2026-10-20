import { CrosswordGrid, CrosswordProvider, DirectionClues, type CluesInput } from '@jaredreisinger/react-crossword'
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

export default function CrosswordPanel({ crossword }: { crossword: Crossword }) {
  return (
    <CrosswordProvider
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
