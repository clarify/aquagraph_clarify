from pydantic import BaseModel

# example
class NodeModel(BaseModel):
    label: str
    propertry_name: str
    propertry_value: str