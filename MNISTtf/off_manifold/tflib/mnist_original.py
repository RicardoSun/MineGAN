import numpy

import os
import urllib
import gzip
#import cPickle as pickle
import pickle
import pdb
import math

def mnist_generator(data, batch_size, n_labelled, limit=None, selecting_label = None, bias = None):
    images, targets = data
    if bias is not None :
        images = images[targets!=bias] 
        targets = targets[targets!=bias] 
    if selecting_label is None:
        rng_state = numpy.random.get_state()
        numpy.random.shuffle(images)
        numpy.random.set_state(rng_state)
        numpy.random.shuffle(targets)
    else:
        images = images[targets == selecting_label[0]] 

        targets = targets[targets == selecting_label[0]]

        rng_state = numpy.random.get_state()
        numpy.random.shuffle(images)
        numpy.random.set_state(rng_state)
        numpy.random.shuffle(targets)
    
    def rounddown(x):
        return int(math.floor(x / 100.0)) * 100
        
    if limit is not None:
        if len(images) > 4500:
            L = 4500
        elif len(images) > 4400 and len(images) < 4500:
            L = 4400
        elif len(images) > 4300 and len(images) < 4400:
            L = 4300
        elif len(images) > 4200 and len(images) < 4300:
            L = 4200
        else:
            #L = 4000
            #L=rounddown(len(images))
            L=1000
        print("WARNING ONLY FIRST {} MNIST DIGITS".format(L))
        images = images.astype('float32')[:L]
        targets = targets.astype('int32')[:L]
    if n_labelled is not None:
        labelled = numpy.zeros(len(images), dtype='int32')
        labelled[:n_labelled] = 1
        
    def get_epoch():
        rng_state = numpy.random.get_state()
        numpy.random.shuffle(images)
        numpy.random.set_state(rng_state)
        numpy.random.shuffle(targets)

        if n_labelled is not None:
            numpy.random.set_state(rng_state)
            numpy.random.shuffle(labelled)

        image_batches = images.reshape(-1, batch_size, 784)
        target_batches = targets.reshape(-1, batch_size)
        
        if n_labelled is not None:
            labelled_batches = labelled.reshape(-1, batch_size)

            for i in xrange(len(image_batches)):
                yield (numpy.copy(image_batches[i]), numpy.copy(target_batches[i]), numpy.copy(labelled))

        else:
            for i in xrange(len(image_batches)):
                yield (numpy.copy(image_batches[i]), numpy.copy(target_batches[i]))
        
    return get_epoch

def load(batch_size, test_batch_size, n_labelled=None, limit= 50000, selecting_label = None, bias = None):
    filepath = '/tmp/mnist.pkl.gz'
    url = 'http://www.iro.umontreal.ca/~lisa/deep/data/mnist/mnist.pkl.gz'

    if not os.path.isfile(filepath):
        print("Couldn't find MNIST dataset in /tmp, downloading...")
        urllib.urlretrieve(url, filepath)

    with gzip.open('/tmp/mnist.pkl.gz', 'rb') as f:
        train_data, dev_data, test_data = pickle.load(f)
        
    epoch_function_test=mnist_generator(test_data, test_batch_size, n_labelled, limit=len(test_data[1]), selecting_label = selecting_label, bias = bias)
    epoch_function_train=mnist_generator(train_data, batch_size, n_labelled, limit=len(train_data[1]), selecting_label = selecting_label, bias = bias)
    epoch_function_dev=mnist_generator(dev_data, test_batch_size, n_labelled, limit=len(dev_data[1]), selecting_label = selecting_label, bias = bias)
    
    return epoch_function_train,epoch_function_dev,epoch_function_test
        
        
        
        
        #mnist_generator(train_data, batch_size, n_labelled, limit=limit, selecting_label = selecting_label, bias = bias), 
        #mnist_generator(dev_data, test_batch_size, n_labelled, limit=10*test_batch_size, selecting_label = selecting_label, bias = bias), 
        #mnist_generator(test_data, test_batch_size, n_labelled, limit=10*test_batch_size, selecting_label = selecting_label, bias = bias)
    
    