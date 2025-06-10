import pandas as pd
from whoosh.index import open_dir

class DataLoader:
    def __init__(self) -> None:
        self.choice_path = './indexdir'
        self.data_path = "./un_data_final_chunks.csv"
    
    def load(self):
        data = pd.read_csv(self.data_path)
        return data, open_dir(self.choice_path)

