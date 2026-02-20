from flask import Flask, render_template, request, redirect, session
import os
import psycopg2
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY")

# Mail config
app.config["MAIL_SERVER"] = os.environ.get("MAIL_SERVER")
app.config["MAIL_PORT"] = int(os.environ.get("MAIL_PORT", 587))
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = os.environ.get("MAIL_USERNAME")
app.config["MAIL_PASSWORD"] = os.environ.get("MAIL_PASSWORD")
app.config["MAIL_DEFAULT_SENDER"] = os.environ.get("MAIL_DEFAULT_SENDER")

mail = Mail(app)
serializer = URLSafeTimedSerializer(app.secret_key)


import uuid  # Generates unique file names so uploads never collide

ALLOWED_PROFILE_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}  # Allowed image types
PROFILE_UPLOAD_FOLDER = os.path.join(app.root_path, "static", "uploads", "profile_pictures")  # folger path
os.makedirs(PROFILE_UPLOAD_FOLDER, exist_ok=True)  # Creates folder if it does not exist
app.config["MAX_CONTENT_LENGTH"] = 3 * 1024 * 1024  # Max upload size = 3 MB

def allowed_profile_image(filename):  # Small validator for uploaded file names
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_PROFILE_EXTENSIONS  # True only for allowed extensions


def get_db_connection():
    database_url = os.environ.get("DB_URL")
    if database_url:
        return psycopg2.connect(database_url)
    else:
        return psycopg2.connect(
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),

        )


def get_student_id_by_user_id(cur, user_id):
    cur.execute("SELECT student_id FROM student WHERE user_id = %s", (user_id,))
    row = cur.fetchone()
    return row[0] if row else None


def is_admin():
    if "user_id" not in session:
        return False
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT role FROM users WHERE id = %s", (session["user_id"],))
    user = cur.fetchone()
    cur.close()
    conn.close()
    return user is not None and user[0] == "admin"


def get_user_row(cur, user_id):
    cur.execute(
        "SELECT id, username, email, role, profile_picture FROM users WHERE id = %s",
        (user_id,)
    )
    row = cur.fetchone()
    if not row:
        return None
    return {
        "id": row[0],
        "username": row[1],
        "email": row[2],
        "role": row[3],
        "profile_picture": row[4],
    }


def admin_room_redirect(message=None, error=None):
    query_parts = []
    if message:
        query_parts.append(f"room_msg={message}")
    if error:
        query_parts.append(f"room_err={error}")
    query_string = "&".join(query_parts)
    if query_string:
        return redirect(f"/admin/rooms?{query_string}")
    return redirect("/admin/rooms")


def get_admin_summary_stats(cur):
    cur.execute("SELECT COUNT(*) FROM student")
    total_students = cur.fetchone()[0]

    cur.execute("SELECT COUNT(DISTINCT student_id) FROM room_assignment")
    assigned_students = cur.fetchone()[0]
    unassigned_students = max(total_students - assigned_students, 0)

    cur.execute("SELECT COUNT(*) FROM room")
    total_rooms = cur.fetchone()[0]

    cur.execute(
        """
        SELECT
            COALESCE(COUNT(*) FILTER (WHERE COALESCE(current_occupancy, 0) > 0), 0),
            COALESCE(COUNT(*) FILTER (WHERE COALESCE(current_occupancy, 0) < COALESCE(capacity, 0)), 0)
        FROM room
        """
    )
    occupied_rooms, available_rooms = cur.fetchone()

    cur.execute("SELECT COUNT(*) FROM roommate_request WHERE COALESCE(request_status, '') ILIKE 'pending'")
    pending_requests = cur.fetchone()[0]

    cur.execute(
        """
        SELECT COALESCE(SUM(capacity), 0), COALESCE(SUM(COALESCE(current_occupancy, 0)), 0)
        FROM room
        """
    )
    total_capacity, occupied_capacity = cur.fetchone()
    capacity_left = max(total_capacity - occupied_capacity, 0)
    occupancy_percent = round((occupied_capacity / total_capacity) * 100, 1) if total_capacity else 0

    system_status = (
        "System Status: Stable"
        if unassigned_students == 0 and pending_requests == 0
        else f"Warning: {unassigned_students} students unassigned"
    )

    stats = {
        "total_students": total_students,
        "assigned_students": assigned_students,
        "unassigned_students": unassigned_students,
        "total_rooms": total_rooms,
        "occupied_rooms": occupied_rooms,
        "available_rooms": available_rooms,
        "pending_requests": pending_requests,
        "capacity_left": capacity_left,
        "occupancy_percent": occupancy_percent,
    }
    return stats, system_status

#compat scores calculation

def calculate_compatibility(s1,s2):
    score = 0
    if s1["sleep_time"] == s2["sleep_time"]:
        score += 25

    if s1["study_style"] == s2["study_style"]:
        score += 20

    if abs(int(s1["cleanliness_level"]) - int(s2["cleanliness_level"])) <= 1:
        score += 20

    if abs(int(s1["noise_tolerance"]) - int(s2["noise_tolerance"])) <= 1:
        score += 20

    if s1["guest_preference"] == s2["guest_preference"]:
        score += 15

    return score


@app.route("/")
def home():
    if "user_id" not in session:
        return render_template("index.html", user_type=None)

    if is_admin():
        user_type = "admin"
    else:
        user_type = "student"

    return render_template("index.html", user_type=user_type)

@app.route("/register", methods=["GET", "POST"])
def register():
    error = None

    if request.method == "POST":
        username = request.form["username"].strip()
        email = request.form["email"].strip()
        password = generate_password_hash(request.form["password"])

        conn = get_db_connection()
        cur = conn.cursor()

        # Check duplicate username
        cur.execute("SELECT 1 FROM users WHERE username = %s", (username,))
        if cur.fetchone():
            error = "Username already exists. Please choose another."
        else:
            # Check duplicate email
            cur.execute("SELECT 1 FROM users WHERE email = %s", (email,))
            if cur.fetchone():
                error = "Email already registered. Please use another."
            else:
                # Insert user with is_verified = False
                cur.execute(
                    "INSERT INTO users (username, password, email, is_verified) VALUES (%s, %s, %s, %s)",
                    (username, password, email, False)
                )
                conn.commit()

                # Generate verification token and send email
                token = serializer.dumps(email, salt="email-verify")
                verify_url = f"http://127.0.0.1:5001/verify/{token}"

                msg = Message("Verify your DormAlign account", recipients=[email])
                msg.body = f"Hi {username},\n\nPlease verify your email by clicking this link:\n{verify_url}\n\nThis link expires in 1 hour.\n\n- DormAlign Team"
                mail.send(msg)

                cur.close()
                conn.close()
                return redirect("/verify-pending")

        cur.close()
        conn.close()

    return render_template("register.html", error=error)

