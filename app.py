import os
from fastapi import FastAPI
from proxmoxer import ProxmoxAPI

app = FastAPI()

def pve():
    host = os.environ["PVE_HOST"]
    user = os.environ["PVE_USER"]
    token_name = os.environ["PVE_TOKEN_NAME"]
    token_value = os.environ["PVE_TOKEN_VALUE"]
    verify_ssl = os.environ.get("PVE_VERIFY_SSL", "false").lower() == "true"

    return ProxmoxAPI(
        host,
        user=user,
        token_name=token_name,
        token_value=token_value,
        verify_ssl=verify_ssl,
        timeout=10,
    )

@app.get("/nodes")
def nodes():
    prox = pve()
    resources = prox.cluster.resources.get()

    out = [{
        "id": "cluster",
        "title": "PVE Cluster",
        "subTitle": "proxmox",
        "mainStat": "",
        "secondaryStat": "",
    }]

    # nodes
    for r in resources:
        if r.get("type") == "node":
            nid = f"node:{r['node']}"
            status = r.get("status", "unknown")
            out.append({
                "id": nid,
                "title": r["node"],
                "subTitle": "node",
                "mainStat": status,
            })

    # vms/ct
    for r in resources:
        if r.get("type") in ("qemu", "lxc"):
            vmid = r.get("vmid")
            kind = r.get("type")
            name = r.get("name", f"{kind}-{vmid}")
            status = r.get("status", "unknown")
            node = r.get("node", "unknown")
            out.append({
                "id": f"vm:{vmid}",
                "title": name,
                "subTitle": f"{kind} @ {node}",
                "mainStat": status,
            })

    # bridges (vmbrX) из конфигов ВМ
    bridges = set()
    for r in resources:
        t = r.get("type")
        if t not in ("qemu", "lxc"):
            continue
        node = r.get("node")
        vmid = r.get("vmid")
        cfg = prox.nodes(node).qemu(vmid).config.get() if t == "qemu" else prox.nodes(node).lxc(vmid).config.get()
        for k, v in cfg.items():
            if k.startswith("net") and isinstance(v, str) and "bridge=" in v:
                parts = dict(p.split("=", 1) for p in v.split(",") if "=" in p)
                br = parts.get("bridge")
                if br:
                    bridges.add((node, br))

    for node, br in sorted(bridges):
        out.append({
            "id": f"br:{node}:{br}",
            "title": br,
            "subTitle": f"bridge @ {node}",
        })

    return out

@app.get("/edges")
def edges():
    prox = pve()
    resources = prox.cluster.resources.get()

    out = []
    eid = 1

    # cluster -> node
    for r in resources:
        if r.get("type") == "node":
            out.append({"id": f"e{eid}", "source": "cluster", "target": f"node:{r['node']}"})
            eid += 1

    # node -> vm
    for r in resources:
        if r.get("type") in ("qemu", "lxc"):
            node = r.get("node", "unknown")
            vmid = r.get("vmid")
            out.append({"id": f"e{eid}", "source": f"node:{node}", "target": f"vm:{vmid}"})
            eid += 1

    # bridge -> vm (net0/net1...)
    for r in resources:
        t = r.get("type")
        if t not in ("qemu", "lxc"):
            continue
        node = r.get("node")
        vmid = r.get("vmid")
        cfg = prox.nodes(node).qemu(vmid).config.get() if t == "qemu" else prox.nodes(node).lxc(vmid).config.get()

        for k, v in cfg.items():
            if k.startswith("net") and isinstance(v, str) and "bridge=" in v:
                parts = dict(p.split("=", 1) for p in v.split(",") if "=" in p)
                br = parts.get("bridge")
                if br:
                    out.append({
                        "id": f"e{eid}",
                        "source": f"br:{node}:{br}",
                        "target": f"vm:{vmid}",
                        "mainStat": k,
                    })
                    eid += 1

    return out

