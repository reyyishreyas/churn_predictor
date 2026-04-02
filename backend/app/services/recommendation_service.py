from __future__ import annotations

from app.config import settings


def recommend_actions(reasons: list[str]) -> list[str]:
    actions: list[str] = []
    for reason in reasons:
        actions.extend(settings.action_map.get(reason, []))
    deduped: list[str] = []
    seen: set[str] = set()
    for action in actions:
        if action not in seen:
            seen.add(action)
            deduped.append(action)
    return deduped[:4]
