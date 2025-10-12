# Interactive Graph Explorer: Game of Thrones Character Network

![Bokeh Logo](https://docs.bokeh.org/en/latest/_images/bokeh-transparent.png)  

An interactive network visualization of Game of Thrones character interactions using Python, Bokeh Server, NetworkX, and Neo4j AuraDB. Explore characters and their interactions dynamically with hover tooltips, search/filter, and dynamic highlighting.

---

## Features

- Graph rendering using NetworkX spring layout  
- Nodes as circles, edges colored by relationship type  
- Hover tooltips: Node degree, relations, edge weight  
- Tap tool: Highlight connected nodes and edges  
- Search/filter nodes by name dynamically  
- Zoom and pan navigation  
- Deployable on Render.com or runnable locally  

---

## Repository Structure

```

bokeh_graph_app/
├── main.py             # Bokeh application script
├── render_start.sh     # Startup script for Render deployment
├── requirements.txt    # Python dependencies
└── README.md           # Project documentation

````

---

## Live Demo

[https://bokeh-graph-app.onrender.com/main](https://bokeh-graph-app.onrender.com/main)

---

## Quick Start

### Run Locally

1. Clone the repository:

```bash
git clone https://github.com/ssnsii/bokeh_graph_app.git
cd bokeh_graph_app
````

2. (Optional) Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Run the Bokeh Server:

```bash
bokeh serve --show main.py
```

Open [http://localhost:5006/main](http://localhost:5006/main) in your browser.

---

### Deploy on Render.com

1. Push repo to GitHub
2. Create a **New Web Service** on Render and connect GitHub repo
3. Configure:
   * Environment: Python 3.11+
   * Build Command: `pip install -r requirements.txt`
   * Start Command: `bash render_start.sh`
     Ensure `--allow-websocket-origin=bokeh-graph-app.onrender.com` is included
4. Deploy and access the app live at [https://bokeh-graph-app.onrender.com/main](https://bokeh-graph-app.onrender.com/main)

---

## Neo4j Setup

* Uses Neo4j AuraDB (cloud-hosted)
* Apply cypher queries to import data to neo4j 
* Ensure node uniqueness and relationship attributes

Example Cypher query:

```cypher
CREATE CONSTRAINT ON (c:Character) ASSERT c.name IS UNIQUE;

LOAD CSV WITH HEADERS FROM 'URL' AS row
MERGE (src:Character {name: row.Source})
MERGE (tgt:Character {name: row.Target})
MERGE (src)-[r:INTERACTS1]->(tgt)
ON CREATE SET r.weight = toInteger(row.weight), r.book = 1;
```

---

## Dependencies

* Python 3.11+
* Bokeh
* NetworkX
* py2neo
* Neo4j AuraDB
