--
-- PostgreSQL database dump
--

-- Dumped from database version 14.13 (Homebrew)
-- Dumped by pg_dump version 14.15 (Homebrew)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: public; Type: SCHEMA; Schema: -; Owner: roctbb
--

CREATE SCHEMA public;


ALTER SCHEMA public OWNER TO roctbb;

--
-- Name: SCHEMA public; Type: COMMENT; Schema: -; Owner: roctbb
--

COMMENT ON SCHEMA public IS 'standard public schema';


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


ALTER TABLE public.alembic_version OWNER TO postgres;

--
-- Name: comments; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.comments (
    id integer NOT NULL,
    object_id integer NOT NULL,
    user_id integer NOT NULL,
    text text,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone DEFAULT now(),
    deleted_at timestamp without time zone
);


ALTER TABLE public.comments OWNER TO postgres;

--
-- Name: comments_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.comments_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.comments_id_seq OWNER TO postgres;

--
-- Name: comments_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.comments_id_seq OWNED BY public.comments.id;


--
-- Name: form_categories; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.form_categories (
    id integer NOT NULL,
    name character varying(256),
    params json DEFAULT '{}'::json,
    created_at timestamp without time zone DEFAULT now(),
    updated_at timestamp without time zone DEFAULT now(),
    deleted_at timestamp without time zone,
    creator_id integer,
    deleter_id integer,
    category_id integer
);


ALTER TABLE public.form_categories OWNER TO postgres;

--
-- Name: form_categories_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.form_categories_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.form_categories_id_seq OWNER TO postgres;

--
-- Name: form_categories_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.form_categories_id_seq OWNED BY public.form_categories.id;


--
-- Name: forms; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.forms (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    available_params json DEFAULT '[]'::json,
    fields json DEFAULT '[]'::json,
    created_at timestamp without time zone DEFAULT now(),
    updated_at timestamp without time zone DEFAULT now(),
    deleted_at timestamp without time zone,
    creator_id integer,
    deleter_id integer,
    category_id integer NOT NULL
);


ALTER TABLE public.forms OWNER TO postgres;

--
-- Name: forms_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.forms_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.forms_id_seq OWNER TO postgres;

--
-- Name: forms_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.forms_id_seq OWNED BY public.forms.id;


--
-- Name: invitations; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.invitations (
    id integer NOT NULL,
    email character varying(100),
    key character varying(100),
    role character varying(100) NOT NULL,
    created_at timestamp without time zone DEFAULT now(),
    updated_at timestamp without time zone DEFAULT now(),
    deleted_at timestamp without time zone,
    used_at timestamp without time zone,
    object_id integer,
    creator_id integer,
    deleter_id integer,
    user_id integer
);


ALTER TABLE public.invitations OWNER TO postgres;

--
-- Name: invitations_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.invitations_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.invitations_id_seq OWNER TO postgres;

--
-- Name: invitations_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.invitations_id_seq OWNED BY public.invitations.id;


--
-- Name: object_types; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.object_types (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    code character varying(100) NOT NULL,
    available_attributes json DEFAULT '[]'::json,
    available_params json DEFAULT '[]'::json,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone DEFAULT now() NOT NULL,
    params json DEFAULT '{}'::json
);


ALTER TABLE public.object_types OWNER TO postgres;

--
-- Name: object_types_form_categories; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.object_types_form_categories (
    object_type_id integer NOT NULL,
    form_category_id integer NOT NULL
);


ALTER TABLE public.object_types_form_categories OWNER TO postgres;

--
-- Name: object_types_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.object_types_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.object_types_id_seq OWNER TO postgres;

--
-- Name: object_types_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.object_types_id_seq OWNED BY public.object_types.id;


--
-- Name: object_user_association; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.object_user_association (
    object_id integer NOT NULL,
    user_id integer NOT NULL
);


ALTER TABLE public.object_user_association OWNER TO postgres;

--
-- Name: objects; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.objects (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    params json DEFAULT '{}'::json,
    attributes json DEFAULT '{}'::json,
    created_at timestamp without time zone DEFAULT now(),
    updated_at timestamp without time zone DEFAULT now(),
    deleted_at timestamp without time zone,
    type_id integer NOT NULL,
    creator_id integer,
    deleter_id integer
);


ALTER TABLE public.objects OWNER TO postgres;

--
-- Name: objects_children; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.objects_children (
    parent_id integer NOT NULL,
    child_id integer NOT NULL
);


ALTER TABLE public.objects_children OWNER TO postgres;

--
-- Name: objects_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.objects_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.objects_id_seq OWNER TO postgres;

