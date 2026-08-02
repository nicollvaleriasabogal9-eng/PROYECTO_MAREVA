from flask import Flask
from routes.auth_routes import auth_bp
from routes.home_routes import home_bp
from routes.paquetes_routes import paquetes_bp


main = Flask(__name__, template_folder="../frontend/templates", static_folder="../frontend/static")

main.secret_key = "mareva_secret_2026"

main.register_blueprint(paquetes_bp)
main.register_blueprint(auth_bp)
main.register_blueprint(home_bp)


if __name__ == "__main__":
    main.run(debug=True)