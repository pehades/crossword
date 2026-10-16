
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
    }

]