from crossword.common.factories import AgentsFactory

USER_QUERY = 'Make a crossword about Panathinaikos'


def main() -> None:
    agent = AgentsFactory.get_quiz_agent()

    result = agent.invoke({'messages': [{'role': 'user', 'content': USER_QUERY}]})

    for message in result['messages']:
        message.pretty_print()

    quiz = result['structured_response']
    for i, item in enumerate(quiz.items, start=1):
        print(f'{i}. {item.question} -> {item.answer}')


if __name__ == '__main__':
    main()
