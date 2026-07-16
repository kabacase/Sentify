import secrets

from flask import Flask

import db
from auth import auth_bp
from upload import upload_bp
from dashboard import dashboard_bp
from export import export_bp

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

app.register_blueprint(auth_bp)
app.register_blueprint(upload_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(export_bp)


if __name__ == "__main__":
    db.init_db()
    app.run(debug=True)
