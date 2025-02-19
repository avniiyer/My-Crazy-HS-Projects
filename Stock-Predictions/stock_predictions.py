# -*- coding: utf-8 -*-
"""Stock Predictions

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1KqHJMujsoefGDBcfvEmEnpT3-IWYif_-
"""

# Importing necessary libraries
import pandas as pd
import requests
import pytz
import argparse
from tqdm import tqdm

# Set the timezone to Eastern Standard Time
timezone = pytz.timezone('US/Eastern')

stocks = None
# Function to get data from an API, process it and save as a CSV file
def get_data(api_key, page_size, ticker, tail):
    # List of page numbers to iterate through
    page_no = [0, 1, 2, 3]
    # A list to store dataframes obtained from each API call
    data_list = []


    # Loop through each page number
    for i in tqdm(page_no, desc="Processing pages", unit="page"):
        # Making API requests to get OHLC and RSI data
        response_ohlc = requests.get(f'https://api.finazon.io/latest/time_series?dataset=sip_non_pro&ticker={ticker}&prepost=true&interval=1m&page={i}&page_size={page_size}&order=desc&apikey={api_key}')
        response_rsi = requests.get(f'https://api.finazon.io/latest/time_series/rsi?dataset=sip_non_pro&ticker={ticker}&prepost=true&interval=1m&page={i}&page_size={page_size}&order=desc&apikey={api_key}')

        # Checking if both API requests were successful
        if response_ohlc.status_code == 200 and response_rsi.status_code == 200:
            # Creating dataframes from the API responses
            df_ohlc = pd.DataFrame(response_ohlc.json()['data'])
            df_rsi = pd.DataFrame(response_rsi.json())
            #print rsi here to check if thre are any nan
            '''
                Output from the OHLC api looks like as below:
                {
                    "data":
                    [
                        {
                            "c": 145.46001,
                            "h": 145.49001,
                            "l": 145.13,
                            "o": 145.35001,
                            "t": 1675256340,
                            "v": 1006162
                        }
                    ]
                }
                Output from the RSI api looks like as below:
                {
                    "data":
                    [
                        {
                            "t":1705035600,
                            "rsi":"43.82645098569"
                        }
                    ]
                }
            '''
            # Checking if 'data' column exists in df_rsi
            if 'data' in df_rsi.columns:
                # Extracting 't' (time) and 'rsi' from the 'data' column in df_rsi
                df_rsi['t'] = df_rsi['data'].apply(lambda x: x['t'])
                df_rsi['rsi'] = df_rsi['data'].apply(lambda x: x['rsi'])

                # Rounding the 'rsi' column values to 2 decimal places
                df_rsi['rsi'] = df_rsi['rsi'].astype(float).round(2)

                # Dropping the original 'data' column from df_rsi
                df_rsi = df_rsi.drop(['data'], axis=1)

                # Merging the OHLC and RSI dataframes on the 't' column
                merged_df = pd.merge(df_ohlc, df_rsi, on='t', how='left')

                #print the merged df here as well to check for nan

                # Converting the 't' column to datetime format
                merged_df['t'] = pd.to_datetime(merged_df['t'], unit='s')

                # Converting UTC to local timezone and formatting the timestamp
                local_timezone = timezone
                merged_df['t'] = merged_df['t'].dt.tz_localize('UTC').dt.tz_convert(local_timezone).dt.strftime('%Y-%m-%d %H:%M:%S')

                # Appending the merged dataframe to the data_list
                data_list.append(merged_df)

            else:
                print(f"Error: 'data' key not found in response_rsi JSON (page {i})")
        else:
            print(f"Error in API request (page {i}). Status codes: {response_ohlc.status_code}, {response_rsi.status_code}")

    # Checking if there is data in the data_list
    if data_list:
        # Concatenating all the dataframes in the list
        final_df = pd.concat(data_list, ignore_index=True)

        # Saving the final dataframe to a CSV file
        final_df.to_csv("finanzon-ohlc-rsi-data.csv", index=False)

        print("Tail of the dataframe:")
        global rsi_df
        rsi_df = final_df






#if __name__ == "__main__":
    #parser = argparse.ArgumentParser(description="Fetch and process financial data.")
    #parser.add_argument("--api_key", type=str, help="Your API key", required=True)
    #parser.add_argument("--page_size", type=int, help="Page size for API request", required=True)
    #parser.add_argument("--ticker", type=str, help="Financial ticker symbol", required=True)
    #parser.add_argument("--tail", type=int, help="Number of rows to display in tail", required=True)

    #args = parser.parse_args()
    #get_data(args.api_key, args.page_size, args.ticker, args.tail)


get_data(api_key = '9a140c3601fa48d0b5757677eb66ed6ain', page_size = 450, ticker = 'SOXL', tail = 15 )
rsi_df_original = rsi_df

