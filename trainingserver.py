from flask import Flask
from flask import jsonify
from flask import request
from json import loads
from flask_mongoengine import MongoEngine

app = Flask(__name__)

app.config["MONGODB_SETTINGS"] = {"db": "lab5", "host": "localhost", "port": 27017}

db = MongoEngine()
db.init_app(app)


class Data(db.EmbeddedDocument):
    readings = db.ListField()


class DataSet(db.Document):
    meta = {"collection": "training_data"}
    letter = db.StringField()
    data_list = db.ListField()


@app.route("/train", methods=["POST"])
def train():

    data = loads(request.json)

    letter = data["letter"]
    reading = data["readings"]
    data = Data(readings=reading)

    data_set = DataSet.objects(letter=letter).first()
    print("Letter: ", letter)
    print("Reading: ", reading)
    if data_set == None:
        data_set = DataSet(letter=letter)
        data_set.data_list = [data]
    else:
        data_set.data_list.append(data)
    data_set.save()
    print(len(data_set.data_list))

    return (
        "There are now " + str(len(data_set.data_list)) + " data points for " + letter
    )


@app.route("/reset", methods=["POST"])
def reset():
    data = loads(request.json)
    letter = data["letter"]

    data_set = DataSet.objects(letter=letter).first()
    if data_set != None:
        data_set.delete()
    return jsonify({"result": "Successful"})


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8080)
