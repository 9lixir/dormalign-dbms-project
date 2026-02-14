CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password TEXT NOT NULL
);


CREATE TABLE hostel (
    hostel_id SERIAL PRIMARY KEY,
    hostel_name VARCHAR(100),
    hostel_type VARCHAR(50),
    total_rooms INT
);


INSERT INTO hostel (hostel_name, hostel_type, total_rooms)
VALUES
('Boys Hostel', 'Boys', 50),
('Girls Hostel', 'Girls', 60);


CREATE TABLE student (
    student_id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    gender VARCHAR(10),
    department VARCHAR(50),
    year INT,
    hostel_id INT,
    FOREIGN KEY (hostel_id) REFERENCES hostel(hostel_id)
);


CREATE TABLE lifestyle_preferences (
    preference_id SERIAL PRIMARY KEY,
    student_id INT UNIQUE,
    sleep_time VARCHAR(20),
    cleanliness_level INT,
    noise_tolerance INT,
    guest_preference BOOLEAN,
    study_style VARCHAR(50),
    FOREIGN KEY (student_id) REFERENCES student(student_id)
);


CREATE TABLE roommate_request (
    request_id SERIAL PRIMARY KEY,
    student_id INT,
    preferred_room_type VARCHAR(50),
    request_status VARCHAR(20),
    FOREIGN KEY (student_id) REFERENCES student(student_id)
);


CREATE TABLE room (
    room_id SERIAL PRIMARY KEY,
    hostel_id INT,
    room_number VARCHAR(10),
    capacity INT,
    current_occupancy INT,
    FOREIGN KEY (hostel_id) REFERENCES hostel(hostel_id)
);


CREATE TABLE room_assignment (
    assignment_id SERIAL PRIMARY KEY,
    room_id INT,
    student_id INT,
    assigned_date DATE,
    FOREIGN KEY (room_id) REFERENCES room(room_id),
    FOREIGN KEY (student_id) REFERENCES student(student_id)
);


CREATE TABLE match_history (
    match_id SERIAL PRIMARY KEY,
    student1_id INT,
    student2_id INT,
    start_date DATE,
    end_date DATE,
    success_rating INT,
    FOREIGN KEY (student1_id) REFERENCES student(student_id),
    FOREIGN KEY (student2_id) REFERENCES student(student_id)
);


CREATE TABLE compatibility_score (
    score_id SERIAL PRIMARY KEY,
    student1_id INT,
    student2_id INT,
    compatibility_score INT,
    calculated_date DATE,
    FOREIGN KEY (student1_id) REFERENCES student(student_id),
    FOREIGN KEY (student2_id) REFERENCES student(student_id)
);