"""Naive DeepSeek-R1 client (with shell access) for AIOpsLab.

"DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via Reinforcement Learning" arXiv preprint arXiv:2501.12948 (2025).

Paper: https://arxiv.org/abs/2501.12948
"""


import argparse
import asyncio

import wandb
import time

from aiopslab.orchestrator import Orchestrator
from aiopslab.orchestrator.problems.registry import ProblemRegistry
from clients.utils.llm import DeepSeekR1
from clients.utils.templates import DOCS_SHELL_ONLY


class Agent:
    def __init__(self):
        self.history = []
        self.llm = DeepSeekR1()

    def init_context(self, problem_desc: str, instructions: str, apis: str):
        """Initialize the context for the agent."""

        self.shell_api = self._filter_dict(apis, lambda k, _: "exec_shell" in k)
        self.submit_api = self._filter_dict(apis, lambda k, _: "submit" in k)
        stringify_apis = lambda apis: "\n\n".join(
            [f"{k}\n{v}" for k, v in apis.items()]
        )

        self.system_message = DOCS_SHELL_ONLY.format(
            prob_desc=problem_desc,
            shell_api=stringify_apis(self.shell_api),
            submit_api=stringify_apis(self.submit_api),
        )

        self.task_message = instructions

        self.history.append({"role": "system", "content": self.system_message})
        self.history.append({"role": "user", "content": self.task_message})

    async def get_action(self, input) -> str:
        """Wrapper to interface the agent with OpsBench.

        Args:
            input (str): The input from the orchestrator/environment.

        Returns:
            str: The response from the agent.
        """
        self.history.append({"role": "user", "content": input})
        response = self.llm.run(self.history)
        self.history.append({"role": "assistant", "content": response[0]})
        return response[0]

    def _filter_dict(self, dictionary, filter_func):
        return {k: v for k, v in dictionary.items() if filter_func(k, v)}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="DeepSeek R1 client for AIOpsLab")
    parser.add_argument(
        "--use_wandb",
        action="store_true",
        default=False,
        help="Enable Weights & Biases logging"
    )
    args = parser.parse_args()

    registry = ProblemRegistry()
    pids = list(registry.PROBLEM_REGISTRY.keys())

    if args.use_wandb:
        # Initialize wandb run
        wandb.init(project="AIOpsLab", entity="bita-tech")

    for pid in pids:
        agent = Agent()

        orchestrator = Orchestrator(use_wandb=args.use_wandb)
        orchestrator.register_agent(agent, name="deepseek-r1")
        try:
            problem_desc, instructs, apis = orchestrator.init_problem(pid)
            agent.init_context(problem_desc, instructs, apis)
            asyncio.run(orchestrator.start_problem(max_steps=10))
            print(f"Successfully processed pid {pid}.")

        except Exception as e:
            print(f"Failed to process pid {pid}. Error: {e}")
            time.sleep(60)
            continue

    if args.use_wandb:
        # Finish the wandb run
        wandb.finish()
