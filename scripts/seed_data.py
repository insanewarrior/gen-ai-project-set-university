#!/usr/bin/env python3
"""
Seed realistic training sessions into DynamoDB local for all three dev users.

  test-user-free       →  5 sessions  (grip only)           → "low confidence" AI responses
  test-user-onboarding → 12 sessions  (grip + armwrestling)  → "medium confidence"
  test-user-premium    → 60 sessions  (all sports, patterns)  → "high confidence" + trend detection

Usage:
  python scripts/seed_data.py
  python scripts/seed_data.py --endpoint http://localhost:8000
  python scripts/seed_data.py --clear   # wipe existing seed data first
"""

import argparse
import os
import sys
import uuid
from datetime import date, timedelta
from decimal import Decimal

import boto3

ENDPOINT = os.getenv("DYNAMODB_ENDPOINT", "http://localhost:8000")
REGION = os.getenv("AWS_REGION", "us-east-1")
TABLE = os.getenv("SESSIONS_TABLE_NAME", "Sessions")


def get_table(endpoint: str):
    dynamodb = boto3.resource(
        "dynamodb",
        region_name=REGION,
        endpoint_url=endpoint,
        aws_access_key_id="fake",
        aws_secret_access_key="fake",
    )
    return dynamodb.Table(TABLE)


def to_decimal(obj):
    if isinstance(obj, list):
        return [to_decimal(i) for i in obj]
    if isinstance(obj, dict):
        return {k: to_decimal(v) for k, v in obj.items()}
    if isinstance(obj, float):
        return Decimal(str(obj))
    return obj


def days_ago(n: int) -> str:
    return (date.today() - timedelta(days=n)).isoformat()


def make_session(user_id: str, session_date: str, sport: str, exercises: list, notes: str = None) -> dict:
    session_id = str(uuid.uuid4())
    sk = f"{session_date}#{session_id}"
    item = {
        "userId": user_id,
        "sk": sk,
        "sessionId": session_id,
        "sessionDate": session_date,
        "sport": sport,
        "exercises": to_decimal(exercises),
        "createdAt": f"{session_date}T10:00:00Z",
    }
    if notes:
        item["notes"] = notes
    return item


def sets_of(weight: float, reps: int, rpe: float, count: int) -> list:
    return [{"setNumber": i + 1, "weight": weight, "reps": reps, "rpe": rpe} for i in range(count)]


# ---------------------------------------------------------------------------
# SESSION POOLS
# ---------------------------------------------------------------------------

def sessions_free_user() -> list:
    """5 grip sessions — just getting started, low data confidence."""
    return [
        make_session("test-user-free", days_ago(28), "grip", [
            {"exerciseId": "grip-gripper-close", "exerciseName": "Gripper Close", "sportType": "grip",
             "sets": sets_of(60.0, 5, 7.0, 3)},
        ]),
        make_session("test-user-free", days_ago(21), "grip", [
            {"exerciseId": "grip-gripper-close", "exerciseName": "Gripper Close", "sportType": "grip",
             "sets": sets_of(60.0, 5, 7.5, 3)},
            {"exerciseId": "grip-hub-lift", "exerciseName": "Hub Lift", "sportType": "grip",
             "sets": sets_of(20.0, 3, 7.0, 2)},
        ]),
        make_session("test-user-free", days_ago(14), "grip", [
            {"exerciseId": "grip-gripper-close", "exerciseName": "Gripper Close", "sportType": "grip",
             "sets": sets_of(65.0, 5, 8.0, 3)},
        ]),
        make_session("test-user-free", days_ago(7), "grip", [
            {"exerciseId": "grip-gripper-close", "exerciseName": "Gripper Close", "sportType": "grip",
             "sets": sets_of(65.0, 5, 8.5, 3)},
            {"exerciseId": "grip-pinch-block", "exerciseName": "Pinch Block", "sportType": "grip",
             "sets": sets_of(15.0, 5, 7.0, 3)},
        ]),
        make_session("test-user-free", days_ago(2), "grip", [
            {"exerciseId": "grip-gripper-close", "exerciseName": "Gripper Close", "sportType": "grip",
             "sets": sets_of(70.0, 5, 9.0, 3)},
        ], notes="Felt strong today"),
    ]


