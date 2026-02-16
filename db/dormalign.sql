--
-- PostgreSQL database dump
--

\restrict sdTxawss358WPYKWmba9zf3M6o1B7cbDzjOMtTywCXeqF6UeL8oIqvexOMpaddD

-- Dumped from database version 18.1
-- Dumped by pg_dump version 18.1

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: compatibility_score; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.compatibility_score (
    score_id integer NOT NULL,
    student1_id integer,
    student2_id integer,
    compatibility_score integer,
    calculated_date date
);


ALTER TABLE public.compatibility_score OWNER TO postgres;

--
-- Name: compatibility_score_score_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.compatibility_score_score_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.compatibility_score_score_id_seq OWNER TO postgres;

--
-- Name: compatibility_score_score_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.compatibility_score_score_id_seq OWNED BY public.compatibility_score.score_id;


--
-- Name: hostel; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.hostel (
    hostel_id integer NOT NULL,
    hostel_name character varying(100),
    hostel_type character varying(50),
    total_rooms integer
);


ALTER TABLE public.hostel OWNER TO postgres;

--
-- Name: hostel_hostel_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.hostel_hostel_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.hostel_hostel_id_seq OWNER TO postgres;

--
-- Name: hostel_hostel_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.hostel_hostel_id_seq OWNED BY public.hostel.hostel_id;


--
-- Name: lifestyle_preferences; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.lifestyle_preferences (
    preference_id integer NOT NULL,
    student_id integer,
    sleep_time character varying(20),
    cleanliness_level integer,
    noise_tolerance integer,
    guest_preference boolean,
    study_style character varying(50)
);


ALTER TABLE public.lifestyle_preferences OWNER TO postgres;

--
-- Name: lifestyle_preferences_preference_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.lifestyle_preferences_preference_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.lifestyle_preferences_preference_id_seq OWNER TO postgres;

--
-- Name: lifestyle_preferences_preference_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.lifestyle_preferences_preference_id_seq OWNED BY public.lifestyle_preferences.preference_id;


--
-- Name: match_history; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.match_history (
    match_id integer NOT NULL,
    student1_id integer,
    student2_id integer,
    start_date date,
    end_date date,
    success_rating integer
);


ALTER TABLE public.match_history OWNER TO postgres;

--
-- Name: match_history_match_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.match_history_match_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.match_history_match_id_seq OWNER TO postgres;

--
-- Name: match_history_match_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.match_history_match_id_seq OWNED BY public.match_history.match_id;


--
-- Name: room; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.room (
    room_id integer NOT NULL,
    hostel_id integer,
    room_number character varying(10),
    capacity integer,
    current_occupancy integer
);


ALTER TABLE public.room OWNER TO postgres;

--
-- Name: room_assignment; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.room_assignment (
    assignment_id integer NOT NULL,
    room_id integer,
    student_id integer,
    assigned_date date
);


ALTER TABLE public.room_assignment OWNER TO postgres;

--
-- Name: room_assignment_assignment_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.room_assignment_assignment_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.room_assignment_assignment_id_seq OWNER TO postgres;

--
-- Name: room_assignment_assignment_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.room_assignment_assignment_id_seq OWNED BY public.room_assignment.assignment_id;


--
-- Name: room_room_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.room_room_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.room_room_id_seq OWNER TO postgres;

--
-- Name: room_room_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.room_room_id_seq OWNED BY public.room.room_id;


--
-- Name: roommate_request; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.roommate_request (
    request_id integer NOT NULL,
    student_id integer,
    preferred_room_type character varying(50),
    request_status character varying(20)
);


ALTER TABLE public.roommate_request OWNER TO postgres;

--
-- Name: roommate_request_request_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.roommate_request_request_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.roommate_request_request_id_seq OWNER TO postgres;

--
-- Name: roommate_request_request_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.roommate_request_request_id_seq OWNED BY public.roommate_request.request_id;


--
-- Name: student; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.student (
    student_id integer NOT NULL,
    name character varying(100),
    gender character varying(10),
    department character varying(50),
    year integer,
    hostel_id integer,
    user_id integer
);


ALTER TABLE public.student OWNER TO postgres;

--
-- Name: student_student_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.student_student_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.student_student_id_seq OWNER TO postgres;

