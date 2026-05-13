# Scenario Map

Scenarios mirror the agent-under-test package names under `src/`. Every
scenario directory contains the same six files so commands are predictable
across reference agents and participant agents.

| Agent Package | Scenario Directory |
|---------------|--------------------|
| `src/agent_under_test/` | `scenarios/agent_under_test/` |
| `src/agent_under_test_codex/` | `scenarios/agent_under_test_codex/` |
| `src/agent_under_test_codex_planner/` | `scenarios/agent_under_test_codex_planner/` |
| `src/agent_under_test_codex_python/` | `scenarios/agent_under_test_codex_python/` |

| Scenario File | Mode | Task Selection |
|---------------|------|----------------|
| `local_smoke.toml` | Local Python | Train split, one task from each task type, one trial |
| `local_test_set.toml` | Local Python | Test split, all tasks from each task type, three trials |
| `local_docker_smoke.toml` | Docker local build | Train split, one task from each task type, one trial |
| `local_docker_test_set.toml` | Docker local build | Test split, all tasks from each task type, three trials |
| `ghcr_smoke.toml` | Docker published image | Train split, one task from each task type, one trial |
| `ghcr_test_set.toml` | Docker published image | Test split, all tasks from each task type, three trials |

Generate Docker Compose from any `local_docker_*.toml` or `ghcr_*.toml` file:

```bash
uv run python generate_compose.py --scenario scenarios/agent_under_test/local_docker_smoke.toml
docker compose --env-file .env -f scenarios/agent_under_test/docker-compose.yml up --abort-on-container-exit
```
