def build_system_prompt(agents: list[dict]) -> str:
    n_agents = len(agents)
    n_sredstva = len({a["sredstvo"] for a in agents})
    catalog = "\n".join(
        f"[{a['agent_id']}] {a['sredstvo']} — {a['name']}: {a['role']}. {a['expectedBehavior']}"
        for a in agents
    )
    return (
        f"Ты — эксперт по EdTech и образовательным технологиям. У нас есть каталог из "
        f"{n_agents} ИИ-агентов (наших решений), сгруппированных по {n_sredstva} средствам ПМО "
        "(Персонализированная Модель Образования). Тебе дают описание стартапа. "
        "Выбери ОДНОГО агента из каталога, к которому стартап ближе всего по сути и "
        "назначению. Если стартап не подходит ни к одному агенту — верни agent_id 0.\n\n"
        f"КАТАЛОГ АГЕНТОВ:\n{catalog}\n\n"
        "Оцени релевантность лучшего совпадения по шкале 0–10, где 10 — стартап делает "
        "ровно то же, что агент, а 0 — совпадения нет.\n\n"
        "Ответь СТРОГО валидным JSON без markdown-ограждений:\n"
        '{"agent_id": <int 1-44 или 0>, "relevance": <int 0-10>, '
        '"rationale": "<одно предложение по-русски>"}'
    )


def build_user_prompt(row: dict) -> str:
    def g(key: str) -> str:
        value = row.get(key)
        return str(value) if value not in (None, "") else "N/A"

    return (
        f"Название: {g('name')}\n"
        f"Сектора: {g('sectors')}\n"
        f"Описание: {g('description')}\n"
        f"Оценки ПМО (0-10) — траектория: {g('pmo_traj')}, материалы: {g('pmo_mat')}, "
        f"совместность: {g('pmo_collab')}, геймификация: {g('pmo_game')}, "
        f"обратная связь: {g('pmo_feedback')}"
    )
