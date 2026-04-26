import csv
import io
from decimal import Decimal


def _to_num(val):
    if val is None:
        return ''
    if isinstance(val, Decimal):
        f = float(val)
        return int(f) if f == int(f) else f
    return val


def generate_csv(sessions: list) -> str:
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['date', 'sport', 'exercise', 'set', 'weight', 'reps', 'rpe', 'notes'])
    for session in sessions:
        session_date = session.get('sessionDate', '')
        sport = session.get('sport', '')
        notes = session.get('notes', '')
        first_set_of_session = True
        for exercise in session.get('exercises', []):
            exercise_name = exercise.get('exerciseName', '')
            for s in exercise.get('sets', []):
                row_notes = notes if first_set_of_session else ''
                first_set_of_session = False
                writer.writerow([
                    session_date,
                    sport,
                    exercise_name,
                    _to_num(s.get('setNumber', '')),
                    _to_num(s.get('weight')),
                    _to_num(s.get('reps')),
                    _to_num(s.get('rpe')),
                    row_notes,
                ])
    return output.getvalue()
