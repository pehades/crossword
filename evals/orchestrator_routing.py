from uuid import uuid4

from langchain_core.messages import HumanMessage, AIMessage

from evals.runner import run
from tests.fakes import FakeQuizAgent
from crossword.common.factories import AgentsFactory


def orchestrator_target():

    orchestrator_with_fake_quiz_agent = AgentsFactory.get_orchestrator_agent(quiz_agent=FakeQuizAgent())

    def target(inputs: dict):

        response = orchestrator_with_fake_quiz_agent.invoke(
            {'messages': HumanMessage(content=inputs['message'])},
            {'configurable': {'thread_id': str(uuid4())}}
        )

        tool_calls = [call['name'] for m in response['messages'] if isinstance(m, AIMessage) for call in m.tool_calls]
        return {'tool_calls': tool_calls, 'messages': response['messages']}
    return target


def check_calls_create_quiz(outputs: dict, reference_outputs: dict):
    return ('create_quiz' in outputs['tool_calls']) == reference_outputs['calls_create_quiz_tool']


evals_dataset = [
    {
        'inputs': {'message': 'create a quiz about Mathematicians'},
        'outputs': {'calls_create_quiz_tool': True}
    },
    {
        'inputs': {'message': 'make a crossword about whiskey drinks'},
        'outputs': {'calls_create_quiz_tool': True}
    },
    {
        'inputs': {'message': 'make a quiz'},
        'outputs': {'calls_create_quiz_tool': False}
    },
    {
        'inputs': {'message': 'make a quiz with questions from abrah katabrah'},
        'outputs': {'calls_create_quiz_tool': False}
    },
    # broad topics are fine, the quiz can cover any of their aspects
    {
        'inputs': {'message': 'a crossword about World War II'},
        'outputs': {'calls_create_quiz_tool': True}
    },
    {
        'inputs': {'message': 'make me a crossword about wine regions'},
        'outputs': {'calls_create_quiz_tool': True}
    },
    {
        'inputs': {'message': 'quiz on football tactics'},
        'outputs': {'calls_create_quiz_tool': True}
    },
    {
        'inputs': {'message': 'create a crossword about Greek mythology'},
        'outputs': {'calls_create_quiz_tool': True}
    },
    # specific topics
    {
        'inputs': {'message': 'a crossword about the Apollo 11 moon landing'},
        'outputs': {'calls_create_quiz_tool': True}
    },
    {
        'inputs': {'message': 'quiz about the albums of Pink Floyd in the 1970s'},
        'outputs': {'calls_create_quiz_tool': True}
    },
    # ambiguous terms made clear by the user
    {
        'inputs': {'message': 'make a crossword about Jaguar, the car brand'},
        'outputs': {'calls_create_quiz_tool': True}
    },
    {
        'inputs': {'message': 'crossword about the Python programming language'},
        'outputs': {'calls_create_quiz_tool': True}
    },
    # ambiguous terms that refer to unrelated subjects
    {
        'inputs': {'message': 'make a crossword about Jaguar'},
        'outputs': {'calls_create_quiz_tool': False}
    },
    {
        'inputs': {'message': 'quiz about Python'},
        'outputs': {'calls_create_quiz_tool': False}
    },
    {
        'inputs': {'message': 'create a crossword about Apple'},
        'outputs': {'calls_create_quiz_tool': False}
    },
    {
        'inputs': {'message': 'a quiz about Phoenix'},
        'outputs': {'calls_create_quiz_tool': False}
    },
    # no topic or missing context
    {
        'inputs': {'message': 'surprise me with a crossword'},
        'outputs': {'calls_create_quiz_tool': False}
    },
    {
        'inputs': {'message': 'make a crossword about the thing we discussed'},
        'outputs': {'calls_create_quiz_tool': False}
    },
    # not a crossword request
    {
        'inputs': {'message': 'what is the capital of France?'},
        'outputs': {'calls_create_quiz_tool': False}
    },
    {
        'inputs': {'message': 'write me a poem about the sea'},
        'outputs': {'calls_create_quiz_tool': False}
    }
]

dataset_name = 'evals-1'
targets = [orchestrator_target()]
evaluators = [check_calls_create_quiz]


if __name__ == '__main__':
    run(dataset_name=dataset_name, examples=evals_dataset, targets=targets, evaluators=evaluators)




