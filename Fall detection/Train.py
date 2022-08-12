from sklearn import preprocessing
from math import sqrt
import pandas as pd
import numpy as np
import glob
import os
import time
from xgboost import XGBClassifier
import pickle
import random

random.seed(272)

import warnings
warnings.filterwarnings("ignore")

#Check for data files
if not (os.path.exists("Sisfall_data_train.npz") and os.path.exists("Sisfall_data_test.npz")):
    print('Processed data files do not exist. Run Data_preparation.py')

npz = np.load("Sisfall_data_train.npz")
train_inputs = preprocessing.scale(npz["inputs"].astype(np.float))
train_targets = npz["targets"].astype(np.int)


npz = np.load("Sisfall_data_test.npz")
test_inputs = preprocessing.scale(npz["inputs"].astype(np.float))
test_targets = npz["targets"].astype(np.int)

#Training using XG Boost algorithm
model = XGBClassifier(n_estimators=400, random_state=272,max_depth = 4,  tree_method = "gpu_hist")
eval_set = [(train_inputs, train_targets), (test_inputs, test_targets)]
eval_metric = ["auc","error"]
model.fit(train_inputs, train_targets, eval_metric=eval_metric, eval_set=eval_set, verbose=False)

#Saving model
file_name = "xgb_model.pkl"
pickle.dump(model, open(file_name, "wb"))
