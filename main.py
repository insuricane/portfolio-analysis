import numpy as np
import pandas as pd
import math
import pickle
import warnings
import json
import sys
warnings.filterwarnings('ignore')
import model
from shapely.geometry import shape, Point

def probDestroyed(long, lat):
    ''' Return the conjunction pseudo-probability of both things destroyed'''
    return model.Insuricane("Noodle", Point((long, lat))).calc_max_hurricane().values[0]

def distance(origin, destination):
    lon1, lat1 = origin
    lon2, lat2 = destination
    radius = 6371  # km

    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) * math.sin(dlat / 2) +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon / 2) * math.sin(dlon / 2))
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    d = radius * c

    return d

def calcJoint(rad):
    if rad < 50:
        return 1
    if rad < 100:
        return 0.75
    if rad < 150:
        return 0.4
    if rad < 200:
        return 0.25
    if rad < 300:
        return 0.15
    if rad < 350:
        return 0.05
    if rad < 500:
        return 0.02
    return 0.0


fl = pickle.load(open( "cached_probs.p", "rb" ) )
ex_home = (float(sys.argv[1]), float(sys.argv[2]))
for i, row in fl.iterrows():
    if calcJoint((distance(ex_home, (fl.loc[i, 'Longitude'], fl.loc[i, 'Latitude'])))) == 0:
        fl = fl.drop(i)
    else:
        fl.loc[i, 'LFV'] = fl.loc[i, 'LFV'] * calcJoint((distance(ex_home, (fl.loc[i, 'Longitude'], fl.loc[i, 'Latitude']))))

total = fl.groupby("ticker")["LFV"].sum()

caps = pd.read_csv("mktCap.csv")
caps = caps[caps["Ticker"].isin(total.index)]
caps['position'] = total.values / (caps['ValueBillions']) # account for volatility based on cap
caps['position'] = caps['position'] / caps['position'].sum() # normalize

houseProb = probDestroyed(float(sys.argv[1]), float(sys.argv[2]))

toret = {"house_destroyed": float(houseProb), "positions": {i[0]:i[2] for i in caps.values}}

print(json.dumps(toret))