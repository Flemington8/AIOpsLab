# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

"""An common abstraction for a cached LLM inference setup. Currently supports OpenAI's gpt-4-turbo and DeepSeek-R1 models."""

import os
from dotenv import load_dotenv
from openai import OpenAI
from pathlib import Path
import json

# Load environment variables from the .env file
load_dotenv()

CACHE_DIR = Path("./cache_dir")
CACHE_PATH = CACHE_DIR / "cache.json"


class Cache:
    """A simple cache implementation to store the results of the LLM inference."""

    def __init__(self) -> None:
        if os.path.exists(CACHE_PATH):
            with open(CACHE_PATH) as f:
                self.cache_dict = json.load(f)
        else:
            os.makedirs(CACHE_DIR, exist_ok=True)
            self.cache_dict = {}

    @staticmethod
    def process_payload(payload):
        if isinstance(payload, (list, dict)):
            return json.dumps(payload)
        return payload

    def get_from_cache(self, payload):
        payload_cache = self.process_payload(payload)
        if payload_cache in self.cache_dict:
            return self.cache_dict[payload_cache]
        return None

    def add_to_cache(self, payload, output):
        payload_cache = self.process_payload(payload)
        self.cache_dict[payload_cache] = output

    def save_cache(self):
        with open(CACHE_PATH, "w") as f:
            json.dump(self.cache_dict, f, indent=4)


class GPT4Turbo:
    """Abstraction for OpenAI's GPT-4 Turbo model."""

    def __init__(self):
        self.cache = Cache()

    def inference(self, payload: list[dict[str, str]]) -> list[str]:
        if self.cache is not None:
            cache_result = self.cache.get_from_cache(payload)
            if cache_result is not None:
                return cache_result

        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        try:
            response = client.chat.completions.create(
                messages=payload,  # type: ignore
                model="gpt-4o-mini",
                max_tokens=1024,
                temperature=0.5,
                top_p=0.95,
                frequency_penalty=0.0,
                presence_penalty=0.0,
                n=1,
                timeout=60,
                stop=[],
            )
        except Exception as e:
            print(f"Exception: {repr(e)}")
            raise e

        return [c.message.content for c in response.choices]  # type: ignore

    def run(self, payload: list[dict[str, str]]) -> list[str]:
        response = self.inference(payload)
        if self.cache is not None:
            self.cache.add_to_cache(payload, response)
            self.cache.save_cache()
        return response


class DeepSeekR1:
    """Abstraction for DeepSeek-R1 model."""

    def __init__(self):
        self.cache = Cache()

    def inference(self, payload: list[dict[str, str]]) -> list[str]:
        if self.cache is not None:
            cache_result = self.cache.get_from_cache(payload)
            if cache_result is not None:
                return cache_result

        client = OpenAI(api_key=os.getenv("DEEPSEEK_API_KEY"), base_url="https://api.deepseek.com")
        try:
            payload = self.ensure_interleaved_messages(payload)
            response = client.chat.completions.create(
                messages=payload,  # type: ignore
                model="deepseek-reasoner",
                max_tokens=1024,
                n=1,
                timeout=60,
                stop=[],
            )
        except Exception as e:
            print(f"Exception: {repr(e)}")
            raise e

        return [c.message.content for c in response.choices]  # type: ignore

    def run(self, payload: list[dict[str, str]]) -> list[str]:
        response = self.inference(payload)
        if self.cache is not None:
            self.cache.add_to_cache(payload, response)
            self.cache.save_cache()
        return response
    
    def ensure_interleaved_messages(self, payload: list[dict[str, str]]) -> list[dict[str, str]]:
        """
        deepseek-reasoner does not support successive user or assistant messages.
        Ensures that the messages list is properly interleaved with user/assistant roles.
        If two consecutive user messages are detected, merge or restructure them.
        """
        interleaved_messages = []
        last_role = None

        for message in payload:
            if last_role == message["role"]:
                # If two consecutive user messages appear, merge them
                if message["role"] == "user":
                    interleaved_messages[-1]["content"] += f"\n\n{message['content']}"
                else:
                    interleaved_messages.append({"role": "assistant", "content": "..."})  # Placeholder
            else:
                interleaved_messages.append(message)

            last_role = message["role"]

        return interleaved_messages