def sessions_onboarding_user() -> list:
    """12 sessions across grip + armwrestling — medium confidence."""
    sessions = []

    # Grip block — 8 sessions
    grip_data = [
        (55, 5, 6.5, 3), (55, 5, 7.0, 3), (60, 5, 7.0, 3), (60, 5, 7.5, 4),
        (65, 4, 8.0, 3), (65, 4, 8.5, 3), (70, 3, 8.5, 3), (70, 3, 9.0, 3),
    ]
    for i, (w, r, rpe, s) in enumerate(grip_data):
        sessions.append(make_session("test-user-onboarding", days_ago(55 - i * 6), "grip", [
            {"exerciseId": "grip-gripper-close", "exerciseName": "Gripper Close", "sportType": "grip",
             "sets": sets_of(float(w), r, rpe, s)},
            {"exerciseId": "grip-hub-lift", "exerciseName": "Hub Lift", "sportType": "grip",
             "sets": sets_of(float(w // 3), r, rpe - 1.0, 2)},
        ]))

    # Armwrestling — 4 sessions
    aw_data = [
        (20, 5, 7.0, 3), (20, 5, 7.5, 3), (22, 5, 7.5, 3), (22, 5, 8.0, 3),
    ]
    for i, (w, r, rpe, s) in enumerate(aw_data):
        sessions.append(make_session("test-user-onboarding", days_ago(22 - i * 5), "armwrestling", [
            {"exerciseId": "aw-pronation", "exerciseName": "Pronation", "sportType": "armwrestling",
             "sets": sets_of(float(w), r, rpe, s)},
            {"exerciseId": "aw-hook", "exerciseName": "Hook", "sportType": "armwrestling",
             "sets": sets_of(float(w - 5), r, rpe - 0.5, s)},
        ]))

    return sessions


def sessions_premium_user() -> list:
    """
    60 sessions over ~5 months — all three sports, realistic progression with:
    - Clear gripper close volume increase then RPE plateau (stall pattern)
    - Powerlifting peaking cycle
    - Cross-sport fatigue visible in notes
    """
    sessions = []

    # ── GRIP: 25 sessions over 24 weeks, progressive load then stall ──────────
    grip_plan = [
        # (days_ago, weight, reps, rpe, set_count, notes)
        (168, 60, 5, 6.5, 3, None),
        (161, 60, 5, 7.0, 3, None),
        (154, 65, 5, 7.0, 3, None),
        (147, 65, 5, 7.5, 4, None),
        (140, 70, 5, 7.5, 4, None),
        (133, 70, 5, 8.0, 4, None),
        (126, 72, 4, 8.0, 4, None),
        (119, 72, 4, 8.5, 4, None),
        (112, 75, 4, 8.0, 4, None),  # deload
        (105, 75, 4, 8.5, 5, None),
        (98,  78, 4, 8.5, 5, None),
        (91,  78, 4, 9.0, 5, None),
        (84,  80, 3, 8.5, 5, None),
        (77,  80, 3, 9.0, 5, None),
        (70,  80, 3, 9.5, 5, "Grip felt sticky"),
        (63,  80, 3, 9.5, 5, "Struggled to hit depth"),
        (56,  80, 3, 9.5, 6, "No improvement — same weight"),
        (49,  80, 3, 10.0, 6, "Maxed out, couldn't progress"),
        (42,  80, 3, 10.0, 6, "Felt tired"),
        (35,  80, 3, 10.0, 6, "Felt tired"),
        (28,  75, 3, 8.0, 4, "Deload week — reducing load"),
        (21,  75, 4, 8.0, 4, None),
        (14,  82, 3, 8.5, 5, "Back to heavy — feeling fresh"),
        (7,   82, 3, 9.0, 5, None),
        (2,   85, 3, 9.0, 5, "New PR attempt next week"),
    ]
    for days, w, r, rpe, s, notes in grip_plan:
        sessions.append(make_session("test-user-premium", days_ago(days), "grip", [
            {"exerciseId": "grip-gripper-close", "exerciseName": "Gripper Close", "sportType": "grip",
             "sets": sets_of(float(w), r, float(rpe), s)},
            {"exerciseId": "grip-pinch-block", "exerciseName": "Pinch Block", "sportType": "grip",
             "sets": sets_of(float(w // 4), r, float(rpe - 1.0), 3)},
        ], notes))

    # ── ARMWRESTLING: 20 sessions, pronation + hook focus ─────────────────────
    aw_plan = [
        (160, 18, 6, 7.0, 3), (152, 18, 6, 7.5, 3), (144, 20, 6, 7.5, 3),
        (136, 20, 6, 8.0, 3), (128, 22, 5, 8.0, 4), (120, 22, 5, 8.5, 4),
        (112, 24, 5, 8.0, 4), (104, 24, 5, 8.5, 4), (96,  25, 5, 8.5, 4),
        (88,  25, 5, 9.0, 4), (80,  26, 4, 8.5, 5), (72,  26, 4, 9.0, 5),
        (64,  28, 4, 9.0, 5), (56,  28, 4, 9.5, 5), (48,  28, 4, 9.5, 5),
        (40,  25, 4, 8.0, 4), (32,  28, 4, 8.5, 4), (24,  30, 3, 8.5, 5),
        (16,  30, 3, 9.0, 5), (8,   32, 3, 9.0, 5),
    ]
    for days, w, r, rpe, s in aw_plan:
        sessions.append(make_session("test-user-premium", days_ago(days), "armwrestling", [
            {"exerciseId": "aw-pronation", "exerciseName": "Pronation", "sportType": "armwrestling",
             "sets": sets_of(float(w), r, float(rpe), s)},
            {"exerciseId": "aw-hook", "exerciseName": "Hook", "sportType": "armwrestling",
             "sets": sets_of(float(w - 6), r, float(rpe - 0.5), s)},
            {"exerciseId": "aw-side-pressure", "exerciseName": "Side Pressure", "sportType": "armwrestling",
             "sets": sets_of(float(w - 4), r, float(rpe - 1.0), 3)},
        ]))

    # ── POWERLIFTING: 15 sessions, peaking cycle ──────────────────────────────
    pl_plan = [
        (150, 120, 5, 7.0, 5, 80, 5, 7.0, 5, 160, 5, 7.0, 4),
        (143, 125, 5, 7.5, 5, 82, 5, 7.5, 5, 165, 5, 7.5, 4),
        (136, 130, 4, 7.5, 5, 85, 5, 7.5, 5, 170, 4, 7.5, 4),
        (129, 135, 4, 8.0, 4, 87, 4, 8.0, 4, 175, 4, 8.0, 4),
        (122, 140, 3, 8.0, 4, 90, 4, 8.0, 4, 180, 3, 8.0, 4),
        (115, 145, 3, 8.5, 4, 92, 3, 8.5, 4, 185, 3, 8.5, 3),
        (108, 150, 3, 8.5, 3, 95, 3, 8.5, 3, 190, 3, 8.5, 3),
        (101, 155, 2, 9.0, 3, 97, 2, 9.0, 3, 195, 2, 9.0, 3),
        (94,  160, 2, 9.0, 3, 100, 2, 9.0, 3, 200, 2, 9.0, 3),
        (87,  165, 1, 9.5, 3, 102, 1, 9.5, 3, 205, 1, 9.5, 3),
        (80,  120, 5, 7.0, 5, 80,  5, 7.0, 5, 160, 5, 7.0, 4),  # deload
        (73,  145, 3, 8.0, 4, 92,  3, 8.0, 4, 185, 3, 8.0, 3),
        (66,  155, 2, 8.5, 3, 97,  2, 8.5, 3, 195, 2, 8.5, 3),
        (59,  162, 1, 9.0, 3, 102, 1, 9.0, 3, 205, 1, 9.0, 3),
        (52,  167, 1, 9.5, 2, 105, 1, 9.5, 2, 210, 1, 9.5, 2),
    ]
    for row in pl_plan:
        d, sw, sr, srpe, ss, bw, br, brpe, bs, dw, dr, drpe, ds = row
        sessions.append(make_session("test-user-premium", days_ago(d), "powerlifting", [
            {"exerciseId": "pl-squat", "exerciseName": "Squat", "sportType": "powerlifting",
             "sets": sets_of(float(sw), sr, float(srpe), ss)},
            {"exerciseId": "pl-bench-press", "exerciseName": "Bench Press", "sportType": "powerlifting",
             "sets": sets_of(float(bw), br, float(brpe), bs)},
            {"exerciseId": "pl-deadlift", "exerciseName": "Deadlift", "sportType": "powerlifting",
             "sets": sets_of(float(dw), dr, float(drpe), ds)},
        ]))

    return sessions


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------

def clear_user(table, user_id: str):
    response = table.query(
        KeyConditionExpression=boto3.dynamodb.conditions.Key("userId").eq(user_id)
    )
    with table.batch_writer() as batch:
        for item in response["Items"]:
            batch.delete_item(Key={"userId": item["userId"], "sk": item["sk"]})
    print(f"  Cleared existing sessions for {user_id}")


def seed_user(table, user_id: str, sessions: list):
    with table.batch_writer() as batch:
        for s in sessions:
            batch.put_item(Item=s)
    print(f"  ✓  {user_id:30s} → {len(sessions)} sessions")


def main():
    parser = argparse.ArgumentParser(description="Seed dev training sessions into DynamoDB local")
    parser.add_argument("--endpoint", default=ENDPOINT, help="DynamoDB local endpoint")
    parser.add_argument("--clear", action="store_true", help="Delete existing seed data before inserting")
    args = parser.parse_args()

    table = get_table(args.endpoint)

    users = {
        "test-user-free":       sessions_free_user(),
        "test-user-onboarding": sessions_onboarding_user(),
        "test-user-premium":    sessions_premium_user(),
    }

    print(f"\nSeeding {sum(len(v) for v in users.values())} sessions into {TABLE} @ {args.endpoint}\n")

    for user_id, sessions in users.items():
        if args.clear:
            clear_user(table, user_id)
        seed_user(table, user_id, sessions)

    print("\nDone. Switch dev users via  x-dev-user: free | onboarding | premium  header.\n")


if __name__ == "__main__":
    # Allow running from project root without installing the package
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))
    import boto3.dynamodb.conditions  # noqa: F401 — needed after path insert
    main()
