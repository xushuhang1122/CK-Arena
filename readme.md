# Undercover Game

A language-based multiplayer game where players try to identify the "undercover" among them based on their descriptions of a given concept.

## Overview

This project implements a language model-based version of the popular social deduction game "Undercover". The game assigns different concepts to players who then make statements about their assigned concept. The goal is to identify the player(s) with a different concept (the "undercover") through voting rounds.

## Project Structure

```
├── undecover/
│   ├── agents                 
│   │   ├── player_agent.py    # LLM-based player implementation
│   │   ├── judge_agent.py     # LLM-based judge implementation
│   │   ├── prompts.py         # Contains prompt templates for different languages
│   │   └── utils.py           # Utility functions for API calls
│   ├── game.py                # Core game logic and state management
│   ├── judge.py               # Abstract base class for judges
│   └── player.py              # Abstract base class for players
├── data/
│   └── word_list_1/           # Contains word pairs for the game
│       ├── cn_755/
│       └── ...
├── logs/
│   └── en/                    # Game records in English
├── undercover_audience/
│   ├── agents               
│   │   ├── audience_agent.py  # LLM-based audience implementation
│   │   ├── player_agent.py    # LLM-based player implementation
│   │   ├── judge_agent.py     # LLM-based judge implementation
│   │   ├── prompts.py         # Contains prompt templates for different languages
│   │   └── utils.py           # Utility functions for API calls
│   ├── game.py                # Core game logic and state management
│   ├── audience.py            # Abstract base class for audiences
│   ├── judge.py               # Abstract base class for judges
│   └── player.py              # Abstract base class for players
└── main.py                    # Entry point for running games
```

## Key Components

### Core Game Classes

- **UndercoverGame** (`undercover/game.py`): Manages the game state, coordinates player interactions, and handles the game flow including statement and voting rounds.
- **Player** (`undercover/player.py`): Abstract base class defining the interface for player implementations.
- **Judge** (`undercover/judge.py`): Abstract base class defining the interface for judge implementations.

### Agent Implementations

- **LLMPlayer** (`agents/player_agent.py`): Language model-based player implementation that generates statements and makes voting decisions.
- **LLMJudge** (`agents/judge_agent.py`): Language model-based judge that evaluates player statements for novelty, relevance, and reasonableness.

### Multi-language Support

The game supports multiple languages through language-specific prompt templates:
- English (en) (Experimental used)
- Chinese (zh)
- French (fr)
- Spanish (es)
- Italian (it)
- Portuguese (pt)
- German (de)
- Russian (ru)
- Arabic (ar)
- Japanese (ja)

## How to Run

```bash
pip install openai
pip install requests
python main.py
```
You can adjust the language, round settings, participating players, and referees of the game by modifying the class **game_settings** and player/judge initialization information in `main.py`.

## Game Flow

1. **Initialization**:
   - Players and judges are created
   - Players are assigned roles (civilian or undercover)
   - Each role gets an assigned concept

2. **Statement Rounds**:
   - Each player makes statements about their assigned concept
   - Judges evaluate statements for quality

3. **Voting Rounds**:
   - After a specified number of statement rounds, players vote
   - The player with the most votes is eliminated
   - The game continues until a winning condition is met

4. **Winning Conditions**:
   - Civilians win if all undercovers are eliminated
   - Undercovers win if the ratio of undercovers to civilians becomes equal

## Configuration

Game settings can be customized in `main.py`:
- Topic category
- Concept pairs
- Number of civilians and undercovers
- Maximum statement rounds
- Number of statements before voting
- Language setting

## Logs and Records

Game records are stored in the `logs/` directory, organized by language and topic category. Each game record contains:
- Game ID and timestamp
- Player information and roles
- All statements and voting results
- Game summary and analysis

## Development

To extend the game with new player or judge implementations, extend the base classes in `undercover/` and implement the required methods.

To add support for a new language, create new prompt template files in `agents/prompts/` following the existing pattern.
