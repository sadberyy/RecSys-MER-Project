import pickle
from typing import List
from tqdm import tqdm  
import pandas as pd


def save_model_toppop(model, filename: str):
    with open(filename, 'wb') as f:
        pickle.dump(model, f)
    print(f"Model saved to {filename}")

def load_model_toppop(filename: str):
    with open(filename, 'rb') as f:
        model = pickle.load(f)
    print(f"Model loaded from {filename}")
    return model

class TopPopular:
    def __init__(self):
        self.trained = False
        self.recommendations = []
    
    def fit(self, df: pd.DataFrame, col='playcount'):
        counts = {}
        for _, row in tqdm(df.iterrows(), total=len(df), desc="fit model"):
            track_id = row['track_id']
            playcount = row[col]
            counts[track_id] = counts.get(track_id, 0) + playcount
        counts = sorted(counts.items(), key=lambda x: x[1], reverse=True)
        self.recommendations = [x[0] for x in counts]
        self.trained = True 
        
    def predict(self, df: pd.DataFrame, topn=10) -> List[List[str]]:
        assert self.trained, "Model must be trained before making predictions"
        return [self.recommendations[:topn] for _ in range(len(df))]
    
    

user_history = pd.read_csv('User Listening History.csv')
music_info = pd.read_csv('Music Info.csv', usecols=['track_id', 'name', 'artist'])

track_info_dict = music_info.set_index('track_id')[['name', 'artist']].to_dict(orient='index')


toppop = TopPopular()
toppop.fit(user_history)

save_model_toppop(toppop, 'TopPopular_model2.pkl')
