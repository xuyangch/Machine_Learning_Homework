from scipy.io import loadmat
import numpy as np
import random
from numpy import linalg as LA
import math
import sys

#random.seed(datetime.now())
def main():
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


    category_true = [0]
    category_false = [1,2,3,4,5,6,7,8,9]
    print("category true: {}".format(category_true))
    print("category false: {}".format(category_false))
    test_given_class_svm(train_x, train_labels, test_x, test_labels, category_true,
    category_false)

    category_true = [7]
    category_false = [0,1,2,3,4,5,6,8,9]
    print("category true: {}".format(category_true))
    print("category false: {}".format(category_false))
    test_given_class_svm(train_x, train_labels, test_x, test_labels, category_true,
    category_false)


    category_true = [4]
    category_false = [9]
    print("category true: {}".format(category_true))
    print("category false: {}".format(category_false))
    test_given_class_svm(train_x, train_labels, test_x, test_labels, category_true,
    category_false)


    category_true = [0]
    category_false = [8]
    print("category true: {}".format(category_true))
    print("category false: {}".format(category_false))
    test_given_class_svm(train_x, train_labels, test_x, test_labels, category_true,
    category_false)


    category_true = [0,8,3]
    category_false = [1,7,9]
    print("category true: {}".format(category_true))
    print("category false: {}".format(category_false))
    test_given_class_svm(train_x, train_labels, test_x, test_labels, category_true,
    category_false)

def test_given_class_svm(train_x, train_labels, test_x, test_labels,
        category_true, category_false):

    print(test_x.shape)    

    svm = test_mnist_with_given_category(category_true, category_false,
        1000, 1000, train_x, train_labels)

    print("Start Testing")
    final_svm_test_x = None

    for category in category_true:
        (svm_test_x, svm_test_label) = \
        generate_training_given_category(category, 1, test_x, test_labels, None)
        if final_svm_test_x is None:
            final_svm_test_x = svm_test_x
            final_svm_test_label = svm_test_label
        else:
            final_svm_test_x = np.concatenate((final_svm_test_x, svm_test_x), axis=1)
            final_svm_test_label = np.concatenate((final_svm_test_label, svm_test_label), axis=1)

    for category in category_false:
        (svm_test_x, svm_test_label) = \
        generate_training_given_category(category, -1, test_x, test_labels, None)
        if final_svm_test_x is None:
            final_svm_test_x = svm_test_x
            final_svm_test_label = svm_test_label
        else:
            final_svm_test_x = np.concatenate((final_svm_test_x, svm_test_x), axis=1)
            final_svm_test_label = np.concatenate((final_svm_test_label, svm_test_label), axis=1)

    svm.test(final_svm_test_x, final_svm_test_label)    
    print("End Testing")

def test_multi_class_svm():
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
    svms = []
    test_size = test_x.shape[1]

    categories = 10

    for i in range (categories):
        svms.append(test_mnist_with_category(i, train_x, train_labels, test_x, test_labels))
    
    correct = 0

    print("Start Testing")
    for i in range(test_size):
        maxi = 0
        prediction = 0
        for j in range(categories):
            res = svms[j].pred(test_x.T[i])
            if maxi < res:
                maxi = res
                prediction = j
        if prediction == test_labels[0][i]:
            correct += 1
    print("End Testing")
    print("accuracy is: {}".format(correct/test_size))

def test_mnist_with_category(category, train_x, train_labels, test_x, test_labels):    
    radical_basis_kernel.sigma = 5
    print("sigma is {}".format(radical_basis_kernel.sigma))
    kernel = radical_basis_kernel
    
    positive_sample_num = 120
    false_sample_num = 960
    test_pos_num = 5
    test_false_num = 7

    print("positive_sample_num: {}".format(positive_sample_num))
    print("false_sample_num: {}".format(false_sample_num))
    print("test_pos_num: {}".format(test_pos_num))
    print("test_false_num: {}".format(test_false_num))
    
    print("Start generating data...")
    (svm_train_x, svm_train_label, svm_test_x, svm_test_label) = \
        generate_data(category, train_x, train_labels, test_x, test_labels, 
        positive_sample_num, false_sample_num, test_pos_num, test_false_num)
    print("Generating data successful...")    
    print("SVM training size is: {}".format(svm_train_x.shape))
    print("SVM testing size is: {}".format(svm_test_x.shape))

    sample_nums = svm_train_x.shape[1]    
    
    print("Init SVM and GRAM Matrix...")
    svm = SVM(sample_nums, svm_train_x, svm_train_label, kernel)
    print("Initialization successful")
    print("Start training...")
    svm.train(C=1, max_iter=60, epsilon=0.000001)
    print("Training successful")
    
    #print("Start testing...")
    #print(svm.test(svm_test_x, svm_test_label))
    #print("Testing successful")
    return svm

