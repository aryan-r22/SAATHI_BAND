from math import sqrt
import pandas as pd
import numpy as np
import glob
import os
import zipfile
import random

random.seed(272)

import warnings
warnings.filterwarnings("ignore")

#Checking for dataset files
if not (os.path.exists('SisFall_dataset.zip') and os.path.exists('SisFall_enhanced.zip')):
    print("Download datatset files")

if not (os.path.exists('SisFall_dataset')):
    with zipfile.ZipFile('SisFall_dataset.zip',"r") as zip_ref:
        zip_ref.extractall('SisFall_dataset')

if not (os.path.exists('SisFall_enhanced')):
    with zipfile.ZipFile('SisFall_enhanced.zip',"r") as zip_ref:
        zip_ref.extractall('SisFall_enhanced')


#Appending all files to the path
def get_file_name(path):
  allfiles = []
  allFolders = glob.glob(path + "*")
  for files in allFolders:
      allfiles.append(glob.glob(files+"/*.txt"))
  if 'desktop.ini' in allfiles:
        allfiles.remove('desktop.ini')
  return np.hstack(allfiles)

#Reading data into pandas dataframe
def read_data(data_path):
    data = pd.read_csv(data_path, header=None)
    data.columns = ['ADXL345_x', 'ADXL345_y', 'ADXL345_z', 'ITG3200_x', 'ITG3200_y', 'ITG3200_z', 'MMA8451Q_x',
                    'MMA8451Q_y', 'MMA8451Q_z']
    data['MMA8451Q_z'] = data['MMA8451Q_z'].map(lambda x: str(x)[:-1])
    for name in data.columns :
      data[name] = data[name].astype(float)
    return data

#Computing features
def add_features(dataset,data_path):
    new_dataset = pd.DataFrame()
    new_dataset['acc_1'] = dataset.apply(
        lambda row: sqrt((row.ADXL345_x ** 2 + row.ADXL345_y ** 2 + row.ADXL345_z ** 2)), axis=1)
    new_dataset['acc_2'] = dataset.apply(
        lambda row: sqrt((row.MMA8451Q_x ** 2 + row.MMA8451Q_y ** 2 + row.MMA8451Q_z ** 2)), axis=1)
    new_dataset['geo'] = dataset.apply(
        lambda row: sqrt((row.ITG3200_x ** 2 + row.ITG3200_y ** 2 + row.ITG3200_z ** 2)), axis=1)
    new_dataset['label'] = get_label(data_path)
    return np.round(new_dataset.to_numpy(),2)

#Get labels for each file
def get_label(data_path):
    label = data_path[21]
    if label =='D':
      return int(0)
    elif label =='F':  
      label_path = data_path.replace('dataset','enhanced')
      labels = pd.read_csv(label_path,header=None)
      labels[labels == 2] = 1
      return labels

#Split data into test and train (30% - 70%)
def split_address(dataset_address):
  np.random.shuffle(dataset_address)
  train, test = np.split(dataset_address, [int(len(dataset_address)*0.7)])
  return train, test

#Converting datasets to numpy array
def datasets_to_nparray(datasets_address_array):
  result = np.empty((0, 4), int)
  for address in datasets_address_array:
    result = np.concatenate(
        (result,add_features(read_data(address),address)),axis=0)
  return result

#Performing windowing for time series data
def windowing(dataset,window_size = 200):
  window = window_size * (dataset.shape[1]-1)
  cut = dataset.shape[0] % window_size
  feature = dataset[:-cut,0:-1]
  label = dataset[:-cut,-1]
  feature = feature.ravel().reshape(feature.size//window,window)
  label = label.reshape(label.size//window_size,window_size)
  label = label.sum(axis=1)
  label[label > 0] = 1
  return feature,label

#Converting data points to tensors
def dataset_to_tensor(test,train,window_size):
  test_feature , test_label = windowing(datasets_to_nparray(test),window_size)
  np.savez('Sisfall_data_test', inputs=test_feature, targets=test_label)
  train_feature , train_label = windowing(datasets_to_nparray(train),window_size)
  np.savez('Sisfall_data_train', inputs=train_feature, targets=train_label)


train, test = split_address(get_file_name("SisFall_dataset/"))
window_size = 200
dataset_to_tensor(test,train,window_size)