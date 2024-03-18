import json
import re
import numpy as np
from utils.labels import labels
# Replace 'your_file.json' with the path to your actual JSON file
file_path = 'id_url.json'

# Open the JSON file for reading and load its content into a dictionary
with open(file_path, 'r') as file:
    data = json.load(file)


print("present in labels not in keys")
for i in labels:
    if i not in np.unique(data.keys())[0]:
        print(i)

print("************************************")

print("present in keys not in labels")
for i in np.unique(data.keys())[0]:
    if i not in labels:
        print(i)