@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT id, password, is_verified FROM users WHERE username = %s",
            (username,)
        )
        user = cur.fetchone()
        cur.close()
        conn.close()

        if user and check_password_hash(user[1], password):
            if not user[2]:  # is_verified is False
                error = "Please verify your email before logging in."
                return render_template("login.html", error=error)
            session["user_id"] = user[0]
            return redirect("/")
        error = "Invalid username or password."
        return render_template("login.html", error=error)

    return render_template("login.html", error=error)
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

@app.route("/verify-pending")
def verify_pending():
    return render_template("verify_pending.html")


@app.route("/verify/<token>")
def verify_email(token):
    try:
        email = serializer.loads(token, salt="email-verify", max_age=3600)
    except SignatureExpired:
        return render_template("login.html", error="Verification link has expired. Please register again.")
    except BadSignature:
        return render_template("login.html", error="Invalid verification link.")

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE users SET is_verified = TRUE WHERE email = %s",
        (email,)
    )
    conn.commit()
    cur.close()
    conn.close()
    return redirect("/login?verified=1")


@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    message = None
    error = None
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT username FROM users WHERE email = %s", (email,))
        user = cur.fetchone()
        cur.close()
        conn.close()

        if user:
            token = serializer.dumps(email, salt="password-reset")
            reset_url = f"http://127.0.0.1:5001/reset-password/{token}"
            msg = Message("Reset your DormAlign password", recipients=[email])
            msg.body = f"Hi {user[0]},\n\nClick this link to reset your password:\n{reset_url}\n\nThis link expires in 1 hour.\n\n- DormAlign Team"
            mail.send(msg)
        message = "If that email is registered, a reset link has been sent."

    return render_template("forgot_password.html", message=message, error=error)


@app.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):
    try:
        email = serializer.loads(token, salt="password-reset", max_age=3600)
    except SignatureExpired:
        return render_template("login.html", error="Reset link has expired. Please try again.")
    except BadSignature:
        return render_template("login.html", error="Invalid reset link.")

    error = None
    if request.method == "POST":
        new_password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        if not new_password:
            error = "Password cannot be empty."
        elif new_password != confirm_password:
            error = "Passwords do not match."
        else:
            hashed = generate_password_hash(new_password)
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute(
                "UPDATE users SET password = %s WHERE email = %s",
                (hashed, email)
            )
            conn.commit()
            cur.close()
            conn.close()
            return redirect("/login?reset=1")

    return render_template("reset_password.html", token=token, error=error)

@app.route("/roommate", methods=["GET", "POST"])
def roommate():
    if "user_id" not in session:
        return redirect("/login")

    if request.method == "POST":
        name = request.form.get("name")
        gender = request.form.get("gender")
        department = request.form.get("department")
        year = request.form.get("year")
        hostel_id = request.form.get("hostel_id")

        sleep_time = request.form.get("sleep_time")
        cleanliness_level = request.form.get("cleanliness_level")
        noise_tolerance = request.form.get("noise_tolerance")
        guest_preference = request.form.get("guest_preference") == "True"
        study_style = request.form.get("study_style")

        preferred_room_type = request.form.get("preferred_room_type")

        conn = get_db_connection()
        cur = conn.cursor()

        user_id = session["user_id"]
        student_id = get_student_id_by_user_id(cur, user_id)

        if student_id:
            cur.execute("""
                UPDATE student
                SET name = %s, gender = %s, department = %s, year = %s, hostel_id = %s
                WHERE student_id = %s
            """, (name, gender, department, year, hostel_id, student_id))
        else:
            cur.execute("""
                INSERT INTO student (user_id, name, gender, department, year, hostel_id)
                VALUES (%s, %s, %s, %s, %s, %s) RETURNING student_id
            """, (user_id, name, gender, department, year, hostel_id))
            student_id = cur.fetchone()[0]

        cur.execute("""
            INSERT INTO lifestyle_preferences
            (student_id, sleep_time, cleanliness_level, noise_tolerance, guest_preference, study_style)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (student_id)
            DO UPDATE SET
                sleep_time = EXCLUDED.sleep_time,
                cleanliness_level = EXCLUDED.cleanliness_level,
                noise_tolerance = EXCLUDED.noise_tolerance,
                guest_preference = EXCLUDED.guest_preference,
                study_style = EXCLUDED.study_style
        """, (student_id, sleep_time, cleanliness_level, noise_tolerance, guest_preference, study_style))

        cur.execute("SELECT request_id FROM roommate_request WHERE student_id = %s", (student_id,))
        request_row = cur.fetchone()
        if request_row:
            cur.execute("""
                UPDATE roommate_request
                SET preferred_room_type = %s
                WHERE request_id = %s
            """, (preferred_room_type, request_row[0]))
        else:
            cur.execute("""
                INSERT INTO roommate_request (student_id, preferred_room_type, request_status)
                VALUES (%s, %s, %s)
            """, (student_id, preferred_room_type, "Pending"))

        conn.commit()
        cur.close()
        conn.close()

        return redirect("/dashboard")

    return render_template("roommate_form.html")

@app.route("/submissions")
def submissions():
    if "user_id" not in session:
        return redirect("/login")
    if not is_admin():
        return "Access Denied", 403

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT s.student_id, s.name, s.gender, s.department, s.year, h.hostel_name,
               l.sleep_time, l.cleanliness_level, l.noise_tolerance, l.guest_preference, l.study_style,
               r.preferred_room_type
        FROM student s
        JOIN hostel h ON s.hostel_id = h.hostel_id
        LEFT JOIN lifestyle_preferences l ON s.student_id = l.student_id
        LEFT JOIN roommate_request r ON s.student_id = r.student_id
    """)
    students = cur.fetchall()
    cur.close()
    conn.close()

    return render_template("submissions.html", students=students)

@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect("/login")

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT s.student_id, s.name, s.department, s.year, h.hostel_name,
               l.sleep_time, l.study_style, l.cleanliness_level, l.noise_tolerance
        FROM student s
        JOIN hostel h ON s.hostel_id = h.hostel_id
        LEFT JOIN lifestyle_preferences l ON s.student_id = l.student_id
        WHERE s.user_id = %s
    """, (session["user_id"],))
    
    data = cur.fetchone()
    cur.close()
    conn.close()

    if not data:
        return "<h2>No data found for this user.</h2>"

    student = {
        "student_id": data[0],
        "name": data[1],
        "department": data[2],
        "year": data[3],
        "hostel_name": data[4]
    }

    preferences = {
        "sleep_time": data[5],
        "study_style": data[6],
        "cleanliness_level": data[7],
        "noise_tolerance": data[8]
    }

    return render_template("dashboard.html", student=student, preferences=preferences)


