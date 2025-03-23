def rearrange_tracks(user_mood, tracks_with_moods):
    mood_values = {
        'Anger': 0,
        'Sad': 1,
        'Joy': 2,
        'Pleasure': 3
    }
    mood_ids = {v: k for k, v in mood_values.items()}

    tracks_with_moods["mood"] = tracks_with_moods["mood"].map(mood_values)
    sorted_tracks = tracks_with_moods.sort_values(by = "mood", key = lambda track: (track-mood_values[user_mood]).abs())
    sorted_tracks["mood"] = sorted_tracks["mood"].map(mood_ids)
    return sorted_tracks
