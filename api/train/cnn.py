import imghdr
import json
import os
import tempfile
import matplotlib.pyplot as plt

from keras import Sequential
from keras.applications import Xception
from keras.layers import Flatten, Dense, Dropout
from keras.optimizers import Adam
from keras.preprocessing.image import ImageDataGenerator


class CnnModel:

    def __init__(self, model_id, dataset_path, image_size=(256, 256), batch_size=32, epochs=20, validation_split=0.3):
        self.model_id = model_id
        self.dataset_path = dataset_path
        self.image_size = image_size
        self.batch_size = batch_size
        self.epochs = epochs
        self.validation_split = validation_split

    def run(self):
        self.dataset_clean()
        # Data preprocessing
        datagen = ImageDataGenerator(
            rescale=1. / 255,
            validation_split=self.validation_split
        )

        train_generator = datagen.flow_from_directory(
            self.dataset_path,
            target_size=self.image_size,
            batch_size=self.batch_size,
            class_mode='sparse',
            subset='training'
        )

        validation_generator = datagen.flow_from_directory(
            self.dataset_path,
            target_size=self.image_size,
            batch_size=self.batch_size,
            class_mode='sparse',
            subset='validation'
        )

        base_model = Xception(weights='imagenet',
                              include_top=False,
                              input_shape=(self.image_size[0], self.image_size[1], 3))

        for layer in base_model.layers:
            layer.trainable = False

        # Define the model
        model = Sequential([
            base_model,
            Flatten(),
            Dense(128, activation='relu'),
            Dense(256, activation='relu'),
            Dropout(0.5),
            Dense(len(train_generator.class_indices), activation='softmax')
        ])

        # Compile the model
        model.compile(optimizer=Adam(), loss='sparse_categorical_crossentropy', metrics=['accuracy'])

        # Train the model
        model_history = model.fit(train_generator, epochs=self.epochs, validation_data=validation_generator)

        # Create a temporary directory to store training results
        results_temp_dir = tempfile.mkdtemp()

        # Save the model to the temporary directory
        model_path = os.path.join(results_temp_dir, f"{self.model_id}.h5")
        model.save(model_path)

        # Get the class labels
        class_labels = list(train_generator.class_indices.keys())

        # Save the class labels to a file in the temporary directory
        class_labels_path = os.path.join(results_temp_dir, "class_labels.txt")
        with open(class_labels_path, "w") as f:
            for label in class_labels:
                f.write(label + "\n")

        self.generate_report(model_history, results_temp_dir)

        # Return the location of the temporary directory with the results
        return results_temp_dir

    def dataset_clean(self):
        allowed_extensions = ['jpg', 'jpeg', 'png', 'bmp']
        for image_class in os.listdir(self.dataset_path):
            for image in os.listdir(os.path.join(self.dataset_path, image_class)):
                image_path = os.path.join(self.dataset_path, image_class, image)
                ext = imghdr.what(image_path)
                if ext not in allowed_extensions:
                    os.remove(image_path)

    @staticmethod
    def generate_report(model_history, results_temp_dir):

        # Plot training and validation accuracy
        plt.plot(model_history.history['accuracy'], label='Training Accuracy')
        plt.plot(model_history.history['val_accuracy'], label='Validation Accuracy')
        plt.xlabel('Epoch')
        plt.ylabel('Accuracy')
        plt.title('Training and Validation Accuracy')
        plt.legend()
        plt.savefig(os.path.join(results_temp_dir, 'accuracy_plot.png'))  # Save the plot without displaying it
        plt.close()  # Close the plot to free up memory

        # Plot training and validation loss
        plt.plot(model_history.history['loss'], label='Training Loss')
        plt.plot(model_history.history['val_loss'], label='Validation Loss')
        plt.xlabel('Epoch')
        plt.ylabel('Loss')
        plt.title('Training and Validation Loss')
        plt.legend()
        plt.savefig(os.path.join(results_temp_dir, 'loss_plot.png'))  # Save the plot without displaying it
        plt.close()  # Close the plot to free up memory

        training_accuracy = model_history.history['accuracy'][-1]
        validation_accuracy = model_history.history['val_accuracy'][-1]
        training_loss = model_history.history['loss'][-1]
        validation_loss = model_history.history['val_loss'][-1]

        # Construct a summary report
        report_data = {
            'training_accuracy': training_accuracy,
            'validation_accuracy': validation_accuracy,
            'training_loss': training_loss,
            'validation_loss': validation_loss
        }
        with open(os.path.join(results_temp_dir, "report_data.json"), 'w') as json_file:
            json.dump(report_data, json_file)

        pass
