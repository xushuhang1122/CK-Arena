# utils.py

from openai import OpenAI
import random
import itertools
import time
import json
import http.client
from datetime import datetime
import csv
from typing import List, Dict, Optional
import os
import requests
from openai import AzureOpenAI

llm_set = {"temperature": 0.6, "max_tokens": 1024, "top_p": 1.0, "languadge": "en"}

# Fill in your OpenAI API key here, or set the OPENAI_API_KEY environment variable.
# Leave as None to use the environment variable automatically.
OPENAI_API_KEY = None  # e.g. "sk-..."
OPENAI_BASE_URL = None  # Set a custom base URL if using a proxy or compatible API, e.g. "https://api.example.com/v1"


def call_api(llm_info):
    """
    Call the LLM API and return the model's text response.

    Input format (llm_info dict):
        {
            "model":         str,   # Model name, e.g. "gpt-4o", "gpt-3.5-turbo"
            "temperature":   float, # Sampling temperature, e.g. 0.6
            "max_tokens":    int,   # Maximum tokens in the response, e.g. 1024
            "input_messages": list  # List of message dicts in OpenAI chat format:
                                    #   [{"role": "system", "content": "..."},
                                    #    {"role": "user",   "content": "..."},
                                    #    ...]
        }

    Output:
        str  - The raw text content returned by the model.
               If the model wraps its answer in a markdown code block
               (``` or ```json), the wrapper is stripped automatically.

    Example usage:
        llm_info = {
            "model": "gpt-4o",
            "temperature": 0.6,
            "max_tokens": 1024,
            "input_messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user",   "content": "Say hello in JSON format."},
            ]
        }
        response_text = call_api(llm_info)

    If you do not have an OpenAI key, replace the body of this function with
    your own API call and make sure it returns a plain string.
    """
    client = OpenAI(
        api_key=OPENAI_API_KEY or os.environ.get("OPENAI_API_KEY"),
        base_url=OPENAI_BASE_URL,  # ignored when None
    )

    response = client.chat.completions.create(
        model=llm_info["model"],
        messages=llm_info["input_messages"],
        temperature=llm_info.get("temperature", llm_set["temperature"]),
        max_tokens=llm_info.get("max_tokens", llm_set["max_tokens"]),
    )

    ret = response.choices[0].message.content or ""

    # Extract JSON if wrapped in markdown code blocks
    if '```json' in ret:
        # Find the start and end of the JSON content
        json_start = ret.find('```json')
        if json_start != -1:
            json_start = ret.find('\n', json_start) + 1  # Move to the line after ```json
            json_end = ret.find('```', json_start)
            if json_end != -1:
                ret = ret[json_start:json_end].strip()
    elif '```' in ret:
        # Handle case where there's just ``` without json tag
        json_start = ret.find('```') + 3
        json_end = ret.find('```', json_start)
        if json_start > 2 and json_end > json_start:
            ret = ret[json_start:json_end].strip()

    return ret.strip()

