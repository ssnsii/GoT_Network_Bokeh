# Import libraries
# py2neo to connect Python with Neo4j
from py2neo import Graph
# pandas for handling tabular data from Neo4j
import pandas as pd
# networkx for building and manipulating the graph
import networkx as nx
# Bokeh for interactive plotting
from bokeh.models import Circle, MultiLine, HoverTool, TapTool, TextInput, CustomJS
from bokeh.plotting import figure, from_networkx, curdoc
from bokeh.layouts import column
import os

# Get credentials from environment variables
uri = os.getenv("NEO4J_URI")
user = os.getenv("NEO4J_USER")
password = os.getenv("NEO4J_PASSWORD")

# Connect to Neo4j
# Create a connection to the aura Neo4j database
# Authentication is provided with username and password
graph = Graph(uri, auth=(user, password))

# Query Neo4j
# Run a Cypher query to get all Character nodes and their interactions
# The query returns:
#   - 'source': name of the starting node
#   - 'target': name of the target node
#   - 'relation': type of the relationship
#   - 'weight': weight property of the relationship
query = """
MATCH (c:Character)-[r]->(d:Character)
RETURN c.name AS source, d.name AS target, type(r) AS relation, r.weight AS weight
LIMIT 100
"""
# Convert the query result to a pandas DataFrame for preprocessing
data = graph.run(query).to_data_frame()

# Preprocessing
# Filter out weak interactions (weight < 2)
data = data[data['weight'] >= 2]
# Remove self-loops (nodes connecting to themselves)
data = data[data['source'] != data['target']]

# Map relationship types to colors for visualization
color_map = {'INTERACTS1':'purple','INTERACTS2':'red','INTERACTS3':'green','INTERACTS45':'blue'}
data['edge_color'] = data['relation'].map(color_map)

# Build NetworkX graph
# Convert the DataFrame into a NetworkX graph
# Nodes are characters, edges are relationships with attributes
G = nx.from_pandas_edgelist(data, 'source', 'target', edge_attr=True)

# Add node attributes for visualization
for n in G.nodes():
    edges = G.edges(n, data=True)  # get edges connected to the node
    G.nodes[n]['degree'] = len(edges)  # store node degree (number of connections)
    # store concatenated relationship info for hover tooltip
    G.nodes[n]['relations'] = ", ".join([f"{e[2]['relation']} ({e[2]['weight']})" for e in edges])
    G.nodes[n]['node_color'] = 'skyblue'  # default node color

# Bokeh plot setup
# Create an interactive Bokeh figure
plot = figure(title="Interactive Graph Explorer",
              x_range=(-1.5,1.5), y_range=(-1.5,1.5),
              tools="pan,wheel_zoom,save,reset", width=900, height=700)

# Compute node positions using spring layout
pos = nx.spring_layout(G, seed=42)
# Convert NetworkX graph to Bokeh GraphRenderer
graph_renderer = from_networkx(G, pos)

# Node data for Bokeh
# Attach attributes to node renderer for tooltips and styling
graph_renderer.node_renderer.data_source.data['degree'] = [G.nodes[n]['degree'] for n in G.nodes()]
graph_renderer.node_renderer.data_source.data['relations'] = [G.nodes[n]['relations'] for n in G.nodes()]
graph_renderer.node_renderer.data_source.data['node_color'] = [G.nodes[n]['node_color'] for n in G.nodes()]

# Edge data for Bokeh
# Attach attributes to edge renderer for tooltips and styling
# use string node names as Bokeh expects them
graph_renderer.edge_renderer.data_source.data['relation'] = [G.edges[e]['relation'] for e in G.edges()]
graph_renderer.edge_renderer.data_source.data['weight'] = [G.edges[e]['weight'] for e in G.edges()]
graph_renderer.edge_renderer.data_source.data['line_color'] = [G.edges[e]['edge_color'] for e in G.edges()]

# Styling nodes and edges
graph_renderer.node_renderer.glyph = Circle(radius=0.05, fill_color='node_color', fill_alpha=0.8)
graph_renderer.edge_renderer.glyph = MultiLine(line_color='line_color', line_alpha=0.8, line_width=2)

# Add the graph renderer to the plot
plot.renderers.append(graph_renderer)

# Interactivity
# Add hover tool for nodes showing name, degree, and relations
plot.add_tools(HoverTool(tooltips=[("Node","@index"),("Degree","@degree"),("Relations","@relations")],
                         renderers=[graph_renderer.node_renderer]))
# Add hover tool for edges showing relation type and weight
plot.add_tools(HoverTool(tooltips=[("Relation","@relation"),("Weight","@weight")],
                         renderers=[graph_renderer.edge_renderer]))
# Add tap tool for selecting nodes
plot.add_tools(TapTool())

# Search / Filter input
# Create a text input widget for filtering nodes by name
text_input = TextInput(title="Filter nodes by name:")

# JavaScript callback to filter nodes and highlight connected edges dynamically
search_callback = CustomJS(
    args=dict(renderer=graph_renderer, text=text_input),
    code="""
const value = text.value.toLowerCase();
const nodes = renderer.node_renderer.data_source;
const edges = renderer.edge_renderer.data_source;

// Find node indices matching the filter
const node_indices = nodes.data['index'].map((n,i)=>n.toLowerCase().includes(value)?i:null).filter(x=>x!==null);

// Find edges connected to the filtered nodes
const edge_indices = [];
for(let i=0;i<edges.data['start'].length;i++){
    if(node_indices.includes(i) || node_indices.includes(i)){
        edge_indices.push(i);
    }
}

// Update selection to highlight nodes and edges
nodes.selected.indices = node_indices;
edges.selected.indices = edge_indices;
"""
)
# Connect the callback to the text input
text_input.js_on_change('value', search_callback)

# Highlight nodes connected to selected nodes
highlight_callback = CustomJS(
    args=dict(renderer=graph_renderer),
    code="""
const nodes = renderer.node_renderer.data_source;
const edges = renderer.edge_renderer.data_source;
const selected = nodes.selected.indices;

let connected_nodes = [];
let connected_edges = [];
for(let i=0;i<edges.data['start'].length;i++){
    if(selected.includes(i) || selected.includes(i)){
        connected_edges.push(i);
        connected_nodes.push(i);
        connected_nodes.push(i);
    }
}
nodes.selected.indices = [...new Set(connected_nodes)];
edges.selected.indices = connected_edges;
"""
)
# Trigger highlight when node selection changes
graph_renderer.node_renderer.data_source.selected.js_on_change('indices', highlight_callback)

# Layout and add to document
# Arrange the search input and plot vertically
layout = column(text_input, plot)
# Add layout to the Bokeh document
curdoc().add_root(layout)
# Set document title
curdoc().title = "Interactive Graph Explorer"
