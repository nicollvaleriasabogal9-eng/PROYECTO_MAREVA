from flask import Flask, render_template

app = Flask(__name__, template_folder="frontend/templates")

@app.route("/inicio")
def inicio():
    return render_template("")

if __name__ == "__main__":
    app.run(debug=True)