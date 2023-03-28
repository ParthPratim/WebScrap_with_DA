#Import scikit-learn dataset library
from sklearn import datasets
import pandas as pd

#Load dataset
df = pd.read_csv('scrap_dataset.csv', header=0)
df.describe()
