import os
os.environ["CUDA_VISIBLE_DEVICES"]="3"
import pdb
from keras.preprocessing.image import ImageDataGenerator, array_to_img, img_to_array, load_img
import keras
from tensorflow.keras.applications.resnet50 import preprocess_input
from tensorflow.keras.preprocessing import image
from sklearn.utils import class_weight
from keras.callbacks import ModelCheckpoint
import numpy as np

root_dir = '/ext/classification'
batch_size = 32
input_shape = (60, 128, 3)
# train_datagen = ImageDataGenerator(rescale=1./255, rotation_range=40, shear_range=0.2, horizontal_flip=True, brightness_range=(-0.3, 0.3))
train_datagen = ImageDataGenerator(rescale=1./255, brightness_range=(-0.2, 0.2))
test_datagen = ImageDataGenerator(rescale=1./255)

train_generator = train_datagen.flow_from_directory(root_dir + '/Pedestrian/train/',
                                                    target_size=input_shape[:2],
                                                    batch_size=batch_size,
                                                    shuffle=True,
                                                    class_mode='binary')

validation_generator = test_datagen.flow_from_directory(root_dir + '/Pedestrian/val/',
                                                        target_size=input_shape[:2],
                                                        batch_size=batch_size,
                                                        shuffle=False,
                                                        class_mode='binary')

class_weights = class_weight.compute_class_weight('balanced', np.unique(train_generator.classes), train_generator.classes)
base_model = keras.applications.MobileNetV2(input_shape=input_shape, alpha=0.5, include_top=False, weights="imagenet", input_tensor=None, pooling=None)

base_model.summary()

inputs = keras.Input(shape=input_shape)
base_model.trainable = True
x = base_model(inputs)
x = keras.layers.GlobalAveragePooling2D()(x)
# outputs = keras.layers.Dense(1, activation='tanh')(x)
outputs = keras.layers.Dense(1, activation='sigmoid')(x)
model = keras.Model(inputs, outputs)

model.compile(optimizer=keras.optimizers.SGD(0.0005),
              loss=keras.losses.BinaryCrossentropy(),
              # loss=keras.losses.SquaredHinge(),
              metrics=[keras.metrics.BinaryAccuracy()])

# for epoch in range(0, 5):
#     model.fit_generator(train_generator, steps_per_epoch=17834 // batch_size,
#                         epochs=1,
#                         validation_data=validation_generator,
#                         validation_steps=6845 // batch_size,
#                         class_weight=class_weights)
#     model.save_weights(root_dir + '/pedestrian_classifier_{}.h5'.format(epoch))

checkpoint = ModelCheckpoint(root_dir + '/pedestrian_model_{epoch:08d}.h5', monitor='val_acc', verbose=1, save_best_only=False, mode='auto', period=1)

# model.fit_generator(train_generator, steps_per_epoch=44451 // batch_size,
#                     epochs=2,
#                     validation_data=validation_generator,
#                     validation_steps=17432 // batch_size,
#                     class_weight=class_weights,
#                     callbacks=[checkpoint])

# model.save_weights(root_dir + '/pedestrian_classifier_{}.h5'.format(2))

pdb.set_trace()
negative_files = os.listdir(root_dir + '/Pedestrian/val/0/')
print("negative samples")
for neg_file in negative_files[:5]:
    img_path = root_dir + '/Pedestrian/val/0/' + neg_file
    img = image.load_img(img_path, target_size=input_shape[:2])
    x = image.img_to_array(img)
    x = np.expand_dims(x, axis=0)
    x = preprocess_input(x)
    preds = model.predict(x)
    print(preds)

positive_files = os.listdir(root_dir + '/Pedestrian/val/1/')
print("positive samples")
for neg_file in negative_files[:5]:
    img_path = root_dir + '/Pedestrian/val/1/' + neg_file
    img = image.load_img(img_path, target_size=input_shape[:2])
    x = image.img_to_array(img)
    x = np.expand_dims(x, axis=0)
    x = preprocess_input(x)
    preds = model.predict(x)
    print(preds)