@app.route("/student/compatibility")
def student_compatibility():
    if "user_id" not in session:
        return redirect("/login")

    conn = get_db_connection()
    cur = conn.cursor()

    student_id = get_student_id_by_user_id(cur, session["user_id"])
    if not student_id:
        cur.close()
        conn.close()
        return redirect("/roommate")

    cur.execute(
        """
        SELECT s.name, s.department, s.year
        FROM student s
        WHERE s.student_id = %s
        """,
        (student_id,)
    )
    me = cur.fetchone()

    cur.execute(
        """
        SELECT assigned_roommate_id, COALESCE(request_status, ''), COALESCE(preferred_room_type, '')
        FROM roommate_request
        WHERE student_id = %s
        ORDER BY request_id
        LIMIT 1
        """,
        (student_id,)
    )
    my_request = cur.fetchone()
    current_target_id = my_request[0] if my_request else None
    current_status = (my_request[1] if my_request else "").lower()
    preferred_room_type = (my_request[2] if my_request else "").lower()

    cur.execute(
        """
        SELECT
            other.student_id,
            other.name,
            other.department,
            other.year,
            c.compatibility_score
        FROM compatibility_score c
        JOIN student other
          ON other.student_id = CASE
                WHEN c.student1_id = %s THEN c.student2_id
                ELSE c.student1_id
             END
        WHERE c.student1_id = %s OR c.student2_id = %s
        ORDER BY c.compatibility_score DESC, other.name ASC
        """,
        (student_id, student_id, student_id)
    )
    rows = cur.fetchall()

    cur.execute(
        """
        SELECT EXISTS(
            SELECT 1 FROM room_assignment WHERE student_id = %s
        )
        """,
        (student_id,)
    )
    has_room_assignment = bool(cur.fetchone()[0])

    cur.close()
    conn.close()

    cards = []
    for row in rows:
        cards.append(
            {
                "student_id": row[0],
                "name": row[1],
                "department": row[2],
                "year": row[3],
                "score": row[4],
                "request_sent": current_target_id == row[0] and current_status == "pending",
            }
        )

    request_error = request.args.get("err")
    request_ok = request.args.get("ok")
    block_reason = None
    if has_room_assignment:
        block_reason = "You already have a room assigned."
    elif preferred_room_type == "single":
        block_reason = "Single-room preference is active; roommate requests are disabled."

    current_user = {
        "name": me[0] if me else "",
        "department": me[1] if me else "",
        "year": me[2] if me else "",
    }

    return render_template(
        "student_compatibility.html",
        current_user=current_user,
        matches=cards,
        block_reason=block_reason,
        request_ok=request_ok,
        request_error=request_error,
    )


@app.route("/student/send_request/<int:target_student_id>", methods=["POST"])
def student_send_request(target_student_id):
    if "user_id" not in session:
        return redirect("/login")

    conn = get_db_connection()
    cur = conn.cursor()

    student_id = get_student_id_by_user_id(cur, session["user_id"])
    if not student_id:
        cur.close()
        conn.close()
        return redirect("/roommate")

    if student_id == target_student_id:
        cur.close()
        conn.close()
        return redirect("/student/compatibility?err=self_request")

    cur.execute(
        """
        SELECT s1.hostel_id, s2.hostel_id
        FROM student s1
        JOIN student s2 ON s2.student_id = %s
        WHERE s1.student_id = %s
        """,
        (target_student_id, student_id)
    )
    hostels = cur.fetchone()
    if not hostels or hostels[0] != hostels[1]:
        cur.close()
        conn.close()
        return redirect("/student/compatibility?err=hostel_mismatch")

    cur.execute(
        "SELECT EXISTS(SELECT 1 FROM room_assignment WHERE student_id = %s)",
        (student_id,)
    )
    if cur.fetchone()[0]:
        cur.close()
        conn.close()
        return redirect("/student/compatibility?err=already_assigned")

    cur.execute(
        """
        SELECT COALESCE(preferred_room_type, '')
        FROM roommate_request
        WHERE student_id = %s
        ORDER BY request_id
        LIMIT 1
        """,
        (student_id,)
    )
    room_pref = cur.fetchone()
    if room_pref and str(room_pref[0]).lower() == "single":
        cur.close()
        conn.close()
        return redirect("/student/compatibility?err=single_pref")

    cur.execute(
        """
        UPDATE roommate_request
        SET assigned_roommate_id = %s, request_status = 'Pending'
        WHERE student_id = %s
        """,
        (target_student_id, student_id)
    )
    if cur.rowcount == 0:
        cur.execute(
            """
            INSERT INTO roommate_request (student_id, preferred_room_type, request_status, assigned_roommate_id)
            VALUES (%s, 'Double', 'Pending', %s)
            """,
            (student_id, target_student_id)
        )

    conn.commit()
    cur.close()
    conn.close()
    return redirect("/student/compatibility?ok=1")


@app.route("/student/assignment")
def student_assignment():
    if "user_id" not in session:
        return redirect("/login")

    conn = get_db_connection()
    cur = conn.cursor()

    student_id = get_student_id_by_user_id(cur, session["user_id"])
    if not student_id:
        cur.close()
        conn.close()
        return redirect("/roommate")

    cur.execute(
        """
        SELECT
            r.room_id,
            r.room_number,
            h.hostel_name,
            ra.assigned_date
        FROM room_assignment ra
        JOIN room r ON r.room_id = ra.room_id
        JOIN hostel h ON h.hostel_id = r.hostel_id
        WHERE ra.student_id = %s
        ORDER BY ra.assignment_id DESC
        LIMIT 1
        """,
        (student_id,)
    )
    assignment = cur.fetchone()

    roommates = []
    if assignment:
        cur.execute(
            """
            SELECT s.name
            FROM room_assignment ra
            JOIN student s ON s.student_id = ra.student_id
            WHERE ra.room_id = %s
              AND ra.student_id <> %s
            ORDER BY s.name
            """,
            (assignment[0], student_id)
        )
        roommates = [r[0] for r in cur.fetchall()]

    cur.close()
    conn.close()

    assignment_data = None
    if assignment:
        assignment_data = {
            "room_number": assignment[1],
            "hostel_name": assignment[2],
            "assigned_date": assignment[3],
            "roommates": roommates,
        }

    return render_template("student_assignment.html", assignment=assignment_data)