--
-- Name: objects_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.objects_id_seq OWNED BY public.objects.id;


--
-- Name: submissions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.submissions (
    id integer NOT NULL,
    params json DEFAULT '{}'::json,
    answers json DEFAULT '{}'::json,
    created_at timestamp without time zone DEFAULT now(),
    updated_at timestamp without time zone DEFAULT now(),
    deleted_at timestamp without time zone,
    form_id integer NOT NULL,
    object_id integer NOT NULL,
    creator_id integer,
    deleter_id integer
);


ALTER TABLE public.submissions OWNER TO postgres;

--
-- Name: submissions_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.submissions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.submissions_id_seq OWNER TO postgres;

--
-- Name: submissions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.submissions_id_seq OWNED BY public.submissions.id;


--
-- Name: uploaded_files; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.uploaded_files (
    id integer NOT NULL,
    user_id integer NOT NULL,
    original_filename character varying(255) NOT NULL,
    stored_filename character varying(255)
);


ALTER TABLE public.uploaded_files OWNER TO postgres;

--
-- Name: uploaded_files_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.uploaded_files_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.uploaded_files_id_seq OWNER TO postgres;

--
-- Name: uploaded_files_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.uploaded_files_id_seq OWNED BY public.uploaded_files.id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.users (
    id integer NOT NULL,
    name character varying(100),
    email character varying(100) NOT NULL,
    password character varying(256),
    role character varying(100) NOT NULL,
    created_at timestamp without time zone DEFAULT now(),
    updated_at timestamp without time zone DEFAULT now()
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


ALTER TABLE public.users_id_seq OWNER TO postgres;

--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: users_objects; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.users_objects (
    object_id integer NOT NULL,
    user_id integer NOT NULL
);


ALTER TABLE public.users_objects OWNER TO postgres;

--
-- Name: comments id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.comments ALTER COLUMN id SET DEFAULT nextval('public.comments_id_seq'::regclass);


--
-- Name: form_categories id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.form_categories ALTER COLUMN id SET DEFAULT nextval('public.form_categories_id_seq'::regclass);


--
-- Name: forms id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.forms ALTER COLUMN id SET DEFAULT nextval('public.forms_id_seq'::regclass);


--
-- Name: invitations id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.invitations ALTER COLUMN id SET DEFAULT nextval('public.invitations_id_seq'::regclass);


--
-- Name: object_types id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.object_types ALTER COLUMN id SET DEFAULT nextval('public.object_types_id_seq'::regclass);


--
-- Name: objects id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.objects ALTER COLUMN id SET DEFAULT nextval('public.objects_id_seq'::regclass);


--
-- Name: submissions id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.submissions ALTER COLUMN id SET DEFAULT nextval('public.submissions_id_seq'::regclass);


--
-- Name: uploaded_files id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.uploaded_files ALTER COLUMN id SET DEFAULT nextval('public.uploaded_files_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Data for Name: alembic_version; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.alembic_version (version_num) FROM stdin;
66cedc709741
\.


--
-- Data for Name: comments; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.comments (id, object_id, user_id, text, created_at, updated_at, deleted_at) FROM stdin;
1	1	1	test	2025-03-02 18:14:17.773146	2025-03-02 18:14:17.773146	\N
5	1	1	Test	2025-03-02 18:17:56.470397	2025-03-02 18:35:44.399383	2025-03-02 18:35:44.399383
4	1	1	test	2025-03-02 18:15:45.561385	2025-03-02 18:35:46.806941	2025-03-02 18:35:46.806941
3	1	1	test	2025-03-02 18:15:14.665879	2025-03-02 18:35:48.596134	2025-03-02 18:35:48.596134
2	1	1	test	2025-03-02 18:14:54.042825	2025-03-02 18:35:51.362067	2025-03-02 18:35:51.362067
\.


--
-- Data for Name: form_categories; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.form_categories (id, name, params, created_at, updated_at, deleted_at, creator_id, deleter_id, category_id) FROM stdin;
1	Тьюторинг	{}	2025-03-02 19:02:15.091935	2025-03-02 19:02:15.091935	\N	\N	\N	\N
2	Успеваемость	{}	2025-03-02 19:02:15.091935	2025-03-02 19:02:15.091935	\N	\N	\N	\N
\.


--
-- Data for Name: forms; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.forms (id, name, available_params, fields, created_at, updated_at, deleted_at, creator_id, deleter_id, category_id) FROM stdin;
1	test1	[]	[{"name": "test", "code": "4brr6ig51uq4d1chdyvvjf", "type": "text", "required": false, "options": []}]	2025-03-02 22:38:53.211269	2025-03-02 22:53:25.452475	\N	1	\N	1
2	qwerqwe	[]	[{"name": "weqrqwer", "code": "j6lynziib6n91rp6pohnxf", "type": "text", "required": false, "options": []}, {"name": "qwerqwer", "code": "s5svax8ctfap2i39buvpu", "type": "text", "required": false, "options": []}, {"name": "qwerqwer", "code": "rnz9su0d5rfcmvocilt9pn", "type": "text", "required": false, "options": []}]	2025-03-02 22:56:13.580117	2025-03-02 22:56:56.670647	2025-03-02 22:56:56.670647	1	\N	2
3	sdf	[]	[{"name": "sdfsdf", "code": "so22hw5jdeq5az1tkghqei", "type": "text", "required": false, "options": []}]	2025-03-02 22:57:14.915691	2025-03-02 22:57:14.915691	\N	1	\N	2
\.


--
-- Data for Name: invitations; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.invitations (id, email, key, role, created_at, updated_at, deleted_at, used_at, object_id, creator_id, deleter_id, user_id) FROM stdin;
1	\N	12345	admin	2025-03-01 16:57:04.795216	2025-03-01 20:00:24.197365	\N	2025-03-01 20:00:24.197365	\N	\N	\N	1
\.


--
-- Data for Name: object_types; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.object_types (id, name, code, available_attributes, available_params, created_at, updated_at, params) FROM stdin;
2	Группы	groups	[]	[]	2025-03-01 16:55:07.970591	2025-03-01 16:55:07.970591	{"index": 4, "possible_children": ["students"]}
3	События	events	[]	[]	2025-03-01 16:55:07.970591	2025-03-01 16:55:07.970591	{"index": 3, "possible_children": ["students"]}
1	Ученики	students	[{"name": "Класс", "code": "grade", "type": "number", "display": true, "show_off": true}, {"name": "Фото", "code": "photo", "type": "file", "display": false, "show_off": false}, {"name": "Дата рождения", "code": "birthday", "type": "date", "display": true, "show_off": true}, {"name": "Телефон", "code": "phone", "type": "string", "display": true, "show_off": false}, {"name": "Telegram", "code": "tg", "type": "string", "display": true, "show_off": false}, {"name": "Контакты родителей", "code": "tg", "type": "text", "display": true, "show_off": false}]	[]	2025-03-01 16:55:07.970591	2025-03-01 16:55:07.970591	{"index": 1, "possible_children": []}
4	Проекты	projects	[{"name": "Описание", "code": "description", "type": "text", "display": true, "show_off": false}, {"name": "Репозиторий", "code": "repo", "type": "string", "display": true, "show_off": false}, {"name": "Направления", "code": "groups", "type": "checkboxes", "options": ["Математика", "ИТ", "Физика", "Лингвистика"], "display": true, "show_off": true}, {"name": "Тип", "code": "type", "type": "select", "options": ["Проект", "Исследование"], "display": true, "show_off": true}]	[]	2025-03-01 16:55:07.970591	2025-03-01 16:55:07.970591	{"index": 2, "possible_children": ["students", "events"]}
\.


--
-- Data for Name: object_types_form_categories; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.object_types_form_categories (object_type_id, form_category_id) FROM stdin;
1	1
1	2
\.


--
-- Data for Name: object_user_association; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.object_user_association (object_id, user_id) FROM stdin;
\.


--
-- Data for Name: objects; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.objects (id, name, params, attributes, created_at, updated_at, deleted_at, type_id, creator_id, deleter_id) FROM stdin;
1	Иванов Иван	{}	{"birthday": "27.04.1994", "grade": 7, "photo": "https://sun9-46.userapi.com/impg/IiUiukOkBu93UXF9jG4tFJYnP7yv0IvEqTtlRQ/uVIb1ndnhLg.jpg?size=545x604&quality=96&sign=ea1415c4a0f92613e5c3ee5b7f2f7eff&type=album"}	2025-03-01 20:07:44.599041	2025-03-01 22:07:14.170614	\N	1	1	\N
4	Иванов Иван	{}	{"birthday": "12.05.2014", "grade": 7, "photo": "http://localhost:8081/api/files/folder_3/rubcev.jpeg", "phone": "89150187307"}	2025-03-01 21:36:05.637954	2025-03-01 22:54:46.087587	\N	1	1	\N
5	Лупатория	{}	{}	2025-03-01 23:41:10.323705	2025-03-01 23:41:10.323705	\N	3	1	\N
2	Петр Петров1	{}	{"grade": 8, "photo": "http://localhost:8081/api/files/folder_4/rubcev.jpeg", "phone": "89150187307"}	2025-03-01 20:07:51.487502	2025-03-02 16:31:24.990722	\N	1	1	\N
3	Кандибобер	{}	{"description": "\\u041e\\u0447\\u0435\\u043d\\u044c \\u0438\\u043d\\u0442\\u0435\\u0440\\u0435\\u0441\\u043d\\u044b\\u0439 \\u043f\\u0440\\u043e\\u0435\\u043a\\u0442", "groups": ["\\u0418\\u0422", "\\u041c\\u0430\\u0442\\u0435\\u043c\\u0430\\u0442\\u0438\\u043a\\u0430"], "type": "\\u041f\\u0440\\u043e\\u0435\\u043a\\u0442"}	2025-03-01 20:50:29.562204	2025-03-02 16:47:23.919284	\N	4	1	\N
\.


--
-- Data for Name: objects_children; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.objects_children (parent_id, child_id) FROM stdin;
3	1
3	2
3	5
\.


--
-- Data for Name: submissions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.submissions (id, params, answers, created_at, updated_at, deleted_at, form_id, object_id, creator_id, deleter_id) FROM stdin;
\.


--
-- Data for Name: uploaded_files; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.uploaded_files (id, user_id, original_filename, stored_filename) FROM stdin;
1	1	rubcev.jpeg	rubcev.jpeg
2	1	rubcev.jpeg	rubcev.jpeg
3	1	rubcev.jpeg	rubcev.jpeg
4	1	rubcev.jpeg	rubcev.jpeg
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.users (id, name, email, password, role, created_at, updated_at) FROM stdin;
1	Ростислав	roctbb@gmail.com	$2b$12$e0owr5VVX1x/JjCAZyydAOCbTI7BVXmpL3o3Iesg8t4BGswtywZfm	admin	2025-03-01 20:00:24.197365	2025-03-01 20:00:24.197365
\.


--
-- Data for Name: users_objects; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.users_objects (object_id, user_id) FROM stdin;
\.


--
-- Name: comments_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.comments_id_seq', 5, true);


--
-- Name: form_categories_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.form_categories_id_seq', 2, true);


--
-- Name: forms_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.forms_id_seq', 3, true);


--
-- Name: invitations_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.invitations_id_seq', 1, true);


--
-- Name: object_types_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.object_types_id_seq', 4, true);


--
-- Name: objects_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.objects_id_seq', 5, true);


--
-- Name: submissions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.submissions_id_seq', 1, false);


--
-- Name: uploaded_files_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.uploaded_files_id_seq', 4, true);


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.users_id_seq', 1, true);


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: comments comments_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.comments
    ADD CONSTRAINT comments_pkey PRIMARY KEY (id);


--
-- Name: form_categories form_categories_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.form_categories
    ADD CONSTRAINT form_categories_pkey PRIMARY KEY (id);


--
-- Name: forms forms_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.forms
    ADD CONSTRAINT forms_pkey PRIMARY KEY (id);


--
-- Name: invitations invitations_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.invitations
    ADD CONSTRAINT invitations_pkey PRIMARY KEY (id);


--
-- Name: object_types_form_categories object_types_form_categories_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.object_types_form_categories
    ADD CONSTRAINT object_types_form_categories_pkey PRIMARY KEY (object_type_id, form_category_id);


--
-- Name: object_types object_types_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.object_types
    ADD CONSTRAINT object_types_pkey PRIMARY KEY (id);


--
-- Name: object_user_association object_user_association_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.object_user_association
    ADD CONSTRAINT object_user_association_pkey PRIMARY KEY (object_id, user_id);


--
-- Name: objects_children objects_children_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.objects_children
    ADD CONSTRAINT objects_children_pkey PRIMARY KEY (parent_id, child_id);


--
-- Name: objects objects_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.objects
    ADD CONSTRAINT objects_pkey PRIMARY KEY (id);


--
-- Name: submissions submissions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.submissions
    ADD CONSTRAINT submissions_pkey PRIMARY KEY (id);


--
-- Name: uploaded_files uploaded_files_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.uploaded_files
    ADD CONSTRAINT uploaded_files_pkey PRIMARY KEY (id);


--
-- Name: users users_email_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_email_key UNIQUE (email);


--
-- Name: users_objects users_objects_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users_objects
    ADD CONSTRAINT users_objects_pkey PRIMARY KEY (object_id, user_id);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: comments comments_object_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.comments
    ADD CONSTRAINT comments_object_id_fkey FOREIGN KEY (object_id) REFERENCES public.objects(id) ON DELETE CASCADE;


--
-- Name: comments comments_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.comments
    ADD CONSTRAINT comments_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: form_categories form_categories_category_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.form_categories
    ADD CONSTRAINT form_categories_category_id_fkey FOREIGN KEY (category_id) REFERENCES public.form_categories(id) ON DELETE CASCADE;


--
-- Name: form_categories form_categories_creator_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.form_categories
    ADD CONSTRAINT form_categories_creator_id_fkey FOREIGN KEY (creator_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: form_categories form_categories_deleter_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.form_categories
    ADD CONSTRAINT form_categories_deleter_id_fkey FOREIGN KEY (deleter_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: forms forms_category_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.forms
    ADD CONSTRAINT forms_category_id_fkey FOREIGN KEY (category_id) REFERENCES public.form_categories(id) ON DELETE CASCADE;


--
-- Name: forms forms_creator_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.forms
    ADD CONSTRAINT forms_creator_id_fkey FOREIGN KEY (creator_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: forms forms_deleter_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.forms
    ADD CONSTRAINT forms_deleter_id_fkey FOREIGN KEY (deleter_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: invitations invitations_creator_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.invitations
    ADD CONSTRAINT invitations_creator_id_fkey FOREIGN KEY (creator_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: invitations invitations_deleter_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.invitations
    ADD CONSTRAINT invitations_deleter_id_fkey FOREIGN KEY (deleter_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: invitations invitations_object_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.invitations
    ADD CONSTRAINT invitations_object_id_fkey FOREIGN KEY (object_id) REFERENCES public.objects(id) ON DELETE CASCADE;


--
-- Name: invitations invitations_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.invitations
    ADD CONSTRAINT invitations_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: object_types_form_categories object_types_form_categories_form_category_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.object_types_form_categories
    ADD CONSTRAINT object_types_form_categories_form_category_id_fkey FOREIGN KEY (form_category_id) REFERENCES public.form_categories(id) ON DELETE CASCADE;


--
-- Name: object_types_form_categories object_types_form_categories_object_type_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.object_types_form_categories
    ADD CONSTRAINT object_types_form_categories_object_type_id_fkey FOREIGN KEY (object_type_id) REFERENCES public.object_types(id) ON DELETE CASCADE;


--
-- Name: object_user_association object_user_association_object_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.object_user_association
    ADD CONSTRAINT object_user_association_object_id_fkey FOREIGN KEY (object_id) REFERENCES public.objects(id);


--
-- Name: object_user_association object_user_association_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.object_user_association
    ADD CONSTRAINT object_user_association_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: objects_children objects_children_child_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.objects_children
    ADD CONSTRAINT objects_children_child_id_fkey FOREIGN KEY (child_id) REFERENCES public.objects(id) ON DELETE CASCADE;


--
-- Name: objects_children objects_children_parent_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.objects_children
    ADD CONSTRAINT objects_children_parent_id_fkey FOREIGN KEY (parent_id) REFERENCES public.objects(id) ON DELETE CASCADE;


--
-- Name: objects objects_creator_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.objects
    ADD CONSTRAINT objects_creator_id_fkey FOREIGN KEY (creator_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: objects objects_deleter_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.objects
    ADD CONSTRAINT objects_deleter_id_fkey FOREIGN KEY (deleter_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: objects objects_type_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.objects
    ADD CONSTRAINT objects_type_id_fkey FOREIGN KEY (type_id) REFERENCES public.object_types(id) ON DELETE CASCADE;


--
-- Name: submissions submissions_creator_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.submissions
    ADD CONSTRAINT submissions_creator_id_fkey FOREIGN KEY (creator_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: submissions submissions_deleter_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.submissions
    ADD CONSTRAINT submissions_deleter_id_fkey FOREIGN KEY (deleter_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: submissions submissions_form_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.submissions
    ADD CONSTRAINT submissions_form_id_fkey FOREIGN KEY (form_id) REFERENCES public.forms(id) ON DELETE CASCADE;


--
-- Name: submissions submissions_object_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.submissions
    ADD CONSTRAINT submissions_object_id_fkey FOREIGN KEY (object_id) REFERENCES public.objects(id) ON DELETE CASCADE;


--
-- Name: uploaded_files uploaded_files_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.uploaded_files
    ADD CONSTRAINT uploaded_files_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: users_objects users_objects_object_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users_objects
    ADD CONSTRAINT users_objects_object_id_fkey FOREIGN KEY (object_id) REFERENCES public.objects(id) ON DELETE CASCADE;


--
-- Name: users_objects users_objects_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users_objects
    ADD CONSTRAINT users_objects_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--

