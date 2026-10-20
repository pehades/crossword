from crossword.business_logic.models import Crossword, PlacedWord, Quiz


class CrossWordBuilder:
    """
    The classic greedy crossword layout:
    1. Sort the answers from longest to shortest.
    2. Place the first answer across.
    3. For every next answer, look for a letter it shares with an already placed word,
       and try to place it crossing that word in the other direction. Use the first spot that fits.
    4. Answers that cross nothing go to unplaced.
    """

    def build(self, quiz: Quiz) -> Crossword:
        grid: dict[tuple[int, int], str] = {}  # (row, col) -> letter, rows and cols may go negative
        placed, unplaced = [], []

        items = sorted(quiz.items, key=lambda item: len(self.normalize(item.answer)), reverse=True)
        for item in items:
            answer = self.normalize(item.answer)
            spot = (0, 0, 'across') if not placed else self.find_spot(grid, placed, answer)
            if spot is None:
                unplaced.append(item)
                continue

            row, col, direction = spot
            for k, ch in enumerate(answer):
                grid[self.cell(row, col, direction, k)] = ch
            placed.append((item, answer, row, col, direction))

        return self.to_crossword(grid, placed, unplaced)

    @staticmethod
    def normalize(answer: str) -> str:
        return ''.join(ch for ch in answer.upper() if ch.isalpha())

    @staticmethod
    def cell(row: int, col: int, direction: str, k: int) -> tuple[int, int]:
        """The cell of the k-th letter of a word that starts at (row, col)."""
        return (row, col + k) if direction == 'across' else (row + k, col)

    def find_spot(self, grid: dict, placed: list, answer: str) -> tuple[int, int, str] | None:
        for _, word, row, col, direction in placed:
            new_direction = 'down' if direction == 'across' else 'across'
            for j, placed_ch in enumerate(word):
                for i, ch in enumerate(answer):
                    if ch != placed_ch:
                        continue
                    # Shift the start so that letter i of the answer lands on letter j of the placed word
                    cross_row, cross_col = self.cell(row, col, direction, j)
                    if new_direction == 'down':
                        start = (cross_row - i, cross_col)
                    else:
                        start = (cross_row, cross_col - i)
                    if self.fits(grid, answer, *start, new_direction):
                        return *start, new_direction
        return None

    def fits(self, grid: dict, answer: str, row: int, col: int, direction: str) -> bool:
        # The cells right before and after the word must be empty, otherwise it merges with another word
        if self.cell(row, col, direction, -1) in grid or self.cell(row, col, direction, len(answer)) in grid:
            return False

        for k, ch in enumerate(answer):
            r, c = self.cell(row, col, direction, k)
            if (r, c) in grid:
                if grid[(r, c)] != ch:
                    return False
            else:
                # A new letter must not touch other letters on its sides, otherwise it forms nonsense words
                sides = [(r - 1, c), (r + 1, c)] if direction == 'across' else [(r, c - 1), (r, c + 1)]
                if any(side in grid for side in sides):
                    return False
        return True

    @staticmethod
    def to_crossword(grid: dict, placed: list, unplaced: list) -> Crossword:
        if not placed:
            return Crossword(rows=0, cols=0, words=[], unplaced=unplaced)

        # Shift everything so that the top left cell is (0, 0)
        min_row = min(r for r, _ in grid)
        min_col = min(c for _, c in grid)
        rows = max(r for r, _ in grid) - min_row + 1
        cols = max(c for _, c in grid) - min_col + 1

        # Numbers go in reading order; across and down starting in the same cell share a number
        starts = sorted({(row, col) for _, _, row, col, _ in placed})
        numbers = {start: number for number, start in enumerate(starts, start=1)}

        words = [
            PlacedWord(
                number=numbers[(row, col)],
                direction=direction,
                row=row - min_row,
                col=col - min_col,
                answer=answer,
                clue=item.question,
                chunk_id=item.chunk_id,
            )
            for item, answer, row, col, direction in placed
        ]
        return Crossword(rows=rows, cols=cols, words=words, unplaced=unplaced)
