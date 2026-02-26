#!/usr/bin/env python3
"""
Knowledge Graph Visualization Generator
Generate interactive HTML knowledge graph from JSON data

Usage:
    python generate_knowledge_graph.py input.json -o output.html
    python generate_knowledge_graph.py input.json  # Default output: knowledge_graph.html
"""

import json
import argparse
from pathlib import Path
from typing import Dict, List, Set, Any


# Stop phrases filter list
STOP_PHRASES = [
    'this creature', 'this insect', 'this animal', 'the creature',
    'its ability', 'its role', 'its importance', 'its presence',
    'a role', 'a touch', 'various', 'another', 'which', 'others',
    'the health', 'the balance', 'the growth', 'the company',
    'many plants', 'one flower', 'various ways', 'various stages',
    'a living being', 'movement', 'life', 'has wings', 'observe it',
    'small creature', 'tiny creature', 'small insect', 'tiny insect',
    'flying insect', 'winged creature', 'flying creature',
    'a small', 'a tiny', 'a winged', 'a flying', 'a delicate',
    'a graceful', 'a colorful', 'an important', 'a crucial', 'a vital',
    'plays role', 'adds touch', 'undergoes metamorphosis',
]

# Generic words
GENERIC_WORDS = {
    'thing', 'something', 'anything', 'nothing',
    'way', 'ways', 'kind', 'type', 'form',
    'part', 'place', 'time', 'day', 'year',
    'it', 'they', 'them', 'their', 'its',
}


def is_valid_feature(name: str, feature: Dict[str, Any],
                     min_frequency: int = 2,
                     min_relevance: float = 0.4,
                     min_length: int = 3) -> bool:
    """
    Check if a feature is valid (filter noise)

    Args:
        name: Feature name
        feature: Feature data
        min_frequency: Minimum frequency threshold
        min_relevance: Minimum relevance threshold
        min_length: Minimum character length

    Returns:
        bool: Whether the feature is valid
    """
    lower_name = name.lower().strip()
    
    # Filter short words
    if len(lower_name) < min_length:
        return False
    
    # Filter low frequency words
    if feature.get('frequency', 0) < min_frequency:
        return False
    
    # Filter low relevance
    if feature.get('avg_relevance', 0) < min_relevance:
        return False
    
    # Filter stop phrases
    for stop_phrase in STOP_PHRASES:
        if stop_phrase.lower() in lower_name or lower_name in stop_phrase.lower():
            return False
    
    # Filter generic words
    words = set(lower_name.split())
    if words & GENERIC_WORDS == words:  # All generic words
        return False
    
    # Filter purely descriptive long phrases (starting with articles and more than 4 words)
    if lower_name.split()[0] in {'a', 'an', 'the', 'its', 'this', 'that'}:
        if len(lower_name.split()) > 4:
            return False
    
    return True


def process_features(features_data: Dict[str, Any],
                    concepts: List[str],
                    min_frequency: int = 2,
                    min_relevance: float = 0.4) -> Dict[str, Any]:
    """
    Process and filter feature data

    Args:
        features_data: Raw feature data
        concepts: List of concepts
        min_frequency: Minimum frequency
        min_relevance: Minimum relevance

    Returns:
        Processed feature dictionary
    """
    processed = {}
    
    for name, feature in features_data.items():
        if not is_valid_feature(name, feature, min_frequency, min_relevance):
            continue
        
        # Ensure concept list is valid
        valid_concepts = [c for c in feature.get('concepts', []) if c in concepts]
        if not valid_concepts:
            continue
        
        processed[name] = {
            'name': feature.get('name', name),
            'frequency': feature.get('frequency', 1),
            'avg_relevance': feature.get('avg_relevance', 0.5),
            'concepts': valid_concepts,
            'is_shared': len(valid_concepts) > 1,
            'feature_type': feature.get('feature_type', 'unknown')
        }
    
    return processed