@app.route("/update_preferences", methods=["GET", "POST"])
def update_preferences():
    if "user_id" not in session:
        return redirect("/login")

    conn = get_db_connection()
    cur = conn.cursor()
    student_id = get_student_id_by_user_id(cur, session["user_id"])

    if not student_id:
        cur.close()
        conn.close()
        return redirect("/roommate")

    # Get current preferences
    cur.execute("""
        SELECT sleep_time, cleanliness_level, noise_tolerance, guest_preference, study_style
        FROM lifestyle_preferences
        WHERE student_id = %s
    """, (student_id,))
    pref = cur.fetchone()

    if request.method == "POST":
        sleep_time = request.form.get("sleep_time")
        cleanliness_level = request.form.get("cleanliness_level")
        noise_tolerance = request.form.get("noise_tolerance")
        guest_preference = request.form.get("guest_preference") == "True"
        study_style = request.form.get("study_style")

        # Update preferences
        if pref:
            cur.execute("""
                UPDATE lifestyle_preferences
                SET sleep_time=%s, cleanliness_level=%s, noise_tolerance=%s,
                    guest_preference=%s, study_style=%s
                WHERE student_id=%s
            """, (sleep_time, cleanliness_level, noise_tolerance, guest_preference, study_style, student_id))
        else:
            cur.execute("""
                INSERT INTO lifestyle_preferences (student_id, sleep_time, cleanliness_level, noise_tolerance, guest_preference, study_style)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (student_id, sleep_time, cleanliness_level, noise_tolerance, guest_preference, study_style))

        conn.commit()
        cur.close()
        conn.close()
        return redirect("/dashboard")

    cur.close()
    conn.close()
    return render_template("update_preferences.html", pref=pref)

@app.route("/profile/edit", methods=["GET", "POST"])
def edit_profile():  
    if "user_id" not in session:  # Only logged-in users can edit profile.
        return redirect("/login")  
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(  # Load current profile values
        "SELECT username, email, profile_picture FROM users WHERE id = %s",
        (session["user_id"],)
    )
    row = cur.fetchone()
    if not row:
        cur.close()
        conn.close()
        session.clear()
        return redirect("/login")#force login
    
    user = {  # Data shown in form fields
        "username": row[0],  
        "email": row[1],  
        "profile_picture": row[2]  
    }
    errors = []
    updated = request.args.get("updated") == "1"

    if request.method == "POST":  # Form was submitted.
        username = request.form.get("username", "").strip() 
        email = request.form.get("email", "").strip() 
        new_password = request.form.get("password", "")  
        profile_file = request.files.get("profile_picture")  
        next_picture = user["profile_picture"] 
        next_filename = None 

        if not username:  # Validate username and email required.
            errors.append("Username is required.")  
        if not email:  
            errors.append("Email is required.")  

        cur.execute(  # Check username uniqueness except current user ko
            "SELECT 1 FROM users WHERE username = %s AND id <> %s",
            (username, session["user_id"])
        )

        if cur.fetchone():  # Username already used by someone else
            errors.append("That username is already taken.")  

        cur.execute(  # Check email uniqueness except current user
            "SELECT 1 FROM users WHERE email = %s AND id <> %s",
            (email, session["user_id"])
        )
        if cur.fetchone():  # Email already used by someone else
            errors.append("That email is already registered.")  
        
        if profile_file and profile_file.filename:  # Only validate file if selected
            if not allowed_profile_image(profile_file.filename):  # Extension check
                errors.append("Image must be png, jpg, jpeg, gif, or webp.")  
            else:
                ext = os.path.splitext(profile_file.filename)[1].lower()  # Keep original ext
                next_filename = f"user_{session['user_id']}_{uuid.uuid4().hex}{ext}"  # Unique
                next_picture = f"uploads/profile_pictures/{next_filename}" 
        if not errors:  # Continue only if validation passed.
            if next_filename:  # Save uploaded image if provided.
                profile_file.save(os.path.join(PROFILE_UPLOAD_FOLDER, next_filename))  # Write file to disk.

            if new_password:  # Update password only when user typed one.
                hashed_password = generate_password_hash(new_password)  # Hash securely.
                cur.execute(
                    """
                    UPDATE users
                    SET username = %s, email = %s, password = %s, profile_picture = %s
                    WHERE id = %s
                    """,
                    (username, email, hashed_password, next_picture, session["user_id"])
                )
            else:  # Keep old password if password field was blank
                cur.execute(
                    """
                    UPDATE users
                    SET username = %s, email = %s, profile_picture = %s
                    WHERE id = %s
                    """,
                    (username, email, next_picture, session["user_id"])
                )

            conn.commit()
            cur.close()  # Close cursor
            conn.close()  # Close connection
            return redirect("/profile/edit?updated=1")  # PRG pattern to prevent re-submit

        user["username"] = username  # Refill form after errors
        user["email"] = email  # Refill form after errors
        user["profile_picture"] = next_picture  # Show current/new image path
    cur.close()  
    conn.close()  
    return render_template("edit_profile.html", user=user, errors=errors, updated=updated)  # Render page


        
# admin helper functions

def is_student_assigned(cur, student_id):
    cur.execute(
        """
        SELECT (
            EXISTS (
                SELECT 1
                FROM roommate_request
                WHERE student_id = %s
                  AND (
                      assigned_roommate_id IS NOT NULL
                      OR COALESCE(request_status, '') ILIKE 'assigned'
                  )
            )
            OR
            EXISTS (
                SELECT 1
                FROM room_assignment
                WHERE student_id = %s
            )
        )
        """,
        (student_id, student_id)
    )
    row = cur.fetchone()
    return bool(row and row[0])


def set_roommate_assignment(cur, student_id, roommate_id, status="Assigned"):
    cur.execute(
        "SELECT request_id FROM roommate_request WHERE student_id = %s ORDER BY request_id LIMIT 1",
        (student_id,)
    )
    row = cur.fetchone()

    if row:
        cur.execute("""
            UPDATE roommate_request
            SET assigned_roommate_id = %s, request_status = %s
            WHERE request_id = %s
        """, (roommate_id, status, row[0]))
    else:
        cur.execute("""
            INSERT INTO roommate_request (student_id, preferred_room_type, request_status, assigned_roommate_id)
            VALUES (%s, %s, %s, %s)
        """, (student_id, "Double", status, roommate_id))


def clear_roommate_assignment(cur, student_id):
    cur.execute("""
        UPDATE roommate_request
        SET assigned_roommate_id = NULL, request_status = 'Pending'
        WHERE student_id = %s
    """, (student_id,))


def get_available_room_id(cur, hostel_id):
    cur.execute("""
        SELECT room_id
        FROM room
        WHERE hostel_id = %s
          AND COALESCE(capacity, 0) - COALESCE(current_occupancy, 0) >= 2
        ORDER BY (COALESCE(capacity, 0) - COALESCE(current_occupancy, 0)) ASC, room_id ASC
        LIMIT 1
    """, (hostel_id,))
    row = cur.fetchone()
    return row[0] if row else None


def get_available_single_room_id(cur, hostel_id):
    cur.execute(
        """
        SELECT room_id
        FROM room
        WHERE hostel_id = %s
          AND COALESCE(capacity, 0) = 1
          AND COALESCE(current_occupancy, 0) < COALESCE(capacity, 0)
        ORDER BY room_id ASC
        LIMIT 1
        """,
        (hostel_id,)
    )
    row = cur.fetchone()
    return row[0] if row else None


def set_single_assignment(cur, student_id, status="Assigned"):
    cur.execute(
        """
        UPDATE roommate_request
        SET assigned_roommate_id = NULL,
            preferred_room_type = COALESCE(preferred_room_type, 'Single'),
            request_status = %s
        WHERE student_id = %s
        """,
        (status, student_id)
    )
    if cur.rowcount == 0:
        cur.execute(
            """
            INSERT INTO roommate_request (student_id, preferred_room_type, request_status, assigned_roommate_id)
            VALUES (%s, 'Single', %s, NULL)
            """,
            (student_id, status)
        )


def upsert_room_assignment(cur, student_id, room_id):
    cur.execute(
        "SELECT assignment_id, room_id FROM room_assignment WHERE student_id = %s ORDER BY assignment_id LIMIT 1",
        (student_id,)
    )
    row = cur.fetchone()

    if row:
        assignment_id, old_room_id = row
        if old_room_id == room_id:
            return

        cur.execute(
            "UPDATE room_assignment SET room_id = %s, assigned_date = CURRENT_DATE WHERE assignment_id = %s",
            (room_id, assignment_id)
        )

        if old_room_id:
            cur.execute(
                "UPDATE room SET current_occupancy = GREATEST(COALESCE(current_occupancy, 0) - 1, 0) WHERE room_id = %s",
                (old_room_id,)
            )

        cur.execute(
            "UPDATE room SET current_occupancy = COALESCE(current_occupancy, 0) + 1 WHERE room_id = %s",
            (room_id,)
        )
    else:
        cur.execute(
            "INSERT INTO room_assignment (room_id, student_id, assigned_date) VALUES (%s, %s, CURRENT_DATE)",
            (room_id, student_id)
        )
        cur.execute(
            "UPDATE room SET current_occupancy = COALESCE(current_occupancy, 0) + 1 WHERE room_id = %s",
            (room_id,)
        )


def remove_room_assignment(cur, student_id):
    cur.execute(
        "SELECT assignment_id, room_id FROM room_assignment WHERE student_id = %s ORDER BY assignment_id LIMIT 1",
        (student_id,)
    )
    row = cur.fetchone()
    if not row:
        return

    assignment_id, room_id = row
    cur.execute("DELETE FROM room_assignment WHERE assignment_id = %s", (assignment_id,))

    if room_id:
        cur.execute(
            "UPDATE room SET current_occupancy = GREATEST(COALESCE(current_occupancy, 0) - 1, 0) WHERE room_id = %s",
            (room_id,)
        )


def record_match_history(cur, student1_id, student2_id, room_id, score):
    s1 = min(student1_id, student2_id)
    s2 = max(student1_id, student2_id)

    cur.execute("""
        SELECT match_id
        FROM match_history
        WHERE LEAST(student1_id, student2_id) = %s
          AND GREATEST(student1_id, student2_id) = %s
          AND end_date IS NULL
        ORDER BY match_id DESC
        LIMIT 1
    """, (s1, s2))
    if cur.fetchone():
        return

    cur.execute("""
        INSERT INTO match_history (student1_id, student2_id, room_id, compatibility_score, start_date)
        VALUES (%s, %s, %s, %s, CURRENT_DATE)
    """, (s1, s2, room_id, score))


def close_match_history(cur, student1_id, student2_id):
    s1 = min(student1_id, student2_id)
    s2 = max(student1_id, student2_id)

    cur.execute("""
        UPDATE match_history
        SET end_date = CURRENT_DATE
        WHERE LEAST(student1_id, student2_id) = %s
          AND GREATEST(student1_id, student2_id) = %s
          AND end_date IS NULL
    """, (s1, s2))




# admin profile

@app.route("/admin/profile", methods=["GET", "POST"])
def admin_profile():
    if "user_id" not in session:
        return redirect("/login")
    if not is_admin():
        return "Access Denied", 403

    conn = get_db_connection()
    cur = conn.cursor()

    admin = get_user_row(cur, session["user_id"])
    if not admin:
        cur.close()
        conn.close()
        session.clear()
        return redirect("/login")

    errors = []
    updated = request.args.get("updated") == "1"

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        new_password = request.form.get("password", "")
        profile_file = request.files.get("profile_picture")

        next_picture = admin["profile_picture"]
        next_filename = None

        if not username:
            errors.append("Username is required.")
        if not email:
            errors.append("Email is required.")

        # Uniqueness checks
        cur.execute(
            "SELECT 1 FROM users WHERE username = %s AND id <> %s",
            (username, session["user_id"])
        )
        if cur.fetchone():
            errors.append("That username is already taken.")

        cur.execute(
            "SELECT 1 FROM users WHERE email = %s AND id <> %s",
            (email, session["user_id"])
        )
        if cur.fetchone():
            errors.append("That email is already registered.")

        if profile_file and profile_file.filename:
            if not allowed_profile_image(profile_file.filename):
                errors.append("Image must be png, jpg, jpeg, gif, or webp.")
            else:
                ext = os.path.splitext(profile_file.filename)[1].lower()
                next_filename = f"admin_{session['user_id']}_{uuid.uuid4().hex}{ext}"
                next_picture = f"uploads/profile_pictures/{next_filename}"

        if not errors:
            if next_filename:
                profile_file.save(os.path.join(PROFILE_UPLOAD_FOLDER, next_filename))

            if new_password:
                hashed_password = generate_password_hash(new_password)
                cur.execute(
                    """
                    UPDATE users
                    SET username = %s, email = %s, password = %s, profile_picture = %s
                    WHERE id = %s
                    """,
                    (username, email, hashed_password, next_picture, session["user_id"])
                )
            else:
                cur.execute(
                    """
                    UPDATE users
                    SET username = %s, email = %s, profile_picture = %s
                    WHERE id = %s
                    """,
                    (username, email, next_picture, session["user_id"])
                )

            conn.commit()
            cur.close()
            conn.close()
            return redirect("/admin/profile?updated=1")

        admin["username"] = username
        admin["email"] = email
        admin["profile_picture"] = next_picture

    cur.close()
    conn.close()
    return render_template("admin_profile.html", admin=admin, errors=errors, updated=updated)


# admin dashboard 

@app.route("/admin/rooms/create", methods=["POST"])
def admin_create_room():
    if "user_id" not in session:
        return redirect("/login")
    if not is_admin():
        return "Access Denied", 403

    room_number = request.form.get("room_number", "").strip()
    hostel_id_raw = request.form.get("hostel_id", "").strip()
    capacity_raw = request.form.get("capacity", "0").strip()
    occupancy_raw = request.form.get("current_occupancy", "0").strip()

    if not room_number:
        return admin_room_redirect(error="missing_room_number")
    if not hostel_id_raw.isdigit():
        return admin_room_redirect(error="invalid_hostel")
    if not capacity_raw.isdigit():
        return admin_room_redirect(error="invalid_capacity")
    if not occupancy_raw.isdigit():
        return admin_room_redirect(error="invalid_occupancy")

    hostel_id = int(hostel_id_raw)
    capacity = int(capacity_raw)
    current_occupancy = int(occupancy_raw)
    if capacity <= 0:
        return admin_room_redirect(error="invalid_capacity")
    if current_occupancy < 0 or current_occupancy > capacity:
        return admin_room_redirect(error="invalid_occupancy")

    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT 1 FROM hostel WHERE hostel_id = %s", (hostel_id,))
        if not cur.fetchone():
            return admin_room_redirect(error="invalid_hostel")

        cur.execute(
            "SELECT 1 FROM room WHERE hostel_id = %s AND room_number = %s",
            (hostel_id, room_number)
        )
        if cur.fetchone():
            return admin_room_redirect(error="duplicate_room")

        cur.execute(
            """
            INSERT INTO room (hostel_id, room_number, capacity, current_occupancy)
            VALUES (%s, %s, %s, %s)
            """,
            (hostel_id, room_number, capacity, current_occupancy)
        )
        conn.commit()
    finally:
        cur.close()
        conn.close()
    return admin_room_redirect(message="created")


@app.route("/admin/rooms/<int:room_id>/update", methods=["POST"])
def admin_update_room(room_id):
    if "user_id" not in session:
        return redirect("/login")
    if not is_admin():
        return "Access Denied", 403

    room_number = request.form.get("room_number", "").strip()
    hostel_id_raw = request.form.get("hostel_id", "").strip()
    capacity_raw = request.form.get("capacity", "0").strip()
    occupancy_raw = request.form.get("current_occupancy", "0").strip()

    if not room_number:
        return admin_room_redirect(error="missing_room_number")
    if not hostel_id_raw.isdigit():
        return admin_room_redirect(error="invalid_hostel")
    if not capacity_raw.isdigit():
        return admin_room_redirect(error="invalid_capacity")
    if not occupancy_raw.isdigit():
        return admin_room_redirect(error="invalid_occupancy")

    hostel_id = int(hostel_id_raw)
    capacity = int(capacity_raw)
    current_occupancy = int(occupancy_raw)
    if capacity <= 0:
        return admin_room_redirect(error="invalid_capacity")
    if current_occupancy < 0 or current_occupancy > capacity:
        return admin_room_redirect(error="invalid_occupancy")

    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT 1 FROM hostel WHERE hostel_id = %s", (hostel_id,))
        if not cur.fetchone():
            return admin_room_redirect(error="invalid_hostel")

        cur.execute(
            """
            SELECT 1
            FROM room
            WHERE hostel_id = %s
              AND room_number = %s
              AND room_id <> %s
            """,
            (hostel_id, room_number, room_id)
        )
        if cur.fetchone():
            return admin_room_redirect(error="duplicate_room")

        cur.execute(
            """
            UPDATE room
            SET hostel_id = %s, room_number = %s, capacity = %s, current_occupancy = %s
            WHERE room_id = %s
            """,
            (hostel_id, room_number, capacity, current_occupancy, room_id)
        )
        conn.commit()
    finally:
        cur.close()
        conn.close()
    return admin_room_redirect(message="updated")


@app.route("/admin/rooms/<int:room_id>/delete", methods=["POST"])
def admin_delete_room(room_id):
    if "user_id" not in session:
        return redirect("/login")
    if not is_admin():
        return "Access Denied", 403

    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "SELECT 1 FROM room_assignment WHERE room_id = %s LIMIT 1",
            (room_id,)
        )
        if cur.fetchone():
            return admin_room_redirect(error="room_in_use")

        cur.execute("DELETE FROM room WHERE room_id = %s", (room_id,))
        conn.commit()
    finally:
        cur.close()
        conn.close()
    return admin_room_redirect(message="deleted")


@app.route("/admin/dashboard")
def admin_dashboard():
    if "user_id" not in session:
        return redirect("/login")
    if not is_admin():
        return "Access Denied", 403
    
    conn = get_db_connection()
    cur = conn.cursor()

    admin = get_user_row(cur, session["user_id"])
    if not admin:
        cur.close()
        conn.close()
        session.clear()
        return redirect("/login")

    stats, system_status = get_admin_summary_stats(cur)

    cur.close()
    conn.close()

    auto_assigned = request.args.get("auto_assigned")
    auto_assigned = int(auto_assigned) if auto_assigned and auto_assigned.isdigit() else None

    pair_assigned = request.args.get("auto_pairs") or request.args.get("pairs")
    pair_assigned = int(pair_assigned) if pair_assigned and pair_assigned.isdigit() else None
    single_assigned = request.args.get("auto_single")
    single_assigned = int(single_assigned) if single_assigned and single_assigned.isdigit() else None
    return render_template(
        "admin_dashboard.html",
        admin=admin,
        stats=stats,
        system_status=system_status,
        auto_assigned=auto_assigned,
        pair_assigned=pair_assigned,
        single_assigned=single_assigned,
    )


@app.route("/admin/pending-requests")
def admin_pending_requests():
    if "user_id" not in session:
        return redirect("/login")
    if not is_admin():
        return "Access Denied", 403

    conn = get_db_connection()
    cur = conn.cursor()
    admin = get_user_row(cur, session["user_id"])
    if not admin:
        cur.close()
        conn.close()
        session.clear()
        return redirect("/login")

    stats, system_status = get_admin_summary_stats(cur)
    cur.execute(
        """
        SELECT
            rr.request_id,
            s.student_id,
            s.name,
            COALESCE(rr.preferred_room_type, '-'),
            s.hostel_id,
            EXISTS (
                SELECT 1
                FROM room_assignment ra
                WHERE ra.student_id = s.student_id
            ) AS has_room
        FROM roommate_request rr
        JOIN student s ON s.student_id = rr.student_id
        WHERE COALESCE(rr.request_status, '') ILIKE 'pending'
        ORDER BY rr.request_id DESC
        LIMIT 50
        """
    )
    pending_rows = cur.fetchall()

    cur.close()
    conn.close()

    single_msg = request.args.get("single_msg")
    single_err = request.args.get("single_err")
    return render_template(
        "admin_pending_requests.html",
        admin=admin,
        stats=stats,
        system_status=system_status,
        pending_rows=pending_rows,
        single_msg=single_msg,
        single_err=single_err,
    )


@app.route("/admin/rooms")
def admin_rooms():
    if "user_id" not in session:
        return redirect("/login")
    if not is_admin():
        return "Access Denied", 403

    conn = get_db_connection()
    cur = conn.cursor()
    admin = get_user_row(cur, session["user_id"])
    if not admin:
        cur.close()
        conn.close()
        session.clear()
        return redirect("/login")

    stats, system_status = get_admin_summary_stats(cur)
    cur.execute(
        """
        SELECT
            r.room_id,
            r.room_number,
            COALESCE(h.hostel_name, 'Unknown Hostel') AS hostel_name,
            COALESCE(r.capacity, 0) AS capacity,
            COALESCE(r.current_occupancy, 0) AS occupied,
            COALESCE(r.capacity, 0) - COALESCE(r.current_occupancy, 0) AS available,
            CASE
                WHEN COALESCE(r.capacity, 0) <= 0 THEN 'Invalid'
                WHEN COALESCE(r.current_occupancy, 0) >= COALESCE(r.capacity, 0) THEN 'Full'
                WHEN COALESCE(r.current_occupancy, 0) = 0 THEN 'Empty'
                ELSE 'Available'
            END AS room_status,
            r.hostel_id
        FROM room r
        LEFT JOIN hostel h ON h.hostel_id = r.hostel_id
        ORDER BY h.hostel_name ASC, r.room_number ASC
        """
    )
    room_rows = cur.fetchall()

    cur.execute(
        """
        SELECT hostel_id, hostel_name
        FROM hostel
        ORDER BY hostel_name ASC
        """
    )
    hostels = cur.fetchall()

    cur.execute(
        """
        SELECT h.hostel_name,
               COUNT(r.room_id) AS room_count,
               COALESCE(SUM(r.capacity), 0) AS total_capacity,
               COALESCE(SUM(COALESCE(r.current_occupancy, 0)), 0) AS occupied,
               COALESCE(SUM(r.capacity), 0) - COALESCE(SUM(COALESCE(r.current_occupancy, 0)), 0) AS available
        FROM hostel h
        LEFT JOIN room r ON r.hostel_id = h.hostel_id
        GROUP BY h.hostel_name
        ORDER BY h.hostel_name
        """
    )
    occupancy_summary = cur.fetchall()

    cur.close()
    conn.close()

    room_msg = request.args.get("room_msg")
    room_err = request.args.get("room_err")
    return render_template(
        "admin_rooms.html",
        admin=admin,
        stats=stats,
        system_status=system_status,
        room_rows=room_rows,
        hostels=hostels,
        occupancy_summary=occupancy_summary,
        room_msg=room_msg,
        room_err=room_err,
    )


@app.route("/admin/auto-assign-top-matches", methods=["POST"])
def auto_assign_top_matches():
    if "user_id" not in session:
        return redirect("/login")
    if not is_admin():
        return "Access Denied", 403

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT c.student1_id, c.student2_id, c.compatibility_score, s1.hostel_id
        FROM compatibility_score c
        JOIN student s1 ON s1.student_id = c.student1_id
        JOIN student s2 ON s2.student_id = c.student2_id
        WHERE s1.hostel_id = s2.hostel_id
        ORDER BY c.compatibility_score DESC, c.score_id ASC
    """)
    pairs = cur.fetchall()

    used_students = set()
    assigned_pairs = 0
    assigned_students = 0
    single_assigned = 0

    for s1_id, s2_id, score, hostel_id in pairs:
        if s1_id in used_students or s2_id in used_students:
            continue
        if is_student_assigned(cur, s1_id) or is_student_assigned(cur, s2_id):
            continue

        room_id = get_available_room_id(cur, hostel_id)
        if not room_id:
            continue

        set_roommate_assignment(cur, s1_id, s2_id, "Assigned")
        set_roommate_assignment(cur, s2_id, s1_id, "Assigned")
        upsert_room_assignment(cur, s1_id, room_id)
        upsert_room_assignment(cur, s2_id, room_id)
        record_match_history(cur, s1_id, s2_id, room_id, score)

        used_students.add(s1_id)
        used_students.add(s2_id)
        assigned_pairs += 1
        assigned_students += 2

    cur.execute(
        """
        SELECT rr.student_id, s.hostel_id
        FROM roommate_request rr
        JOIN student s ON s.student_id = rr.student_id
        WHERE COALESCE(rr.request_status, '') ILIKE 'pending'
          AND COALESCE(rr.preferred_room_type, '') ILIKE 'single'
        ORDER BY rr.request_id ASC
        """
    )
    single_requests = cur.fetchall()

    for student_id, hostel_id in single_requests:
        if student_id in used_students:
            continue
        if is_student_assigned(cur, student_id):
            continue

        room_id = get_available_single_room_id(cur, hostel_id)
        if not room_id:
            continue

        upsert_room_assignment(cur, student_id, room_id)
        set_single_assignment(cur, student_id, "Assigned")
        used_students.add(student_id)
        assigned_students += 1
        single_assigned += 1

    conn.commit()
    cur.close()
    conn.close()
    return redirect(f"/admin/dashboard?auto_assigned={assigned_students}&auto_pairs={assigned_pairs}&auto_single={single_assigned}")


