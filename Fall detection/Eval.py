from sklearn.metrics import make_scorer, accuracy_score,precision_recall_fscore_support
import pickle
from sklearn import preprocessing
import os
import numpy as np
import random

random.seed(272)

import warnings
warnings.filterwarnings("ignore")

if not os.path.exists('xgb_model.pkl'):
	print('Model checkpoint not found. Run Train.py')

#Loading model
with open('xgb_model.pkl','rb') as f:
	model = pickle.load(f)

npz = np.load("Sisfall_data_test.npz")
test_inputs = preprocessing.scale(npz["inputs"].astype(np.float))
test_targets = npz["targets"].astype(np.int)

#Evaluating model
pred_test = model.predict(test_inputs)
print('Test Accuracy: ', accuracy_score(test_targets, pred_test))
metrics_m= precision_recall_fscore_support(test_targets, pred_test,average = 'weighted')
print('Test Precision:',metrics_m[0])
print('Test Recall:',metrics_m[1])
print('Test F1:',metrics_m[2])
