--
-- PostgreSQL database dump
--

\restrict HTPmYcmXzdKp1icPGREKED7UV6K0e7kYaF1aR3FbihCibNOh73y7baztsdhazLz

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
    request_status character varying(20),
    assigned_roommate_id integer
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
    id integer CONSTRAINT users_if_not_null NOT NULL,
    username character varying(100) NOT NULL,
    password text NOT NULL,
    role character varying(20) DEFAULT 'student'::character varying,
    email character varying(200) NOT NULL
);


ALTER TABLE public.users OWNER TO postgres;

--
-- Name: users_if_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.users_if_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.users_if_seq OWNER TO postgres;

--
-- Name: users_if_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.users_if_seq OWNED BY public.users.id;


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

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_if_seq'::regclass);


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
-- Name: users users_email_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_email_key UNIQUE (email);


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
-- Name: roommate_request roommate_request_assigned_roommate_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.roommate_request
    ADD CONSTRAINT roommate_request_assigned_roommate_id_fkey FOREIGN KEY (assigned_roommate_id) REFERENCES public.student(student_id);


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

\unrestrict HTPmYcmXzdKp1icPGREKED7UV6K0e7kYaF1aR3FbihCibNOh73y7baztsdhazLz

