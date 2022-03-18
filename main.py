from fastapi import FastAPI
import os
from dotenv import load_dotenv
from neo4j import GraphDatabase

# from models.nodes import NodeModel

load_dotenv()
uri = os.getenv("NEO4J_URI")
user = os.getenv("NEO4J_USERNAME")
pwd = os.getenv("NEO4J_PASSWORD")


def connection():
    driver = GraphDatabase.driver(uri=uri, auth=(user, pwd))
    return driver


class Neo4jNodes:
    def __init__(self, driver):
        self.driver = driver

    def create_batch_node(self, batchId):
        def create_batch(tx):
            cypher = """
                create (n :Batch {batchID: $batchId})
                return n as node
            """

            results = tx.run(cypher, batchId=batchId)
            data = [{"Node": row["node"]} for row in results]
            return {"response": data}

        with self.driver.session() as session:
            return session.write_transaction(create_batch)

    def add_item_contraints(
        self,
    ):
        def add_item_contraints(tx):
            cypher = """
                create constraint uniqueItemId
                on (n :Item) assert n.itemID is unique 
            """
            tx.run(cypher)
            return {"response": "Added 1 constraint in item node -> Unique itemID"}

        with self.driver.session() as session:
            return session.write_transaction(add_item_contraints)

    def add_batch_contraints(
        self,
    ):
        def add_batch_contraints(tx):
            cypher = """
                create constraint uniqueBatchId
                on (n :Batch) assert n.batchID is unique 
            """
            tx.run(cypher)
            return {"response": "Added 1 constraint in batch node -> Unique batchID"}

        with self.driver.session() as session:
            return session.write_transaction(add_batch_contraints)

    def add_relationship_contraints(
        self,
    ):
        def add_relationship_contraints(tx):
            cypher = """
                create constraint date
                on ()-[r:Transported]-() assert exists(r.date) 
            """
            tx.run(cypher)
            return {
                "response": "Added 1 constraint on Transported relationship -> Must have date property"
            }

        with self.driver.session() as session:
            return session.write_transaction(add_relationship_contraints)

    def see_all_contraints(
        self,
    ):
        def see_all_contraints(tx):
            cypher = """
                call db.constraints
            """
            results = tx.run(cypher)
            data = [{row["name"]: row["description"]} for row in results]
            return {"response": data}

        with self.driver.session() as session:
            return session.write_transaction(see_all_contraints)

    def delete_one_contraints(self, constraint_name):
        def delete_one_contraints(tx):
            cypher = """
                drop constraint {0}
            """.format(
                constraint_name
            )

            tx.run(cypher, {"constraint_name": constraint_name})
            return {"response": "Removed 1 constaint: " + constraint_name}

        with self.driver.session() as session:
            return session.write_transaction(delete_one_contraints)

    def batch_path_locations(self, batchIDs):
        def get_locations(tx):
            cypher = """
                with $batchIDs  as batchids
                match(batch:Batch)
                where any (id in batchids where batch.batchID = id)
                match (batch)-[r:Located_at]-(e)-[:Container_in]->(l)
                return [r.fromDate, r.toDate, e.location, l.site] as batch, batch.batchID as id
            """

            results = tx.run(cypher, {"batchIDs": batchIDs})
            data = [{row["id"]: row["batch"]} for row in results]
            return {"response": data}

        with self.driver.session() as session:
            return session.write_transaction(get_locations)

    def batches_paths_common_locations(self, batchIDs1, batchIDs2):
        def get_common_locations(tx, batchIDs1, batchIDs2):

            cypher = """
                with $batchIDs1 as b1,  $batchIDs2 as b2
                match p1 = (batch1 :Batch)-[:Located_at]-(e:Enhet)-[]-(:Lokalitet)
                match p2 = (batch2 :Batch)-[:Located_at]-(e)-[]-(:Lokalitet)
                where any (id1 in b1 where batch1.batchID = id1) and any(id2 in b2 where batch2.batchID = id2)
                return [nodes(p1),relationships(p1)] as path1, [nodes(p2), relationships(p2) ] as path2
            """
            result = tx.run(cypher, batchIDs1=batchIDs1, batchIDs2=batchIDs2)
            data1 = []
            data2 = []
            for row in result:
                data1.append(row["path1"])
                data2.append(row["path2"])
            return {"response": {"1": data1, "2": data2}}

        with self.driver.session() as session:
            return session.read_transaction(get_common_locations, batchIDs1, batchIDs2)

    def batch_all_locations(self, batchid):
        def get_all_locations(tx):
            cypher = """
                match p =(n :Batch)-[]-(:Enhet)-[]-(:Lokalitet)
                where n.batchID starts with "{0}"
                return [p] as p
            """.format(
                batchid
            )

            results = tx.run(cypher, {"batchID": batchid})

            data = [{"p": row["p"]} for row in results]
            return {"response": data}

        with self.driver.session() as session:
            return session.write_transaction(get_all_locations)

    def find_shortest_path(self, start_batchID, end_batchID, path_id):
        results = []
        path_id = "^" + path_id + ".*"
        cypher = """
            MATCH (b1:Batch {batchID: $start_batchID} ),
                    (b2:Batch {batchID: $end_batchID} ),
                    p = shortestPath((b1)-[*]->(b2))
            WHERE any(r IN nodes(p) WHERE r.batchID =~ $path_id)
            return p
        """
        with self.driver.session() as session:
            with session.begin_transaction() as tx:
                for record in tx.run(
                    cypher,
                    start_batchID=start_batchID,
                    end_batchID=end_batchID,
                    path_id=path_id,
                ):
                    relationships = record["p"].relationships
                    nodes = record["p"].nodes

                    path = ""
                    for i in range(len(relationships)):
                        print(nodes[i]["batchID"])
                        print(relationships[i].type)
                        path += "{0}-[{1}]".format(nodes[i], relationships[i])
                    path += nodes[-1]["batchID"]
                    results.append(path)
        return results


