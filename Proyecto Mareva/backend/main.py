from flask import Flask
from routes.auth_routes import auth_bp


main = Flask(__name__)

main.register_blueprint(auth_bp)


if __name__ == "__main__":
    main.run(debug=True)