import os
import json
import numpy as np
from sklearn.manifold import TSNE
import matplotlib.pyplot as plt

def process_json_files(directory_path):
    """
    Process all JSON files in the given directory, extracting statements, LLM IDs, and concepts.
    """
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

def save_statements_to_json(statements, output_path):
    """
    Save extracted statements to a new JSON file.
    """
    with open(output_path, 'w') as file:
        json.dump(statements, file, indent=2)

def generate_embeddings(statements):
    """
    TODO: Generate embeddings for statements using a large language model.
    
    For now, we'll use random embeddings as placeholders.
    """
    for statement in statements:
        # This is where you would call your LLM's embedding API
        # For example: embedding = call_embedding_api(statement['statement'])
        
        # Generate random embedding (placeholder)
        statement['embedding'] = [float(x) for x in np.random.rand(384)]
    
    return statements

def perform_tsne(statements_with_embeddings):
    """
    Apply t-SNE to the embeddings and add coordinates to each statement.
    """
    # Extract embeddings as a list of lists
    embeddings = [s['embedding'] for s in statements_with_embeddings]
    
    # Apply t-SNE
    tsne = TSNE(n_components=2, random_state=42, perplexity=min(30, len(embeddings)-1))
    tsne_results = tsne.fit_transform(embeddings)
    
    # Add t-SNE coordinates to statements
    for i, statement in enumerate(statements_with_embeddings):
        statement['x'] = float(tsne_results[i, 0])
        statement['y'] = float(tsne_results[i, 1])
    
    return statements_with_embeddings

def visualize_tsne(statements_with_coords, output_file='tsne_visualization.png'):
    """
    Create and save a matplotlib visualization of the t-SNE results.
    """
    # Create a dictionary to map LLM IDs to colors
    unique_llms = list(set(item['llm_id'] for item in statements_with_coords))
    colors = plt.cm.rainbow(np.linspace(0, 1, len(unique_llms)))
    llm_to_color = {llm: colors[i] for i, llm in enumerate(unique_llms)}
    
    # Create a dictionary to map concepts to markers
    unique_concepts = list(set(item['concept'] for item in statements_with_coords))
    markers = ['o', 's', '^', 'D', '*', 'p', 'h', 'x']  # Different marker styles
    concept_to_marker = {concept: markers[i % len(markers)] for i, concept in enumerate(unique_concepts)}
    
    # Plot
    plt.figure(figsize=(12, 8))
    
    for item in statements_with_coords:
        llm = item['llm_id']
        concept = item['concept']
        plt.scatter(
            item['x'], 
            item['y'],
            color=llm_to_color[llm],
            marker=concept_to_marker[concept],
            s=100,
            label=f"{llm} ({concept})"
        )
    
    # Create legend with unique entries
    handles, labels = plt.gca().get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    plt.legend(by_label.values(), by_label.keys(), loc='center left', bbox_to_anchor=(1, 0.5))
    
    plt.title('t-SNE Visualization of LLM Statements')
    plt.xlabel('t-SNE Dimension 1')
    plt.ylabel('t-SNE Dimension 2')
    plt.tight_layout()
    plt.savefig(output_file, dpi=300)
    plt.close()

def main():
    input_directory = "logs/en/different_llm_standard/en/artifacts"  # Replace with actual directory path
    output_json_path = "t-sne/statements_with_embeddings.json"
    
    # Process JSON files
    print("Processing JSON files...")
    statements = process_json_files(input_directory)
    
    # Save statements to JSON before embedding
    statements_output_path = "extracted_statements.json"
    save_statements_to_json(statements, statements_output_path)
    print(f"Extracted statements saved to {statements_output_path}")
    
    # Generate embeddings
    print("Generating embeddings...")
    statements_with_embeddings = generate_embeddings(statements)
    
    # Apply t-SNE
    print("Applying t-SNE...")
    statements_with_coords = perform_tsne(statements_with_embeddings)
    
    # Save results to JSON
    print(f"Saving results to {output_json_path}...")
    save_statements_to_json(statements_with_coords, output_json_path)
    
    # Create visualization
    print("Creating visualization...")
    visualize_tsne(statements_with_coords)
    
    print(f"Processed {len(statements)} statements from JSON files.")
    print(f"Results saved to {output_json_path}")
    print("t-SNE visualization saved as tsne_visualization.png")

if __name__ == "__main__":
    main()