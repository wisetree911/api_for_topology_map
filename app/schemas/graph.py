from typing import Optional, List
from pydantic import BaseModel

class NodeDTO(BaseModel):
    id: str
    title: str
    subTitle: Optional[str] = None
    mainStat: Optional[str] = None
    secondaryStat: Optional[str] = None

class EdgeDTO(BaseModel):
    id: str
    source: str
    target: str
    mainStat: Optional[str] = None

class TopologyDTO(BaseModel):
    nodes: List[NodeDTO]
    edges: List[EdgeDTO]