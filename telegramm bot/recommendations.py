import pandas as pd
import catboost
from TopPopular_file import load_from_cbm
# from als_recs import get_als_recommendations
import pickle
from implicit.als import AlternatingLeastSquares
from scipy.sparse import csr_matrix
# from bot2 import flags, user_data
import bot2


user_history_path = "UserListening History.csv"  
songs_path = "Music Info.csv"  


user_history = pd.read_csv(user_history_path)
songs = pd.read_csv(songs_path)


with open("als_model.pkl", "rb") as f:
    artifacts = pickle.load(f)

als_model = artifacts["model"]
user_encoder = artifacts["user_encoder"]
track_encoder = artifacts["track_encoder"]
minfo = artifacts["minfo"]


TopPopular_path = 'TopPopular_model.cbm'
TopPopular_loaded_model = load_from_cbm(TopPopular_path)


def build_user_item_matrix(user_history, user_encoder, track_encoder):
    user_history = user_history.dropna(subset=["user_id", "track_id"]) 
    user_ids = user_encoder.transform(user_history["user_id"])
    track_ids = track_encoder.transform(user_history["track_id"])
    data = [1] * len(user_ids)  
    user_item_matrix = csr_matrix(
        (data, (user_ids, track_ids)),
        shape=(len(user_encoder.classes_), len(track_encoder.classes_))
    )
    
    return user_item_matrix

user_item_matrix = build_user_item_matrix(user_history, user_encoder, track_encoder)

def get_als_recommendations(user_id, model, user_encoder, track_encoder, minfo, user_item_matrix, history_df, top_k = 10):
    try:
        if user_id not in user_encoder.classes_:
            return pd.DataFrame(columns = ["artist", "name"])
        internal_id = user_encoder.transform([user_id])[0]
        if internal_id >= user_item_matrix.shape[0]:
            return pd.DataFrame(columns = ["artist", "name"])
        
        item_ids, scores = model.recommend(internal_id, user_item_matrix[internal_id], N=top_k*2, filter_already_liked_items = False, )
        listened_tracks = history_df[history_df["user_id"]== user_id]["track_id"].unique()
        
        track_ids = track_encoder.inverse_transform(item_ids)
        recommendations = minfo[minfo["track_id"].isin(track_ids)]
        
        recommendations = recommendations[~recommendations["track_id"].isin(listened_tracks)]
        return recommendations.head(top_k)
    except Exception as e:
        print(f"Ошибка в генерации рекомендаций {str(e)}")
        return pd.DataFrame(columns =["artist", "name"])
    

def recommend_top_popular(user_id:int, topn:int = 10)-> pd.DataFrame:    
    recommendations = TopPopular_loaded_model.predict(user_history, topn=topn)
    recommended_tracks = recommendations[0]
    recommended_songs = songs[songs["track_id"].isin(recommended_tracks)]
    return recommended_songs


def get_recommendations(user_id:int, topn:int = 10)-> pd.DataFrame:
    
    user_new_or_not = bot2.flags.get(bot2.user_data, True)
    if user_new_or_not ==True or user_id == 0:
        return recommend_top_popular(user_id, topn)
    else:
        return get_als_recommendations(user_id, als_model, user_encoder, track_encoder, songs, user_item_matrix, user_history, top_k=topn)
    
    

