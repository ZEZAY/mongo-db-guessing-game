from flask import Flask, request, jsonify, redirect
from pymongo import MongoClient
import os
from bson import json_util
import json
import redis
from string import Template
import random
import datetime


# App
application = Flask(__name__)

# connect to MongoDB
mongoClient = MongoClient('mongodb://' + os.environ['MONGODB_USERNAME'] + ':' + os.environ['MONGODB_PASSWORD'] +
                          '@' + os.environ['MONGODB_HOSTNAME'] + ':27017/' + os.environ['MONGODB_AUTHDB'])
db = mongoClient[os.environ['MONGODB_DATABASE']]

# connect to Redis
redisClient = redis.Redis(host=os.environ.get("REDIS_HOST", "localhost"), port=os.environ.get(
    "REDIS_PORT", 6379), db=os.environ.get("REDIS_DB", 0))


# when fill all text field
def update_last_record(answer):
    last_record = db.game.find().sort([("start_time", -1)])[0]
    new_hint = []
    for i in range(4):
        if (answer[i] == last_record['question'][i]) or (last_record['hint'][i] == last_record['question'][i]):
            new_hint.append(last_record['question'][i])
        else:
            new_hint.append('_')

    update_data = {"$set":
                   {
                       "answer": answer,
                       "hint": new_hint,
                       "fail": last_record['fail'] + 1,
                   }}
    db.game.update_one(last_record, update_data)


# when answer == question
def update_end_game():
    last_record = db.game.find().sort([("start_time", -1)])[0]
    time = (datetime.datetime.utcnow() - last_record['start_time']).total_seconds()
    score = round(1000 - (last_record['fail'] * 10) - time)
    if score < 0:
        score = 0
    update_data = {"$set":
                   {
                       "answer": last_record['question'],
                       "score": score,
                       "end_time": datetime.datetime.utcnow()
                   }}
    db.game.update_one(last_record, update_data)


@application.route('/')
def index():
    with open('index.html', 'r') as f:
        html = f.read()
    return html


@application.route('/rank')
def rank():
    ranking = db.game.find({'score': {'$ne': 0}}).sort([("score", -1)]).limit(5)
    with open('ranking.html', 'r') as f:
        html = f.read()
    count = 0
    for record in ranking:
        count += 1
        score = record['score']
        time = (record['end_time'] - record['start_time']).total_seconds()
        fail = record['fail']
        html += f"""
          <tr>
            <th scope="row">{count}</th>
            <td>{score}</td>
            <td>{time}</td>
            <td>{fail}</td>
          </tr>
        """
    html += "</tbody></table>"
    return html


# when cilck 'start' btn
@application.route('/start')
def start_new_game():
    question = [random.choice(["A", "B", "C", "D"]) for i in range(4)]
    record = {
        "question": question,
        "answer": [],
        "hint": ["_", "_", "_", "_"],
        "score": 0,
        "fail": 0,
        "start_time": datetime.datetime.utcnow(),
        "end_time": 0
    }
    db.game.insert_one(record)
    return redirect("/play")


@application.route('/play', methods=['GET', 'POST'])
def play():
    with open('play.html', 'r') as f:
        html = f.read()

    if request.method == 'POST':
        guess = [
            request.form.get("pos0"),
            request.form.get("pos1"),
            request.form.get("pos2"),
            request.form.get("pos3"),
        ]
        update_last_record(guess)

    last_record = db.game.find().sort([("start_time", -1)])[0]

    html = Template(html).safe_substitute(
        count = last_record['fail']+1,
        hint = ' '.join(last_record['hint']),
        question = last_record['question']
    )
    return html


@application.route('/gameover', methods=['GET', 'POST'])
def gameover():
    with open('gameover.html', 'r') as f:
        html = f.read()

    if request.method == 'POST':
        update_end_game()
    
    last_record = db.game.find().sort([("start_time", -1)])[0]
    html = Template(html).safe_substitute(
        count=last_record['fail'],
        score=last_record['score']
    )
    return html


@application.route('/sample')
def sample():
    doc = db.game.find().sort([("start_time", -1)])[0]
    # return jsonify(doc)
    body = '<div style="text-align:center;">'
    body += '<h1>Python</h1>'
    body += '<p>'
    body += '<a target="_blank" href="https://flask.palletsprojects.com/en/1.1.x/quickstart/">Flask v1.1.x Quickstart</a>'
    body += ' | '
    body += '<a target="_blank" href="https://pymongo.readthedocs.io/en/stable/tutorial.html">PyMongo v3.11.2 Tutorial</a>'
    body += ' | '
    body += '<a target="_blank" href="https://github.com/andymccurdy/redis-py">redis-py v3.5.3 Git</a>'
    body += '</p>'
    body += '</div>'
    body += '<h1>MongoDB</h1>'
    body += '<pre>'
    body += json.dumps(doc, indent=4, default=json_util.default)
    body += '</pre>'
    res = redisClient.set('Hello', 'World')
    if res == True:
        # Display MongoDB & Redis message.
        body += '<h1>Redis</h1>'
        body += 'Get Hello => '+redisClient.get('Hello').decode("utf-8")
    return body


if __name__ == "__main__":
    ENVIRONMENT_DEBUG = os.environ.get("FLASK_DEBUG", True)
    ENVIRONMENT_PORT = os.environ.get("FLASK_PORT", 5000)
    application.run(host='0.0.0.0', port=ENVIRONMENT_PORT,
                    debug=ENVIRONMENT_DEBUG)
