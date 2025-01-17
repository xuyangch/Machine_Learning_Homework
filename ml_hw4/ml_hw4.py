import numpy as np
import random
from scipy.io import loadmat
import argparse
import cProfile

def chunk(iterable, chunk_size):
    """Generate sequences of `chunk_size` elements from `iterable`."""
    iterable = iter(iterable)
    while True:
        chunk = []
        try:
            for _ in range(chunk_size):
                chunk.append(iterable.__next__())
            yield chunk
        except StopIteration:
            if chunk:
                yield chunk
            break

def sigmoid(x, deri=False):
    if deri:
        fx = sigmoid(x)
        return fx * (1 - fx)
    else:
        return 1/(1 + np.exp(-x))

def tanh(x, deri=False):
    if deri:
        fx = tanh(x)
        return 1 - np.square(fx)
    else:
        return np.tanh(x)

def relu(x, deri=False):
    if deri:
        return 1 * (x > 0)
    else:
        return x * (x > 0)

def selu(x, deri=False):
    alpha = 1.67326
    lam = 1.0507
    if deri:
        return lam * (x >= 0) + lam * alpha * np.exp(x) * (x < 0)
        
    else:
        return lam * x * (x >= 0) + lam * alpha * (np.exp(x) - 1) * (x < 0)

class Layer:
    def __init__(self, in_num, out_num, activation, lr, bias, batch_size):
        self.bias = bias
        self.in_num = in_num
        self.batch_size = batch_size

        if self.bias:
            self.in_num += 1

        self.out_num = out_num
        self.lr = lr
        self.activation = activation            
        self.W = np.random.uniform(-0.3, 0.3, (self.out_num, self.in_num))
        self.W[:, self.in_num - 1] = 0
        # print(self.W)
        self.input = None
        self.output = None
        self.derivative = np.zeros((self.out_num, self.in_num))

        self.gpwx = None            
        self.wx = None
        self.gpld = None

    def forward(self, inp, force_batch_size=None):
        if self.bias:
            if force_batch_size is None:
                inp = np.vstack((inp, np.ones((1, self.batch_size))))
            else:
                inp = np.vstack((inp, np.ones((1, force_batch_size))))
            #inp = np.append(inp, 1)

        self.input = inp
        #self.input = np.append(self.input, 1)
        self.wx = np.matmul(self.W, self.input)
        #self.wx = np.squeeze(self.wx)
        self.output = self.activation(self.wx)
        return self.output
    
    def update_delta_w(self, lam):
        assert not self.input is None, "Input is None!"
        # lam = np.squeeze(lam)
        # gprime
        self.gpwx = self.activation(self.wx, deri=True)
        self.gpld = self.gpwx * lam
        
        self.derivative = np.einsum('ik,jk->ij', self.gpld, self.input)
        
        self.derivative /= self.batch_size        
        #self.derivative = np.outer(self.gpld, self.input)
    
    def get_lambda(self):
        lam = np.matmul(self.W.T, self.gpld)        
        if not self.bias:
            return lam
        else:
            return lam[:-1]

    
    def update_w(self):
        self.W = self.W - self.lr * self.derivative
        #self.derivative(0)

class Network:
    def __init__(self, neurals, activation, label_nums, lr, batch_size, loss, bias=False):
        self.bias = bias
        self.label_nums = int(label_nums)
        self.layers = []
        self.batch_size = batch_size
        self.lr = lr
        self.loss = loss
        for inp, outp in zip(neurals, neurals[1:]):
            self.layers.append(Layer(inp, outp, activation, self.lr, self.bias, self.batch_size))

    def train_once(self, inp, exp, one_hot = False):
        if one_hot:
            exp_hot = np.zeros((self.label_nums, self.batch_size))
            exp_hot[exp, np.arange(self.batch_size)] = 1
            exp = exp_hot

        output = self.forward(inp)
        self.back_propagation(output, exp)
        if self.loss == 'square':
            return np.sum((output - exp)**2)
        else:
            ce = -np.log(self.softmax(output)) * exp
            return np.sum(ce)

    def forward(self, inp, force_batch_size=None, one_hot=False):
        output = inp
        for layer in self.layers:
            output = layer.forward(output, force_batch_size)
        if one_hot:
            return np.argmax(output,axis=0)
        return output

    def softmax(self, x):
        exps = np.exp(x)

        return exps / np.sum(exps, axis=0)

    def back_propagation(self, output, expect):
        if self.loss == 'square':
            lam = output - expect
        elif self.loss == 'cross_entropy':            
            lam = self.softmax(output) - expect

        for layer in reversed(self.layers):
            layer.update_delta_w(lam)
            lam = layer.get_lambda()

        for layer in self.layers:
            layer.update_w()

