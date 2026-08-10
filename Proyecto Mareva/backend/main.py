from flask import Flask
from routes.auth_routes import auth_bp
from routes.home_routes import home_bp
from routes.paquetes_routes import paquetes_bp
from routes.reserva_routes import reserva_bp
from datetime import timedelta


main = Flask(__name__, template_folder="../frontend/templates", static_folder="../frontend/static")

main.secret_key = "mareva_secret_2026"

main.register_blueprint(reserva_bp)
main.register_blueprint(paquetes_bp)
main.register_blueprint(auth_bp)
main.register_blueprint(home_bp)
main.permanent_session_lifetime = timedelta(days=30) 

if __name__ == "__main__":
    main.run(debug=True)