def test_mnist_with_given_category(category_pos, category_false, 
        positive_sample_num, false_sample_num, 
        train_x, train_labels):
    radical_basis_kernel.sigma = 3
    print("sigma is {}".format(radical_basis_kernel.sigma))
    kernel = radical_basis_kernel
    
    positive_per_num = int(positive_sample_num / len(category_pos))
    false_per_num = int(false_sample_num / len(category_false))

    print("positive_sample_num: {}".format(positive_sample_num))
    print("false_sample_num: {}".format(false_sample_num))
    print("Start generating data...")
    final_svm_train_x = None
    final_svm_train_label = None
    for category in category_pos:
        (svm_train_x, svm_train_label) = \
            generate_training_given_category(category, 1, train_x, train_labels, positive_per_num)

        if final_svm_train_x is None:
            final_svm_train_x = svm_train_x
            final_svm_train_label = svm_train_label
        else:
            final_svm_train_x = np.concatenate((final_svm_train_x, svm_train_x), axis=1)
            final_svm_train_label = np.concatenate((final_svm_train_label, svm_train_label), axis=1)
    
    for category in category_false:
        (svm_train_x, svm_train_label) = \
        generate_training_given_category(category, -1, train_x, train_labels, false_per_num)
        if final_svm_train_x is None:
            final_svm_train_x = svm_train_x
            final_svm_train_label = svm_train_label
        else:
            final_svm_train_x = np.concatenate((final_svm_train_x, svm_train_x), axis=1)
            final_svm_train_label = np.concatenate((final_svm_train_label, svm_train_label), axis=1)

    final_train_sz = final_svm_train_x.shape[1]

    selected_rows = random.sample(range(final_train_sz),k=final_train_sz)

    final_svm_train_x = final_svm_train_x[:, selected_rows]
    final_svm_train_label = final_svm_train_label[:, selected_rows]

    print("Generating data successful...")    
    print("SVM training size is: {}".format(final_svm_train_x.shape))

    sample_nums = final_svm_train_x.shape[1]    
    
    print("Init SVM and GRAM Matrix...")
    svm = SVM(sample_nums, final_svm_train_x, final_svm_train_label, kernel)
    print("Initialization successful")
    print("Start training...")
    svm.train(C=1, max_iter=60, epsilon=0.000001)
    print("Training successful")
    
    #print("Start testing...")
    #print(svm.test(svm_test_x, svm_test_label))
    #print("Testing successful")
    return svm

def test_mnist():
    kernel = None
    print(sys.argv[1] + " kernel")
    if (sys.argv[1] == 'poly'):
        polynomial_kernel.c = float(sys.argv[2])
        polynomial_kernel.d = int(sys.argv[3])
        print("c is {}".format(polynomial_kernel.c))
        print("d is {}".format(polynomial_kernel.d))
        kernel = polynomial_kernel
    elif (sys.argv[1] == 'radical'):
        radical_basis_kernel.sigma = int(sys.argv[2])
        print("sigma is {}".format(radical_basis_kernel.sigma))
        kernel = radical_basis_kernel
    
    category = 1
    
    positive_sample_num = 50
    false_sample_num = 200
    test_pos_num = None
    test_false_num = None

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

    print("positive_sample_num: {}".format(positive_sample_num))
    print("false_sample_num: {}".format(false_sample_num))
    print("test_pos_num: {}".format(test_pos_num))
    print("test_false_num: {}".format(test_false_num))
    
    print("Start generating data...")
    (svm_train_x, svm_train_label, svm_test_x, svm_test_label) = \
        generate_data(category, train_x, train_labels, test_x, test_labels, 
        positive_sample_num, false_sample_num, test_pos_num, test_false_num)
    print("Generating data successful...")    
    print("SVM training size is: {}".format(svm_train_x.shape))
    print("SVM testing size is: {}".format(svm_test_x.shape))

    sample_nums = svm_train_x.shape[1]    
    
    print("Init SVM and GRAM Matrix...")
    svm = SVM(sample_nums, svm_train_x, svm_train_label, kernel)
    print("Initialization successful")
    print("Start training...")
    svm.train(C=np.inf, max_iter=60, epsilon=0.000001)
    print("Training successful")
    
    print("Start testing...")
    print(svm.test(svm_test_x, svm_test_label))
    print("Testing successful")

