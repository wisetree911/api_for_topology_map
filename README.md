# Proxmox Topology API (FastAPI)

Мини-сервис на FastAPI, который подключается к **Proxmox VE API** и отдаёт **топологию кластера** в удобном для визуализации виде:  
`cluster → nodes → VMs/CTs → bridges (vmbr*)`.

Проект сделан как интеграционный backend: его можно подключить к UI/дашборду (граф) или к внешним системам мониторинга/инвентаризации.

Пример использования: Grafana + плагин Infinity data source + панель Node graph

## Реализовано

- Получает список ресурсов из Proxmox: ноды, машины, контейнеры
- Анализирует сетевые интерфейсы и собирает bridge связи (vmbrX)
- API:
  - `GET /nodes` — список узлов графа
  - `GET /edges` — список связей графа
  - `GET /topology` — полная информация (обьединение обеих ручек)

## Технологии

- Python 3.12
- FastAPI + Uvicorn
- proxmoxer (Proxmox API client)
- Pydantic / pydantic-settings
- Docker / Docker Compose