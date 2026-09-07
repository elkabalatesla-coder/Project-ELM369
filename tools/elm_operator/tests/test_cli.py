from __future__ import annotations

from tools.elm_operator.cli import main
from tools.elm_operator.provenance import PRIMARY_ID, COMPANION_ID, envelope


def test_envelope_dual_id():
    env = envelope({"ping": True})
    assert env["spine"] == "operator-spine-v0.1"
    assert env["dual_id"]["primary"] == PRIMARY_ID
    assert env["dual_id"]["companion"] == COMPANION_ID
    assert env["location"]["postal_code"] == "46902"
    assert env["data"]["ping"] is True


def test_stamp_exits_zero():
    assert main(["stamp"]) == 0
