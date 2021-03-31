from flask import Flask
from flask import jsonify
from flask import request
from json import loads
from flask_mongoengine import MongoEngine
from sklearn.svm import SVC
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.neural_network import MLPClassifier
import numpy as np

app = Flask(__name__)
app.config["MONGODB_SETTINGS"] = {"db": "lab5", "host": "localhost", "port": 27017}
db = MongoEngine()
db.init_app(app)
model = None


class Data(db.EmbeddedDocument):
    readings = db.ListField()


class DataSet(db.Document):
    meta = {"collection": "training_data"}
    letter = db.StringField()
    data_list = db.ListField()


def train():
    letters = ["c", "o", "l", "u", "m", "b", "i", "a"]
    y = []
    X = []

    for letter in letters:
        data_set = DataSet.objects(letter=letter).first()
        if data_set == None:
            print("letter: ", letter, "missing from db")
            return jsonify({"result": "ERROR"})

        for data in data_set.data_list:
            X.append(list(data.readings))
            y.append(ord(letter))

    X = np.array(X, dtype="object")
    y = np.array(y)

    clf = make_pipeline(
        StandardScaler(), SVC(gamma="auto", decision_function_shape="ovo")
    )
    # clf = MLPClassifier(solver="lbfgs")
    clf.fit(X, y)

    return clf


@app.route("/train", methods=["POST"])
def test():
    global model
    data = loads(request.json)
    readings = [data["readings"]]
    X = np.array(readings)
    guess = model.predict(X)
    print(chr(guess[0]))
    return chr(guess[0])


@app.route("/junk", methods=["POST"])
def reset():
    return jsonify({"result": "Successful"})


if __name__ == "__main__":
    model = train()
    app.run(debug=True, host="0.0.0.0", port=8080)
