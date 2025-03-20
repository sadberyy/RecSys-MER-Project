import pandas as pd
import catboost
from typing import List
import pandas as pd

def save_model_cbm(model, filename:str):
    model.save_model(filename)
    print(f"Model saved to {filename}")
    
def load_from_cbm(filename:str):
    model = catboost.CatBoostClassifier()
    model.load_model(filename)
    print(f"Model loaded from {filename} ")
    return model

class TopPopular:
    def __init__(self):
        self.trained = False
        self.recommendations = []
    def fit(self, df: pd.DataFrame, col ='playcount'):
        counts={}
        for _, row in df.iterrows():
            track_id = row['track_id']
            playcount = row[col]
            if track_id in counts:
                counts[track_id]+=playcount 
            else:
                counts[track_id] = playcount 
        counts = sorted(counts.items(), key = lambda x: x[1], reverse = True)
        self.recommendations = [x[0] for x in counts]
        self.trained = True 
        
    def predict(self, df: pd.DataFrame, topn = 10 ) -> List[List[int]]:
        assert self.trained, "Model must be trained before making predictions"
        return [self.recommendations[:topn] for _ in range (len(df))]
    
    
    
user_history_path = "C:/Users/aellieme/Desktop/vs code projects/проект рек сис/User Listening History.csv"
user_history = pd.read_csv(user_history_path)


toppop = TopPopular()
toppop.fit(user_history)

save_model_cbm(toppop, 'TopPopular_model.cbm')
TopPopular_loaded_model = load_from_cbm('TopPopular_model.cbm')


recommendations = TopPopular_loaded_model.predict(user_history, topn=10)





