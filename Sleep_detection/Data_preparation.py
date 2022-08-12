import numpy as np
import glob
import pandas as pd
from scipy import stats
import random

random.seed(272)

import warnings
warnings.filterwarnings("ignore")

#Checking for dataset files
if not (os.path.exists('ICHI14 dataset')):
    print("Download datatset files")

#Loading filepaths
filepaths = glob.glob('./ICHI14 dataset/data/*')
total_subjects = len(filepaths)
#Splitting data into train and test (80% - 20%)
train_num = int(0.8*total_subjects)

# Creating training split
df_train = pd.DataFrame(columns = ['timestamp','d','x','y','z','l','gt'])
for i in range(train_num):
  x = pd.DataFrame(np.load(filepaths[i]),columns = ['timestamp','d','x','y','z','l','gt'], index=None)
  df_train = df_train.append(x)
df_train = df_train.drop(columns = ['d','timestamp','l'])

# Creating test split
df_test = pd.DataFrame(columns = ['timestamp','d','x','y','z','l','gt'])
for i in range(train_num,total_subjects):
  x = pd.DataFrame(np.load(filepaths[i]),columns = ['timestamp','d','x','y','z','l','gt'], index=None)
  df_test = df_test.append(x)
df_test = df_test.drop(columns = ['d','timestamp','l'])

#Performing windowing for time series data
def windowing(dataset,window_size = 100):
  window = window_size * (dataset.shape[1]-1)
  cut = dataset.shape[0] % window_size
  feature = dataset[:-cut,0:-1]
  label = dataset[:-cut,-1]
  label = label.reshape(label.size//window_size,window_size)
  label_f =np.zeros(label.shape[0],)
  for mm in range(label.shape[0]):
    label_f[mm] = int(stats.mode(label[mm])[0][0])
  feature = feature.ravel().reshape(feature.size//window,window)
  return feature, label_f.astype(int)

def prepare_data(dataset):
  dataset['pitch'] = dataset.apply(lambda row: np.arctan(-row.x/np.sqrt( row.y ** 2 + row.z ** 2+0.0001**2)), axis=1)
  dataset['roll'] = dataset.apply(lambda row: np.arctan(row.y/ (row.z+0.001)), axis=1)
  dataset = dataset[dataset['gt']!=0]  #Removing datapoints for which the label was 
  #1-5 for sleep ; 6-7 for awake
  mapping = {1:0, 2:0, 3:0, 5:1, 6:2, 7:2}
  dataset['labels'] = dataset['gt'].map(mapping)
  dataset = dataset.drop(columns = ['gt'])
  return windowing(np.array(dataset))


X_train, Y_train = prepare_data(df_train)
X_test, Y_test = prepare_data(df_test)
#Saving processed data
np.savez('ICHI14_test', inputs=X_test, targets=Y_test)
np.savez('ICHI14_train', inputs=X_train, targets=Y_train)