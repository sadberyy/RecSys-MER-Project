import os
import random
import pandas as pd
import pickle
from implicit.als import AlternatingLeastSquares
from scipy.sparse import csr_matrix
from todobot.mer_emotion import predict_emotions
from todobot.reranging import rearrange_tracks

def load_model_toppop(filename: str):
    with open(filename, 'rb') as f:
        model = pickle.load(f)
    print(f"Model loaded from {filename}")
    return model

def build_user_item_matrix(user_history, user_encoder, track_encoder):
    user_history = user_history.dropna(subset=["user_id", "track_id"]) 
    user_ids = [user_encoder.get(uid, -1) for uid in user_history["user_id"]]

    track_ids = [track_encoder.get(uid, -1) for uid in user_history["track_id"]]
    data = [1] * len(user_ids) 
    user_item_matrix = csr_matrix(
        (data, (user_ids, track_ids)),
        shape=(len(user_encoder), len(track_encoder))  
    )
    
    return user_item_matrix

def get_als_recommendations(user_id, model, user_encoder, track_encoder, minfo, user_item_matrix, history_df, top_k = 10):
    try:
        
        if user_id not in user_encoder:
            print(f"Пользователь {user_id} не найден в ALS, переключаемся на TopPopular")
            return recommend_top_popular(user_id, top_k)
       
        internal_id = user_encoder[user_id]
        
        if internal_id >= user_item_matrix.shape[0]:
            return pd.DataFrame(columns = ["artist", "name"])
        
        item_ids, scores = model.recommend(internal_id, user_item_matrix[internal_id], N=top_k*2, filter_already_liked_items = False, )
        listened_tracks = history_df[history_df["user_id"]== user_id]["track_id"].unique()
        track_ids = [id for id in track_encoder.keys() if track_encoder[id] in item_ids]
        recommendations = minfo[minfo["track_id"].isin(track_ids)]
        recommendations = recommendations[~recommendations["track_id"].isin(listened_tracks)]
        recommendations_with_emotions = pd.DataFrame(predict_emotions(recommendations["track_id"].tolist()), columns = ["artist", "track_name", "mood"])


        return recommendations_with_emotions.head(top_k)
    except Exception as e:
        print(f"Ошибка в генерации рекомендаций {str(e)}")
        return pd.DataFrame(columns =["artist", "name"])
def recommend_top_popular(user_id: str, topn: int = 10) -> pd.DataFrame:
    predictions_path = 'todobot/TopPopular_predictions.pkl'

    if not os.path.exists(predictions_path):
        raise FileNotFoundError(f"Файл {predictions_path} не найден! Пересчитайте предсказания.")

    with open(predictions_path, 'rb') as f:
        recommended_track_ids = pickle.load(f)

    random_index = random.randint(0, len(recommended_track_ids) - 1)
    random_recommendations = recommended_track_ids[random_index]

    results = predict_emotions(random_recommendations)
    print(pd.DataFrame(results, columns = ["artist", "track_name", "mood"]))
    return pd.DataFrame(results, columns = ["artist", "track_name", "mood"])


def get_recommendations(flags, user_data, user_id:int, topn:int = 10)-> pd.DataFrame:
    
    user_new_or_not = flags.get(user_id, True)
    if user_new_or_not ==True or user_id == 0:
        return recommend_top_popular(user_id, topn)
    else:
        return get_als_recommendations(user_id, als_model, user_encoder, track_encoder, songs, user_item_matrix, user_history, top_k=topn)


user_history_path = "todobot/User Listening History.csv"
songs_path = "todobot/Music Info.csv"
user_history = pd.read_csv(user_history_path)
songs = pd.read_csv(songs_path)

with open("todobot/als_model.pkl", "rb") as f:
    artifacts = pickle.load(f)

als_model = artifacts["model"]
user_encoder = artifacts["user_encoder"]
track_encoder = artifacts["track_encoder"]
minfo = artifacts["minfo"]

user_item_matrix = build_user_item_matrix(user_history, user_encoder, track_encoder)

 
