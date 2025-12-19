# Proxmox Topology API (FastAPI)

Мини-сервис на FastAPI, который подключается к **Proxmox VE API** и отдаёт **топологию кластера** в удобном для визуализации виде:  
`cluster → nodes → VMs/CTs → bridges (vmbr*)`.

Проект сделан как “интеграционный backend”: его можно подключить к UI/дашборду (граф) или к внешним системам мониторинга/инвентаризации.


## Что умеет

- Получает список ресурсов из Proxmox: ноды, VM (QEMU), CT (LXC)
- Анализирует сетевые интерфейсы VM/CT и собирает bridge связи (`bridge=vmbrX`)
- Отдаёт:
  - `GET /nodes` — список узлов графа
  - `GET /edges` — список связей графа
  - `GET /topology` — всё сразу `{ nodes, edges }`
- Swagger UI: `GET /docs`


## Технологии

- Python 3.12
- FastAPI + Uvicorn
- proxmoxer (Proxmox API client)
- Pydantic / pydantic-settings
- Docker / Docker Compose