def rearrange_tracks(user_mood, tracks_with_moods):
    mood_values = {
        'Anger': 0,
        'Sad': 1,
        'Joy': 2,
        'Pleasure': 3
    }

    def mood_similarity(user_mood, tracks_with_moods):
        return abs(mood_values[user_mood] - mood_values[tracks_with_moods])

    sorted_tracks = sorted(tracks_with_moods, key=lambda track: mood_similarity(user_mood, track['mood']))

    return sorted_tracks

# def print_sorted(user_mood, tracks_with_moods):
#     sorted_tracks = rearrange_tracks(user_mood, tracks_with_moods)
#     for track in sorted_tracks:
#         print(f'{track["track_name"]} - {track["mood"]}')
