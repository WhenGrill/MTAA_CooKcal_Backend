DROP DATABASE IF EXISTS cookcal;

CREATE DATABASE cookcal
    OWNER = postgres;

DROP TABLE IF EXISTS public.users;

CREATE TABLE public.users
(
    id serial NOT NULL,
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

ALTER TABLE IF EXISTS public.users
    OWNER to postgres;

DROP TABLE IF EXISTS public.weightmeasurements;

CREATE TABLE public.weightmeasurements
(
    id serial NOT NULL,
    id_user integer NOT NULL,
    weight double precision NOT NULL CHECK (weight > 0),
    measure_time timestamp with time zone NOT NULL,

    CONSTRAINT fk_weightmeasurements_id_user
        FOREIGN KEY (id_user)
        REFERENCES users (id),

    CONSTRAINT pk_idweightmeasurement_id_user
        PRIMARY KEY (id, id_user)
);

ALTER TABLE IF EXISTS public.weightmeasurements
    OWNER to postgres;


DROP TABLE IF EXISTS public.recipes;

CREATE TABLE IF NOT EXISTS public.recipes
(
    id serial NOT NULL,
    id_user integer NOT NULL,
    reciepe_picture bytea NULL,
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

ALTER TABLE IF EXISTS public.recipes
    OWNER to postgres;

DROP TABLE IF EXISTS public.food;

CREATE TABLE public.food
(
    id serial NOT NULL,
    title character varying(80) NOT NULL,
    kcal_100g double precision NOT NULL CHECK(kcal_100g > 0),

    CONSTRAINT pk_idfood
        PRIMARY KEY (id)
);

ALTER TABLE IF EXISTS public.food
    OWNER to postgres;


DROP TABLE IF EXISTS public.foodlist;
CREATE TABLE public.foodlist
(
    id serial NOT NULL,
    id_user integer NOT NULL,
    id_food integer NOT NULL,
    amount double precision NOT NULL CHECK (amount > 0),
    "time" timestamp with time zone DEFAULT now() NOT NULL,

    CONSTRAINT fk_foodlist_id_user
        FOREIGN KEY (id_user)
        REFERENCES users (id),

    CONSTRAINT fk_foodlist_id_food
        FOREIGN KEY (id_food)
        REFERENCES food (id),

    CONSTRAINT pk_idfoodlist_id_user
        PRIMARY KEY (id, id_user)
);

ALTER TABLE IF EXISTS public.foodlist
    OWNER to postgres;