from agent_matcher.agents_loader import load_agents


def test_loads_exactly_44_agents():
    agents = load_agents()
    assert len(agents) == 44


def test_agent_ids_are_sequential_1_to_44():
    ids = [a["agent_id"] for a in load_agents()]
    assert ids == list(range(1, 45))


def test_each_agent_has_required_fields():
    for a in load_agents():
        for field in ("name", "sredstvo", "role", "expectedBehavior", "developmentStatus"):
            assert field in a, f"missing {field}"
            assert a[field] is not None, f"null {field}"
