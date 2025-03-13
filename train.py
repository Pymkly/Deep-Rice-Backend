

import common
from tensorflow.keras.layers import GlobalAveragePooling2D, Dense, Dropout, Input
from tensorflow.keras.applications import ResNet50
from tensorflow.keras.models import Model
import tensorflow as tf

from config import MODEL_PATH
from tensorflow.keras.applications.resnet50 import preprocess_input


def load_train_data():
    return common.load_data()

def fit_model(_train_data, _val_data):
    class_names = _val_data.class_names
    input_tensor = Input(shape=(224, 224, 3))
    base_model = ResNet50(weights='imagenet', include_top=False, input_tensor=input_tensor)
    x = base_model.output
    x = GlobalAveragePooling2D()(x)  # Réduit la dimensionnalité tout en conservant les informations globales
    x = Dense(1024, activation='relu')(x)  # Couche dense pour apprendre des combinaisons non linéaires des features
    x = Dropout(0.5)(x)  # Dropout pour réduire le surapprentissage
    predictions = Dense(len(class_names), activation='softmax')(
        x)  # 5 neurones pour nos 5 classes, avec softmax pour la classification multi-classe
    # Créer le modèle final
    model_ = Model(inputs=base_model.input, outputs=predictions)

    # Freezw
    for layer in base_model.layers:
        layer.trainable = False
    model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
    train_dataset = train_data.map(lambda x, y: (preprocess_input(x), y))
    val_dataset = _val_data.map(lambda x, y: (preprocess_input(x), y))
    history_ = model.fit(
        train_dataset,
        epochs=10,  # À ajuster selon tes observations
        validation_data=val_dataset
    )
    return model_, history_

    # return None

if __name__ == "__main__":
    train_data, val_data, test_data = load_train_data()
    model, history = fit_model(train_data, test_data)
    common.persist_model(model, MODEL_PATH)

# def fit_model(_train_data, _test_data):
#     _model = models.Sequential()
#     # Conv Layer
#     _model.add(tf.keras.layers.Conv2D(64, 5, activation='relu'))
#     _model.add(tf.keras.layers.MaxPooling2D(2, 2))
#     # Conv Layer
#     _model.add(tf.keras.layers.Conv2D(32, 5, activation='relu'))
#     _model.add(tf.keras.layers.MaxPooling2D(2, 2))
#     # Dropout
#     _model.add(tf.keras.layers.Dropout(0.2))
#     # Flatten
#     _model.add(tf.keras.layers.Flatten())
#     # Dense Layer
#     _model.add(tf.keras.layers.Dense(activation='relu', units=128))
#     # Output layer
#     _model.add(layers.Dense(units=5, activation='softmax'))
#     _model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])
#     _history = _model.fit(_train_data, validation_data=_test_data, epochs=10)
#     return _model, _history