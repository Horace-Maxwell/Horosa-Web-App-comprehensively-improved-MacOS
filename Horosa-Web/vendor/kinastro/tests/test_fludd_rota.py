from astro.fludd_rota import RotaConfig, compute_reading


def test_fludd_rota_has_lifespan_fields() -> None:
    reading = compute_reading(RotaConfig())

    assert reading.lifespan_score == 59
    assert reading.lifespan_level == "中壽"
    assert "壽命趨勢分數：59/100" in reading.lifespan_text
    assert "壽命趨勢" in reading.summary


def test_fludd_rota_node_modifier_impacts_lifespan_score() -> None:
    north_reading = compute_reading(
        RotaConfig(
            sun=0.0,
            moon=0.0,
            mercury=0.0,
            venus=0.0,
            mars=0.0,
            jupiter=0.0,
            saturn=0.0,
            ascendant=0.0,
            north_node=0.0,
            south_node=180.0,
        )
    )
    south_reading = compute_reading(
        RotaConfig(
            sun=0.0,
            moon=0.0,
            mercury=0.0,
            venus=0.0,
            mars=0.0,
            jupiter=0.0,
            saturn=0.0,
            ascendant=0.0,
            north_node=180.0,
            south_node=0.0,
        )
    )

    assert north_reading.node_modifier_key == "north_node"
    assert south_reading.node_modifier_key == "south_node"
    assert north_reading.lifespan_score == 59
    assert south_reading.lifespan_score == 49
