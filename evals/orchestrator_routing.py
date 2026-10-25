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


def check_single_quiz_call(outputs: dict) -> bool:
    return outputs['tool_calls'].count('create_quiz') <= 1


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
    }
]

dataset_name = 'evals-1'
targets = [orchestrator_target()]
evaluators = [check_calls_create_quiz, check_single_quiz_call]


if __name__ == '__main__':
    run(dataset_name=dataset_name, examples=evals_dataset, targets=targets, evaluators=evaluators)




