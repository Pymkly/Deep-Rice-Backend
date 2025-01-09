import common
from tensorflow.keras import models, layers

import tensorflow as tf

from config import MODEL_PATH


def load_train_data():
    return common.load_data()


def fit_model(_train_data, _test_data):
    _model = models.Sequential()
    # Conv Layer
    _model.add(tf.keras.layers.Conv2D(64, 5, activation='relu'))
    _model.add(tf.keras.layers.MaxPooling2D(2, 2))
    # Conv Layer
    _model.add(tf.keras.layers.Conv2D(32, 5, activation='relu'))
    _model.add(tf.keras.layers.MaxPooling2D(2, 2))
    # Dropout
    _model.add(tf.keras.layers.Dropout(0.2))
    # Flatten
    _model.add(tf.keras.layers.Flatten())
    # Dense Layer
    _model.add(tf.keras.layers.Dense(activation='relu', units=128))
    # Output layer
    _model.add(layers.Dense(units=5, activation='softmax'))
    _model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])
    _history = _model.fit(_train_data, validation_data=_test_data, epochs=10)
    return _model, _history
    # return None

if __name__ == "__main__":
    train_data, val_data, test_data = load_train_data()
    model, history = fit_model(train_data, test_data)
    common.persist_model(model, MODEL_PATH)