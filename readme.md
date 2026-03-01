# CK-Arena

[![Paper](https://img.shields.io/badge/Paper-arXiv%3A2505.17512-b31b1b)](https://arxiv.org/abs/2505.17512)
[![Homepage](https://img.shields.io/badge/Homepage-ck--arena.site-blue)](https://ck-arena.site)
[![HuggingFace](https://img.shields.io/badge/HuggingFace-Dataset-yellow)](https://huggingface.co/datasets/Xushuhaha/CK-Arena)

![CK-Arena Overview](docs/figure/overview.png)

## Introduction

CK-Arena is a multi-agent benchmark that evaluates whether large language models truly master concept knowledge. The benchmark uses a language-based social deduction game ("Undercover") where LLM players describe assigned concepts, and LLM judges score the statements. By comparing similar word pairs and tracking model performance over many games, CK-Arena produces a reliable ELO-based leaderboard of concept-level knowledge.

## Table of Contents

- [Dataset](#dataset)
- [Project Structure](#project-structure)
- [Usage](#usage)
- [Leaderboard](#leaderboard)
- [Citation](#citation)

## Dataset

### Overview

The dataset is hosted on HuggingFace: [Xushuhaha/CK-Arena](https://huggingface.co/datasets/Xushuhaha/CK-Arena).

It consists of two parts: word pair lists used in gameplay and fine-tuning data for the judge model.

### Word Pair Lists

Word pairs are stored in `data/word_list_1/en_628/` and organised by part of speech:

```
data/word_list_1/en_628/
├── adjective_100.json        # 100 adjective pairs
├── adverb_109.json           # 109 adverb pairs
├── verb_100.json             # 100 verb pairs
└── en_substaintive_noun_220/ # 220 substantive noun pairs split by category
    ├── Animals_16.json
    ├── Food_33_.json
    ├── Tools_19.json
    └── ...
```

Each JSON file is a list of two-element arrays, one pair per entry:

```json
[
  ["happy", "joyful"],
  ["angry", "furious"],
  ["sad", "melancholic"]
]
```

### Judge Fine-tuning Data Format

`data/train.jsonl` and `data/test.jsonl` contain training and test data for fine-tuning the judge model. Each line is a JSON object with a `messages` field following the chat format:

```json
{
  "messages": [
    {
      "role": "system",
      "content": "You will receive a word and a descriptive sentence, please judge whether this sentence is reasonable for describing the word."
    },
    {
      "role": "user",
      "content": "\nWhat needs to be judged:\nWord: bee\nSentence: An organism that lives in complex social structures with a hierarchical organization\n"
    },
    {
      "role": "assistant",
      "content": "1"
    }
  ]
}
```

The assistant outputs `"1"` for a valid statement and `"0"` for an invalid one.

## Project Structure

```
CK-Arena/
├── undercover/
│   ├── agents/
│   │   ├── player_agent.py    # LLM-based player
│   │   ├── judge_agent.py     # LLM-based judge
│   │   ├── prompts.py         # Prompt templates for all supported languages
│   │   └── utils.py           # API call utilities
│   ├── game.py                # Core game logic and state management
│   ├── game_automated.py      # Automated mode using SFT and embedding models
│   ├── judge.py               # Abstract base class for judges
│   └── player.py              # Abstract base class for players
├── undercover_audience/
│   ├── agents/
│   │   ├── audience_agent.py  # LLM-based audience
│   │   ├── player_agent.py
│   │   ├── judge_agent.py
│   │   ├── prompts.py
│   │   └── utils.py
│   ├── game.py
│   ├── audience.py
│   ├── judge.py
│   └── player.py
├── data/
│   ├── word_list_1/en_628/    # Word pair files by POS and category
│   ├── train.jsonl            # Judge fine-tuning training split
│   └── test.jsonl             # Judge fine-tuning test split
├── docs/figure/               # Figures used in this README
├── logs/                      # Game records organised by language
├── main.py                    # Entry point for a single game
├── main_batch.py              # Batch game runner
└── rating.py                  # ELO rating calculator
```

## Usage

### Installation

```bash
pip install openai requests
```

### Single Game

```bash
python main.py
```

Adjust the language, round settings, participating models, and judge by modifying `game_settings` and the player/judge initialisation in `main.py`.

### Batch Games

```bash
python main_batch.py
```

Configure the number of games, parallel processing options, and word pair lists for efficient repeated experiments.

### Rating Calculation

```bash
python rating.py
```

Processes game logs in `logs/` to compute ELO ratings and generate performance reports for all participating models.

## Leaderboard

![Model Leaderboard](docs/figure/leaderboard.png)

*Last updated: March 2026*

## Citation

If you find this work useful, please cite:

```bibtex
@article{xu2025CKarena,
  title={Is Your LLM Really Mastering the Concept? A Multi-Agent Benchmark},
  author={Shuhang Xu and Weijian Deng and Yixuan Zhou and Fangwei Zhong},
  journal={arXiv preprint arXiv:2505.17512},
  year={2026}
}
```