def generate_html(data: Dict[str, Any],
                  title: str = "Knowledge Graph",
                  min_frequency: int = 2,
                  min_relevance: float = 0.4) -> str:
    """
    Generate interactive HTML knowledge graph

    Args:
        data: Input JSON data
        title: Page title
        min_frequency: Minimum feature frequency
        min_relevance: Minimum feature relevance

    Returns:
        HTML string
    """
    # Extract concepts
    concepts = list(data.get('concepts', {}).keys())
    if not concepts:
        raise ValueError("No concepts found in data")
    
    # Process features
    features = process_features(
        data.get('features', {}), 
        concepts,
        min_frequency=min_frequency,
        min_relevance=min_relevance
    )
    
    # Generate concept display names and colors
    concept_colors = ['#f39c12', '#9b59b6', '#1abc9c', '#e67e22', '#3498db']
    concept_emojis = ['🐝', '🦋', '🌸', '🌿', '🌍']
    
    concepts_js = []
    for i, concept in enumerate(concepts):
        color = concept_colors[i % len(concept_colors)]
        emoji = concept_emojis[i % len(concept_emojis)] if i < len(concept_emojis) else ''
        concepts_js.append({
            'id': concept,
            'name': f"{concept.title()} {emoji}",
            'color': color
        })
    
    # Convert to JSON string
    concepts_json = json.dumps(concepts_js, ensure_ascii=False, indent=2)
    features_json = json.dumps(features, ensure_ascii=False, indent=2)
    
    # Generate legend HTML
    legend_items = []
    for i, concept in enumerate(concepts):
        color = concept_colors[i % len(concept_colors)]
        legend_items.append(f'''
                <div class="legend-item">
                    <div class="legend-circle" style="background: {color};"></div>
                    <span>{concept.title()}</span>
                </div>''')
    
    # Feature color legend
    feature_colors_legend = '''
                <div class="legend-item">
                    <div class="legend-circle" style="background: #e74c3c;"></div>
                    <span>Concept 1 Unique</span>
                </div>
                <div class="legend-item">
                    <div class="legend-circle" style="background: #3498db;"></div>
                    <span>Concept 2 Unique</span>
                </div>
                <div class="legend-item">
                    <div class="legend-circle" style="background: #2ecc71;"></div>
                    <span>Shared Feature</span>
                </div>'''
    
    legend_html = '\n'.join(legend_items) + feature_colors_legend
    
    html_template = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/d3/7.8.5/d3.min.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
            min-height: 100vh;
            color: #e8e8e8;
            overflow: hidden;
        }}
        
        .container {{
            display: flex;
            height: 100vh;
        }}
        
        .sidebar {{
            width: 320px;
            background: rgba(0,0,0,0.3);
            backdrop-filter: blur(10px);
            padding: 20px;
            overflow-y: auto;
            border-right: 1px solid rgba(255,255,255,0.1);
        }}
        
        .main {{
            flex: 1;
            position: relative;
        }}
        
        h1 {{
            font-size: 1.4rem;
            margin-bottom: 20px;
            background: linear-gradient(90deg, #f39c12, #e74c3c);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}
        
        .legend {{
            margin-bottom: 20px;
        }}
        
        .legend-title {{
            font-size: 0.9rem;
            font-weight: 600;
            margin-bottom: 10px;
            color: #aaa;
        }}
        
        .legend-item {{
            display: flex;
            align-items: center;
            margin: 8px 0;
            font-size: 0.85rem;
        }}
        
        .legend-circle {{
            width: 16px;
            height: 16px;
            border-radius: 50%;
            margin-right: 10px;
            flex-shrink: 0;
        }}
        
        .legend-line {{
            width: 30px;
            height: 3px;
            margin-right: 10px;
            flex-shrink: 0;
            border-radius: 2px;
        }}
        
        .filters {{
            margin-bottom: 20px;
        }}
        
        .filter-group {{
            margin-bottom: 15px;
        }}
        
        .filter-label {{
            font-size: 0.85rem;
            color: #aaa;
            margin-bottom: 8px;
            display: block;
        }}
        
        .slider-container {{
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        
        input[type="range"] {{
            flex: 1;
            -webkit-appearance: none;
            height: 6px;
            background: rgba(255,255,255,0.2);
            border-radius: 3px;
            outline: none;
        }}
        
        input[type="range"]::-webkit-slider-thumb {{
            -webkit-appearance: none;
            width: 16px;
            height: 16px;
            background: #f39c12;
            border-radius: 50%;
            cursor: pointer;
        }}
        
        .slider-value {{
            font-size: 0.85rem;
            color: #f39c12;
            min-width: 30px;
        }}
        
        .checkbox-group {{
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
        }}
        
        .checkbox-item {{
            display: flex;
            align-items: center;
            gap: 6px;
            font-size: 0.85rem;
            cursor: pointer;
        }}
        
        .checkbox-item input {{
            accent-color: #f39c12;
        }}
        
        .stats {{
            background: rgba(255,255,255,0.05);
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 20px;
        }}
        
        .stats-title {{
            font-size: 0.9rem;
            font-weight: 600;
            margin-bottom: 10px;
            color: #aaa;
        }}
        
        .stat-row {{
            display: flex;
            justify-content: space-between;
            font-size: 0.85rem;
            margin: 5px 0;
        }}
        
        .stat-value {{
            color: #f39c12;
            font-weight: 600;
        }}
        
        #tooltip {{
            position: absolute;
            background: rgba(0,0,0,0.9);
            border: 1px solid rgba(255,255,255,0.2);
            border-radius: 8px;
            padding: 12px;
            font-size: 0.85rem;
            pointer-events: none;
            opacity: 0;
            transition: opacity 0.2s;
            max-width: 300px;
            z-index: 1000;
        }}
        
        .tooltip-title {{
            font-weight: 600;
            margin-bottom: 8px;
            color: #f39c12;
        }}
        
        .tooltip-row {{
            margin: 4px 0;
            color: #ccc;
        }}
        
        .tooltip-label {{
            color: #888;
        }}
        
        svg {{
            width: 100%;
            height: 100%;
        }}
        
        .node-label {{
            font-size: 11px;
            fill: #fff;
            pointer-events: none;
            text-shadow: 0 1px 3px rgba(0,0,0,0.8);
        }}
        
        .concept-label {{
            font-size: 16px;
            font-weight: bold;
            fill: #fff;
            text-shadow: 0 2px 4px rgba(0,0,0,0.8);
        }}
        
        .info-panel {{
            position: absolute;
            bottom: 20px;
            left: 20px;
            background: rgba(0,0,0,0.7);
            border-radius: 10px;
            padding: 15px;
            font-size: 0.8rem;
            max-width: 300px;
        }}
        
        .info-panel p {{
            margin: 5px 0;
            color: #aaa;
        }}
        
        .info-panel strong {{
            color: #f39c12;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="sidebar">
            <h1>{title}</h1>
            
            <div class="legend">
                <div class="legend-title">Node Types</div>
                {legend_html}
            </div>

            <div class="legend">
                <div class="legend-title">Edge Strength</div>
                <div class="legend-item">
                    <div class="legend-line" style="background: rgba(255,255,255,0.8);"></div>
                    <span>Strong (relevance > 1.0)</span>
                </div>
                <div class="legend-item">
                    <div class="legend-line" style="background: rgba(255,255,255,0.4);"></div>
                    <span>Medium</span>
                </div>
                <div class="legend-item">
                    <div class="legend-line" style="background: rgba(255,255,255,0.15);"></div>
                    <span>Weak (relevance < 0.5)</span>
                </div>
            </div>
            
            <div class="filters">
                <div class="filter-group">
                    <label class="filter-label">Min Frequency (filter low-frequency features)</label>
                    <div class="slider-container">
                        <input type="range" id="freqFilter" min="1" max="20" value="3">
                        <span class="slider-value" id="freqValue">3</span>
                    </div>
                </div>

                <div class="filter-group">
                    <label class="filter-label">Min Relevance</label>
                    <div class="slider-container">
                        <input type="range" id="relevanceFilter" min="0" max="100" value="50">
                        <span class="slider-value" id="relevanceValue">0.5</span>
                    </div>
                </div>

                <div class="filter-group">
                    <label class="filter-label">Feature Types</label>
                    <div class="checkbox-group">
                        <label class="checkbox-item">
                            <input type="checkbox" id="showUnique" checked>
                            <span>Unique</span>
                        </label>
                        <label class="checkbox-item">
                            <input type="checkbox" id="showShared" checked>
                            <span>Shared</span>
                        </label>
                    </div>
                </div>
            </div>
            
            <div class="stats">
                <div class="stats-title">Statistics</div>
                <div class="stat-row">
                    <span>Features Displayed</span>
                    <span class="stat-value" id="featureCount">0</span>
                </div>
                <div class="stat-row">
                    <span>Unique Features</span>
                    <span class="stat-value" id="uniqueCount">0</span>
                </div>
                <div class="stat-row">
                    <span>Shared Features</span>
                    <span class="stat-value" id="sharedCount">0</span>
                </div>
            </div>
        </div>
        
        <div class="main">
            <svg id="graph"></svg>
            <div id="tooltip"></div>
            <div class="info-panel">
                <p><strong>Interactions:</strong></p>
                <p>* Drag nodes to reposition</p>
                <p>* Scroll to zoom</p>
                <p>* Hover for details</p>
                <p>* Use filters to reduce noise</p>
            </div>
        </div>
    </div>

    <script>
        // Concept data
        const conceptsData = {concepts_json};
        
        // Feature data
        const featuresData = {features_json};
        
        // Feature color mapping
        const uniqueColors = ['#e74c3c', '#3498db', '#e67e22', '#1abc9c', '#9b59b6'];
        const sharedColor = '#2ecc71';
        
        // Prepare node and edge data
        let nodes = [];
        let links = [];

        function prepareData(minFreq, minRelevance, showUnique, showShared) {{
            nodes = [];
            links = [];
            
            // Add concept nodes
            conceptsData.forEach(concept => {{
                nodes.push({{
                    id: concept.id,
                    name: concept.name,
                    type: 'concept',
                    color: concept.color,
                    radius: 40
                }});
            }});

            // Add feature nodes
            Object.entries(featuresData).forEach(([key, feature]) => {{
                if (feature.frequency < minFreq) return;
                if (feature.avg_relevance < minRelevance) return;
                
                const isShared = feature.is_shared;
                
                if (!isShared && !showUnique) return;
                if (isShared && !showShared) return;
                
                let color;
                if (isShared) {{
                    color = sharedColor;
                }} else {{
                    // Determine color based on first related concept
                    const conceptIndex = conceptsData.findIndex(c => c.id === feature.concepts[0]);
                    color = uniqueColors[conceptIndex % uniqueColors.length];
                }}
                
                const radius = Math.max(8, Math.min(25, feature.frequency * 1.2));
                
                nodes.push({{
                    id: key,
                    name: feature.name,
                    type: 'feature',
                    color: color,
                    radius: radius,
                    frequency: feature.frequency,
                    relevance: feature.avg_relevance,
                    concepts: feature.concepts,
                    isShared: isShared,
                    featureType: feature.feature_type
                }});
                
                // Add connections
                feature.concepts.forEach(concept => {{
                    links.push({{
                        source: key,
                        target: concept,
                        relevance: feature.avg_relevance,
                        strength: Math.min(1, feature.avg_relevance / 2)
                    }});
                }});
            }});
            
            // Update statistics
            const featureNodes = nodes.filter(n => n.type === 'feature');
            document.getElementById('featureCount').textContent = featureNodes.length;
            document.getElementById('uniqueCount').textContent = featureNodes.filter(n => !n.isShared).length;
            document.getElementById('sharedCount').textContent = featureNodes.filter(n => n.isShared).length;
        }}

        // D3 visualization
        const svg = d3.select('#graph');
        const width = document.querySelector('.main').clientWidth;
        const height = document.querySelector('.main').clientHeight;
        
        const g = svg.append('g');
        
        // Zoom
        const zoom = d3.zoom()
            .scaleExtent([0.3, 3])
            .on('zoom', (event) => {{
                g.attr('transform', event.transform);
            }});
        
        svg.call(zoom);
        
        // Initial zoom to center
        svg.call(zoom.transform, d3.zoomIdentity.translate(width/2, height/2).scale(0.8));

        let simulation;
        
        function updateGraph() {{
            const minFreq = parseInt(document.getElementById('freqFilter').value);
            const minRelevance = parseInt(document.getElementById('relevanceFilter').value) / 100;
            const showUnique = document.getElementById('showUnique').checked;
            const showShared = document.getElementById('showShared').checked;
            
            prepareData(minFreq, minRelevance, showUnique, showShared);
            
            // Clear old elements
            g.selectAll('*').remove();
            
            // Force-directed simulation
            simulation = d3.forceSimulation(nodes)
                .force('link', d3.forceLink(links).id(d => d.id).distance(d => {{
                    return d.relevance > 1 ? 80 : 120;
                }}).strength(d => d.strength * 0.5))
                .force('charge', d3.forceManyBody().strength(d => d.type === 'concept' ? -500 : -100))
                .force('center', d3.forceCenter(0, 0))
                .force('collision', d3.forceCollide().radius(d => d.radius + 5));
            
            // Draw edges
            const link = g.append('g')
                .selectAll('line')
                .data(links)
                .join('line')
                .attr('stroke', d => {{
                    if (d.relevance > 1) return 'rgba(255,255,255,0.6)';
                    if (d.relevance > 0.7) return 'rgba(255,255,255,0.35)';
                    return 'rgba(255,255,255,0.15)';
                }})
                .attr('stroke-width', d => Math.max(1, d.relevance * 2));
            
            // Draw nodes
            const node = g.append('g')
                .selectAll('g')
                .data(nodes)
                .join('g')
                .call(d3.drag()
                    .on('start', dragstarted)
                    .on('drag', dragged)
                    .on('end', dragended));
            
            // Node glow effect
            const defs = svg.select('defs').empty() ? svg.append('defs') : svg.select('defs');
            defs.selectAll('*').remove();
            
            nodes.forEach((n, i) => {{
                const filter = defs.append('filter')
                    .attr('id', `glow-${{i}}`)
                    .attr('x', '-50%')
                    .attr('y', '-50%')
                    .attr('width', '200%')
                    .attr('height', '200%');
                
                filter.append('feGaussianBlur')
                    .attr('stdDeviation', '3')
                    .attr('result', 'coloredBlur');
                
                const feMerge = filter.append('feMerge');
                feMerge.append('feMergeNode').attr('in', 'coloredBlur');
                feMerge.append('feMergeNode').attr('in', 'SourceGraphic');
            }});
            
            node.append('circle')
                .attr('r', d => d.radius)
                .attr('fill', d => d.color)
                .attr('stroke', '#fff')
                .attr('stroke-width', d => d.type === 'concept' ? 3 : 1.5)
                .attr('opacity', d => d.type === 'concept' ? 1 : 0.85)
                .style('filter', (d, i) => `url(#glow-${{i}})`)
                .style('cursor', 'pointer');
            
            // Node labels
            node.append('text')
                .attr('class', d => d.type === 'concept' ? 'concept-label' : 'node-label')
                .attr('text-anchor', 'middle')
                .attr('dy', d => d.type === 'concept' ? 5 : (d.radius + 14))
                .text(d => d.name.length > 20 ? d.name.substring(0, 18) + '...' : d.name);
            
            // Tooltip
            const tooltip = document.getElementById('tooltip');
            
            node.on('mouseover', (event, d) => {{
                if (d.type === 'feature') {{
                    tooltip.innerHTML = `
                        <div class="tooltip-title">${{d.name}}</div>
                        <div class="tooltip-row"><span class="tooltip-label">Frequency: </span>${{d.frequency}}</div>
                        <div class="tooltip-row"><span class="tooltip-label">Relevance: </span>${{d.relevance.toFixed(2)}}</div>
                        <div class="tooltip-row"><span class="tooltip-label">Type: </span>${{d.isShared ? 'Shared' : 'Unique'}}</div>
                        <div class="tooltip-row"><span class="tooltip-label">Feature Type: </span>${{d.featureType}}</div>
                        <div class="tooltip-row"><span class="tooltip-label">Related Concepts: </span>${{d.concepts.join(', ')}}</div>
                    `;
                }} else {{
                    tooltip.innerHTML = `
                        <div class="tooltip-title">${{d.name}}</div>
                        <div class="tooltip-row">Core Concept Node</div>
                    `;
                }}
                tooltip.style.opacity = 1;
                tooltip.style.left = (event.pageX + 15) + 'px';
                tooltip.style.top = (event.pageY - 10) + 'px';
            }})
            .on('mousemove', (event) => {{
                tooltip.style.left = (event.pageX + 15) + 'px';
                tooltip.style.top = (event.pageY - 10) + 'px';
            }})
            .on('mouseout', () => {{
                tooltip.style.opacity = 0;
            }});
            
            // Update positions
            simulation.on('tick', () => {{
                link
                    .attr('x1', d => d.source.x)
                    .attr('y1', d => d.source.y)
                    .attr('x2', d => d.target.x)
                    .attr('y2', d => d.target.y);
                
                node.attr('transform', d => `translate(${{d.x}},${{d.y}})`);
            }});
        }}
        
        function dragstarted(event, d) {{
            if (!event.active) simulation.alphaTarget(0.3).restart();
            d.fx = d.x;
            d.fy = d.y;
        }}
        
        function dragged(event, d) {{
            d.fx = event.x;
            d.fy = event.y;
        }}
        
        function dragended(event, d) {{
            if (!event.active) simulation.alphaTarget(0);
            d.fx = null;
            d.fy = null;
        }}
        
        // Event listeners
        document.getElementById('freqFilter').addEventListener('input', (e) => {{
            document.getElementById('freqValue').textContent = e.target.value;
            updateGraph();
        }});
        
        document.getElementById('relevanceFilter').addEventListener('input', (e) => {{
            document.getElementById('relevanceValue').textContent = (e.target.value / 100).toFixed(1);
            updateGraph();
        }});
        
        document.getElementById('showUnique').addEventListener('change', updateGraph);
        document.getElementById('showShared').addEventListener('change', updateGraph);
        
        // Initialize
        updateGraph();
    </script>
</body>
</html>'''
    
    return html_template


def main():
    parser = argparse.ArgumentParser(
        description='Generate interactive knowledge graph HTML from JSON data',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
    python generate_knowledge_graph.py kg_data.json
    python generate_knowledge_graph.py kg_data.json -o my_graph.html
    python generate_knowledge_graph.py kg_data.json --title "Concept Comparison" --min-freq 5
        '''
    )

    parser.add_argument('input', help='Input JSON file path')
    parser.add_argument('-o', '--output', default='D:\MyWorks\KnowledgeEdge\icml_exp\KG\output\htmls\knowledge_graph.html',
                        help='Output HTML file path (default: knowledge_graph.html)')
    parser.add_argument('--title', default='Knowledge Graph',
                        help='Page title (default: Knowledge Graph)')
    parser.add_argument('--min-freq', type=int, default=2,
                        help='Minimum feature frequency threshold (default: 2)')
    parser.add_argument('--min-relevance', type=float, default=0.4,
                        help='Minimum feature relevance threshold (default: 0.4)')
    
    args = parser.parse_args()
    
    # Read input file
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: Input file not found '{args.input}'")
        return 1
    
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error: JSON parsing failed - {e}")
        return 1
    
    # Generate HTML
    try:
        html_content = generate_html(
            data,
            title=args.title,
            min_frequency=args.min_freq,
            min_relevance=args.min_relevance
        )
    except ValueError as e:
        print(f"Error: {e}")
        return 1
    
    # Write output file
    output_path = Path(args.output)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"Knowledge graph generated: {output_path.absolute()}")
    print(f"   Concepts: {len(data.get('concepts', {}))}")
    print(f"   Raw features: {len(data.get('features', {}))}")
    
    return 0


if __name__ == '__main__':
    exit(main())