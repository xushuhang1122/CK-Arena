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

llm_set = {"temperature": 0.6, "max_tokens": 1024, "top_p": 1.0, "languadge": "en"}


def call_api(llm_info):
    
    #TODO you should add your own function to call api here.
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