@app.route("/admin/assign-single/<int:student_id>", methods=["POST"])
def assign_single_student(student_id):
    if "user_id" not in session:
        return redirect("/login")
    if not is_admin():
        return "Access Denied", 403

    conn = get_db_connection()
    cur = conn.cursor()
    try:
        if is_student_assigned(cur, student_id):
            return redirect("/admin/pending-requests?single_err=already_assigned")

        cur.execute("SELECT hostel_id FROM student WHERE student_id = %s", (student_id,))
        row = cur.fetchone()
        if not row:
            return redirect("/admin/pending-requests?single_err=student_missing")

        room_id = get_available_single_room_id(cur, row[0])
        if not room_id:
            return redirect("/admin/pending-requests?single_err=no_single_room")

        upsert_room_assignment(cur, student_id, room_id)
        set_single_assignment(cur, student_id, "Assigned")
        conn.commit()
        return redirect("/admin/pending-requests?single_msg=assigned")
    finally:
        cur.close()
        conn.close()


@app.route("/admin/unassign/<int:student_id>", methods=["POST"])
def unassign_student(student_id):
    if "user_id" not in session:
        return redirect("/login")
    if not is_admin():
        return "Access Denied", 403

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT assigned_roommate_id FROM roommate_request WHERE student_id = %s ORDER BY request_id LIMIT 1",
        (student_id,)
    )
    row = cur.fetchone()

    if row and row[0]:
        roommate_id = row[0]

        clear_roommate_assignment(cur, student_id)
        clear_roommate_assignment(cur, roommate_id)

        remove_room_assignment(cur, student_id)
        remove_room_assignment(cur, roommate_id)

        close_match_history(cur, student_id, roommate_id)
        conn.commit()
    else:
        remove_room_assignment(cur, student_id)
        clear_roommate_assignment(cur, student_id)
        conn.commit()

    cur.close()
    conn.close()
    return redirect("/admin/dashboard")




