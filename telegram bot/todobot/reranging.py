import pandas as pd
def rearrange_tracks(user_mood, tracks_with_moods):

    mood_sort_order = {
        'Sad': ['Sad', 'Anger', 'Pleasure', 'Joy'],
        'Anger': ['Anger', 'Sad', 'Joy', 'Pleasure'],
        'Joy': ['Joy', 'Pleasure', 'Anger', 'Sad'],
        'Pleasure': ['Pleasure', 'Joy', 'Sad', 'Anger']
    }

    desired_mood_order = mood_sort_order[user_mood]

    tracks_with_moods['mood'] = pd.Categorical(
        tracks_with_moods['mood'],
        categories=desired_mood_order,
        ordered=True
    )

    sorted_tracks = tracks_with_moods.sort_values(by='mood')

    return sorted_tracks

def print_sorted(user_mood, tracks_with_moods):
    sorted_tracks = rearrange_tracks(user_mood, tracks_with_moods)
    for track in sorted_tracks:
        print(f'{track["track_name"]} - {track["mood"]}')
