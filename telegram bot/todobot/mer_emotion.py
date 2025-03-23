import pandas as pd
from catboost import CatBoostClassifier

def predict_emotions(random_recommendations):
    results = []
    for track_id in random_recommendations:
        if track_id in opensmile_df["track_id"].values:
            track_features = opensmile_df.loc[opensmile_df["track_id"] == track_id].drop(columns=["genre", "name","artist", "tags", "energy", "valence", "emotion","track_id"])
            predicted_emotion = cb_model.predict(track_features)[0, 0]
        else:
            emotion_row = music_arousal_valence.loc[music_arousal_valence["track_id"] == track_id, "emotion"]
            predicted_emotion = emotion_row.values[0] if not emotion_row.empty else "Unknown"

        track_info = music_arousal_valence.loc[music_arousal_valence["track_id"] == track_id, ["name", "artist"]]
        if not track_info.empty:
            track_name = track_info["name"].values[0]
            artist_name = track_info["artist"].values[0]
        else:
            track_name, artist_name = "Unknown Track", "Unknown Artist"

        results.append([track_name, artist_name, predicted_emotion])

    return results

opensmile_df = pd.read_csv("todobot\opensmile_file.csv")
music_info_df = pd.read_csv("todobot\Music Info.csv")
music_arousal_valence = pd.read_csv("todobot/music_arousal_valence.csv")

cb_model = CatBoostClassifier()
cb_model.load_model("todobot\cb_oversampled.cbm")

