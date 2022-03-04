from pydantic import BaseModel
from pydantic.fields import Optional
from typing import List, Union, Dict, Literal
from datetime import datetime
import random
import uuid
import hashlib

StyleProperty = Literal[
    "font-family",
    "background-color",
    "node-color",
    "border-width",
    "border-color",
    "radius",
    "node-padding",
    "node-margin",
    "outside-position",
    "node-icon-image",
    "node-background-image",
    "icon-position",
    "icon-size",
    "caption-position",
    "caption-max-width",
    "caption-color",
    "caption-font-size",
    "caption-font-weight",
    "label-position",
    "label-display",
    "label-color",
    "label-background-color",
    "label-border-color",
    "label-border-width",
    "label-font-size",
    "label-padding",
    "label-margin",
    "directionality",
    "detail-position",
    "detail-orientation",
    "arrow-width",
    "arrow-color",
    "margin-start",
    "margin-end",
    "margin-peer",
    "attachment-start",
    "attachment-end",
    "relationship-icon-image",
    "type-color",
    "type-background-color",
    "type-border-color",
    "type-border-width",
    "type-font-size",
    "type-padding",
    "property-position",
    "property-alignment",
    "property-color",
    "property-font-size",
    "property-font-weight",
]
StyleField = Dict[StyleProperty, Optional[Union[int, str]]]
PropertyField = Dict[str, Optional[str]]

class Point(BaseModel):
    x: float
    y: float


class ArrowsNode(BaseModel):
    id: str
    position: Point
    caption: str = ""
    labels: Optional[List[str]]
    properties: Optional[PropertyField]={}
    style: Optional[StyleField]={}


class ArrowsRelationship(BaseModel):
    id: str
    type: str = ""
    fromId: str
    toId: str
    properties: Optional[PropertyField]={}
    style: Optional[StyleField]={}


class ArrowGraph(BaseModel):
    style: Optional[StyleField]={}
    nodes: List[ArrowsNode]=[]
    relationships: Optional[List[ArrowsRelationship]]=[]


class GraphFactory:
    def __init__(self):
        self.posx=0.0
        self.posy=0.0
        self.maxy=0.0
        self.nodes=dict()
        self.edges=dict()

    def create_node(self,id, caption="", labels={}, properties={}, style={}):
        if id in self.nodes:
            return self.nodes[id]
        else:
            position = Point(x=self.posx,y=self.posy)
            self.maxy=min(self.maxy, self.posy)
            node = ArrowsNode(id=id,position=position,caption=caption,labels=labels,properties=properties, style=style)
            self.nodes.update({id:node})
            self.posx+=50+((-1)**(random.randrange(0,2)))*200.0
            self.posy-=20+((-1)**(random.randrange(0,2)))*200.0
            if random.randrange(0,30)==10:
                self.posx=0.0
                self.posy=self.maxy-200
            return node
    
    def new_collection_positions(self):
        self.posx=0.0
        self.posy=self.maxy-500.0

    def connect(self, from_id, to_id, type="", properties={}, style={}):
        m = hashlib.md5()
        m.update((str(from_id)+str(to_id)).encode('utf-8'))
        edgeid=str(uuid.UUID(m.hexdigest()))
        if edgeid in self.edges:
            return self.edges[edgeid]
        else:
            relation=ArrowsRelationship(id=edgeid, fromId=from_id, toId=to_id,type=type, properties=properties, style=style)
            self.edges.update({edgeid:relation})
            return relation

    def gen_graph(self, style={}):
        nodes = list(self.nodes.values())
        edges = list(self.edges.values())
        graph = ArrowGraph(style=style, nodes=nodes, relationships=edges)
        return graph


