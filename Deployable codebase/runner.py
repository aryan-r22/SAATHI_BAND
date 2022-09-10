import numpy as np
import pandas as pd
import random
from sklearn import preprocessing
import os
import time
import pickle
from math import sqrt
from xgboost import XGBClassifier
from sklearn.decomposition import PCA  


random.seed(272)

import warnings
warnings.filterwarnings("ignore")

def get_sleep_preds(csv_file, window = 19):
	#Importing data file
	df = pd.read_csv(csv_file)
	df = df.drop(columns = ['ROT_X',	'ROT_Y',	'ROT_Z',
			'AMB TEMP MLX',	' OBJ TEMP MLX',	'GSR',
			'HEARTRATE', 'SpO2 %'])

	#Helper func - windowing for time series data
	def windowing(dataset,window_size = window):
		window = window_size * (dataset.shape[1])
		cut = dataset.shape[0] % window_size
		feature = dataset[:-cut,0:]
		feature = feature.ravel().reshape(feature.size//window,window)
		return feature

	#Data preparation function
	def prepare_data(dataset):
		dataset['pitch'] = dataset.apply(lambda row: np.arctan(-row.GFORCEX/np.sqrt( row.GFORCEY ** 2 + row.GFORCEZ ** 2+0.0001**2)), axis=1)
		dataset['roll'] = dataset.apply(lambda row: np.arctan(row.GFORCEY/ (row.GFORCEZ+0.001)), axis=1)
		return windowing(np.array(dataset))

	X_eval = prepare_data(df)

	if not os.path.exists('xgb_model_sleep.pkl'):
		print('Model checkpoint not found. Run Train.py on ICHI14')

	#Loading model
	with open('xgb_model_sleep.pkl','rb') as f:
		model = pickle.load(f)

	npz = np.load("ICHI14_train.npz", allow_pickle=True)
	train_inputs = preprocessing.scale(npz["inputs"].astype(np.float))
	test_inputs = preprocessing.scale(X_eval.astype(np.float))

	#Applying PCA fitted over train dataset
	pca=PCA()                                  
	pca.fit(train_inputs)                                           
	test_inputs=pca.transform(test_inputs)

	#Getting predictions
	pred_test = model.predict(test_inputs)
	return pred_test

def get_fall_preds(csv_file, window = 19):
	#Importing data file
	df = pd.read_csv(csv_file)
	df = df.drop(columns = ['SpO2 %', 'AMB TEMP MLX',	' OBJ TEMP MLX',	
		'GSR','HEARTRATE'])

	#Computing features
	def add_features(dataset):
		new_dataset = pd.DataFrame()
		new_dataset['acc_1'] = dataset.apply(
			lambda row: sqrt((row.GFORCEX ** 2 + row.GFORCEY ** 2 + row.GFORCEZ ** 2)), axis=1)
		new_dataset['acc_2'] = dataset.apply(
			lambda row: sqrt((row.GFORCEX ** 2 + row.GFORCEY ** 2 + row.GFORCEZ ** 2)), axis=1)
		new_dataset['geo'] = dataset.apply(
			lambda row: sqrt((row.ROT_X ** 2 + row.ROT_Y ** 2 + row.ROT_Z ** 2)), axis=1)
		return np.round(new_dataset.to_numpy(),2)

	#helper function fior windowing
	def windowing(dataset,window_size = window):
		window = window_size * (dataset.shape[1])
		cut = dataset.shape[0] % window_size
		feature = dataset[:-cut,0:]
		feature = feature.ravel().reshape(feature.size//window,window)
		return feature

	X_eval = windowing(add_features(df))

	if not os.path.exists('xgb_model_fall.pkl'):
		print('Model checkpoint not found. Run Train.py on SisFall')

	#Loading model
	with open('xgb_model_fall.pkl','rb') as f:
		model = pickle.load(f)

	test_inputs = preprocessing.scale(X_eval.astype(np.float))

	#Getting predictions
	pred_test = model.predict(test_inputs)
	return pred_test



#GSR - 10.1109/ICICCT.2018.8473010
#VMU - 10.1145/2750858.2805834



def get_stress_level(csv_file, window = 19):

	#Read data
	df = pd.read_csv(csv_file)

	GFORCEX = df['GFORCEX'].tolist()
	GFORCEY = df['GFORCEY'].tolist()
	GFORCEZ = df['GFORCEZ'].tolist()
	HRT_RT = df['HEARTRATE'].tolist()
	GSR = df['GSR'].tolist()

	preds = []

	#Perform windowing
	for x in range(len(GFORCEX)//window):

		low = 0
		high = -1 if (x == (len(GFORCEX)//window-1)) else x+window

		#Calculating metrics
		mean_vmu = np.sqrt(np.mean(GFORCEX[low:high])**2 + np.mean(GFORCEY[low:high])**2 + np.mean(GFORCEZ[low:high])**2)
		median_heartbeat = np.median(HRT_RT[low:high])
		mean_gsr = np.mean(GSR[low:high])

		#Determining severity of stress wrt each metric
		res = []

		if(mean_vmu<0.06):
			res.append(0)
		elif(mean_vmu<0.2):
			res.append(1)
		elif(mean_vmu<0.8):
			res.append(2)
		else:
			res.append(3)

		if(median_heartbeat>=60 and median_heartbeat<=100):
			res.append(0)
		elif(median_heartbeat>=101 and median_heartbeat<=140):
			res.append(1)
		elif(median_heartbeat>=141 and median_heartbeat<=170):
			res.append(2)
		else:
			res.append(3)

		if(mean_gsr>500):
			res.append(0)
		elif(mean_gsr>450):
			res.append(1)
		elif(mean_gsr>400):
			res.append(2)
		else:
			res.append(3)

		#Finding stress level
		if(res.count(3)>=2):
			preds.append(3)
		elif(res.count(3)>0 and res.count(2)>=2):
			preds.append(2)
		elif((res.count(3)==0 and res.count(2)>0) or res.count(1) > 1):
			preds.append(1)
		else:
			preds.append(0)

	return(preds)


path = 'all.csv'
preds_fall = get_fall_preds(path)
preds_sleep = get_sleep_preds(path)
preds_stress = get_stress_level(path)

df_full = pd.DataFrame(data = {'sleep':preds_sleep, 'fall':preds_fall, 'stress':preds_stress})
df_full.to_csv('Preds_Net.csv',index=False)


### Guide
# Stress -> 0 to 3, with 3 denoting highest severity
# Fall -> 1/0, 1 denotes fall
# Sleep -> 0: Mild sleep, 1: Deep sleep, 2: Awake