@app.route("/admin/calculate_compatibility")
def generate_compatibility():
    if not is_admin():
        return "Access Denied", 403

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("DELETE FROM compatibility_score")

    cur.execute("""
        SELECT s.student_id, s.gender, s.hostel_id,
               lp.sleep_time, lp.cleanliness_level, lp.noise_tolerance,
               lp.guest_preference, lp.study_style
        FROM student s
        JOIN lifestyle_preferences lp ON s.student_id = lp.student_id
        JOIN roommate_request rr ON s.student_id = rr.student_id
        WHERE rr.preferred_room_type != 'Single'
    """)
    students = cur.fetchall()

    student_list = []
    for row in students:
        student_list.append({
            "student_id": row[0],
            "gender": row[1],
            "hostel_id": row[2],
            "sleep_time": row[3],
            "cleanliness_level": row[4],
            "noise_tolerance": row[5],
            "guest_preference": row[6],
            "study_style": row[7],
        })

    for i in range(len(student_list)):
        for j in range(i + 1, len(student_list)):
            s1 = student_list[i]
            s2 = student_list[j]

            if s1["gender"] != s2["gender"]:
                continue
            if s1["hostel_id"] != s2["hostel_id"]:
                continue

            score = calculate_compatibility(s1, s2)
            pair_a = min(s1["student_id"], s2["student_id"])
            pair_b = max(s1["student_id"], s2["student_id"])

            cur.execute("""
                INSERT INTO compatibility_score
                    (student1_id, student2_id, compatibility_score, calculated_date)
                VALUES (%s, %s, %s, CURRENT_DATE)
                ON CONFLICT (student1_id, student2_id)
                DO UPDATE
                SET compatibility_score = EXCLUDED.compatibility_score,
                    calculated_date = EXCLUDED.calculated_date
            """, (pair_a, pair_b, score))

    conn.commit()
    cur.close()
    conn.close()
    return "Scores calculated successfully"


