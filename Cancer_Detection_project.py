# -*- coding: utf-8 -*-
"""fichfati.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1TJNiYwbBNjg125p1fHkIA6g-TGl-4X-p
"""

import os
import cv2
import numpy as np
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.applications import ResNet50
from tensorflow.keras.preprocessing.image import img_to_array, load_img
from tensorflow.keras.utils import to_categorical

from google.colab import drive
drive.mount('/content/drive')

# Définir le chemin vers le répertoire contenant les images MRI par classe
data_dir = "/content/drive/MyDrive/mlPROJEST_dataset"
classes = os.listdir(data_dir)

# Définir le chemin vers les dossiers de sortie
output_dir = "/content/drive/MyDrive/output_dossier"
train_dir = os.path.join(output_dir, "train")
test_dir = os.path.join(output_dir, "test")
val_dir = os.path.join(output_dir, "validation")

# Créer les dossiers de sortie s'ils n'existent pas déjà
for directory in [train_dir, test_dir, val_dir]:
    os.makedirs(directory, exist_ok=True)
    for class_name in classes:
        os.makedirs(os.path.join(directory, class_name), exist_ok=True)

# Définir les listes pour stocker les images et les labels
images = []
labels = []

# Charger les images et les labels
for class_idx, class_name in enumerate(classes):
    class_dir = os.path.join(data_dir, class_name)
    for image_name in os.listdir(class_dir):
        image_path = os.path.join(class_dir, image_name)
        image = cv2.imread(image_path)
        # Resize l'image à une taille fixe pour le prétraitement (par exemple 180x180)
        image = cv2.resize(image, (180,180))
        # Vous pouvez ajouter d'autres étapes de prétraitement ici (normalisation, filtres, etc.)
        images.append(image)
        labels.append(class_idx)

# Convertir en numpy arrays
images = np.array(images)
labels = np.array(labels)

# One-hot encode les labels
labels = to_categorical(labels)

# Diviser en ensembles d'entraînement, de validation et de test
X_train, X_test_val, y_train, y_test_val = train_test_split(images, labels, test_size=0.4, random_state=42)
X_test, X_val, y_test, y_val = train_test_split(X_test_val, y_test_val, test_size=0.5, random_state=42)

# Vérifier les dimensions des ensembles
print("Train set:", X_train.shape, y_train.shape)
print("Test set:", X_test.shape, y_test.shape)
print("Val set:", X_val.shape, y_val.shape)

# Copier les images dans les dossiers de sortie
def copy_images_to_folder(image_paths, labels, output_folder):
    for idx, (image, label) in enumerate(zip(image_paths, labels)):
        class_name = classes[np.argmax(label)]  # Utiliser np.argmax(label) pour obtenir l'indice de la classe
        image_filename = f"{class_name}_{idx}.png"
        destination_folder = os.path.join(output_folder, class_name, image_filename)
        cv2.imwrite(destination_folder, image)

copy_images_to_folder(X_train, y_train, train_dir)
copy_images_to_folder(X_test, y_test, test_dir)
copy_images_to_folder(X_val, y_val, val_dir)

# Afficher quelques images de chaque ensemble pour vérification
def show_images_from_folder(folder):
    for class_name in classes:
        class_folder = os.path.join(folder, class_name)
        image_names = os.listdir(class_folder)
        plt.figure(figsize=(10, 5))
        for i in range(5):
            image = cv2.imread(os.path.join(class_folder, image_names[i]))
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            plt.subplot(1, 5, i+1)
            plt.imshow(image)
            plt.title(class_name)
            plt.axis("off")
        plt.show()

print("Images d'entraînement :")
show_images_from_folder(train_dir)

print("Images de test :")
show_images_from_folder(test_dir)

print("Images de validation :")
show_images_from_folder(val_dir)

img_height,img_width=180,180
batch_size=32
train_ds = tf.keras.preprocessing.image_dataset_from_directory(
  train_dir,
  shuffle=True,
  image_size=(img_height, img_width),
  batch_size=batch_size,
  validation_split=False)

class_names = train_ds.class_names
print(class_names)

"""# **Resnet50 :**"""

import os
import PIL
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.layers import Layer  # Importer Layer depuis keras.layers
from tensorflow.keras.models import Sequential
from tensorflow.keras.optimizers import Adam
from tensorflow.python.keras.layers import Dense, Flatten
from tensorflow.keras.models import Sequential
from tensorflow.keras.optimizers import Adam

resnet_model = Sequential()

pretrained_model= tf.keras.applications.ResNet50(include_top=False,
                   input_shape=(180,180,3),
                   pooling='avg',classes=6,
                   weights='imagenet')
for layer in pretrained_model.layers:
        layer.trainable=False

resnet_model.add(pretrained_model)
resnet_model.add(Flatten())
resnet_model.add(Dense(512, activation='relu'))
resnet_model.add(Dense(6, activation='softmax'))

resnet_model.summary()

resnet_model.compile(optimizer=Adam(lr=0.001),loss='categorical_crossentropy',metrics=['accuracy'])

history = resnet_model.fit(X_train, y_train,epochs=10,validation_data=(X_val, y_val))

fig1 = plt.gcf()
plt.plot(history.history['accuracy'])
plt.plot(history.history['val_accuracy'])
plt.axis(ymin=0.4,ymax=1)
plt.grid()
plt.title('Resnet Accuracy')
plt.ylabel('Accuracy')
plt.xlabel('Epochs')
plt.legend(['train', 'validation'])
plt.show()

plt.plot(history.history['loss'])
plt.plot(history.history['val_loss'])
plt.grid()
plt.title('Resnet Loss')
plt.ylabel('Loss')
plt.xlabel('Epochs')
plt.legend(['train', 'validation'])
plt.show()

