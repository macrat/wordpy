import tensorflow as tf
import numpy


def make_small_model():
    inp = tf.keras.layers.Input(shape=(5, 26), name='possibilities_input')
    x = tf.keras.layers.Flatten()(inp)
    x = tf.keras.layers.Dense(64, activation='relu')(x)
    x = tf.keras.layers.Dropout(0.2)(x)
    x = tf.keras.layers.Dense(5*26, activation='relu')(x)
    out = tf.keras.layers.Reshape((5, 26), name='main_output')(x)

    model = tf.keras.models.Model(inputs=inp, outputs=out)
    model.summary()

    loss_fn = tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True)
    model.compile(optimizer='adam', loss=loss_fn, metrics=['accuracy'])

    return model

def make_large_model():
    input_possibilities = tf.keras.layers.Input(shape=(5, 26), name='possibilities_input')
    x = tf.keras.layers.Flatten(name='possibilities_flatten')(input_possibilities)
    x = tf.keras.layers.Dense(128, activation='relu', name='possibilities_dense')(x)
    sub_output = tf.keras.layers.Dense(5*26, activation='relu', name='sub_dense')(x)
    sub_output = tf.keras.layers.Reshape((5, 26), name='sub_output')(sub_output)

    input_includes = tf.keras.layers.Input(shape=26, name='includes_input')
    y = tf.keras.layers.Dense(26, activation='relu', name='includes_dense_1')(input_includes)
    y = tf.keras.layers.Dense(26, activation='relu', name='includes_dense_2')(y)

    z = tf.keras.layers.concatenate([x, y])
    z = tf.keras.layers.Dropout(0.2)(z)
    z = tf.keras.layers.Dense(64, activation='relu', name='dense_1')(z)
    z = tf.keras.layers.Dropout(0.2)(z)
    z = tf.keras.layers.concatenate([
        tf.keras.layers.Dense(26, activation='softmax', name=f'dense_2_{i}')(z)
        for i in range(5)
    ])
    main_output = tf.keras.layers.Reshape((5, 26), name='main_output')(z)

    model = tf.keras.models.Model(inputs=[input_possibilities, input_includes], outputs=[main_output, sub_output])
    model.summary()

    loss_fn = tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True)
    model.compile(optimizer='adam', loss=loss_fn, loss_weights={'main_output': 1, 'sub_output': 0.01}, metrics=['accuracy'])

    return model


def load_dataset():
    dat = numpy.load('output/dataset.npz')
    data_size = dat['answers'].shape[0]
    indices = numpy.random.permutation(data_size)
    train_idx, test_idx = indices[min(100, data_size//10):], indices[:min(100, data_size//10)]
    train_x = {'possibilities_input': dat['possibilities'][train_idx], 'includes_input': dat['includes'][train_idx]}
    train_y = dat['answers'][train_idx]
    test_x = {'possibilities_input': dat['possibilities'][test_idx], 'includes_input': dat['includes'][test_idx]}
    test_y = dat['answers'][test_idx]

    return (train_x, train_y), (test_x, test_y)

if __name__ == '__main__':
    (train_x, train_y), (test_x, test_y) = load_dataset()

    model = make_large_model()
    model.evaluate(test_x, test_y, verbose=2)
    print('-----')
    model.fit(train_x, train_y, epochs=20)
    print('-----')
    model.evaluate(test_x, test_y, verbose=2)

    model.save('output/model')
