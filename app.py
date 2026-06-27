from flask import Flask, render_template, request, redirect, flash, session, send_file
from math import ceil

from database import get_connection
from datetime import datetime
import pandas as pd

app = Flask(__name__)
app.secret_key = "student_management"


# ===============================
# LOGIN PAGE
# ===============================

@app.route("/")
def login_page():
    return render_template("login.html")


# ===============================
# LOGIN
# ===============================

@app.route("/login", methods=["POST"])
def login():

    username = request.form["username"]
    password = request.form["password"]

    if username == "admin" and password == "admin123":

        session["user"] = username

        return redirect("/dashboard")

    flash("Invalid Username or Password")

    return redirect("/")


# ===============================
# LOGOUT
# ===============================

@app.route("/logout")
def logout():

    session.pop("user", None)

    return redirect("/")


# ===============================
# DASHBOARD
# ===============================

@app.route('/dashboard')
def home():

    if 'user' not in session:
        return redirect('/')

    conn = get_connection()
    cursor = conn.cursor()

    # ======================================
    # Dashboard Cards
    # ======================================

    cursor.execute("SELECT COUNT(*) FROM students")
    total_students = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(DISTINCT department) FROM students")
    total_departments = cursor.fetchone()[0]

    courses = 8

    cursor.execute("""
        SELECT COUNT(*)
        FROM students
        WHERE fee_status='Paid'
    """)
    paid_students = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*)
        FROM students
        WHERE fee_status='Pending'
    """)
    pending_students = cursor.fetchone()[0]

    cursor.execute("""
        SELECT ROUND(AVG(attendance),1)
        FROM students
    """)

    average_attendance = cursor.fetchone()[0]

    if average_attendance is None:
        average_attendance = 0

    # ======================================
    # Department Chart
    # ======================================

    cursor.execute("""
        SELECT department, COUNT(*)
        FROM students
        GROUP BY department
        ORDER BY department
    """)

    department_data = cursor.fetchall()

    labels = []
    values = []

    for row in department_data:
        labels.append(row[0])
        values.append(row[1])

    # ======================================
    # Gender Chart
    # ======================================

    cursor.execute("""
        SELECT gender, COUNT(*)
        FROM students
        GROUP BY gender
    """)

    gender_data = cursor.fetchall()

    gender_labels = []
    gender_values = []

    for row in gender_data:
        gender_labels.append(row[0])
        gender_values.append(row[1])

    # ======================================
    # Fee Status Chart
    # ======================================

    cursor.execute("""
        SELECT fee_status, COUNT(*)
        FROM students
        GROUP BY fee_status
    """)

    fee_data = cursor.fetchall()

    fee_labels = []
    fee_values = []

    for row in fee_data:
        fee_labels.append(row[0])
        fee_values.append(row[1])

    # ======================================
    # Recent Admissions
    # ======================================

    cursor.execute("""
        SELECT
            id,
            name,
            department,
            year,
            fee_status
        FROM students
        ORDER BY id DESC
        LIMIT 5
    """)

    recent_students = cursor.fetchall()

    cursor.close()
    conn.close()

    # ======================================
    # Greeting
    # ======================================

    hour = datetime.now().hour

    if hour < 12:
        greeting = "🌅 Good Morning"

    elif hour < 17:
        greeting = "☀ Good Afternoon"

    else:
        greeting = "🌙 Good Evening"

    # ======================================
    # Render Dashboard
    # ======================================

    return render_template(

        "index.html",

        greeting=greeting,

        total_students=total_students,
        total_departments=total_departments,
        courses=courses,

        paid_students=paid_students,
        pending_students=pending_students,
        average_attendance=average_attendance,

        labels=labels,
        values=values,

        gender_labels=gender_labels,
        gender_values=gender_values,

        fee_labels=fee_labels,
        fee_values=fee_values,

        recent_students=recent_students

    )

# ===============================
# ADD STUDENT PAGE
# ===============================

@app.route("/add")
def add_student():

    if "user" not in session:
        return redirect("/")

    return render_template("add_student.html")

# ===============================
# SAVE STUDENT
# ===============================

@app.route("/save_student", methods=["POST"])
def save_student():

    if "user" not in session:
        return redirect("/")

    name = request.form["name"]
    roll_no = request.form["roll_no"]
    email = request.form["email"]
    phone = request.form["phone"]
    department = request.form["department"]
    gender = request.form["gender"]
    year = request.form["year"]
    fee_status = request.form["fee_status"]
    attendance = request.form["attendance"]

    conn = get_connection()
    cursor = conn.cursor()

    # Duplicate Roll Number

    cursor.execute(
        "SELECT id FROM students WHERE roll_no=%s",
        (roll_no,)
    )

    if cursor.fetchone():

        flash("Roll Number already exists!")

        cursor.close()
        conn.close()

        return redirect("/add")

    # Duplicate Email

    cursor.execute(
        "SELECT id FROM students WHERE email=%s",
        (email,)
    )

    if cursor.fetchone():

        flash("Email already exists!")

        cursor.close()
        conn.close()

        return redirect("/add")

    cursor.execute("""

        INSERT INTO students(

            name,
            roll_no,
            email,
            phone,
            department,
            gender,
            year,
            fee_status,
            attendance

        )

        VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)

    """,(

        name,
        roll_no,
        email,
        phone,
        department,
        gender,
        year,
        fee_status,
        attendance

    ))

    conn.commit()

    cursor.close()
    conn.close()

    flash("Student Added Successfully!")

    return redirect("/students")


# ===============================
# STUDENTS LIST
# ===============================

@app.route('/students')
def students():

    if 'user' not in session:
        return redirect('/')

    search = request.args.get('search', '')
    page = request.args.get('page', 1, type=int)

    per_page = 10
    offset = (page - 1) * per_page

    conn = get_connection()
    cursor = conn.cursor()

    if search:

        cursor.execute("""
            SELECT COUNT(*)
            FROM students
            WHERE
            name LIKE %s
            OR roll_no LIKE %s
            OR department LIKE %s
        """, (
            f"%{search}%",
            f"%{search}%",
            f"%{search}%"
        ))

        total = cursor.fetchone()[0]

        cursor.execute("""
            SELECT *
            FROM students
            WHERE
            name LIKE %s
            OR roll_no LIKE %s
            OR department LIKE %s
            LIMIT %s OFFSET %s
        """, (
            f"%{search}%",
            f"%{search}%",
            f"%{search}%",
            per_page,
            offset
        ))

    else:

        cursor.execute("SELECT COUNT(*) FROM students")
        total = cursor.fetchone()[0]

        cursor.execute("""
            SELECT *
            FROM students
            LIMIT %s OFFSET %s
        """, (
            per_page,
            offset
        ))

    students = cursor.fetchall()

    total_pages = ceil(total / per_page)

    cursor.close()
    conn.close()

    return render_template(
        "students.html",
        students=students,
        search=search,
        page=page,
        total_pages=total_pages
    )

@app.route("/student/<int:id>")
def student_profile(id):

    if "user" not in session:
        return redirect("/")

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM students WHERE id=%s",
        (id,)
    )

    student = cursor.fetchone()

    cursor.close()
    conn.close()

    if student is None:
        flash("Student not found!")
        return redirect("/students")

    return render_template(
        "student_profile.html",
        student=student
    )

# ===============================
# EDIT STUDENT
# ===============================

@app.route("/edit/<int:id>")
def edit_student(id):

    if "user" not in session:
        return redirect("/")

    conn=get_connection()
    cursor=conn.cursor()

    cursor.execute(

        "SELECT * FROM students WHERE id=%s",

        (id,)

    )

    student=cursor.fetchone()

    cursor.close()
    conn.close()

    return render_template(

        "edit_student.html",

                student=student

    )


# ===============================
# UPDATE STUDENT
# ===============================

@app.route("/update_student/<int:id>", methods=["POST"])
def update_student(id):

    if "user" not in session:
        return redirect("/")

    name = request.form["name"]
    roll_no = request.form["roll_no"]
    email = request.form["email"]
    phone = request.form["phone"]
    department = request.form["department"]
    gender = request.form["gender"]
    year = request.form["year"]
    fee_status = request.form["fee_status"]
    attendance = request.form["attendance"]

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""

        UPDATE students

        SET

        name=%s,
        roll_no=%s,
        email=%s,
        phone=%s,
        department=%s,
        gender=%s,
        year=%s,
        fee_status=%s,
        attendance=%s

        WHERE id=%s

    """,(

        name,
        roll_no,
        email,
        phone,
        department,
        gender,
        year,
        fee_status,
        attendance,
        id

    ))

    conn.commit()

    cursor.close()
    conn.close()

    flash("Student Updated Successfully!")

    return redirect("/students")


