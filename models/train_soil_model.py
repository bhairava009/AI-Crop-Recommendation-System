import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras import layers, models
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
import json
import os

# Image settings
IMG_SIZE = (150, 150)
BATCH_SIZE = 32

# Advanced Data Augmentation for anti-overfitting
train_datagen = ImageDataGenerator(
    preprocessing_function=tf.keras.applications.mobilenet_v2.preprocess_input,
    rotation_range=30,
    width_shift_range=0.2,
    height_shift_range=0.2,
    zoom_range=0.2,
    horizontal_flip=True,
    validation_split=0.2
)

# Validation generator MUST NOT be augmented (only preprocessed)
val_datagen = ImageDataGenerator(
    preprocessing_function=tf.keras.applications.mobilenet_v2.preprocess_input,
    validation_split=0.2
)

# Go to project root if executed from models/
if not os.path.exists('Soil-Dataset') and os.path.exists('../Soil-Dataset'):
    os.chdir('..')

# Training data
train_data = train_datagen.flow_from_directory(
    'Soil-Dataset/',
    target_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    class_mode='categorical',
    subset='training'
)

# Validation data
val_data = val_datagen.flow_from_directory(
    'Soil-Dataset/',
    target_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    class_mode='categorical',
    subset='validation'
)

# Save class indices for prediction
os.makedirs('models', exist_ok=True)
with open('models/soil_class_indices.json', 'w') as f:
    json.dump(train_data.class_indices, f)
print("Class indices saved to models/soil_class_indices.json")

num_classes = len(train_data.class_indices)

# Load MobileNetV2 Base Model (Transfer Learning)
base_model = MobileNetV2(
    weights='imagenet', 
    include_top=False, 
    input_shape=(150, 150, 3)
)

# Freeze base model layers initially
base_model.trainable = False

# Build robust classification head
model = models.Sequential([
    base_model,
    layers.GlobalAveragePooling2D(),
    layers.Dense(256, activation='relu'),
    layers.Dropout(0.5),  # Aggressive dropout to prevent overfitting
    layers.Dense(num_classes, activation='softmax')
])

# Compile
model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
    loss='categorical_crossentropy',
    metrics=['accuracy']
)

# Callbacks for dynamic training
early_stop = EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True)
reduce_lr = ReduceLROnPlateau(monitor='val_loss', factor=0.2, patience=3, min_lr=1e-6)

print("\n--- Starting Phase 1: Training Classification Head ---")
history = model.fit(
    train_data,
    validation_data=val_data,
    epochs=15,
    callbacks=[early_stop, reduce_lr],
    verbose=1
)

# Optional Phase 2: Fine-tuning top layers of MobileNetV2
print("\n--- Starting Phase 2: Fine-tuning Top Layers ---")
base_model.trainable = True
# Freeze the first 100 layers
for layer in base_model.layers[:100]:
    layer.trainable = False

# Recompile with very low learning rate
model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=1e-5),
    loss='categorical_crossentropy',
    metrics=['accuracy']
)

history_fine = model.fit(
    train_data,
    validation_data=val_data,
    epochs=10,
    callbacks=[early_stop, reduce_lr],
    verbose=1
)

# Save model
model.save("models/soil_model.h5")

print("\n==============================================")
print("MobileNetV2 Soil Model trained successfully!")
print(f"Final Validation Accuracy: {max(history_fine.history['val_accuracy']) * 100:.2f}%")
print("==============================================\n")