@app.route("/admin/view/compatibility")
def view_compatibility():
    if not is_admin():
        return "Access Denied", 403

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT
            c.score_id,
            s1.name AS student1,
            s2.name AS student2,
            c.compatibility_score,
            c.calculated_date,
            rr1.assigned_roommate_id AS s1_assigned,
            rr2.assigned_roommate_id AS s2_assigned,
            s1.student_id AS s1_id,
            s2.student_id AS s2_id,
            COALESCE(r1.room_number, r2.room_number, 'Not Assigned') AS room_number,
            CASE
                WHEN rr1.assigned_roommate_id IS NOT NULL OR rr2.assigned_roommate_id IS NOT NULL THEN 'Assigned'
                ELSE 'Open'
            END AS pair_status
        FROM compatibility_score c
        JOIN student s1 ON c.student1_id = s1.student_id
        JOIN student s2 ON c.student2_id = s2.student_id
        LEFT JOIN roommate_request rr1 ON s1.student_id = rr1.student_id
        LEFT JOIN roommate_request rr2 ON s2.student_id = rr2.student_id
        LEFT JOIN room_assignment ra1 ON ra1.student_id = s1.student_id
        LEFT JOIN room_assignment ra2 ON ra2.student_id = s2.student_id
        LEFT JOIN room r1 ON r1.room_id = ra1.room_id
        LEFT JOIN room r2 ON r2.room_id = ra2.room_id
        ORDER BY c.compatibility_score DESC, c.score_id DESC
    """)
    scores = cur.fetchall()
    cur.close()
    conn.close()

    return render_template("admin_compatibility.html", scores=scores)


@app.route("/admin/assign_roommates/<int:s1_id>/<int:s2_id>", methods=["POST"])
def assign_roommate_pair(s1_id, s2_id):
    if not is_admin():
        return "Access Denied", 403

    conn = get_db_connection()
    cur = conn.cursor()

    if is_student_assigned(cur, s1_id) or is_student_assigned(cur, s2_id):
        cur.close()
        conn.close()
        return "One of the students is already assigned!", 400

    cur.execute("SELECT hostel_id FROM student WHERE student_id = %s", (s1_id,))
    r1 = cur.fetchone()
    cur.execute("SELECT hostel_id FROM student WHERE student_id = %s", (s2_id,))
    r2 = cur.fetchone()

    if not r1 or not r2 or r1[0] != r2[0]:
        cur.close()
        conn.close()
        return "Students must belong to same hostel for assignment.", 400

    room_id = get_available_room_id(cur, r1[0])
    if not room_id:
        cur.close()
        conn.close()
        return "No room with at least 2 free beds is available.", 400

    cur.execute("""
        SELECT compatibility_score
        FROM compatibility_score
        WHERE (student1_id = %s AND student2_id = %s)
           OR (student1_id = %s AND student2_id = %s)
        ORDER BY score_id DESC
        LIMIT 1
    """, (s1_id, s2_id, s2_id, s1_id))
    score_row = cur.fetchone()
    score = score_row[0] if score_row else None

    set_roommate_assignment(cur, s1_id, s2_id, "Assigned")
    set_roommate_assignment(cur, s2_id, s1_id, "Assigned")
    upsert_room_assignment(cur, s1_id, room_id)
    upsert_room_assignment(cur, s2_id, room_id)
    record_match_history(cur, s1_id, s2_id, room_id, score)

    conn.commit()
    cur.close()
    conn.close()
    return redirect("/admin/view/compatibility")

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001)