# ===============================
# DELETE STUDENT
# ===============================

@app.route("/delete/<int:id>")
def delete_student(id):

    if "user" not in session:
        return redirect("/")

    conn=get_connection()
    cursor=conn.cursor()

    cursor.execute(

        "DELETE FROM students WHERE id=%s",

        (id,)

    )

    conn.commit()

    cursor.close()
    conn.close()

    flash("Student Deleted Successfully!")

    return redirect("/students")


# ===============================
# DEPARTMENTS
# ===============================

@app.route("/departments")
def departments():

    if "user" not in session:
        return redirect("/")

    return render_template("departments.html")


@app.route("/department/<department>")
def department_students(department):

    if "user" not in session:
        return redirect("/")

    conn=get_connection()
    cursor=conn.cursor()

    cursor.execute("""

        SELECT *

        FROM students

        WHERE department=%s

        ORDER BY name

    """,(department,))

    students=cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(

        "department_students.html",

        department=department,

        students=students

    )


# ===============================
# REPORTS
# ===============================

@app.route("/reports")
def reports():

    if "user" not in session:
        return redirect("/")

    return render_template("reports.html")


@app.route("/student_report")
def student_report():

    if "user" not in session:
        return redirect("/")

    conn=get_connection()
    cursor=conn.cursor()

    cursor.execute("""

        SELECT *

        FROM students

        ORDER BY department,name

    """)

    students=cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(

        "student_report.html",

        students=students

    )

