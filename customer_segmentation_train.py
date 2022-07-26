# -*- coding: utf-8 -*-
"""Customer_Segmentation_train.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1T0dhh7LAojDREjf9otVbAjLyhqvEdl2B

IMPORT NECESSARY PACKAGES
"""

import os
import pickle
import datetime
import numpy as np
import pandas as pd
import seaborn as sns
import missingno as msno
import scipy.stats as ss
import matplotlib.pyplot as plt

from sklearn.impute import KNNImputer
from tensorflow.keras.utils import plot_model
from tensorflow.keras import Sequential, Input
from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import OneHotEncoder
from sklearn.metrics import ConfusionMatrixDisplay
from tensorflow.keras.callbacks import TensorBoard
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from tensorflow.keras.callbacks import EarlyStopping
from sklearn.metrics import confusion_matrix, classification_report
from tensorflow.keras.layers import Dense, Dropout, BatchNormalization
from customer_segmentation_module import EDA, ModelDevelopment, ModelEvaluation

"""#STEP 1) DATA LOADING"""

CSV_PATH = os.path.join(os.getcwd(),'Train.csv')
cs_df = pd.read_csv(CSV_PATH)

CS_MODEL_SAVE_PATH = os.path.join(os.getcwd(),'cs_model.h5')

"""#STEP 2) DATA VISUALIZATION / INSPECTION

Check dataset's head
"""

cs_df.head()

"""Drop any necessary columns"""

cs_df = cs_df.drop(labels=['id', 'days_since_prev_campaign_contact'],axis=1)

"""Identify categorical and continous columns"""

categorical_col = ['job_type', 'marital', 'education', 'default', 'housing_loan', 'personal_loan', 
                   'communication_type', 'day_of_month','month','prev_campaign_outcome','term_deposit_subscribed']

continouos_col = cs_df.drop(labels=categorical_col, axis=1).columns

cs_df.info()

cs_df.describe().T

"""Check missing NaN"""

msno.matrix(cs_df)

"""Check outliers"""

cs_df.boxplot()

"""Check duplicates"""

cs_df.duplicated().sum()

"""Categorical Graph"""

eda = EDA()
eda.countplot_graph(categorical_col, cs_df)

"""Continouos Graph"""

eda.displot_graph(continouos_col, cs_df)

"""#STEP 3) DATA CLEANING

Check NaNs
"""

cs_df.isna().sum()

msno.bar(cs_df)

"""x - Label Encoder (features)"""

for i in categorical_col:
    if i == 'term_deposit_subscribed':
        continue
    else:
        le = LabelEncoder()
        temp = cs_df[i]
        temp[temp.notnull()] = le.fit_transform(temp[cs_df[i].notnull()])
        cs_df[i] = pd.to_numeric(cs_df[i],errors='coerce')
        PICKLE_SAVE_PATH = os.path.join(os.getcwd(),i+'_encoder.pkl')
        with open(PICKLE_SAVE_PATH,'wb') as file:
            pickle.dump(le,file)

"""Remove NaN

KNN
"""

knn_im = KNNImputer ()
df_imputed = knn_im.fit_transform(cs_df)
df_imputed = pd.DataFrame(df_imputed, index=None)
df_imputed.columns = cs_df.columns

df_imputed['customer_age'] = np.floor(df_imputed['customer_age'])
df_imputed['personal_loan	'] = np.floor(df_imputed['personal_loan'])
df_imputed['last_contact_duration'] = np.floor(df_imputed['last_contact_duration'])

cs_df = df_imputed

"""DUPLICATED

There is no duplicate so no need to drop it.

#STEP 4) FEATURE SELECTION
"""

X = cs_df.drop(labels='term_deposit_subscribed', axis=1)
y = cs_df['term_deposit_subscribed'].astype(int)

selected_features = []

for i in continouos_col:
    lr = LogisticRegression()
    lr.fit(np.expand_dims(X[i],axis=1),y)
    print(i)
    print(lr.score(np.expand_dims(X[i],axis=-1),y))
    if lr.score(np.expand_dims(X[i],axis=-1),y) > 0.7:
        selected_features.append(i)

for i in categorical_col:
    print(i)
    matrix = pd.crosstab(cs_df[i],y).to_numpy()
    print(EDA().cramers_corrected_stat(matrix))
    if EDA().cramers_corrected_stat(matrix) > 0.3:
        selected_features.append(i)

"""#STEP 5) PREPROCESSING"""

ohe = OneHotEncoder(sparse=False)
y = ohe.fit_transform(np.array(y).reshape(-1,1))

X_train, X_test, y_train, y_test = train_test_split(X, y,
                                                    test_size=0.3,
                                                    random_state=123)

"""#MODEL DEVELOPMENT"""

input_shape = np.shape(X_train)[1:]
nb_class = len(np.unique(y_train, axis=0))

md = ModelDevelopment()
model = md.sequential_model(input_shape, nb_class, nb_node=128, droput_rate=0.3)

plot_model(model, show_shapes=True, show_layer_names=True)

"""# TENSORBOARD

Load the TensorBoard notebook extension
"""

# Commented out IPython magic to ensure Python compatibility.
# %load_ext tensorboard

LOGS_PATH = os.path.join(os.getcwd(),'logs',datetime.datetime.now().
                         strftime('%Y%m%d-%H%M%S'))

tensorboard_callback = TensorBoard(log_dir=LOGS_PATH,histogram_freq=1)
early_callback = EarlyStopping(monitor='val_loss', patience=3)

"""# MODEL COMPILATION"""

model.compile(optimizer='adam',
              loss = 'categorical_crossentropy',
              metrics=['acc'])

"""# MODEL TRAINING"""

hist = model.fit(X_train, y_train, epochs=20, validation_data=(X_test, y_test),
                 callbacks = [tensorboard_callback, early_callback])

# Commented out IPython magic to ensure Python compatibility.
# %tensorboard --logdir logs

"""#MODEL EVALUATION"""

me = ModelEvaluation()
me.plot_hist_graph(hist)

"""# **MODEL ANALYSIS**

Confusion Matrix
"""

pred_y = model.predict(X_test)
pred_y = np.argmax(pred_y, axis=1)  
true_y = np.argmax(y_test, axis=1)

cm = confusion_matrix(true_y, pred_y)
cr = classification_report(true_y, pred_y)

print(cr)

labels = ['Not_subscribe', 'Subscribe']
disp = ConfusionMatrixDisplay(confusion_matrix = cm,
                              display_labels = labels)
disp.plot(cmap = plt.cm.BuPu)
plt.show()

print(classification_report)

"""# MODEL SAVING"""

model.save(CS_MODEL_SAVE_PATH)