rsi_df_final = rsi_df.dropna()
rsi_df_final["diff_close_open"] = rsi_df_final["c"] - rsi_df_final["o"]
columns_to_drop = ["t", "h", "o", "c", "l", "v"]
rsi_df_final = rsi_df_final.drop(columns = columns_to_drop, axis = 1)
print(rsi_df_final.head(15))
rsi_df_final.info()

from zlib import crc32
import numpy as np
from sklearn.model_selection import train_test_split

check_time = int(0.1*len(rsi_df_original))
original_ten_percent = rsi_df_original.iloc[:check_time]
print(original_ten_percent.tail())

ten_percent_size = int(0.1 * len(rsi_df_final))

# Exclude the first 10% of the data
remaining_data = rsi_df_final.iloc[ten_percent_size:]

# Split the first 10% of the data
first_10_percent, remaining_data = rsi_df_final.iloc[:ten_percent_size], rsi_df_final.iloc[ten_percent_size:]
#print(first_10_percent)
#print(remaining_data)


#print(first_10_percent.shape)
#print(first_10_percent.columns)

first_10_labels = first_10_percent["diff_close_open"].copy()
first_10_features = first_10_percent.drop("diff_close_open", axis=1)

#Splitting into training and testing sets


#print(first_10_features)
#print(first_10_labels)

#Split the remaining 90% into training and primary test sets
x_train, x_test_primary, y_train_labels, y_test_primary_labels = train_test_split(
    remaining_data.drop("diff_close_open", axis=1),  # Adjust "target_column" to your target variable
    remaining_data["diff_close_open"],  # Adjust "target_column" to your target variable
    test_size=0.2, shuffle = False)


# Print the shapes of the resulting sets
#print(x_train)
#print(x_test_primary)
#print(y_train_labels)
#print(y_test_primary_labels)

train_set, test_set = train_test_split(rsi_df_final, test_size = 0.2)

train_index = train_set.index
test_index = test_set.index

len(train_set)
print(first_10_features.tail())

#This code stratifies data based on rsi - we want based on time
#import pandas as pd


#rsi_df_final["rsi_cat"] = pd.cut(rsi_df_final["rsi"],bins = [0., 30.0, 50.0, 70.0, 90.0, np.inf], labels=[1, 2, 3, 4, 5])
#rsi_df_final["rsi_cat"].hist()

#print(rsi_df_final.head())
#print(rsi_df_final.info())

#train_set, test_set = train_test_split(rsi_df_final, test_size=0.2, random_state=42, stratify=rsi_df_final["rsi_cat"])

#print(train_set)


#train_set["rsi_cat"].value_counts() / len(train_set)

#for set_ in(train_set, test_set):
  #set_.drop("rsi_cat", axis = 1, inplace=True)

#print(train_set.head())

#rsi_df_final = train_set.copy()

#rsi_df_final.plot(kind = "scatter", x = "o", y="rsi", alpha = 0.1)
#rsi_df_final.plot(kind = "scatter", x = "c", y = "rsi", alpha = 0.1)

#corr_matrix = rsi_df_final.corr()
#corr_matrix["rsi"].sort_values(ascending = False)

#from pandas.plotting import scatter_matrix

#attributes = ["c", "h", "l", "o", "v", "rsi"]
#scatter_matrix (rsi_df_final[attributes], figsize=(12,8))

#rsi_df_final.plot(kind = "scatter", x = "rsi", y = "v", alpha = 0.1)

#columns_to_drop = ["rsi", "t"]

#rsi_df_final = train_set.drop(columns = columns_to_drop, axis = 1)
#rsi_labels = train_set["rsi"].copy()
#print(rsi_labels.info())




#from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer

#from sklearn.preprocessing import StandardScaler
#from sklearn.base import BaseEstimator, TransformerMixin
#import numpy as np


#rsi_df_final["diff_high_low"] = rsi_df_final["h"]-rsi_df_final["l"]
#rsi_df_final["diff_close_open"] = rsi_df_final["c"] - rsi_df_final["o"]
#corr_matrix = rsi_df_final.corr()
#corr_matrix["rsi"].sort_values(ascending=False)

#test_set["diff_high_low"] = test_set["h"]-test_set["l"]
#test_set["diff_close_open"] = test_set["c"] - test_set["o"]
#print("test_set", test_set.info())

#rsi_num_final = rsi_df_final

