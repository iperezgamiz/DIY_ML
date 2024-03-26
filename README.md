# DO-IT-YOURSELF MACHINE LEARNING FOR IMAGE CLASSIFICATION
Inigo Perez Gamiz, iperezg@bu.edu

## Description
This project aims to build a Do-It-Yourself Application for Image Classification based on APIs. It is made up of several parts:
- **APIs:** these are the main components of the project. They allow the communication between the user and the server to perform different actions, that can be divided into two main groups. The first ones are related to the user, and include creation of account, deletion, login, logout and open user's data. The other group corresponds to model, and allows to create, open, train, test and deploy a model, as well as infer an image label once the model is deployed.
- **Database**: the project utilizes Redis key-value database to store the required data.
- **MEGA**: for images and models storing purposes, the application demands the usage of a cloud storage, in this case MEGA. The credentials for access need to be introduced.
- **Queues**: the application has 2 queues that aim to handle several requests related to training a model and infering an image.
- **Train**: this module contains the Convulational Neural Network (CNN) algorithm required to train a model with images.
- **Tests**: contains unittests to check the right behaviour of different actions like user login, training a model or testing it.
- **Dockers**: this module has the Dockerfile and docker-compose.yml necessary files to build and run the Flask application and Redis database as containers.

## Usage Guide
How to clone the repository:
```bash
git clone https://github.com/iperezgamiz/DIY_ML/
```

Install dependencies:
```bash
pip install -r requirements.txt
```
Redis database is configured to run on localhost. 

To access MEGA storage, credentials need to be introduced.

To run the application using Docker, please refer to [Docker README](https://github.com/iperezgamiz/DIY_ML/blob/main/dockers/README.md)  
