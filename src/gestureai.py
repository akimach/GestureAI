# coding:utf-8
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import math
import tarfile
import sys, os.path
from glob import glob
if sys.version_info[0] < 3:
    from StringIO import StringIO
else:
    from io import StringIO

import numpy as np
import pandas as pd
seed = 1234
np.random.seed(seed)

from keras.layers.core import Reshape
from keras.models import Sequential
from keras.layers import Dense, Activation
from keras.layers import LSTM, GRU
#from keras import optimizers
#from keras.wrappers.scikit_learn import KerasClassifier
#from keras.utils import np_utils


def load_dataset(path, input_dim=3, timesteps=40):
    """Load dataset of 3-axis acceleration's sequence"""
    X = []
    tar = tarfile.open(path, "r")
    files = []
    for item in tar.getmembers():
        f = tar.extractfile(item.name)
        if f and ".csv" in f.name:
            files.append(f)
    files = sorted(files, key=lambda x:x.name)
    for f in files:
        try:
            text = f.read()
            df = pd.read_csv(StringIO(text))
            arr = df.as_matrix()
            arr = np.r_[arr, np.zeros((timesteps-arr.shape[0], input_dim))]
            X.append(arr)
        except Exception, e:
            print("{} : {}".format(f.name, e), file=sys.stderr)
    return np.array(X)


def rnn(rnn_cell='LSTM', n_hidden=128, activation='tanh', optimizer='rmsprop', input_dim=3, timesteps=40, n_classes=5, coreml=False):
    model = Sequential()
    if coreml:
        model.add(Reshape(input_shape=(timesteps*input_dim,), target_shape=(timesteps, input_dim)))
    if rnn_cell == 'LSTM':
        cell = LSTM(n_hidden, input_shape=(timesteps, input_dim), activation=activation)
    elif rnn_cell == 'GRU':
        cell = GRU(n_hidden, input_shape=(timesteps, input_dim), activation=activation)
    else:
        cell = LSTM(n_hidden, input_shape=(timesteps, input_dim), activation=activation)
    model.add(cell)
    model.add(Dense(n_classes))
    model.add(Activation("softmax"))
    model.compile(loss='sparse_categorical_crossentropy',
              optimizer=optimizer,
              metrics=['accuracy'])
    return model