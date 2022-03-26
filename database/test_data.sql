INSERT INTO users (id, email, password, first_name, last_name, gender, age, goal_weight, height,
                   state, is_nutr_adviser)
  VALUES
        (0, 'unknown@user.com', ' ', 'Unknown' ,'User', 1, 1, 1, 1, 1, false);

INSERT INTO users (email, password, first_name, last_name, gender, age, goal_weight, height,
                   state, is_nutr_adviser)
  VALUES
        ('eget.dictum@icloud.couk', '$2a$12$nDR36dk6/RcAUA.OMTPTpuoAAKUdvjExfMxIQhdpJvbUmFjLpr3bC', 'Bernard' ,'Knowles', 1, 35, 74, 179, 1, false),
        ('lorem.ac@yahoo.com', '$2a$12$nDR36dk6/RcAUA.OMTPTpuoAAKUdvjExfMxIQhdpJvbUmFjLpr3bC', 'Jack' ,'Cooke', 1, 31, 85, 190, 0, true),
        ('aliquam.fringilla@icloud.com', '$2a$12$nDR36dk6/RcAUA.OMTPTpuoAAKUdvjExfMxIQhdpJvbUmFjLpr3bC', 'Aurora' ,'Mcneil', 0, 27, 70, 166, 0, false),
        ('augue.scelerisque@google.ca', '$2a$12$nDR36dk6/RcAUA.OMTPTpuoAAKUdvjExfMxIQhdpJvbUmFjLpr3bC', 'Burke' ,'Mcgee', 1, 42, 70, 183, 0, false),
        ('ac.turpis@outlook.com', '$2a$12$nDR36dk6/RcAUA.OMTPTpuoAAKUdvjExfMxIQhdpJvbUmFjLpr3bC', 'Simon' ,'Carey', 1, 32, 87, 188, 0, true),
        ('lukas@mtaa.com', '$2a$12$nDR36dk6/RcAUA.OMTPTpuoAAKUdvjExfMxIQhdpJvbUmFjLpr3bC', 'Lukas' ,'Strbo', 1, 20, 80, 188, 0, true),
        ('richi@mtaa.com', '$2a$12$nDR36dk6/RcAUA.OMTPTpuoAAKUdvjExfMxIQhdpJvbUmFjLpr3bC', 'Richard' ,'Szarka', 1, 21, 65, 177, 0, true);

INSERT INTO weightmeasurements (id_user, weight, measure_time)
  VALUES
        (1, 86, TO_TIMESTAMP('2022-03-01 9:30:20','YYYY-MM-DD HH24:MI:SS')),
        (2, 84, TO_TIMESTAMP('2022-03-14 7:20:42','YYYY-MM-DD HH24:MI:SS')),
        (3, 85, TO_TIMESTAMP('2022-03-15 17:48:27','YYYY-MM-DD HH24:MI:SS')),
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
        (1, 'Recipe0', 'Ingredients Here', 'Instructions here', 10),
        (1, 'Recipe1', 'Ingredients Here', 'Instructions here', 20),
        (1, 'Recipe2', 'Ingredients Here', 'Instructions here', 30),
        (2, 'Recipe3', 'Ingredients Here', 'Instructions here', 40),
        (2, 'Recipe4', 'Ingredients Here', 'Instructions here', 50),
        (2, 'Recipe5', 'Ingredients Here', 'Instructions here', 60),
        (3, 'Recipe6', 'Ingredients Here', 'Instructions here', 70);


INSERT INTO foodlist (id_user, id_food, amount, time)
    VALUES
        (1, 4, 20, now()),
        (1, 5, 100, now()),
        (1, 6, 5, now()),
        (2, 8, 1, now()),
        (2, 12, 1, now()),
        (3, 7, 4, now()),
        (3, 3, 100, now()),
        (3, 7, 20, now()),
        (7, 1, 1, now()),
        (7, 6, 20, now()),
        (4, 4, 5, now());