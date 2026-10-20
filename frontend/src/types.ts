// mirrors crossword/business_logic/models.py and crossword/api/models.py

export type PlacedWord = {
  number: number
  direction: 'across' | 'down'
  row: number
  col: number
  answer: string
  clue: string
  chunk_id: string
}

export type Crossword = {
  rows: number
  cols: number
  words: PlacedWord[]
  unplaced: { question: string; answer: string; chunk_id: string }[]
}

export type ChatStreamEvent = {
  thread_id: string | null
  message: string
  status: string | null
  quiz: unknown | null
  crossword: Crossword | null
  error: string | null
}
