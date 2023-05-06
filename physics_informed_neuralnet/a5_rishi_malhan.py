# -*- coding: utf-8 -*-
"""A5_Rishi_Malhan.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1lbU8S7zSVqJCdSzWcZWy_wkDsKoapC31

**Assignment-5**
Rishi Malhan
rmalhan@usc.edu

**Exact Solution**
u(x) = (e^((a x)/k) - 1)/(e^(a/k) - 1)
"""

import numpy as np
import tensorflow as tf
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

distribution = "RandomNormal"


def EvalExactSol(x, parameters):
    u = np.divide(
        np.exp(np.divide(parameters[0] * x, parameters[1])) - 1,
        np.exp(np.divide(parameters[0], parameters[1])) - 1,
    )
    u = u.reshape(u.shape[0], 1)
    return u


def construct_model():
    depth = 8
    model = tf.keras.Sequential()
    model.add(tf.keras.layers.Input(shape=(1,)))  # Input
    no_hidden_layers = depth - 1
    for i in range(no_hidden_layers):
        model.add(
            tf.keras.layers.Dense(
                15,
                activation=tf.math.sin,
                use_bias=True,
                kernel_initializer=distribution,
                bias_initializer=distribution,
                kernel_regularizer=tf.keras.regularizers.l2(1e-7),
            )
        )
    model.add(
        tf.keras.layers.Dense(
            1,
            activation=None,
            use_bias=True,
            kernel_initializer=distribution,
            bias_initializer=distribution,
            kernel_regularizer=tf.keras.regularizers.l2(1e-7),
        )
    )  # Output
    return model


def GetLoss(gen_out, udash, uddash, parameters, indv_losses):
    u_zero = tf.cast(gen_out[0], tf.float64)
    u_n = tf.cast(gen_out[-1], tf.float64)
    inner_resi = tf.divide(
        tf.reduce_sum(
            tf.math.square(
                tf.multiply(parameters[0], udash) - tf.multiply(parameters[1], uddash)
            )
        ),
        x.shape[0],
    )
    bndry_resi = tf.multiply(
        parameters[2], (tf.reduce_sum(tf.math.square(u_zero) + tf.math.square(u_n - 1)))
    )

    loss_val = inner_resi + bndry_resi
    indv_losses[0] = inner_resi
    indv_losses[1] = bndry_resi
    return loss_val


if __name__ == "__main__":
    # Training Phase
    max_epoch = 10000
    optimizer = tf.keras.optimizers.Adam(learning_rate=1e-3)
    histories = []
    indv_losses = np.empty((2,))
    a = 2.0
    kappa = 1.0
    lamB = 10
    for N in [25, 50]:
        for a in [2, 5, 10]:
            epoch = 0
            print(
                "\n\nTraining Network with Parameters: N->{0}, a->{1}, K->{2}, lamB->{3}".format(
                    N, a, kappa, lamB
                )
            )

            # 2. Write a function that creates a feed-forward network of width=15, depth=8 with input and output
            # dimensions 1. The weights and biases should initialized using RandomNormal distribution. All hidden
            # layers should make use of a sine activation function, tf.math.sin while no activation should be used
            # in the output layer. Use L2 regularization in all layers with a parameter 1.0e-7.
            model = construct_model()

            # 3. Create an array of N uniformly space nodes in [0;1], including the boundaries. Train a neural network
            # for N = 25;50, a = 2;5;10 and κ = 1 with the following loss function (refer assignment)
            # which is the sum of the interior residual and a scaled boundary residual. Use λb = 10 for the training.
            x = tf.cast(tf.linspace(0, 1, N), tf.float64)
            parameters = tf.cast(tf.constant([a, kappa, lamB]), tf.float64)
            history = {}
            history["loss"] = []
            history["int_residual"] = []
            history["bndry_residual"] = []
            while epoch < max_epoch:
                with tf.GradientTape() as tape1:
                    with tf.GradientTape() as tape2:
                        tape2.watch(x)
                        with tf.GradientTape() as tape3:
                            tape3.watch(x)

                            gen_out = model(x, training=True)
                        udash = tape3.gradient(gen_out, x)
                    uddash = tape2.gradient(udash, x)
                    loss = GetLoss(
                        tf.cast(gen_out, tf.float64),
                        tf.cast(udash, tf.float64),
                        tf.cast(uddash, tf.float64),
                        tf.cast(parameters, tf.float64),
                        indv_losses,
                    )
                grad = tape1.gradient(loss, model.trainable_variables)
                optimizer.apply_gradients(
                    zip(grad, model.trainable_variables)
                )  # zip used to create an iterator over the tuples

                history["loss"].append(loss)
                history["int_residual"].append(indv_losses[0])
                history["bndry_residual"].append(indv_losses[1])
                epoch = epoch + 1

            history["pred_sol"] = gen_out
            history["exact_sol"] = EvalExactSol(np.array(x), np.array(parameters))
            history["params"] = [N, a, kappa, lamB]
            history["x"] = x
            histories.append(history)

    # 4. For each of the 6 neural networks, save the history of the interior residual, boundary residual and the
    # final predicted solution in arrays/lists. Plot them at the end and compare with the exact solution.

    plt.rcParams["figure.figsize"] = (30, 25)
    fig1, axs1 = plt.subplots(6, 3)

    for i in range(len(histories)):
        history = histories[i]
        axs1[i, 0].plot(history["int_residual"], label="Interior Residual vs Epoch")
        axs1[i, 0].legend()
        axs1[i, 1].plot(history["bndry_residual"], label="Boundary Residual vs Epoch")
        axs1[i, 1].legend()
        axs1[i, 2].plot(
            history["x"], history["exact_sol"], label="Exact Solution", linewidth=5
        )
        axs1[i, 2].plot(history["x"], history["pred_sol"], label="Predicted Solution")
        axs1[i, 2].legend()
        axs1[i, 0].set_title("Parameters(N,a,K,lamB): " + str(history["params"]))
        axs1[i, 1].set_title("Parameters(N,a,K,lamB): " + str(history["params"]))
        axs1[i, 2].set_title("Parameters(N,a,K,lamB): " + str(history["params"]))

"""Answer: 5a
As N increases, it becomes easier to train the network since we have more data points to compute the loss. This is also verified by the charts as convergence with a higher N is faster.

Answer: 5b
It is harder to train the network as a increases in value since non-linearity of the curve increases and more kinks are required by the network to introduce. The charts also verify this trend as we can see for a constant N, more iterations are needed to minimize the error and also there are oscillations even when error goes down.

Answer: 5c
If lambda B was set to zero, the boundary conditions wouldn't be met.
"""
