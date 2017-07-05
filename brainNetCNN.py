from __future__ import print_function, division

import matplotlib.pyplot as plt
plt.interactive(False)
import h5py
import numpy as np
from keras.utils import np_utils
from keras.models import Sequential
from keras.layers import Conv2D,MaxPooling2D, Lambda, Conv1D
from keras.layers import Dense, Dropout, Activation, Flatten
from keras.regularizers import l2
from keras.layers.advanced_activations import LeakyReLU
from keras import optimizers, callbacks, regularizers, initializers
from keras import backend as K
from keras.engine.topology import Layer

batch_size = 14
dropout = 0.5
momentum = 0.9
lr = 0.01
decay = 0.0005

reg = regularizers.l2(decay)
kernel_init = initializers.he_uniform()


# Creating E2E,E2N, N2G layers

def E2E_conv(x,num_filters,kernel_h,kernel_w):
    conv1xd = Conv2D(num_filters,kernel_size=(kernel_h,1),strides=(1,1),padding='valid',kernel_regularizer=reg,kernel_initializer=kernel_init)(x)
    convdx1 = Conv2D(num_filters,kernel_size=(1,kernel_w),strides=(1,1),padding='valid',kernel_initializer=kernel_init,kernel_regularizer=reg)(x)
    d = kernel_h
    dup_conv1xd = K.concatenate([conv1xd]*d,axis=1)
    dup_convdx1 = K.concatenate([convdx1]*d,axis=0)
    return dup_conv1xd+dup_convdx1

def E2N_conv(x,num_filters,kernel_h,kernel_w):
    conv_1xd = Conv2D(num_filters,kernel_size=(1,kernel_w),kernel_regularizer=reg,kernel_initializer=kernel_init,strides=1)(x)
    return conv_1xd

def N2G_conv(x,num_filters,kernel_h,kernel_w):
    conv_1xd = Conv2D(num_filters,kernel_size=(kernel_h,1),kernel_regularizer=reg,kernel_initializer=kernel_init,strides=1)(x)
    return conv_1xd





# paramaters
batch_size = 14
dropout = 0.5
momentum = 0.9
lr = 0.01
decay = 0.0005


reg = regularizers.l2(decay)
kernel_init = initializers.he_uniform()


# utility functions



# Loading synthetic data

train = h5py.File('data/generated_synthetic_data/train.h5','r')
valid = h5py.File('data/generated_synthetic_data/valid.h5','r')

(x_train,y_train) = (train[u'data'][:],train[u'label'][:])
(x_valid,y_valid) = (valid[u'data'][:],valid[u'label'][:])


# reshaping data
#x_train = x_train.reshape(x_train.shape[0],x_train.shape[3],x_train.shape[2],x_train.shape[1])
#x_valid = x_valid.reshape(x_valid.shape[0],x_valid.shape[3],x_valid.shape[2],x_valid.shape[1])

print(x_train.shape)

plt.imshow(x_train[0][0])
plt.show()

# Model architecture

model = Sequential()
model.add(Lambda(E2E_conv,input_shape=(90,90,1),arguments={'kernel_h':90,'kernel_w':90,'num_filters':32}))
print(model.output_shape)
model.add(LeakyReLU(alpha=0.33))
print(model.output_shape)
model.add(Lambda(E2E_conv,input_shape=(90,90,32),arguments={'kernel_h':90,'kernel_w':90,'num_filters':32}))
print(model.output_shape)
model.add(LeakyReLU(alpha=0.33))
print(model.output_shape)
model.add(Lambda(E2N_conv,input_shape=(90,90,32),arguments={'kernel_h':90,'kernel_w':90,'num_filters':64}))
print(model.output_shape)
model.add(LeakyReLU(alpha=0.33))
print(model.output_shape)
model.add(Lambda(N2G_conv,input_shape=(90,90,32),arguments={'kernel_h':90,'kernel_w':90,'num_filters':256}))
print(model.output_shape)
model.add(LeakyReLU(alpha=0.33))
print(model.output_shape)
model.add(Dropout(0.5))
model.add(Dense(128,kernel_regularizer=reg,kernel_initializer=kernel_init))
print(model.output_shape)
model.add(LeakyReLU(alpha=0.33))
print(model.output_shape)
model.add(Dropout(0.5))
model.add(Dense(128,kernel_regularizer=reg,kernel_initializer=kernel_init))
print(model.output_shape)
model.add(LeakyReLU(alpha=0.33))
print(model.output_shape)
model.add(Dropout(0.5))
model.add(Dense(30,kernel_regularizer=reg,kernel_initializer=kernel_init))
model.add(LeakyReLU(alpha=0.33))
print(model.output_shape)
model.add(Dropout(0.5))
model.add(Dense(30,kernel_regularizer=reg,kernel_initializer=kernel_init))
model.add(LeakyReLU(alpha=0.33))
print(model.output_shape)

opt = optimizers.SGD(momentum=momentum,decay=decay,nesterov=True,lr=lr)
model.compile(optimizer=opt,loss='mean_squared_error',metrics=['mae'])
csv_logger = callbacks.CSVLogger('BrainCNN.log')
history=model.fit(x_train,y_train,batch_size=14,nb_epoch=100,verbose=1,callbacks=[csv_logger])
model.save('BrainCNN.hdf5')
model.evaluate(x_valid,y_valid)

print(model.output_shape)


