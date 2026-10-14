from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)
DB_NAME = "students.db"


def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                course TEXT NOT NULL,
                age INTEGER NOT NULL
            )
        """)


@app.route("/")
def index():
    search = request.args.get("search", "").strip()
    with get_db() as conn:
        if search:
            students = conn.execute(
                "SELECT * FROM students WHERE name LIKE ? ORDER BY id DESC",
                (f"%{search}%",)
            ).fetchall()
        else:
            students = conn.execute(
                "SELECT * FROM students ORDER BY id DESC"
            ).fetchall()
    return render_template("index.html", students=students, search=search)


@app.route("/add", methods=["POST"])
def add_student():
    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip()
    course = request.form.get("course", "").strip()
    age = request.form.get("age", "").strip()

    if not all([name, email, course, age]):
        return "All fields are required.", 400
    try:
        age = int(age)
        if not 1 <= age <= 120:
            return "Enter a valid age.", 400
    except ValueError:
        return "Age must be a number.", 400

    with get_db() as conn:
        conn.execute(
            "INSERT INTO students (name, email, course, age) VALUES (?, ?, ?, ?)",
            (name, email, course, age)
        )
    return redirect(url_for("index"))


@app.route("/edit/<int:student_id>", methods=["GET", "POST"])
def edit_student(student_id):
    with get_db() as conn:
        student = conn.execute(
            "SELECT * FROM students WHERE id = ?", (student_id,)
        ).fetchone()
        if student is None:
            return "Student not found.", 404

        if request.method == "POST":
            name = request.form.get("name", "").strip()
            email = request.form.get("email", "").strip()
            course = request.form.get("course", "").strip()
            age = request.form.get("age", "").strip()
            if not all([name, email, course, age]):
                return "All fields are required.", 400
            try:
                age = int(age)
                if not 1 <= age <= 120:
                    return "Enter a valid age.", 400
            except ValueError:
                return "Age must be a number.", 400

            conn.execute(
                "UPDATE students SET name=?, email=?, course=?, age=? WHERE id=?",
                (name, email, course, age, student_id)
            )
            return redirect(url_for("index"))

    return render_template("edit.html", student=student)


@app.route("/delete/<int:student_id>", methods=["POST"])
def delete_student(student_id):
    with get_db() as conn:
        conn.execute("DELETE FROM students WHERE id = ?", (student_id,))
    return redirect(url_for("index"))


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
