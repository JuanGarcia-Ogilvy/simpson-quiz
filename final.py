
from flask import Flask, render_template, request
import Frinkiac
import string
import random
import json
import time

app = Flask(__name__)

allquestions = {}
allgames = {}
max_questions = 5


screenshot = Frinkiac.random()
#print(screenshot.image_url())
#print(screenshot.meme_url())
#print(screenshot.caption)

def get_random_string():
  srt_length = 10
  return ''.join(random.choices(string.ascii_uppercase + string.digits, k = srt_length))

@app.route('/')
def index():
  return render_template('index.html', newgame=get_random_string())

@app.route('/newgame', methods=['POST'])
def newgame():
  global allgames
  id = request.form['id']
  name = request.form['name'] or 'unknown'

  newgame = {
    'id': id,
    'name': name,
    'score': 0,
    'question': 1,
    'start_time': time.time(),
    'end_time': 0,
    'total_time': 0,
    'completed': False
  }

  allgames[id] = newgame
  return json.dumps({'status':'OK'})

@app.route('/trivia/<game_id>')
def trivia(game_id):
  global allquestions
  global allgames

  game = allgames[game_id]

  #if new_player:
  num_choices = 6

  question = {
    'id': get_random_string(),
    'choices': [],
    'caption': '',
    'image': '',
    'meme': '',
    'answer': 0,
    'answered': False
  }

  for x in range(num_choices):
    fromfrink = Frinkiac.random()
    item = {
      'image': fromfrink.image_url(),
      'meme': fromfrink.meme_url(),
      'title': fromfrink.ep_title,
      'caption': fromfrink.caption.replace('\n', '<br>'),
      'index': x
    }
    question['choices'].append(item)
  
  answer_index = random.randint(0,2)
  answer = question['choices'][answer_index]
  question['answer'] = answer_index
  question['caption'] = answer['caption']
  question['image'] = answer['image']
  question['meme'] = answer['meme']
  question['title'] = answer['title']

  questions = random.sample(question['choices'], num_choices)

  allquestions[question['id']] = question
  
  return render_template(
    'trivia.html',
    game_id = game_id,
    question_id=question['id'],
    question_number=game['question'],
    questions=questions,
    caption=question['caption']
  )

@app.route('/answer', methods=['POST'])
def answer():
  global allquestions
  global allgames
  global max_questions

  game_id = request.form['game_id']
  question_id = request.form['question_id']
  status = 'NOTOK'
  correct = False
  completed = False

  if game_id in allgames and not allgames[game_id]['completed']:
    status = 'OK'

    game = allgames[game_id]
    answer = int(request.form['answer'])
    question = allquestions[question_id]
    correct = answer == question['answer']

    if correct:
      game['score'] += 1
      status = 'CORRECT'
    else:
      status = 'INCORRECT'
    
    game['question'] += 1

    if game['question'] > max_questions:
      game['completed'] = True
      game['end_time'] = time.time()
      game['total_time'] = game['end_time'] - game['start_time']
      completed = True
  
  return json.dumps({
    'status': status,
    'correct': correct,
    'completed': completed
  })

@app.route('/leader', defaults={"game_id": None})
@app.route('/leader/<game_id>')
def leader(game_id):
  global allgames
  global max_questions

  completed = False
  score = False
  name = False
  completed_games = []

  if game_id in allgames and allgames[game_id]['completed']:
    completed = True
    completed_game = allgames[game_id]
    score = completed_game['score'] / max_questions * 100
    name = completed_game['name']

  for game_ided in allgames:
    game = allgames[game_ided]
    if game['completed']:
      completed_games.append(game)
  
  #completed_games = sorted(completed_games, key = lambda i: i['score']) 
  completed_games = sorted(completed_games, key=lambda e: (-e['score'], e['total_time']))
  
  return render_template(
    'leader.html',
    completed=completed,
    score=score,
    name=name,
    games=completed_games,
    num_questions=max_questions
  )


if __name__ == '__main__':
  app.run(debug=True)