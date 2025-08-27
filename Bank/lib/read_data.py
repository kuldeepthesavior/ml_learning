import pandas as pd
from pathlib import Path
import os

os.environ['HOME_DIR']= 'Bank'

df = pd.read_csv(Path('data/train.csv'))
print(df.shape)