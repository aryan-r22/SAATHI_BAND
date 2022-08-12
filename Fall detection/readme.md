# Fall detection using Machine Learning - SAATHI
## Team 17 - Silicon Labs Entreprenuership Challenge
### **Inter IIT Tech Meet 10.0**

### Description
This machine learning algorithm detects fall detection using accelerometer and gyroscope sensors, both of which are present in our IoT based healthcare solution.

We have used the XGBoost algorithm for fall detection, which is renowned for its performance and efficiency gains. The dataset used is **SisFall: A Fall and Movement Dataset** [[1]](http://sistemic.udea.edu.co/en/investigacion/proyectos/english-falls/), which is available in open domain. We envision our model to be dynamically trained on the data collected by our device, which ensures that our algorithm adapts to the the different variations in external conditions of use.

### Running the code

- Download the dataset zip files from the following links:
```
https://drive.google.com/uc?id=1kyTRhIFhqwRkf9gERof1Xm5FVQ-klLVA
https://drive.google.com/uc?id=1gvOuxPc8dNgTnxuvPcVuCKifOf98-TV0
```
- Run `Data_preparation.py` to prepare the data in the required format for training.
- Run `Train.py` to train the XGBoost model on the generated data and save the trained model for future inference.
- Run `Eval.py` to get the metrics on the test split of the SisFall dataset.

### Metrics on Test Split
Classification Accuracy = 98.04%  
F1 Score (Weighted) = 97.95%  
Precision (Weighted) = 97.92%  
Recall (Weighted) = 98.04%  

Our model performs exceptionally well, and exceeds the performance of the existing approaches on this dataset [[2]](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5298771/).