# ===============================
# DEPARTMENT REPORT
# ===============================

@app.route("/department_report")
def department_report():

    if "user" not in session:
        return redirect("/")

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""

        SELECT
            department,
            COUNT(*) AS total_students

        FROM students

        GROUP BY department

        ORDER BY department

    """)

    departments = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "department_report.html",
        departments=departments
    )


# ===============================
# NEW ADMISSIONS REPORT
# ===============================

@app.route("/new_admissions_report")
def new_admissions_report():

    if "user" not in session:
        return redirect("/")

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""

        SELECT *

        FROM students

        ORDER BY id DESC

        LIMIT 10

    """)

    students = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "new_admissions_report.html",
        students=students
    )


# ===============================
# COURSES
# ===============================

@app.route("/courses")
def courses():

    if "user" not in session:
        return redirect("/")

    return render_template("courses.html")


# ===============================
# ABOUT
# ===============================

@app.route("/about")
def about():

    if "user" not in session:
        return redirect("/")

    return render_template("about.html")


# ===============================
# EXPORT CSV
# ===============================

@app.route("/export/csv")
def export_csv():

    if "user" not in session:
        return redirect("/")

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""

        SELECT
            id,
            name,
            roll_no,
            email,
            phone,
            department,
            gender,
            year,
            fee_status,
            attendance

        FROM students

        ORDER BY id

    """)

    students = cursor.fetchall()

    cursor.close()
    conn.close()

    df = pd.DataFrame(
        students,
        columns=[
            "ID",
            "Name",
            "Roll Number",
            "Email",
            "Phone",
            "Department",
            "Gender",
            "Year",
            "Fee Status",
            "Attendance"
        ]
    )

    filename = "students.csv"

    df.to_csv(filename, index=False)

    return send_file(
        filename,
        as_attachment=True
    )


# ===============================
# RUN APPLICATION
# ===============================

if __name__ == "__main__":

    app.run(
        debug=True
    )