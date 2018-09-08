import pandas as pd
import numpy as np

whole = pd.DataFrame.from_csv("plant_data.csv")
fl = whole.groupby("State")["fl"]
print(fl)