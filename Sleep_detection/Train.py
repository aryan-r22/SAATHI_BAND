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
from sklearn.decomposition import PCA          


random.seed(272)

import warnings
warnings.filterwarnings("ignore")

#Check for data files
if not (os.path.exists("ICHI14_train.npz") and os.path.exists("ICHI14_test.npz")):
    print('Processed data files do not exist. Run Data_preparation.py')

npz = np.load("ICHI14_train.npz")
train_inputs = preprocessing.scale(npz["inputs"].astype(np.float))
train_targets = npz["targets"].astype(np.int)


npz = np.load("ICHI14_test.npz")
test_inputs = preprocessing.scale(npz["inputs"].astype(np.float))
test_targets = npz["targets"].astype(np.int)

#Applying PCA
pca=PCA()                                  
pca.fit(train_inputs)                                           
train_inputs=pca.transform(train_inputs)
test_inputs=pca.transform(test_inputs)

#Training using XG Boost algorithm
model = XGBClassifier(n_estimators=1000, random_state=272,max_depth = 7, tree_method = "gpu_hist", scale_pos_weight=99)
eval_metric = ["error"]
model.fit(train_inputs, train_targets, eval_metric=eval_metric, verbose=False)

#Saving model
file_name = "xgb_model.pkl"
pickle.dump(model, open(file_name, "wb"))
