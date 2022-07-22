# -*- coding: utf-8 -*-
"""Customer_Segmentation_module.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1hwDIEbvhCiNM4OfPoxi2hCntVy6OSIWl

MODULE
"""

import numpy as np
import seaborn as sns
import scipy.stats as ss
import matplotlib.pyplot as plt

from tensorflow.keras import Sequential, Input
from sklearn.metrics import confusion_matrix, classification_report
from tensorflow.keras.layers import Dense, Dropout, BatchNormalization

class EDA:
  def displot_graph(self, continous_col, df):
    # for continous data
    for i in continous_col:
      plt.figure()
      sns.displot(df[i])
      plt.show()

  def countplot_graph(self, categorical_col, df):
    # for categorical data
    for i in categorical_col:
      plt.figure()
      sns.countplot(df[i])
      plt.show()

  def cramers_corrected_stat(self,confusion_matrix):
    """ calculate Cramers V statistic for categorial-categorial association.
        uses correction from Bergsma and Wicher,
        Journal of the Korean Statistical Society 42 (2013): 323-328
    """
    chi2 = ss.chi2_contingency(confusion_matrix)[0]
    n = confusion_matrix.sum()
    phi2 = chi2/n
    r,k = confusion_matrix.shape
    phi2corr = max(0, phi2 - ((k-1)*(r-1))/(n-1))
    rcorr = r - ((r-1)**2)/(n-1)
    kcorr = k - ((k-1)**2)/(n-1)
    return np.sqrt(phi2corr / min( (kcorr-1), (rcorr-1)))

class ModelDevelopment:
  def sequential_model(self, input_shape, nb_class, nb_node=128, droput_rate=0.3):

    model = Sequential()
    model.add(Input(shape=(input_shape)))
    model.add(Dense(nb_node, activation='relu'))
    model.add(BatchNormalization())
    model.add(Dropout(droput_rate))
    model.add(Dense(nb_node, activation='relu'))
    model.add(BatchNormalization())
    model.add(Dropout(droput_rate))
    model.add(Dense(nb_class, activation='softmax'))
    model.summary()

    return model

class ModelEvaluation:
  def plot_hist_graph(self,hist):
    plt.figure()
    plt.plot(hist.history['loss'])
    plt.plot(hist.history['val_loss'])
    plt.legend(['Training Loss', 'Validation Loss'])
    plt.show()

    plt.figure()
    plt.plot(hist.history['acc'])
    plt.plot(hist.history['val_acc'])
    plt.legend(['Training Acc', 'Validation Acc'])
    plt.show()



