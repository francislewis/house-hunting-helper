import os
import pickle
id = 1811237

with open(os.path.join(os.getcwd(), 'saved_properties/1811237.pkl'), 'rb') as f:
    loaded_dict = pickle.load(f)
    print(loaded_dict)