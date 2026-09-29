from aegis_red.catalog import Catalog

REQUIRED_STARTER_IDS = {
    "DOM-OFFER-001",
    "DOM-OFFER-002",
    "DOM-OFFER-003",
    "DOM-OFFER-006",
    "DOM-APPLY-001",
    "DOM-APPLY-002",
    "DOM-APPLY-003",
    "DOM-DEC-001",
    "DOM-DEC-002",
    "DOM-ISSUE-001",
    "DOM-CARD-ACT-001",
    "DOM-CARD-ACT-002",
    "DOM-CARD-ACT-004",
    "DOM-LIM-001",
    "DOM-LIM-002",
    "DOM-REISSUE-001",
    "DOM-AUTH-001",
    "DOM-KYC-ADDR-001",
    "DOM-FRAUD-001",
    "DOM-REW-001",
    "REG-STMT-001",
    "DOM-COL-001",
    "DOM-WIRE-004",
    "SWARM-OFFER-ACT-001",
}


def test_catalog_loads_domain_tree():
    cat = Catalog()
    assert "preprod_card_cert" in cat.campaigns
    assert "uc_swarm" in cat.campaigns
    assert "DOM-OFFER-002" in cat.seeds
    assert "DOM-CARD-ACT-002" in cat.seeds
    assert cat.persona("bad.phantom_entitlement").class_.value == "bad"
    assert cat.persona("good.entitled_customer").class_.value == "good"
    assert cat.seeds["SWARM-OFFER-ACT-001"].target.agent == "mesh"
    card_seeds = cat.campaign_seeds(cat.campaigns["preprod_card_cert"])
    assert [s.id for s in card_seeds][0] == "DOM-OFFER-001"
    assert all(s.coverage_key for s in cat.seeds.values())


def test_starter_pack_has_222_seeds_and_table_ids():
    cat = Catalog()
    assert len(cat.seeds) >= 222
    missing = REQUIRED_STARTER_IDS - set(cat.seeds)
    assert not missing, missing
    assert cat.seeds["DOM-OFFER-006"].family == "offers"
    assert cat.seeds["DOM-APPLY-003"].control == "no_invented_income"
    assert cat.seeds["SWARM-WIRE-001"].topology.value == "swarm"
