#!/usr/bin/env python3
"""
Play Card - Decision Deck card execution helper.

Loads card definition, logs the play, updates meters.
Does NOT auto-execute steps - AI executes manually.

Usage:
    play_card.py CARD-REG-001 [--context "Promoted OPP-023"]
    play_card.py CARD-GIT-001 --outcome failure
"""

import sys
from pathlib import Path
import yaml

# Import session manager functions
from session_manager import (
    get_session,
    init_session,
    log_card_play,
    update_meters,
)


def get_project_root() -> Path:
    """Find PROJECT_elements root."""
    current = Path(__file__).parent
    while current != current.parent:
        if (current / ".agent").exists():
            return current
        current = current.parent
    return Path.home() / "PROJECTS_all" / "PROJECT_elements"


def load_card(card_id: str) -> dict | None:
    """Load card definition from .agent/deck/."""
    root = get_project_root()
    card_path = root / ".agent" / "deck" / f"{card_id}.yaml"

    if not card_path.exists():
        return None

    with open(card_path) as f:
        return yaml.safe_load(f)


def get_available_cards() -> list[dict]:
    """List all available cards."""
    root = get_project_root()
    deck_dir = root / ".agent" / "deck"
    cards = []

    for card_file in sorted(deck_dir.glob("CARD-*.yaml")):
        try:
            with open(card_file) as f:
                card = yaml.safe_load(f)
                cards.append({
                    "id": card.get("id", card_file.stem),
                    "title": card.get("title", "?"),
                    "phase_gate": card.get("phase_gate", ["ANY"]),
                })
        except Exception:
            pass

    return cards


def play(card_id: str, outcome: str = "success", context: str | None = None) -> dict:
    """
    Play a card: log it and update meters.

    Returns dict with:
    - success: bool
    - card: dict (card definition)
    - meters: dict (new meter values)
    - unlocks: list (cards unlocked by this play)
    - steps: list (steps for AI to execute)
    """
    # Ensure session exists
    session = get_session()
    if not session:
        session = init_session()

    # Load card
    card = load_card(card_id)
    if not card:
        return {
            "success": False,
            "error": f"Card not found: {card_id}",
            "available": [c["id"] for c in get_available_cards()],
        }

    # Log the play
    log_card_play(card_id, outcome, context)

    # Get meter deltas from outcome
    outcomes = card.get("outcomes", {})
    outcome_data = outcomes.get(outcome, outcomes.get("success", {}))
    meter_deltas = outcome_data.get("meters", {})

    # Update meters
    new_meters = {}
    if meter_deltas:
        reason = f"Played {card_id}"
        new_meters = update_meters(meter_deltas, reason)

    # Extract steps for AI to execute
    steps = card.get("steps", [])

    # Extract unlocks
    unlocks = outcome_data.get("unlocks", [])

    return {
        "success": True,
        "card": {
            "id": card.get("id"),
            "title": card.get("title"),
            "description": card.get("description"),
        },
        "meters": new_meters,
        "unlocks": unlocks,
        "steps": [
            {
                "action": s.get("action"),
                "description": s.get("description"),
            }
            for s in steps
        ],
    }


def show_card(card_id: str):
    """Display card details."""
    card = load_card(card_id)
    if not card:
        print(f"Card not found: {card_id}")
        available = get_available_cards()
        print("Available cards:")
        for c in available:
            print(f"  {c['id']}: {c['title']}")
        return

    print(f"\n  CARD: {card.get('id')}")
    print(f"  Title: {card.get('title')}")
    print(f"  Phase: {card.get('phase_gate', ['ANY'])}")
    print()

    if card.get("description"):
        print(f"  {card['description'][:60]}...")
        print()

    steps = card.get("steps", [])
    if steps:
        print("  Steps:")
        for i, s in enumerate(steps, 1):
            print(f"    {i}. {s.get('action', '?')}")
        print()

    outcomes = card.get("outcomes", {}).get("success", {})
    meters = outcomes.get("meters", {})
    if meters:
        print(f"  Meters: ", end="")
        for name, delta in meters.items():
            sign = "+" if delta >= 0 else ""
            print(f"{name}:{sign}{delta} ", end="")
        print()

    unlocks = outcomes.get("unlocks", [])
    if unlocks:
        print(f"  Unlocks: {', '.join(unlocks)}")
    print()


def list_cards():
    """List all available cards."""
    cards = get_available_cards()
    print("\n  DECK")
    print("  " + "-" * 40)
    for c in cards:
        phases = ",".join(c["phase_gate"][:2])
        print(f"  {c['id']:<15} {c['title'][:25]:<25} [{phases}]")
    print()


# === CLI ===


def main():
    if len(sys.argv) < 2:
        print("Usage: play_card.py <card_id> [--context <text>] [--outcome success|failure]")
        print("       play_card.py show <card_id>")
        print("       play_card.py list")
        return

    cmd = sys.argv[1]

    if cmd == "list":
        list_cards()
        return

    if cmd == "show":
        if len(sys.argv) < 3:
            print("Usage: play_card.py show <card_id>")
            return
        show_card(sys.argv[2])
        return

    # Play card
    card_id = cmd
    outcome = "success"
    context = None

    # Parse optional args
    i = 2
    while i < len(sys.argv):
        if sys.argv[i] == "--outcome" and i + 1 < len(sys.argv):
            outcome = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == "--context" and i + 1 < len(sys.argv):
            context = sys.argv[i + 1]
            i += 2
        else:
            i += 1

    result = play(card_id, outcome, context)

    if not result.get("success"):
        print(f"Error: {result.get('error')}")
        if result.get("available"):
            print(f"Available: {', '.join(result['available'][:5])}...")
        return

    card = result.get("card", {})
    print(f"\n  PLAYED: {card.get('id')}")
    print(f"  {card.get('title')}")

    meters = result.get("meters", {})
    if meters:
        print(f"  Meters: f:{meters.get('focus', '?')} r:{meters.get('reliability', '?')} d:{meters.get('debt', '?')}")

    steps = result.get("steps", [])
    if steps:
        print("\n  Steps to execute:")
        for i, s in enumerate(steps, 1):
            print(f"    {i}. {s.get('action')}")

    unlocks = result.get("unlocks", [])
    if unlocks:
        print(f"\n  Unlocked: {', '.join(unlocks)}")

    print()


if __name__ == "__main__":
    main()
