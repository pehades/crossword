from crossword.business_logic.models import Quiz, QuestionAnswer

sample_quiz = Quiz(
    items=[
        QuestionAnswer(question='The author of principia mathematica', answer='Isaac Newton', chunk_id='wikipedia:123'),
        QuestionAnswer(question='Polish mathematician, {x} spaces', answer='Banach', chunk_id='wikipedia:123'),
        QuestionAnswer(question='German mathematician, {x} spaces', answer='Hilbert', chunk_id='wikipedia:123')
    ]
)


class FakeQuizAgent:

    def __init__(self, quiz: Quiz = sample_quiz):
        self.quiz = quiz
        self.calls = []

    def invoke(self, inputs: dict) -> dict:
        self.calls.append(inputs)
        return {'structured_response': self.quiz}
