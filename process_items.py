import models
import json
import pyclarify
import random

n_batches = 2
n_items = 50
connect_one_in_each=5

def select_first(lst):
    if len(lst)>0:
        return lst[0]

def select_site_unit(item):
    data = None
    if 'site' in item.labels:
        site=select_first(item.labels['site'])
        if 'unit_name' in item.labels:
            unit=select_first(item.labels['unit_name'])
            data=(site,unit)
        else:
            data=None
    return data

## load items
client = pyclarify.ClarifyClient("clarify-credentials.json")
response = client.select_items_metadata(limit=n_items )
item_ids = list(response.result.items.keys())


## process items to clean the ones without location information
id_loc_map= {item:select_site_unit(response.result.items[item]) for item in response.result.items }
id_loc_map={key:id_loc_map[key] for key in id_loc_map if id_loc_map[key] is not None and id_loc_map[key]!=(None,None)}

### generate arrows graph with location and items metadata

graph_factory=models.arrows.GraphFactory()

## add list of batches
for i in range(n_batches):
    batch_id = f"batch_{i}"
    graph_factory.create_node(batch_id, caption=batch_id, labels=["batch"], style={"node-color": "#dbdf00"})

graph_factory.new_collection_positions()

for item_id in id_loc_map:
    metadata = response.result.items[item_id]
    graph_factory.create_node(item_id, caption=metadata.name, labels=["item"], style={"node-color": "#fcdc00", "radius": 25})

## add new row for containers
graph_factory.new_collection_positions()
for item_id in id_loc_map:
    if id_loc_map[item_id] is not None:
        loc2 = id_loc_map[item_id][1]
        graph_factory.create_node(loc2, caption=loc2, labels=["container"], style={"node-color": "#73d8ff", "caption-color": "#194d33"})

## add new row for sites
graph_factory.new_collection_positions()
for item_id in id_loc_map:
    if id_loc_map[item_id] is not None:
        loc1 = id_loc_map[item_id][0]
        graph_factory.create_node(loc1, caption=loc1, labels=["site"], style={"node-color": "#fe9200", "border-color": "#fcdc00"})

## add edges
for item_id in id_loc_map:
    graph_factory.connect(item_id,loc2,type="located_in")
    random_batch = random.randrange(0,n_batches)
    batch_id = f"batch_{random_batch}"
    if random.randrange(0,connect_one_in_each)==0:
        graph_factory.connect(batch_id, item_id,type="observed_by", properties={"from":"t1","to":"t2"})
    if id_loc_map[item_id] is not None:
        loc1 = id_loc_map[item_id][0]
        loc2 = id_loc_map[item_id][1]
        graph_factory.connect(loc2,loc1,type="located_at")


## save result in file
print("printing to file")
graph = graph_factory.gen_graph()
with open("result.json", "w+") as f:
    data = graph.json(ensure_ascii=False)
    f.write(data)