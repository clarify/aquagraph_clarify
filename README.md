# Aquagraph

Aquagraph visualization in arrows, add user input and use fastapi to make opperations in a Neo4j database.

# Dependencies

To connect with Neo4j and it's database, Neo4j must be installed locally:

- Download Neo4j https://neo4j.com/download/

Steps: Press Download. Add credentials. Click download desktop. Copy the activation key. Click and drag Neo4j Desktop to the Application folder. Open the Neo4j Desktop (go to Security & Privacy and click to open anyway). After you have open the Neo4j Desktop under the software registration paste the key that you have previously copied.

- Create Project and Database

Click to the Project icon (top left corner, looks file a folder). Create a new Project. Click the Add button and add _Local DBMS_. Name the database and create a password. Click create. Hover over the database and click **Start**. After it has been activated you will see a green circle next to the database name. Hover again over the database and click `Open Neo4j Browser`.

**Save your password in the .env file.**

- Python >= v3.9 Interpreter.

# Configure tools

First cd to the directory where requirements.txt is located.

Create local env:

    python3 -m venv venv
    source venv/bin/activate

Install requirements

    pip install --upgrade pip
    pip install -r requirements.txt

Add your credentials from Clarify in the same directory. For more information click [here](https://docs.clarify.io/users/admin/integrations/credentials) and [here](https://colab.research.google.com/github/clarify/data-science-tutorials/blob/main/tutorials/Introduction.ipynb#credentials).

## Aquagraph visualization in arrows

1. Save the credentials `clarify-credentials.json` in the main folder
2. Run the script `python process_items.py`

- In the script you can define how many items to retrieve by changing the variable `n_items`, the number of created batches by changing the variable `n_batches` and the number of (random) initial connections between batch and items via the variable `connect_one_in_each`.

3. Copy the content of the output file `result.json` to arrows.app by importing it.

## How to run the API

1. Make sure the Neo4j database is activated.
2. cd to aquagraph_clarify
3. run

> uvicorn main:app --port 8080 --reload

4. Go to http://localhost:8080/docs
5. In the Neo4j Desktop run `match(n) return n`

For now your database is empty. To add data, go to the arrows app and `export` the data as `Cypher` (click on the Create button and `Copy to clipboard`). Paste the content to a cell in Neo4j Browser and run it. Run `match(n) return n` to see your graph.

# Note

Feel free to make your own changes in the graph, export data and matadata from Clarify using our [Python SDK package](https://pypi.org/project/pyclarify/). You can also add or change post calls in the API, create querys and make opperations on the database.