#h_ix, l_ix, o_ix, c_ix = 2, 3, 1, 4
#class CombinedAttributesAdder(BaseEstimator, TransformerMixin):
  #def __init__(self, add_diff_close_open = True):
    #self.add_diff_close_open= add_diff_close_open
  #def fit(self, X, y=None):
    #return self
 # def transform (self, X):
    #try:
      #diff_high_low = X[:, h_ix] - X[:, l_ix]
      #if self.add_diff_close_open:
        #diff_close_open = X[:,c_ix] - X[:, o_ix]
        #return np.c_[X, diff_high_low, diff_close_open]
      #else:
        #return np.c_[X, diff_high_low]
   # except Exception as e:
      #print(f"Error in transform: {e}")
      #print(f"h_ix={h_ix}, l_ix={l_ix}, o_ix={o_ix}, c_ix={c_ix}")
      #print(f"X shape: {X.shape}")
      #print(f"X values: {X}")
      #raise

#attr_adder = CombinedAttributesAdder(add_diff_close_open = False)
#rsi_extra_attribs = attr_adder.transform(rsi_num_final.values)



#print(rsi_df_final.info())

#print("Rsi_num_final:", rsi_num_final.info())


#class CombinedAttributesAdder()
#num_pipeline = Pipeline([('imputer', SimpleImputer(strateg="median")), ('attribs_adder', CombinedAttributesAdder()), ('std_scaler', StandardScaler())])
#rsi_num_tr = num_pipeline.fit_transform(rsi_num)

from sklearn.pipeline import Pipeline, FunctionTransformer
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer

# Function to convert DataFrame to NumPy array

#def df_to_numpy(rsi_num_final):
    #if isinstance(rsi_num_final, pd.DataFrame):
        #return rsi_num_final.values
    #elif isinstance(rsi_num_final, np.ndarray):
        #return rsi_num_final
    #else:
        #raise ValueError("Unsupported data type. Expecting pandas DataFrame or NumPy array.")
    #except Exception as e:
        #print(f"Error in df_to_numpy: {e}")
        #print(f"rsi_num_final shape: {rsi_num_final.shape}")
        #print(f"rsi_num_final values: {rsi_num_final}")
        #raise

#print("Indices:", h_ix, l_ix, o_ix, c_ix)
#print(rsi_num_final)
#num_pipeline = Pipeline([
#    ('imputer', SimpleImputer(strategy='median'))
#])


#x_train = num_pipeline.fit_transform(x_train)
#print(x_train)


# Access the steps in the pipeline
#steps = rsi_prepared.CombinedAttributesAdder.transformers

# Collect the feature names before and after each transformation
#feature_names_before = rsi_num_final.columns.tolist()

#for name, transformer, columns in steps:
    #if hasattr(transformer, 'get_feature_names_out'):
        # If the transformer has get_feature_names_out method (e.g., OneHotEncoder)
        #feature_names_after = transformer.get_feature_names_out(input_features=columns)
    #else:
        # For transformers without get_feature_names_out, use original column names
        #feature_names_after = columns

    #print(f"\nTransformer: {name}")
    #print(f"Columns before transformation: {columns}")
    #print(f"Feature names before transformation: {feature_names_before}")
    #print(f"Feature names after transformation: {feature_names_after}")

    #feature_names_before = feature_names_after

# Check the final transformed data
#print("\nFinal Transformed Data:")
#print(rsi_prepared)

#non_numeric_columns = rsi_prepared.select_dtypes(exclude=['number']).columns
#print("Non-numeric columns:", non_numeric_columns)

#print(rsi_prepared)

#num_original_columns = rsi_num_final.shape[1]

# Check the number of columns in the transformed data
#num_transformed_columns = rsi_prepared.shape[1]

# Compare the numbers
#if num_original_columns == num_transformed_columns:
    #print("The number of columns is the same before and after transformation.")
#else:
    #print("The number of columns has changed after transformation.")

from sklearn.linear_model import LinearRegression
#print(rsi_labels.head(5))

lin_reg = LinearRegression()
lin_reg.fit(x_train, y_train_labels)

#print(rsi_prepared)
#print(rsi_labels)
y_train_labels = pd.DataFrame(y_train_labels)
x_train = pd.DataFrame(x_train)
some_data = x_train.iloc[:5]
#print(some_data)



some_labels = y_train_labels.head(5)
some_labels = some_labels.to_numpy()

#some_data_selected = some_data[['c', 'rsi']]
some_data_prepared = some_data
print("Predictions:", lin_reg.predict(some_data_prepared))
print("Some labels: " , some_labels)
print("Labels:", list(y_train_labels.head(5)))

from sklearn.metrics import mean_squared_error
c_predictions = lin_reg.predict(x_train)
lin_mse = mean_squared_error(y_train_labels, c_predictions)
lin_rmse = np.sqrt(lin_mse)
lin_rmse

from sklearn.tree import DecisionTreeRegressor

tree_reg = DecisionTreeRegressor()
tree_reg.fit(x_train,y_train_labels)

c_predictions = tree_reg.predict(x_train)
tree_mse = mean_squared_error(y_train_labels, c_predictions)
tree_rmse = np.sqrt(tree_mse)
tree_rmse