def xor_3_kernel(x, y):
    assert x.shape == y.shape, "kernel arguments do not have the same shape"
    assert x.shape == (2,), "kernel arguments are not 1D vector"
    
    return (np.square(x[0]) - np.square(x[1])) * (np.square(y[0]) - np.square(y[1])) + \
                x[0] * x[1] * y[0] * y[1] + \
                    (np.square(x[0]) + np.square(x[1])) * (np.square(y[0]) + np.square(y[1]))

def polynomial_kernel(x, y):    
    assert x.shape == y.shape, "kernel arguments do not have the same shape"
    assert len(x.shape)  == 1
    return (np.dot(x, y) + polynomial_kernel.c) ** polynomial_kernel.d

def radical_basis_kernel(x, y):
    assert x.shape == y.shape, "kernel arguments do not have the same shape"
    # print (LA.norm(x - y))
    return math.exp(-np.square(LA.norm(x - y))/(2 * np.square(radical_basis_kernel.sigma)))

class SVM:
    """
    Args:
        N: training sample sizes, equal to the length of W
        kernel: kernel function
    """
    def __init__(self, N, train_x, train_labels, kernel):
        assert train_x.shape[1] == train_labels.shape[1], "training sample size != label size"
        assert train_x.shape[1] == N, "training sample size != N"
        self.N = N
        self.kernel = kernel
        
        self.train_x = train_x
        self.labels = train_labels.reshape(N)        
        
        # weights
        self.W = np.zeros(N)
        self.b = 0
        
        # Gram matrix
        self.Gram = np.zeros((N, N))
        for i in range(self.N):
            for j in range(i+1):
                self.Gram[i][j] = kernel(self.train_x.T[i], self.train_x.T[j])
                self.Gram[j][i] = self.Gram[i][j]
        
        self.update_pred()
        #print(self.Gram)

        # intrinsic variables
        self.feature_sz = train_x.shape[0]
        self.C = 1
        self.epsilon = 0.001
        self.max_iter = 50
    
    """
    Args: 
        epsilon: training threshold
        C: weight range
    """
    
    def train(self, C=1, max_iter=50, epsilon=0.001):
        self.C = C
        self.max_iter = max_iter
        self.epsilon = epsilon
        
        real_it = 0
        iteration = 0
        
        while iteration < self.max_iter:
            pair_changed = 0

        #while iteration < self.max_iter:
            # select Wi and Wj to update. Select those make |E1-E2| maximal            
            i = 0
            for i in random.sample(range(self.N),k=self.N):
                Ei = self.pred_with_id(i) - self.labels[i]
                max_E = 0
                j = 0
                tj = 0
                for j in range(self.N):
                    Ej = self.pred_with_id(j) - self.labels[j]
                    if abs(Ei - Ej) > max_E:
                        max_E = abs(Ei - Ej)
                        tj = j

                j = tj                        
                yi = self.labels[i]
                yj = self.labels[j]
                Wi_old = self.W[i]
                Wj_old = self.W[j]
                
                eta = self.Gram[i][i] + self.Gram[j][j] - 2 * self.Gram[i][j]
                if (eta <= 0 + self.epsilon):
                    continue
                
                Wj_new = Wj_old + yj * (Ei - Ej) / eta
                
                L = 0
                H = 0
                
                if yi != yj:
                    L = max(0, Wj_old - Wi_old) 
                    H = min(self.C, self.C + Wj_old - Wi_old)
                else:
                    L = max(0, Wi_old + Wj_old - self.C) 
                    H = min(self.C, Wi_old + Wj_old)
                    
                Wj_new = self.clip(Wj_new, L, H)
                Wi_new = Wi_old + yi * yj * (Wj_old - Wj_new)
                self.W[j] = Wj_new
                self.W[i] = Wi_new

                if abs(Wj_new - Wj_old) < self.epsilon:
                    continue

                bi_new = -Ei - yi * self.Gram[i][i] * (Wi_new - Wi_old) - yj * self.Gram[j][i] * (Wj_new - Wj_old) + self.b#+ Wi_old * yi * self.Gram[i][i] + Wj_old * yj * self.Gram[j][i] + self.b - \
                             #       Wi_new * yi * self.Gram[i][i] - Wj_new * yj * self.Gram[j][i]
                
                bj_new = -Ej - yi * self.Gram[i][j] * (Wi_new - Wi_old) - yj * self.Gram[j][j] * (Wj_new - Wj_old) + self.b #yi * self.Gram[i][j] * (Wi_new - Wi_old) - \
                                #yj * self.Gram[j][j] * (Wj_new - Wj_old) + self.b
                
                if 0 < Wi_new < self.C:
                    b_new = bi_new
                elif 0 < Wj_new < C:
                    b_new = bj_new
                else:
                    b_new = (bi_new + bj_new) / 2
                    
                self.b = b_new
                self.update_pred()
                
                pair_changed += 1            

            if pair_changed == 0:
                iteration += 1
            else:
                iteration = 0


            real_it += 1            

            if real_it % 30 == 0:
                print("{}th iteration finishes".format(real_it))

            if self.C > 100 and real_it > 200:
                break
            if real_it % 5 == 0:
                KKT_satisfy = True
                if ((self.W >= (0 - self.epsilon)) & (self.W <= (self.C + self.epsilon))).size > 0:
                    KKT_satisfy = False

                if KKT_satisfy:
                    if abs(np.matmul(self.W, self.labels)) > self.epsilon:
                        KKT_satisfy = False

                if KKT_satisfy:
                    tmp = self.labels * self.prediction
                    for i in range(self.N):
                        if self.W[i] <= 0:
                            if tmp[i] < 1 - self.epsilon:
                                KKT_satisfy = False
                                break
                        elif self.W[i] >= C:
                            if tmp[i] > 1 + self.epsilon:
                                KKT_satisfy = False
                                break
                        else:
                            if abs(tmp[i] - 1) > self.epsilon:
                                KKT_satisfy = False
                                break

                if KKT_satisfy:
                    print("Early stop!")
                    break

    def test(self, test_x, test_label):    
        assert len(test_x.shape) == 2, "test_x shape not right"
        tp = 0
        fn = 0
        fp = 0
        tn = 0
        no = 0
        sz = test_x.shape[1]
        correct = 0        
        for i in range(sz):
            prediction = self.pred(test_x.T[i])
            label = test_label[0][i]
            if (prediction > 0 and label > 0):
                tp += 1                
                correct += 1
            if (prediction > 0 and label < 0):
                fp += 1
            if (prediction < 0 and label > 0):
                fn += 1
            if (prediction < 0 and label < 0):
                tn += 1
                correct += 1

            if (label == 0):
                no += 1
        print("size: {}".format(sz))
        print("true positive: {}".format(tp))
        print("false positive: {}".format(fp))
        print("false negative: {}".format(fn))
        print("true negative: {}".format(tn))
        print("zero: {}".format(no))
        print("precision: {}".format(np.float64(tp) / (tp + fp)))
        print("recall: {}".format(np.float64(tp) / (tp + fn)))
        print("plain accuracy: {}".format(correct / sz))        

    def pred_with_id(self, j):
        
        #prediction = self.b
        
        #prediction += (self.W * self.labels * self.Gram[j]).sum()
        
        return self.prediction[j]
    
    def update_pred(self):

        self.prediction = self.b

        self.prediction += np.matmul(self.W * self.labels, self.Gram)

    """
    Args:
        x: input vector
    """
    def pred(self, x):
        assert x.shape == (self.feature_sz,), "input size not match"
        
        prediction = self.b
        
        for i in range(self.N):
            prediction += self.W[i] * self.labels[i] * self.kernel(self.train_x.T[i], x)
        
        return prediction
    
    def clip(self, W_new, L, H):
        if W_new > H:
            return H
        if W_new < L:
            return L
        return W_new

