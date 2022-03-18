# The json file (result.json) produced from this file is been used in the API.

import models
import json
import pyclarify
import random

n_batches = 2
n_items = 50
iterations = 10


def select_first(lst):
    if len(lst) > 0:
        return lst[0]


def select_site_unit(item):
    data = None
    if "site" in item.labels:
        site = select_first(item.labels["site"])
        if "unit_name" in item.labels:
            unit = select_first(item.labels["unit_name"])
            data = (site, unit)
        else:
            data = None
    return data


## load items
client = pyclarify.ClarifyClient("clarify-credentials.json")
response = client.select_items_metadata(limit=n_items)
item_ids = list(response.result.items.keys())


## process items to clean the ones without location information
id_loc_map = {
    item: select_site_unit(response.result.items[item])
    for item in response.result.items
}
id_loc_map = {
    key: id_loc_map[key]
    for key in id_loc_map
    if id_loc_map[key] is not None and id_loc_map[key] != (None, None)
}

### generate arrows graph with location and items metadata

graph_factory = models.arrows.GraphFactory()

## add list of batches
for i in range(n_batches):
    for int in range(iterations):
        batch_id = f"batch_{i}{int}"
        print(f"{i}{i}{i}_{int}{0}{i+1}")
        graph_factory.create_node(
            batch_id,
            labels=["Batch"],
            properties={"batchID": f"{i}{i}{i}_{int}{0}{i+1}"},
            style={"node-color": "#dbdf00"},
        )


graph_factory.new_collection_positions()

for item_id in id_loc_map:

    metadata = response.result.items[item_id]
    graph_factory.create_node(
        item_id,
        labels=["Item"],
        properties={"itemID": f"{item_id}", "name": metadata.name},
        style={"node-color": "#fcdc00", "radius": 25},
    )

## add new row for containers
graph_factory.new_collection_positions()
for item_id in id_loc_map:

    if id_loc_map[item_id] is not None:
        loc2 = id_loc_map[item_id][1]
        graph_factory.create_node(
            loc2,
            labels=["Enhet"],
            properties={"location": loc2},
            style={"node-color": "#73d8ff", "caption-color": "#194d33"},
        )

## add new row for sites
graph_factory.new_collection_positions()
for item_id in id_loc_map:
    if id_loc_map[item_id] is not None:
        loc1 = id_loc_map[item_id][0]
        graph_factory.create_node(
            loc1,
            labels=["Lokalitet"],
            properties={"site": loc1},
            style={"node-color": "#fe9200", "border-color": "#fcdc00"},
        )

## add edges
for item_id in id_loc_map:
    graph_factory.connect(item_id, loc2, type="Observed_by")
    random_batch = random.randrange(0, n_batches)
    for int in range(iterations):
        batch_id = f"batch_{random_batch}{int}"
        graph_factory.connect(
            batch_id,
            loc2,
            type="Located_at",
            properties={
                "fromDate": "2021-01-01T13:00:00Z",
                "toDate": "2021-01-03T13:00:00Z",
            },
        )

    if id_loc_map[item_id] is not None:
        loc1 = id_loc_map[item_id][0]
        loc2 = id_loc_map[item_id][1]
        graph_factory.connect(loc2, loc1, type="Container_in")


## save result in file
print("printing to file")
graph = graph_factory.gen_graph()
with open("result.json", "w+") as f:
    data = graph.json(ensure_ascii=False)
    f.write(data)
