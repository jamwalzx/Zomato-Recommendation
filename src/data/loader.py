import pandas as pd
from datasets import load_dataset

def load_zomato_dataset() -> pd.DataFrame:
    """
    Load the Zomato restaurant dataset from Hugging Face.
    Returns a pandas DataFrame of the 'train' split.
    """
    dataset = load_dataset('ManikaSaini/zomato-restaurant-recommendation', split='train')
    return dataset.to_pandas()
