# Dockerizing the application

This module contains the required files to dockerize the application. The project is separated into 2 containers, one for the flask application and the other for the Redis database.

## How to dockerize

Within the <greenyellow">dockers</code> directory, the dockers can be built using the command:

```bash
docker-compose build
```

![image](https://github.com/iperezgamiz/DIY_ML/assets/144547977/22ad9127-eed4-457b-b463-2d57846d3f1c)

Once the dockers are built, they can be set up sing the command:

```bash
docker-compose up
```

![image](https://github.com/iperezgamiz/DIY_ML/assets/144547977/796fd653-abc2-43f5-99ac-c38b4171b37c)

![image](https://github.com/iperezgamiz/DIY_ML/assets/144547977/fdef4069-2fe7-40eb-ac3a-b5655d62d383)




