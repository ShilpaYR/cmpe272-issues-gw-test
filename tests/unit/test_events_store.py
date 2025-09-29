# tests/unit/test_events_store.py
from src.models.events_store import save_event, last_events

def test_events_store_limit_and_ordering():
    # insert 10 events (d0 ... d9)
    for i in range(10):
        save_event({
            "id": f"d{i}:issues:opened",
            "event": "issues",
            "action": "opened",
            "issue_number": i,
            "timestamp": str(i)
        })

    out = last_events(3)
    assert len(out) == 3
    # EXPECT newest-first: d9, d8, d7
    assert out[0]["id"].startswith("d9")
    assert out[1]["id"].startswith("d8")
    assert out[2]["id"].startswith("d7")

