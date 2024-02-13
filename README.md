# DIY_ML
Do-It-Yourself Machine Learning

## Definiton of modules

- Data Upload: the user will be able to upload different types of datasets, including training, validation and testing. Following an entity-based structure, there will be a CREATE method that will perform the task, having the dataset, type of dataset and other specific details as parameters.

- Training: the user will have the chance to train a model, specifying the ddesired ML algorithm. This module will use a READ method to retrieve the training data that has already been uploaded (entity-based API) and will have a procedure-based API to perform the training (e.g. trainModel(training_dataset, ml_algorithm).