def generate_data(category, train_x, train_labels, test_x, test_labels, 
                    pos_size = None, false_size = None, test_pos_size = None, test_false_size = None):
    # Generating training data for SVM

    temp_train_x_pos = train_x[:, (train_labels == category)[0]]
    temp_train_label_pos = train_labels[:, (train_labels == category)[0]]
    temp_train_label_pos[:, :] = 1
    
    if pos_size == None:
        pos_size = temp_train_x_pos.shape[1]
    selected_rows = random.sample(range(temp_train_x_pos.shape[1]),k=pos_size) #range(pos_size)

    temp_train_x_pos = temp_train_x_pos[:, selected_rows]
    temp_train_label_pos = temp_train_label_pos[:, selected_rows]
    
    temp_train_x_false = train_x[:, (train_labels != category)[0]]
    temp_train_label_false = train_labels[:, (train_labels != category)[0]]
    temp_train_label_false[:, :] = -1

    if false_size == None:
        false_size = temp_train_x_false.shape[1]
    selected_rows = random.sample(range(temp_train_x_false.shape[1]),k=false_size) #range(false_size) 

    temp_train_x_false = temp_train_x_false[:, selected_rows]
    temp_train_label_false = temp_train_label_false[:, selected_rows]

    svm_train_x = np.concatenate((temp_train_x_pos, temp_train_x_false), axis = 1)
    svm_train_label = np.concatenate((temp_train_label_pos, temp_train_label_false), axis = 1)
    
    final_train_sz = svm_train_x.shape[1]
    selected_rows = random.sample(range(final_train_sz),k=final_train_sz)

    svm_train_x = svm_train_x[:, selected_rows]
    svm_train_label = svm_train_label[:, selected_rows]


    # Generating testing data for SVM    
    temp_test_x_pos = test_x[:, (test_labels == category)[0]]
    temp_test_label_pos = test_labels[:, (test_labels == category)[0]]
    temp_test_label_pos[:, :] = 1

    if test_pos_size == None:
        test_pos_size = temp_test_x_pos.shape[1]
    selected_rows = range(test_pos_size) #random.sample(range(temp_test_x_pos.shape[1]),k=test_pos_size)

    temp_test_x_pos = temp_test_x_pos[:, selected_rows]
    temp_test_label_pos = temp_test_label_pos[:, selected_rows]

    temp_test_x_false = test_x[:, (test_labels != category)[0]]
    temp_test_label_false = test_labels[:, (test_labels != category)[0]]
    temp_test_label_false[:, :] = -1

    if test_false_size == None:
        test_false_size = temp_test_x_false.shape[1]
    selected_rows = range(test_false_size) #random.sample(range(temp_test_x_false.shape[1]),k=test_false_size)

    temp_test_x_false = temp_test_x_false[:, selected_rows]
    temp_test_label_false = temp_test_label_false[:, selected_rows]    

    svm_test_x = np.concatenate((temp_test_x_pos, temp_test_x_false), axis = 1)
    svm_test_label = np.concatenate((temp_test_label_pos, temp_test_label_false), axis = 1)

    return (svm_train_x, svm_train_label, svm_test_x, svm_test_label)

def generate_training_given_category(category, label, train_x, train_labels,
                    pos_size = None):
    # Generating training data for SVM

    temp_train_x_pos = train_x[:, (train_labels == category)[0]]
    temp_train_label_pos = train_labels[:, (train_labels == category)[0]]
    temp_train_label_pos[:, :] = label
    
    if pos_size == None:
        pos_size = temp_train_x_pos.shape[1]
    selected_rows = random.sample(range(temp_train_x_pos.shape[1]),k=pos_size) #range(pos_size)

    temp_train_x_pos = temp_train_x_pos[:, selected_rows]
    temp_train_label_pos = temp_train_label_pos[:, selected_rows]
        
    return (temp_train_x_pos, temp_train_label_pos)

def test_xor():
    train_x = np.array([[-1, 1, -1, 1], [-1, -1, 1, 1]])
    train_labels = np.array([[-1, 1, 1, -1]])    
    sample_nums = 4
    
    svm = SVM(sample_nums, train_x, train_labels, xor_3_kernel)
    
    svm.train(C=1, max_iter=100)
    svm.test(train_x, train_labels)


print("--------------------Begin----------------------")
main()
print("---------------------End-----------------------")