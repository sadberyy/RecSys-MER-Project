import pandas as pd
import mlflow
import mlflow.pyfunc

def load_als_model(model_path:str):
    model = mlflow.pyfunc.load_model(model_path)
    return model

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
    