from sklearn.model_selection import cross_val_score
scores = cross_val_score (tree_reg, x_train, y_train_labels, scoring = "neg_mean_squared_error", cv = 10)
lin_rmse_scores = np.sqrt(-scores)

def display_scores(scores):
  print("Scores:", scores)
  print("Mean:", scores.mean())
  print("Standard deviation: ", scores.std())

display_scores(lin_rmse_scores)

from sklearn.ensemble import RandomForestRegressor
forest_reg = RandomForestRegressor()
forest_reg.fit(x_train, y_train_labels)

scores = cross_val_score (tree_reg, x_train, y_train_labels, scoring = "neg_mean_squared_error", cv = 10)
forest_rmse_scores = np.sqrt(-scores)

display_scores(forest_rmse_scores)

hyperparameters = forest_reg.get_params()
print("Hyperparameters:", hyperparameters)

from sklearn.tree import DecisionTreeRegressor
from sklearn.model_selection import GridSearchCV

param_grid = [{'max_depth': [3, 100, None], 'max_features': [1, 4, 6, 8]}, {'max_depth': [1, 100], 'max_features': [1, 10, None]}]
tree_reg = DecisionTreeRegressor()

grid_search = GridSearchCV(tree_reg, param_grid, cv = 20, scoring = 'neg_mean_squared_error', return_train_score=True)
grid_search.fit(x_train, y_train_labels)
grid_search.best_params_

cvres = grid_search.cv_results_
for mean_score, params in zip(cvres["mean_test_score"], cvres["params"]):
  print(np.sqrt(-mean_score), params)

from sklearn.model_selection import RandomizedSearchCV
from sklearn.ensemble import RandomForestRegressor
from scipy.stats import randint

param_dist = {
    'max_depth': [None, 5, 10, 15],  # The maximum depth of the tree. None means unlimited depth.
    'min_samples_split': [2, 5, 10],  # The minimum number of samples required to split an internal node.
    'min_samples_leaf': [1, 2, 4],  # The minimum number of samples required to be at a leaf node.
    'max_features': ['auto', 'sqrt', 'log2', None],  # The number of features to consider when looking for the best split.
}

# Create a RandomizedSearchCV instance
random_search = RandomizedSearchCV(
    tree_reg,  # Your model
    param_distributions=param_dist,  # Parameter distributions to sample from
    n_iter=100,  # Number of parameter settings that are sampled
    scoring='neg_mean_squared_error',  # Your scoring metric
    cv=5,  # Number of cross-validation folds
    random_state=42  # Random seed for reproducibility
)

# Fit the RandomizedSearchCV to your data
random_search.fit(x_train, y_train_labels)

# Access the best hyperparameters
best_hyperparameters = random_search.best_params_
print("Best Hyperparameters:", best_hyperparameters)

cvres = random_search.cv_results_
for mean_score, params in zip(cvres["mean_test_score"], cvres["params"]):
  print(np.sqrt(-mean_score), params)

#feature_importances = grid_search.best_estimator_.feature_importances_
#feature_importances
#extra_attribs = ["diff_high_low", "diff_close_open"]
#sorted(zip(feature_importances, extra_attribs), reverse=True)

final_model = grid_search.best_estimator_

final_predictions = final_model.predict(x_test_primary)

print("primary_test_labels", y_test_primary_labels)
print("primary_test_features", x_test_primary)
print("final_predictions", final_predictions)

final_mse = mean_squared_error(y_test_primary_labels, final_predictions)
final_rmse = np.sqrt(final_mse)

from scipy import stats
confidence = 0.95
squared_errors = (final_predictions - y_test_primary_labels)**2
np.sqrt(stats.t.interval(confidence, len(squared_errors)-1, loc=squared_errors.mean(), scale = stats.sem(squared_errors)))

import numpy as np
import scipy.stats

final_predictions = final_model.predict(first_10_features)

final_mse = mean_squared_error(first_10_labels, final_predictions)
final_rmse = np.sqrt(final_mse)


confidence = 0.95
squared_errors = (final_predictions - first_10_labels)**2
np.sqrt(stats.t.interval(confidence, len(squared_errors)-1, loc=squared_errors.mean(), scale = stats.sem(squared_errors)))

first_10_labels = first_10_labels.iloc[::-1]
first_10_features = first_10_features.iloc[::-1]

final_predictions.sort()
final_predictions = final_predictions[::-1]
time_at_start = 4

timestamps = [time_at_start + i for i, _ in enumerate(final_predictions)]


# Printing the result
print('first_10_predictions')
for timestamp, value in zip(timestamps, final_predictions):
    print(f"Timestamp: {timestamp}, Value: {value}")

print('first_10_actual', first_10_labels)
print('first_10_rsi', first_10_features)



