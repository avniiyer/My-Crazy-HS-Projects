# -*- coding: utf-8 -*-
"""Higgs Boson

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/12822nYeodi2ZVopLRWL01tpp9JbrLGOZ
"""

import pandas as pd
import os
import tarfile
import zipfile

zip_file_path = '/content/higgs-boson.zip'
extract_path = '/content/'

with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
    zip_ref.extractall(extract_path)

def load_income_data():
  for root, dirs, files in os.walk(extract_path):
      for file in files:
        return(os.path.join(root,file))


load_income_data()



zip_file_path = '/content/test.zip'
extract_path = '/content/'

with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
    zip_ref.extractall(extract_path)

def load_test_data():
        return(os.path.join)


load_test_data()


higgs_test = pd.read_csv('test.csv')

print(higgs_test.head())

zip_file_path = '/content/training.zip'
extract_path = '/content/'

with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
    zip_ref.extractall(extract_path)

def load_training_data():
        return(os.path.join)


load_training_data()


higgs_training = pd.read_csv('training.csv')

print(higgs_training.head())

from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(higgs_training.drop('Label', axis = 1), higgs_training['Label'], test_size = 0.25, random_state = 22)

y_train

columns_to_drop = ['EventId', 'Weight']
X_train = X_train.drop(columns_to_drop, axis = 1)
X_test = X_test.drop(columns_to_drop, axis = 1)
X_train

y_train = y_train.replace(to_replace = {'b': 0, 's': 1})
y_test = y_test.replace(to_replace = {'b': 0, 's': 1})

!pip install tensorflow
import tensorflow as tf
import seaborn as sns
import matplotlib.pyplot as plt

for i in X_train.columns:
  sns.scatterplot(data = higgs_training, x = 'Label', y = i)
  plt.show()

from tensorflow import keras

X_train.shape

model = keras.models.Sequential([
    keras.layers.Dense(30, activation = "relu", input_shape = (30,)),
    keras.layers.Dense(30,activation = "relu"),
    keras.layers.Dense(1, activation = "sigmoid")
])

import /content/HiggsBosonCompetition_AMSMetric_rev1.py

def compile(metric):
  model.compile(loss = "binary_crossentropy", optimizer = keras.optimizers.SGD(learning_rate =0.01 ), metrics = [metric])

result = HiggsBosonCompetition_AMSMetric_rev1.compile()

!python HiggsBosonCompetition_AMSMetric_rev1.py

model.compile(loss = "binary_crossentropy", optimizer = keras.optimizers.SGD(learning_rate =0.01 ), metrics = ["accuracy"])

history = model.fit(X_train, y_train, epochs = 10, validation_data = (X_test, y_test))