app = FastAPI()


@app.post("/create")
def create_batch_node(batchId):
    driver_neo4j = connection()
    nodes = Neo4jNodes(driver_neo4j)
    output = nodes.create_batch_node(batchId)
    return output


@app.post("/add_item_constraint")
def add_item_contraints_on_itemID():
    driver_neo4j = connection()
    nodes = Neo4jNodes(driver_neo4j)
    output = nodes.add_item_contraints()
    return output


@app.post("/add_batch_constraint")
def add_batch_constraint_on_batchID():
    driver_neo4j = connection()
    nodes = Neo4jNodes(driver_neo4j)
    output = nodes.add_batch_contraints()
    return output


@app.post("/add_relationship_contraints")
def add_relationship_contraints_on_Transported():
    driver_neo4j = connection()
    nodes = Neo4jNodes(driver_neo4j)
    output = nodes.add_relationship_contraints()
    return output


@app.post("/see_all_contraints")
def see_all_contraints():
    driver_neo4j = connection()
    nodes = Neo4jNodes(driver_neo4j)
    output = nodes.see_all_contraints()
    return output


@app.post("/delete_one_contraint")
def delete_one_contraint(constraint_name: str):
    driver_neo4j = connection()
    nodes = Neo4jNodes(driver_neo4j)
    output = nodes.delete_one_contraints(constraint_name)
    return output


@app.post("/batch_path_locations")
def batch_path_locations(batchIDs: list = ["111_102", "111_202", "111_302"]):
    driver_neo4j = connection()
    nodes = Neo4jNodes(driver_neo4j)
    output = nodes.batch_path_locations(batchIDs)
    return output


@app.post("/batches_paths_common_locations")
def batches_paths_common_locations(
    batchIDs1: list = ["000_501", "000_301"],
    batchIDs2: list = ["111_602", "111_802", "111_702"],
):
    driver_neo4j = connection()
    nodes = Neo4jNodes(driver_neo4j)
    output = nodes.batches_paths_common_locations(batchIDs1, batchIDs2)
    return output


@app.post("/batch_all_locations")
def batch_all_locations(batchID: str = "000"):
    driver_neo4j = connection()
    nodes = Neo4jNodes(driver_neo4j)
    output = nodes.batch_all_locations(batchID)
    return output


@app.post("/find_shortest_path")
def find_shortest_path(
    start_batchID: str = "000", end_batchID: str = "000_101", path_id: str = "000"
):
    driver_neo4j = connection()
    nodes = Neo4jNodes(driver_neo4j)
    output = nodes.find_shortest_path(start_batchID, end_batchID, path_id)
    return output