--
-- Name: student_student_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.student_student_id_seq OWNED BY public.student.student_id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.users (
    id integer NOT NULL,
    username character varying(100) NOT NULL,
    password text NOT NULL
);


ALTER TABLE public.users OWNER TO postgres;

--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.users_id_seq OWNER TO postgres;

--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: compatibility_score score_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.compatibility_score ALTER COLUMN score_id SET DEFAULT nextval('public.compatibility_score_score_id_seq'::regclass);


--
-- Name: hostel hostel_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.hostel ALTER COLUMN hostel_id SET DEFAULT nextval('public.hostel_hostel_id_seq'::regclass);


--
-- Name: lifestyle_preferences preference_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.lifestyle_preferences ALTER COLUMN preference_id SET DEFAULT nextval('public.lifestyle_preferences_preference_id_seq'::regclass);


--
-- Name: match_history match_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.match_history ALTER COLUMN match_id SET DEFAULT nextval('public.match_history_match_id_seq'::regclass);


--
-- Name: room room_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.room ALTER COLUMN room_id SET DEFAULT nextval('public.room_room_id_seq'::regclass);


--
-- Name: room_assignment assignment_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.room_assignment ALTER COLUMN assignment_id SET DEFAULT nextval('public.room_assignment_assignment_id_seq'::regclass);


--
-- Name: roommate_request request_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.roommate_request ALTER COLUMN request_id SET DEFAULT nextval('public.roommate_request_request_id_seq'::regclass);


