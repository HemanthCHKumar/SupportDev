
import os
import re

import mysql.connector
from flask import Flask, render_template, request
from werkzeug.security import generate_password_hash
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)


def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "127.0.0.1"),
        port=int(os.getenv("DB_PORT", "3306")),
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        database="sqllog",
        connection_timeout=5
    )


@app.route("/", methods=["GET", "POST"])
def register():
    message = ""
    success = False

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        phone = request.form.get("phone", "").strip()
        email = request.form.get("email", "").strip().lower()

        if not all([username, password, phone, email]):
            message = "Please fill in all fields."

        elif len(username) > 100 or len(password) > 128:
            message = "Username or password is too long."

        elif not re.fullmatch(r"[0-9]{7,15}", phone):
            message = "Enter a valid phone number."

        elif not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
            message = "Enter a valid email address."

        else:
            connection = None
            cursor = None

            try:
                connection = get_db_connection()
                cursor = connection.cursor()

                password_hash = generate_password_hash(password)

                cursor.execute(
                    """
                    INSERT INTO users
                        (username, password_hash, phone, email)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (username, password_hash, phone, email)
                )

                connection.commit()
                message = "Registration successful!"
                success = True

            except mysql.connector.IntegrityError:
                if connection:
                    connection.rollback()
                message = "Username or email already exists."

            except mysql.connector.Error:
                if connection:
                    connection.rollback()
                app.logger.exception("MySQL operation failed")
                message = "Database error. Check the application logs."

            finally:
                if cursor:
                    cursor.close()
                if connection and connection.is_connected():
                    connection.close()

    return render_template(
        "register.html",
        message=message,
        success=success
    )


@app.route("/health")
def health():
    return {"status": "healthy"}, 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
