INSERT INTO users (email, password, first_name, last_name, gender, age, goal_weight, height,
                   state, is_nutr_adviser)
  VALUES 
        ('eget.dictum@icloud.couk', '$2a$12$nDR36dk6/RcAUA.OMTPTpuoAAKUdvjExfMxIQhdpJvbUmFjLpr3bC', 'Bernard' ,'Knowles', 1, 35, 74, 179, 1, false),
        ('lorem.ac@yahoo.com', '$2a$12$nDR36dk6/RcAUA.OMTPTpuoAAKUdvjExfMxIQhdpJvbUmFjLpr3bC', 'Jack' ,'Cooke', 1, 31, 85, 190, 0, true),
        ('aliquam.fringilla@icloud.com', '$2a$12$nDR36dk6/RcAUA.OMTPTpuoAAKUdvjExfMxIQhdpJvbUmFjLpr3bC', 'Aurora' ,'Mcneil', 0, 27, 70, 166, 0, false),
        ('augue.scelerisque@google.ca', '$2a$12$nDR36dk6/RcAUA.OMTPTpuoAAKUdvjExfMxIQhdpJvbUmFjLpr3bC', 'Burke' ,'Mcgee', 1, 42, 70, 183, 0, false),
        ('ac.turpis@outlook.com', '$2a$12$nDR36dk6/RcAUA.OMTPTpuoAAKUdvjExfMxIQhdpJvbUmFjLpr3bC', 'Simon' ,'Carey', 1, 32, 87, 188, 0, true);
        ('lukas@mtaa.com', '$2a$12$nDR36dk6/RcAUA.OMTPTpuoAAKUdvjExfMxIQhdpJvbUmFjLpr3bC', 'Lukas' ,'Strbo', 1, 20, 80, 188, 0, true);
        ('richi@mtaa.com', '$2a$12$nDR36dk6/RcAUA.OMTPTpuoAAKUdvjExfMxIQhdpJvbUmFjLpr3bC', 'Richard' ,'Szarka', 1, 21, 65, 177, 0, true);

INSERT INTO weightmeasurements (id_user, weight, measure_time)
  VALUES  
        (0, 86, TO_TIMESTAMP('2022-03-01 9:30:20','YYYY-MM-DD HH24:MI:SS')),
        (0, 84, TO_TIMESTAMP('2022-03-14 7:20:42','YYYY-MM-DD HH24:MI:SS')),
        (1, 85, TO_TIMESTAMP('2022-03-15 17:48:27','YYYY-MM-DD HH24:MI:SS')),
        (2, 90, TO_TIMESTAMP('2022-01-01 16:30:20','YYYY-MM-DD HH24:MI:SS')),
        (2, 84, TO_TIMESTAMP('2022-02-01 9:36:55','YYYY-MM-DD HH24:MI:SS')),
        (2, 79, TO_TIMESTAMP('2022-03-01 6:50:01','YYYY-MM-DD HH24:MI:SS')),
        (3, 74, TO_TIMESTAMP('2022-03-10 21:08:07','YYYY-MM-DD HH24:MI:SS')),
        (4, 90, TO_TIMESTAMP('2022-03-11 18:08:36','YYYY-MM-DD HH24:MI:SS'));

INSERT INTO food (title, kcal_100g)
    VALUES 
        ('Mlieko polotucne', 35),
        ('Hovadzie maso varene', 100),
        ('Taveny syr', 12),
        ('Chlieb biely', 150),
        ('Chlieb celozrnny', 75),
        ('Kaiserka tmava', 89),
        ('Horalky', 78),
        ('Ryza', 21),
        ('Zemiaky', 8),
        ('Cola', 43),
        ('Bravcove maso', 16),
        ('Knedla', 22),
        ('Smotana na varenie 33%', 33);

INSERT INTO recipes (id_user, title, ingredients, instructions, kcal_100g)
    VALUES
        (0, 'Reciepe0', 'Ingredients Here', 'Instructions here', 10),
        (0, 'Reciepe1', 'Ingredients Here', 'Instructions here', 20),
        (1, 'Reciepe2', 'Ingredients Here', 'Instructions here', 30),
        (1, 'Reciepe3', 'Ingredients Here', 'Instructions here', 40),
        (1, 'Reciepe4', 'Ingredients Here', 'Instructions here', 50),
        (1, 'Reciepe5', 'Ingredients Here', 'Instructions here', 60),
        (3, 'Reciepe6', 'Ingredients Here', 'Instructions here', 70);


INSERT INTO foodlist (id_user, id_food, amount, time)
    VALUES
        (0, 0, 20, now()),
        (0, 5, 100, now()),
        (0, 6, 5, now()),
        (1, 8, 1, now()),
        (1, 12, 1, now()),
        (1, 7, 4, now()),
        (1, 3, 100, now()),
        (3, 0, 20, now()),
        (3, 1, 1, now()),
        (3, 6, 20, now()),
        (4, 4, 5, now());