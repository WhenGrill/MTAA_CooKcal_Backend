DROP TABLE IF EXISTS public.users;
DROP SEQUENCE IF EXISTS users_id_seq;
CREATE SEQUENCE users_id_seq START WITH 1;

DROP TABLE IF EXISTS public.foodlist;
DROP SEQUENCE IF EXISTS foodlist_id_seq;
CREATE SEQUENCE foodlist_id_seq START WITH 1;

DROP TABLE IF EXISTS public.weightmeasurements;
DROP SEQUENCE IF EXISTS weightmeasurements_id_seq;
CREATE SEQUENCE weightmeasurements_id_seq START WITH 1;

DROP TABLE IF EXISTS public.recipes;
DROP SEQUENCE IF EXISTS recipes_id_seq;
CREATE SEQUENCE recipes_id_seq START WITH 1;

DROP TABLE IF EXISTS public.food;
DROP SEQUENCE IF EXISTS food_id_seq;
CREATE SEQUENCE food_id_seq START WITH 1;


CREATE TABLE public.users
(
    id int NOT NULL DEFAULT nextval('users_id_seq'),
    email character varying NOT NULL,
    password character varying NOT NULL,
    profile_picture bytea,
    first_name character varying(50) NOT NULL,
    last_name character varying(50) NOT NULL,
    gender integer NOT NULL CHECK (gender BETWEEN 0 AND 2),
    age integer CHECK (age > 0),
    goal_weight double precision CHECK (goal_weight > 0),
    height double precision NOT NULL CHECK (height > 0),
    state integer CHECK (state BETWEEN 0 AND 2),
    is_nutr_adviser boolean NOT NULL,
	created_at timestamp with time zone DEFAULT now() NOT NULL,

    CONSTRAINT pk_iduser
        PRIMARY KEY (id)
);


CREATE TABLE public.weightmeasurements
(
    id int NOT NULL DEFAULT nextval('weightmeasurements_id_seq'),
    id_user integer NOT NULL,
    weight double precision NOT NULL CHECK (weight > 0),
    measure_time timestamp with time zone NOT NULL,

    CONSTRAINT fk_weightmeasurements_id_user
        FOREIGN KEY (id_user)
        REFERENCES users (id),

    CONSTRAINT pk_idweightmeasurement_id_user
        PRIMARY KEY (id, id_user)
);


CREATE TABLE IF NOT EXISTS public.recipes
(
    id int NOT NULL DEFAULT nextval('recipes_id_seq'),
    id_user integer NOT NULL,
    recipe_picture bytea NULL,
    title character varying(80) NOT NULL,
    ingredients text NOT NULL,
    instructions text NOT NULL,
    kcal_100g double precision NOT NULL CHECK(kcal_100g > 0),
	created_at timestamp with time zone DEFAULT now() NOT NULL,

    CONSTRAINT fk_recipes_id_user
        FOREIGN KEY (id_user)
        REFERENCES users (id),

    CONSTRAINT pk_idrecipes_id_user
        PRIMARY KEY (id, id_user)
);


CREATE TABLE public.food
(
    id int NOT NULL DEFAULT nextval('food_id_seq'),
    title character varying(80) NOT NULL,
    kcal_100g double precision NOT NULL CHECK(kcal_100g > 0),

    CONSTRAINT pk_idfood
        PRIMARY KEY (id)
);


CREATE TABLE public.foodlist
(
    id int NOT NULL DEFAULT nextval('foodlist_id_seq'),
    id_user integer NOT NULL,
    id_food integer NOT NULL,
    amount double precision NOT NULL CHECK (amount > 0),
    "time" timestamp with time zone DEFAULT now() NOT NULL,

    CONSTRAINT fk_foodlist_id_user
        FOREIGN KEY (id_user)
        REFERENCES users (id)
        ON DELETE CASCADE,

    CONSTRAINT fk_foodlist_id_food
        FOREIGN KEY (id_food)
        REFERENCES food (id)
        ON DELETE SET NULL,

    CONSTRAINT pk_idfoodlist_id_user
        PRIMARY KEY (id, id_user)
);


ALTER TABLE IF EXISTS public.users
    OWNER to postgres;

ALTER TABLE IF EXISTS public.recipes
    OWNER to postgres;

ALTER TABLE IF EXISTS public.weightmeasurements
    OWNER to postgres;

ALTER TABLE IF EXISTS public.food
    OWNER to postgres;

ALTER TABLE IF EXISTS public.foodlist
    OWNER to postgres;