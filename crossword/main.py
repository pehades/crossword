from langchain_core.messages import HumanMessage

from crossword.common.factories import AgentsFactory

user_query = ''


def main() -> None:

    agent = AgentsFactory.get_quiz_agent()
    config = {'configurable': {'thread_id': 1}}

    result = agent.invoke(
        {'messages': [HumanMessage(content=user_query)]},
        config=config
    )

    for message in result['messages']:
        message.pretty_print()

    quiz = result['structured_response']
    for i, item in enumerate(quiz.items, start=1):
        print(f'{i}. {item.question} -> {item.answer}')


if __name__ == '__main__':
    main()