--
-- Name: student student_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.student ALTER COLUMN student_id SET DEFAULT nextval('public.student_student_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Data for Name: compatibility_score; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.compatibility_score (score_id, student1_id, student2_id, compatibility_score, calculated_date) FROM stdin;
\.


--
-- Data for Name: hostel; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.hostel (hostel_id, hostel_name, hostel_type, total_rooms) FROM stdin;
1	Boys Hostel	Boys	50
2	Girls Hostel	girls	60
\.


--
-- Data for Name: lifestyle_preferences; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.lifestyle_preferences (preference_id, student_id, sleep_time, cleanliness_level, noise_tolerance, guest_preference, study_style) FROM stdin;
1	2	Early bird	1	1	t	Quiet solo
2	3	Flexible	4	3	f	Quiet solo
3	4	Flexible	4	3	f	Quiet solo
\.


--
-- Data for Name: match_history; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.match_history (match_id, student1_id, student2_id, start_date, end_date, success_rating) FROM stdin;
\.


--
-- Data for Name: room; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.room (room_id, hostel_id, room_number, capacity, current_occupancy) FROM stdin;
\.


--
-- Data for Name: room_assignment; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.room_assignment (assignment_id, room_id, student_id, assigned_date) FROM stdin;
\.


--
-- Data for Name: roommate_request; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.roommate_request (request_id, student_id, preferred_room_type, request_status) FROM stdin;
1	2	Single	\N
2	3	Single	\N
3	4	Single	\N
\.


--
-- Data for Name: student; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.student (student_id, name, gender, department, year, hostel_id, user_id) FROM stdin;
2	sd	Male	sd	1	1	\N
3	Purnima Bhandari	Female	computer	3	2	\N
4	Purnima Bhandari	Female	computer	3	2	\N
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.users (id, username, password) FROM stdin;
1	purnima	scrypt:32768:8:1$5CwlvHBddYhGE5tH$6ac1a169fffb63a8123fab9aa6e82cd3802f4fb5f731574e02cea3a03585b53b1e32cb9b9df8b2713e14a20431dc1ba753836eca9d6924456f45979f3ec1b50c
2	purnima2	scrypt:32768:8:1$JDPuMrGD8Pg0yRGF$6b2c5de01e6d632764f61f0154fe69ca08c6ea0cc6ef2973314975d998a759f82a64568a917ae96809c1a5973ee61246811ac12b42e8e3e9348a751b92bf5d80
\.


--
-- Name: compatibility_score_score_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.compatibility_score_score_id_seq', 1, false);


--
-- Name: hostel_hostel_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.hostel_hostel_id_seq', 2, true);


--
-- Name: lifestyle_preferences_preference_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.lifestyle_preferences_preference_id_seq', 3, true);


--
-- Name: match_history_match_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.match_history_match_id_seq', 1, false);


--
-- Name: room_assignment_assignment_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.room_assignment_assignment_id_seq', 1, false);


--
-- Name: room_room_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.room_room_id_seq', 1, false);


--
-- Name: roommate_request_request_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.roommate_request_request_id_seq', 3, true);


--
-- Name: student_student_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.student_student_id_seq', 4, true);


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.users_id_seq', 2, true);


--
-- Name: compatibility_score compatibility_score_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.compatibility_score
    ADD CONSTRAINT compatibility_score_pkey PRIMARY KEY (score_id);


--
-- Name: hostel hostel_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.hostel
    ADD CONSTRAINT hostel_pkey PRIMARY KEY (hostel_id);


--
-- Name: lifestyle_preferences lifestyle_preferences_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.lifestyle_preferences
    ADD CONSTRAINT lifestyle_preferences_pkey PRIMARY KEY (preference_id);


--
-- Name: lifestyle_preferences lifestyle_preferences_student_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.lifestyle_preferences
    ADD CONSTRAINT lifestyle_preferences_student_id_key UNIQUE (student_id);


--
-- Name: match_history match_history_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.match_history
    ADD CONSTRAINT match_history_pkey PRIMARY KEY (match_id);


--
-- Name: room_assignment room_assignment_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.room_assignment
    ADD CONSTRAINT room_assignment_pkey PRIMARY KEY (assignment_id);


--
-- Name: room room_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.room
    ADD CONSTRAINT room_pkey PRIMARY KEY (room_id);


--
-- Name: roommate_request roommate_request_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.roommate_request
    ADD CONSTRAINT roommate_request_pkey PRIMARY KEY (request_id);


--
-- Name: student student_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.student
    ADD CONSTRAINT student_pkey PRIMARY KEY (student_id);


--
-- Name: student student_user_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.student
    ADD CONSTRAINT student_user_id_key UNIQUE (user_id);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: users users_username_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_username_key UNIQUE (username);


--
-- Name: compatibility_score compatibility_score_student1_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.compatibility_score
    ADD CONSTRAINT compatibility_score_student1_id_fkey FOREIGN KEY (student1_id) REFERENCES public.student(student_id);


--
-- Name: compatibility_score compatibility_score_student2_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.compatibility_score
    ADD CONSTRAINT compatibility_score_student2_id_fkey FOREIGN KEY (student2_id) REFERENCES public.student(student_id);


--
-- Name: lifestyle_preferences lifestyle_preferences_student_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.lifestyle_preferences
    ADD CONSTRAINT lifestyle_preferences_student_id_fkey FOREIGN KEY (student_id) REFERENCES public.student(student_id);


--
-- Name: match_history match_history_student1_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.match_history
    ADD CONSTRAINT match_history_student1_id_fkey FOREIGN KEY (student1_id) REFERENCES public.student(student_id);


--
-- Name: match_history match_history_student2_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.match_history
    ADD CONSTRAINT match_history_student2_id_fkey FOREIGN KEY (student2_id) REFERENCES public.student(student_id);


--
-- Name: room_assignment room_assignment_room_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.room_assignment
    ADD CONSTRAINT room_assignment_room_id_fkey FOREIGN KEY (room_id) REFERENCES public.room(room_id);


--
-- Name: room_assignment room_assignment_student_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.room_assignment
    ADD CONSTRAINT room_assignment_student_id_fkey FOREIGN KEY (student_id) REFERENCES public.student(student_id);


--
-- Name: room room_hostel_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.room
    ADD CONSTRAINT room_hostel_id_fkey FOREIGN KEY (hostel_id) REFERENCES public.hostel(hostel_id);


--
-- Name: roommate_request roommate_request_student_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.roommate_request
    ADD CONSTRAINT roommate_request_student_id_fkey FOREIGN KEY (student_id) REFERENCES public.student(student_id);


--
-- Name: student student_hostel_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.student
    ADD CONSTRAINT student_hostel_id_fkey FOREIGN KEY (hostel_id) REFERENCES public.hostel(hostel_id);


--
-- Name: student student_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.student
    ADD CONSTRAINT student_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--

\unrestrict sdTxawss358WPYKWmba9zf3M6o1B7cbDzjOMtTywCXeqF6UeL8oIqvexOMpaddD

