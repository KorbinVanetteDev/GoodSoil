from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "GoodSoil Development from end in progress! Check updated for more information!"

if __name__ == '__main__':
    app.run()
