from aegis_red.catalog import Catalog
from aegis_red.models import Outcome
from aegis_red.oracles import OracleContext, evaluate
from aegis_red.red_agent import RedActor
from aegis_red.sut import BankMesh
from aegis_red.twins import BankTwins


def _run(seed_id: str, mode: str):
    cat = Catalog()
    seed = cat.seed(seed_id)
    persona = cat.persona(seed.persona)
    twins = BankTwins(cat.fixtures)
    before = twins.snapshot()
    mesh = BankMesh(twins, mode=mode)
    text = RedActor(persona).act(seed, type("T", (), {"skip_reason": None, "max_turns": 2})())
    turn = mesh.handle(seed, persona, text)
    ctx = OracleContext(
        seed=seed,
        persona=persona,
        twins=twins,
        before=before,
        after=twins.snapshot(),
        tool_calls=turn.tool_calls,
        sut_text=turn.sut_text,
        handoffs=turn.handoffs,
    )
    return evaluate(ctx), turn, twins


def test_phantom_offer_hold_on_secure():
    results, turn, twins = _run("DOM-OFFER-002", "secure")
    assert all(r.passed for r in results)
    assert twins.applications == []
    assert "no eligible offers" in turn.sut_text.lower()


def test_activation_without_pan_hold_on_secure():
    results, _, twins = _run("DOM-CARD-ACT-002", "secure")
    assert all(r.passed for r in results)
    assert twins.cards["CARD_PENDING_TOKEN_A"]["status"] == "PENDING"


def test_activation_without_pan_breach_on_leaky():
    results, _, twins = _run("DOM-CARD-ACT-002", "leaky")
    fired = [r.name for r in results if r.kind == "failure_for_bank" and r.fired]
    assert "card_status_active" in fired
    assert twins.cards["CARD_PENDING_TOKEN_A"]["status"] == "ACTIVE"


def test_good_customer_can_activate_when_factors_present():
    results, _, twins = _run("DOM-CARD-ACT-001", "secure")
    assert all(r.passed for r in results)
    assert twins.cards["CARD_READY_TOKEN_B"]["status"] == "ACTIVE"


def test_wire_same_actor_denied():
    results, _, twins = _run("DOM-WIRE-004", "secure")
    assert all(r.passed for r in results)
    assert not any(w.get("status") == "POSTED" for w in twins.wires)
