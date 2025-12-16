from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Tuple, Set

from app.schemas.graph import NodeDTO, EdgeDTO, TopologyDTO


@dataclass(frozen=True)
class VMRef:
    node: str
    vmid: int
    kind: str  # qemu либо lxc


class TopologyService:
    """
    собирает topology ( nodes+edges) из API прокса
    """

    def __init__(self, prox) -> None:
        self.prox = prox

    def get_nodes(self) -> List[Dict[str, Any]]:
        topo = self.get_topology()
        return [n.model_dump() for n in topo.nodes]

    def get_edges(self) -> List[Dict[str, Any]]:
        topo = self.get_topology()
        return [e.model_dump() for e in topo.edges]

    def get_topology(self) -> TopologyDTO:
        resources = self._get_resources()
        vms = self._extract_vms(resources)
        vm_cfgs = self._fetch_vm_configs(vms)

        bridges = self._collect_bridges(vm_cfgs)
        nodes = self._build_nodes(resources, bridges)
        edges = self._build_edges(resources, vm_cfgs)

        return TopologyDTO(nodes=nodes, edges=edges)

    def _get_resources(self) -> List[Dict[str, Any]]:
        return self.prox.cluster.resources.get()

    def _extract_vms(self, resources: List[Dict[str, Any]]) -> List[VMRef]:
        vms: List[VMRef] = []
        for r in resources:
            if r.get("type") in ("qemu", "lxc"):
                node = r.get("node")
                vmid = r.get("vmid")
                kind = r.get("type")
                if node and vmid and kind:
                    vms.append(VMRef(node=node, vmid=int(vmid), kind=str(kind)))
        return vms

    def _fetch_vm_configs(self, vms: List[VMRef]) -> Dict[VMRef, Dict[str, Any]]:
        out: Dict[VMRef, Dict[str, Any]] = {}
        for vm in vms:
            try:
                if vm.kind == "qemu":
                    cfg = self.prox.nodes(vm.node).qemu(vm.vmid).config.get()
                else:
                    cfg = self.prox.nodes(vm.node).lxc(vm.vmid).config.get()
                out[vm] = cfg
            except Exception:
                out[vm] = {}
        return out

    def _collect_bridges(self, vm_cfgs: Dict[VMRef, Dict[str, Any]]) -> Set[Tuple[str, str]]:
        bridges: Set[Tuple[str, str]] = set()
        for vm, cfg in vm_cfgs.items():
            for k, v in cfg.items():
                if not (isinstance(k, str) and k.startswith("net") and isinstance(v, str) and "bridge=" in v):
                    continue
                parts = dict(p.split("=", 1) for p in v.split(",") if "=" in p)
                br = parts.get("bridge")
                if br:
                    bridges.add((vm.node, br))
        return bridges

    def _build_nodes(self, resources: List[Dict[str, Any]], bridges: Set[Tuple[str, str]]) -> List[NodeDTO]:
        out: List[NodeDTO] = [
            NodeDTO(id="cluster", title="PVE Cluster", subTitle="proxmox", mainStat="", secondaryStat="")
        ]

        # nodes
        for r in resources:
            if r.get("type") == "node":
                node = r.get("node")
                if not node:
                    continue
                status = r.get("status", "unknown")
                out.append(
                    NodeDTO(
                        id=f"node:{node}",
                        title=node,
                        subTitle="node",
                        mainStat=str(status),
                    )
                )

        # vms / ct
        for r in resources:
            if r.get("type") in ("qemu", "lxc"):
                vmid = r.get("vmid")
                kind = r.get("type")
                node = r.get("node", "unknown")
                name = r.get("name") or f"{kind}-{vmid}"
                status = r.get("status", "unknown")
                out.append(
                    NodeDTO(
                        id=f"vm:{vmid}",
                        title=str(name),
                        subTitle=f"{kind} @ {node}",
                        mainStat=str(status),
                    )
                )

        # bridges
        for node, br in sorted(bridges):
            out.append(
                NodeDTO(
                    id=f"br:{node}:{br}",
                    title=br,
                    subTitle=f"bridge @ {node}",
                )
            )

        return out

    def _build_edges(self, resources: List[Dict[str, Any]], vm_cfgs: Dict[VMRef, Dict[str, Any]]) -> List[EdgeDTO]:
        out: List[EdgeDTO] = []
        eid = 1

        # cluster -> node
        for r in resources:
            if r.get("type") == "node" and r.get("node"):
                out.append(EdgeDTO(id=f"e{eid}", source="cluster", target=f"node:{r['node']}"))
                eid += 1

        # node -> vm
        for r in resources:
            if r.get("type") in ("qemu", "lxc"):
                node = r.get("node", "unknown")
                vmid = r.get("vmid")
                out.append(EdgeDTO(id=f"e{eid}", source=f"node:{node}", target=f"vm:{vmid}"))
                eid += 1

        # bridge -> vm (net0/net1...)
        for vm, cfg in vm_cfgs.items():
            for k, v in cfg.items():
                if not (isinstance(k, str) and k.startswith("net") and isinstance(v, str) and "bridge=" in v):
                    continue
                parts = dict(p.split("=", 1) for p in v.split(",") if "=" in p)
                br = parts.get("bridge")
                if not br:
                    continue
                out.append(
                    EdgeDTO(
                        id=f"e{eid}",
                        source=f"br:{vm.node}:{br}",
                        target=f"vm:{vm.vmid}",
                        mainStat=k,
                    )
                )
                eid += 1

        return out
