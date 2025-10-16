# algorithms.py

def quicksort_trips(trips):
    """
    Accepts either:
      - a list of DB cursor rows (tuples) in the form (trip_id, trip_duration, trip_distance_km, trip_speed_kmh)
      - a list of dictionaries with a 'trip_duration' or 'duration' key

    Normalizes input to a list of dictionaries with a `trip_duration` (float/int) value and
    returns the list sorted by duration (ascending).
    """
    if not trips:
        return []

    normalized = []
    for t in trips:
        if isinstance(t, dict):
            # prefer explicit keys
            if 'trip_duration' in t:
                dur = t['trip_duration']
            else:
                dur = t.get('duration')

            normalized.append({
                'trip_id': t.get('trip_id'),
                'trip_duration': dur,
                'trip_distance_km': t.get('trip_distance_km'),
                'trip_speed_kmh': t.get('trip_speed_kmh')
            })
        else:
            # assume tuple from cursor: (trip_id, trip_duration, trip_distance_km, trip_speed_kmh)
            try:
                trip_id, trip_duration, trip_distance_km, trip_speed_kmh = t
            except Exception:
                # fallback: try index-based extraction
                trip_id = t[0] if len(t) > 0 else None
                trip_duration = t[1] if len(t) > 1 else None
                trip_distance_km = t[2] if len(t) > 2 else None
                trip_speed_kmh = t[3] if len(t) > 3 else None

            normalized.append({
                'trip_id': trip_id,
                'trip_duration': trip_duration,
                'trip_distance_km': trip_distance_km,
                'trip_speed_kmh': trip_speed_kmh
            })

    # Coerce durations to numeric where possible for reliable sorting
    def _dur_value(item):
        d = item.get('trip_duration')
        if d is None:
            return float('inf')
        try:
            # handle timedelta
            from datetime import timedelta
            if isinstance(d, timedelta):
                return d.total_seconds()
            return float(d)
        except Exception:
            try:
                return float(str(d))
            except Exception:
                return float('inf')

    sorted_list = sorted(normalized, key=_dur_value)
    return sorted_list
