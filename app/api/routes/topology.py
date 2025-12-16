from fastapi import APIRouter, Depends
from app.core.pve_client import get_proxmox
from app.schemas.graph import TopologyDTO
from app.services.topology_service import TopologyService

router = APIRouter(tags=["topology"])

@router.get("/nodes")
def nodes(prox=Depends(get_proxmox)):
    svc = TopologyService(prox)
    return svc.get_nodes()

@router.get("/edges")
def edges(prox=Depends(get_proxmox)):
    svc = TopologyService(prox)
    return svc.get_edges()

@router.get("/topology", response_model=TopologyDTO)
def topology(prox=Depends(get_proxmox)):
    svc = TopologyService(prox)
    return svc.get_topology()