def prepare_test_data(train_size, test_size):
    x = loadmat('digits.mat')
    test_imgs = x['testImages']
    train_imgs = x['trainImages']
    test_labels = x['testLabels'].astype(np.int8)
    train_labels = x['trainLabels'].astype(np.int8)    

    test_imgs = test_imgs.reshape(784, 10000)
    train_imgs = train_imgs.reshape(784, 60000)
    avg = train_imgs.mean(axis=1).reshape(784)
    maxi = train_imgs.max(axis=1).reshape(784)
    mini = train_imgs.min(axis=1).reshape(784)
    maxmin = (maxi[:, None] - mini[:, None])
    test_x = np.divide((test_imgs - avg[:, None]), maxmin, where=maxmin!=0)
    train_x = np.divide((train_imgs - avg[:, None]), maxmin, where=maxmin!=0)
    
    test_size_all = test_x.shape[1]
    train_size_all = train_x.shape[1]

    #print(train_size_all)
    #print(test_size_all)
    #print(train_size)
    #print(test_size)
    test_selected_rows = random.sample(range(test_size_all),k=test_size)
    train_selected_rows = random.sample(range(train_size_all),k=train_size)

    return train_x[:, train_selected_rows], train_labels[:, train_selected_rows], \
        test_x[:, test_selected_rows], test_labels[:, test_selected_rows]

def test(network, test_x, test_labels, test_size):    
    sz = test_size
    correct = 0
    prediction = network.forward(test_x, one_hot=True,force_batch_size=sz)
    correct = np.sum(prediction == test_labels)            
    print("Accuracy: {}".format(correct / sz))
    return correct / sz

def main():
    #random.seed(3614)
    print 
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-network",
        nargs="+",  # expects ≥ 0 arguments
        type=int,
        default=[784, 300, 10],  # default list if no arg value
    )
    parser.add_argument(
        "-train_size",
        nargs="?",  # expects ≥ 0 arguments
        type=int,
        default=60000
    )
    parser.add_argument(
        "-test_size",
        nargs="?",  # expects ≥ 0 arguments
        type=int,
        default=10000
    )
    parser.add_argument(
        "-lr",
        nargs="?",  # expects ≥ 0 arguments
        type=float,
        default=0.001
    )
    parser.add_argument(
        "-epochs",
        nargs="?",  # expects ≥ 0 arguments
        type=int,
        default=200
    )
    parser.add_argument(
        "-batch_size",
        nargs="?",  # expects ≥ 0 arguments
        type=int,
        default=64
    )
    parser.add_argument(
        "-activation",        
        default='sigmoid',
        choices=['sigmoid','tanh','relu','selu']
    )
    parser.add_argument(
        "-loss",        
        default='square',
        choices=['square', 'cross_entropy']
    )

    args = parser.parse_args()
    print(args)
    train_size = args.train_size
    test_size = args.test_size
    structure = args.network
    lr = args.lr
    batch_size = args.batch_size
    epochs = args.epochs
    num_labels = 10
    activation = None
    if args.activation == 'sigmoid':
        activation = sigmoid
    elif args.activation == 'tanh':
        activation = tanh
    elif args.activation == 'relu':
        activation = relu
    elif args.activation == 'selu':
        activation = selu
    loss = args.loss

    max_acc = 0

    train_x, train_labels, test_x, test_labels = prepare_test_data(train_size, test_size)
    network = Network(structure, activation, num_labels, lr, batch_size, loss, bias=True)
    # t = test(network, test_x, test_labels, test_size)
    for epoch in range(epochs):
        indexes = random.sample(range(train_size),k=train_size)        
        indexes += random.sample(range(train_size),k= batch_size - (train_size % batch_size))
        mse = 0
        for i in chunk(iter(indexes), batch_size):
            mse += network.train_once(train_x[:, i],train_labels[0][i],one_hot=True)

        mse /= train_size

        if ((epoch + 1) % 1 ==0):
            print("epoch {} completes".format(epoch + 1))
            print("mse is: {}".format(mse))
            #t = test(network, train_x, train_labels, train_size)
            t = test(network, test_x, test_labels, test_size)
            if max_acc < t:
                max_acc = t
            print("max accuracy is: {}".format(max_acc))
    
    # test(network, test_x, test_labels, test_size)
    # test(network, train_x, train_labels, train_size)
    print("max accuracy is: {}".format(max_acc))

if __name__ == "__main__":
    #cProfile.run('main()')
    main()