"""# **Prédiction de Resnet50 :**"""

import tensorflow as tf
import numpy as np

def predict_image(image_path, model, classes):
    # Charger et prétraiter l'image
    image = tf.keras.utils.load_img(image_path, color_mode="rgb", target_size=(180, 180))
    image_array = tf.keras.utils.img_to_array(image)
    image_array = np.expand_dims(image_array, axis=0)  # Ajouter une dimension batch

    # Faire une prédiction avec le modèle
    predictions = model.predict(image_array)
    predicted_class_index = np.argmax(predictions)
    predicted_class = classes[predicted_class_index]

    # Précision de la prédiction
    confidence = np.max(predictions) * 100

    return predicted_class, confidence

# Utilisation de la fonction de prédiction
image_path = "/content/melanoma_6579.jpg"  # Mettez ici le chemin de votre image
predicted_class, confidence = predict_image(image_path, resnet_model, classes)
print("La classe prédite est : {} avec une précision de {:.2f}%".format(predicted_class, confidence))

"""# **CNN :**"""

from tensorflow.keras.layers import Conv2D,MaxPooling2D,Dense,Flatten,Dropout

# Création du modèle CNN
model = keras.Sequential([
    layers.Conv2D(32, (3, 3), activation='relu', input_shape=(180, 180, 3)),
    layers.MaxPooling2D((2, 2)),
    layers.Conv2D(64, (3, 3), activation='relu'),
    layers.MaxPooling2D((2, 2)),
    layers.Conv2D(128, (3, 3), activation='relu'),
    layers.MaxPooling2D((2, 2)),
    layers.Conv2D(128, (3, 3), activation='relu'),
    layers.MaxPooling2D((2, 2)),
    layers.Flatten(),
    layers.Dense(512, activation='relu'),
    layers.Dense(len(classes), activation='softmax')
])

model.summary()
# Compiler le modèle
model.compile(optimizer='adam',
              loss='categorical_crossentropy',
              metrics=['accuracy'])

# Entraîner le modèle
history1 = model.fit(X_train, y_train, epochs=10, batch_size=32, validation_data=(X_val, y_val))

from tensorflow.keras.models import load_model
model.save('/content/drive/MyDrive/saved_models/CNN_finalmodel.h5')

import matplotlib.pyplot as plt

# Traçage de la courbe de précision
fig2 = plt.gcf()
plt.plot(history1.history['accuracy'])
plt.plot(history1.history['val_accuracy'])
plt.axis(ymin=0.4, ymax=1)  # Définir les limites de l'axe y
plt.grid()  # Afficher la grille
plt.title('CNN Accuracy')
plt.ylabel('Accuracy')
plt.xlabel('Epochs')
plt.legend(['train', 'validation'])
plt.show()

plt.plot(history1.history['loss'])
plt.plot(history1.history['val_loss'])
plt.grid()
plt.title('CNN Loss')
plt.ylabel('Loss')
plt.xlabel('Epochs')
plt.legend(['train', 'validation'])
plt.show()

"""# **Prédiction de CNN :**"""

image="/content/no_tumor_0.png"
image=tf.keras.utils.load_img(image,color_mode="rgb",target_size=(180,180))
image_array=tf.keras.utils.array_to_img(image)
image_bat=tf.expand_dims(image_array,0)

predictions=model.predict(image_bat)
confidence=np.max(predictions) * 100

print("the class is: {} with accuracy of:{:0.2f}".format(classes[np.argmax(predictions)],confidence))

"""# **Enregistrement du model :**"""

from tensorflow.keras.models import load_model
model.save('/content/drive/MyDrive/saved_models/CNN-finalmodel.h5')

"""# **Comparaison de CNN  et Resnet50 :**


"""

import matplotlib.pyplot as plt

# Tracer la courbe de précision pour les deux modèles
plt.figure(figsize=(10, 5))

# Précision d'entraînement
plt.subplot(1, 2, 1)
plt.plot(history1.history['accuracy'], label='CNN Train Accuracy')
plt.plot(history.history['accuracy'], label='ResNet Train Accuracy')
plt.title('Train Accuracy Comparison')
plt.xlabel('Epochs')
plt.ylabel('Accuracy')
plt.legend()
plt.grid(True)
plt.ylim(0.4, 1)  # Définit les limites de l'axe y

# Précision de validation
plt.subplot(1, 2, 2)
plt.plot(history1.history['val_accuracy'], label='CNN Validation Accuracy')
plt.plot(history.history['val_accuracy'], label='ResNet Validation Accuracy')
plt.title('Validation Accuracy Comparison')
plt.xlabel('Epochs')
plt.ylabel('Accuracy')
plt.legend()
plt.grid(True)
plt.ylim(0.4, 1)  # Définit les limites de l'axe y

plt.tight_layout()
plt.show()

# Tracer la courbe de perte pour les deux modèles
plt.figure(figsize=(10, 5))

# Perte d'entraînement
plt.subplot(1, 2, 1)
plt.plot(history1.history['loss'], label='CNN Train Loss')
plt.plot(history.history['loss'], label='ResNet Train Loss')
plt.title('Train Loss Comparison')
plt.xlabel('Epochs')
plt.ylabel('Loss')
plt.legend()
plt.grid(True)

# Perte de validation
plt.subplot(1, 2, 2)
plt.plot(history1.history['val_loss'], label='CNN Validation Loss')
plt.plot(history.history['val_loss'], label='ResNet Validation Loss')
plt.title('Validation Loss Comparison')
plt.xlabel('Epochs')
plt.ylabel('Loss')
plt.legend()
plt.grid(True)

plt.tight_layout()
plt.show()