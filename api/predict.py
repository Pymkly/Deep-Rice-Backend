import time

import common
import numpy as np
from fastapi import  UploadFile

from typing import List

from config import MODEL_PATH

model = common.load_model(MODEL_PATH)
#
async def predict_disease_on_images(files_: List[UploadFile]):
    response_ = {
        'individual_results' : []
    }
    for file in files_:
        print("manomboka")
        # Sauvegarder chaque image
        unique_filename = f"{int(time.time())}_{file.filename}"
        file_location = f"uploads/{unique_filename}"
        with open(file_location, "wb") as f:
            content = await file.read()
            f.write(content)
        predicted_class, probabilities = predict_disease(file_location)
        label_, disease_, diseases_ = common.get_classes_db_without_cursor(int(predicted_class))

        response_['individual_results'].append({
            'predicted_class': label_,
            'predicted_class_': disease_,
            'probabilities': [{
                'class' : diseases_[i]['name'],
                'value' : float(probabilities[i])
            } for i in range(len(probabilities))]
        })
        print("vita")
    return response_

def predict_disease(_path):
    processed_image = common.preprocess_image_for_prediction(_path, common.IMG_SIZE)
    predictions = model.predict(processed_image)
    predicted_class = np.argmax(predictions, axis=1)  # Obtenir la classe avec la probabilité la plus élevée
    return predicted_class[0], predictions[0]