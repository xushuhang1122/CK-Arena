import os
import json
import requests
import numpy as np
import time
from typing import List, Dict, Any

class EmbeddingGenerator:
    """Base class for embedding generators."""
    
    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of texts."""
        raise NotImplementedError("Subclasses must implement generate_embeddings")

class OpenAIEmbedding(EmbeddingGenerator):
    """Generate embeddings using OpenAI's API."""
    
    def __init__(self, api_key: str, model: str = "text-embedding-3-small"):
        self.api_key = api_key
        self.model = model
        self.base_url = "https://api.openai.com/v1/embeddings"
    
    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings using OpenAI's API."""
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        all_embeddings = []
        batch_size = 100  # To prevent API limits
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            
            request_data = {
                "input": batch,
                "model": self.model
            }
            
            response = requests.post(
                self.base_url,
                headers=headers,
                json=request_data
            )
            
            if response.status_code != 200:
                raise Exception(f"API Error: {response.text}")
            
            result = response.json()
            batch_embeddings = [item["embedding"] for item in result["data"]]
            all_embeddings.extend(batch_embeddings)
            
            # Respect rate limits
            if i + batch_size < len(texts):
                time.sleep(0.5)
        
        return all_embeddings

class AnthropicEmbedding(EmbeddingGenerator):
    """Generate embeddings using Anthropic's API."""
    
    def __init__(self, api_key: str, model: str = "claude-3-sonnet-20240229"):
        self.api_key = api_key
        self.model = model
        self.base_url = "https://api.anthropic.com/v1/embeddings"
    
    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings using Anthropic's API."""
        headers = {
            "Content-Type": "application/json",
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01"
        }
        
        all_embeddings = []
        batch_size = 50  # To prevent API limits
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            
            for text in batch:
                request_data = {
                    "model": self.model,
                    "input": text
                }
                
                response = requests.post(
                    self.base_url,
                    headers=headers,
                    json=request_data
                )
                
                if response.status_code != 200:
                    raise Exception(f"API Error: {response.text}")
                
                result = response.json()
                all_embeddings.append(result["embedding"])
                
                # Respect rate limits
                time.sleep(0.2)
        
        return all_embeddings

class DummyEmbedding(EmbeddingGenerator):
    """Generate random embeddings for testing."""
    
    def __init__(self, dimensions: int = 384):
        self.dimensions = dimensions
    
    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate random embeddings."""
        return [list(np.random.rand(self.dimensions).astype(float)) for _ in texts]

def process_json_files(directory_path: str) -> List[Dict[str, Any]]:
    """Process all JSON files in the directory and extract statements with metadata."""
    all_statements = []
    
    # List all JSON files in the directory
    json_files = [f for f in os.listdir(directory_path) if f.endswith('.json')]
    
    for file_name in json_files:
        file_path = os.path.join(directory_path, file_name)
        
        with open(file_path, 'r') as file:
            data = json.load(file)
        
        # Extract game record
        game_record = data.get('game_record', {})
        
        # Get player information (mapping player_id to llm_id and concept)
        players = {}
        for player in game_record.get('players', []):
            players[player['player_id']] = {
                'llm_id': player['llm_id'],
                'concept': player['assigned_concept']
            }
        
        # Extract statements
        for statement in game_record.get('game_process', {}).get('statements', []):
            player_id = statement.get('player_id')
            if player_id in players:
                all_statements.append({
                    'statement': statement.get('content', ''),
                    'llm_id': statement.get('llm_id', players[player_id]['llm_id']),
                    'concept': players[player_id]['concept'],
                    'statement_id': statement.get('statement_id'),
                    'statement_round': statement.get('statement_round'),
                    'game_id': game_record.get('game_id')
                })
    
    return all_statements

def main():
    # Configuration
    input_directory = "json_files"  # Replace with your directory
    output_json_path = "statements_with_embeddings.json"
    
    # Process JSON files
    print("Processing JSON files...")
    statements = process_json_files(input_directory)
    
    # Save statements to JSON before embedding
    statements_output_path = "extracted_statements.json"
    with open(statements_output_path, 'w') as file:
        json.dump(statements, file, indent=2)
    print(f"Extracted statements saved to {statements_output_path}")
    
    # TODO: Choose and configure your embedding provider
    # Uncomment one of the following:
    
    # For OpenAI:
    # api_key = os.environ.get("OPENAI_API_KEY", "")
    # embedding_generator = OpenAIEmbedding(api_key=api_key)
    
    # For Anthropic:
    # api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    # embedding_generator = AnthropicEmbedding(api_key=api_key)
    
    # For testing:
    embedding_generator = DummyEmbedding()
    
    # Generate embeddings
    print("Generating embeddings...")
    texts = [item['statement'] for item in statements]
    embeddings = embedding_generator.generate_embeddings(texts)
    
    # Add embeddings to statements
    for i, item in enumerate(statements):
        item['embedding'] = embeddings[i]
    
    # Save results to JSON
    print(f"Saving results to {output_json_path}...")
    with open(output_json_path, 'w') as file:
        json.dump(statements, file, indent=2)
    
    print(f"Processed {len(statements)} statements from JSON files.")
    print(f"Results saved to {output_json_path}")

if __name__ == "__main__":
    main()