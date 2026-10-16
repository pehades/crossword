from typing import Callable

from langsmith import Client

from crossword.common.factories import ConfigFactory


def sync_dataset(client: Client, dataset_name: str, examples: list[dict]):

    if not client.has_dataset(dataset_name=dataset_name):
        client.create_dataset(dataset_name)

    existing = [
        example.inputs for example in client.list_examples(dataset_name=dataset_name)
    ]
    new = [
        example for example in examples if example['inputs'] not in existing
    ]

    if new:
        client.create_examples(
            dataset_name=dataset_name,
            inputs=[example['inputs'] for example in new],
            outputs=[example['outputs'] for example in new]
        )


def run(dataset_name: str, examples: list[dict], targets: list[Callable], evaluators: list[Callable]):

    # load env variables and especially langsmith variables
    env_config = ConfigFactory.get_env_config()
    client = Client()

    sync_dataset(client, dataset_name, examples)

    for target in targets:
        results = client.evaluate(
            target,
            data=dataset_name,
            evaluators=evaluators,
            experiment_prefix=dataset_name,
        )

        df = results.to_pandas()
        feedback = [c for c in df.columns if c.startswith('feedback.')]

        print(f'\n{results.experiment_name}')
        print(df[['inputs.message', 'outputs.tool_calls', *feedback, 'error']].to_string())
        print('\nmean scores:')
        print(df[feedback].mean().to_string())