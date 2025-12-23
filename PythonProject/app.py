import ast
import json
from datetime import datetime

import requests
from flask import Flask, render_template,url_for,request,redirect,jsonify,session,send_file
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import bcrypt

app = Flask(__name__)
app.secret_key = 'supersecretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)
migrate = Migrate(app,db)

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    age= db.Column(db.String(200))
    email= db.Column(db.String(200))
    password = db.Column(db.String(200))
    height = db.Column(db.Integer)
    weight = db.Column(db.Integer)
    def __init__(self,name, age, email,password,height,weight):
        self.name = name
        self.age = age
        self.email = email
        self.password = password
        self.height = height
        self.weight = weight
    def __repr__(self):
        return '<User %r>' % self.id

class TestAnswer(db.Model):
    __tablename__ = 'test_answers'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'),nullable=False)
    answer1 = db.Column(db.String(200))
    answer2 = db.Column(db.String(200))
    answer3 = db.Column(db.String(200))
    user = db.relationship('User',foreign_keys=[user_id])
    def __init__(self,user_id,answer1,answer2,answer3):
        self.user_id = user_id
        self.answer1 = answer1
        self.answer2 = answer2
        self.answer3 = answer3

class WaterUser(db.Model):
    __tablename__ = 'water_users'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    date = db.Column(db.DateTime,default=datetime.utcnow)
    count = db.Column(db.Integer,default=0)
    user = db.relationship('User',foreign_keys=[user_id])
    def __init__(self,user_id,date,count):
        self.user_id = user_id
        self.date = date
        self.count = count

class CaloriesUser(db.Model):
    __tablename__ = 'calories_users'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    date = db.Column(db.DateTime,default=datetime.utcnow)
    count = db.Column(db.Integer,default=0)
    user = db.relationship('User',foreign_keys=[user_id])
    def __init__(self,user_id,date,count):
        self.user_id = user_id
        self.date = date
        self.count = count

class WeeklyProgram(db.Model):
    __tablename__ = 'weekly_programs'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'),nullable=False)
    user = db.relationship('User',foreign_keys=[user_id])
    def __init__(self,user_id):
        self.user_id = user_id

class TrainingDay(db.Model):
    __tablename__ = 'training_days'
    id = db.Column(db.Integer, primary_key=True)
    program_id = db.Column(db.Integer, db.ForeignKey('weekly_programs.id'),nullable=False)
    day_of_week = db.Column(db.String(20),nullable=False)
    program = db.relationship('WeeklyProgram',foreign_keys=[program_id])
    def __init__(self,program_id,day_of_week):
        self.program_id = program_id
        self.day_of_week = day_of_week

class Exercise(db.Model):
    __tablename__ = 'exercises'
    id = db.Column(db.Integer, primary_key=True)
    training_id = db.Column(db.Integer, db.ForeignKey('training_days.id'),nullable=False)
    name = db.Column(db.String(200),nullable=False)
    sets = db.Column(db.Integer,nullable=False)
    reps = db.Column(db.Integer,nullable=False)
    training_day = db.relationship('TrainingDay',foreign_keys=[training_id])
    def __init__(self,training_id,name,sets,reps):
        self.training_id = training_id
        self.name = name
        self.sets = sets
        self.reps = reps

@app.route('/',methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        try:
            if "sum_btn" in request.form:
                is_User = User.query.filter_by(email=email).first()
                session['user'] = {
                    'id':is_User.id,
                    'name':is_User.name,
                    'age':int(is_User.age),
                    'email':is_User.email,
                    'password':is_User.password,
                    'height':int(is_User.height),
                    'weight':int(is_User.weight),
                }
                if is_User:
                    if bcrypt.checkpw(password.encode(),is_User.password):
                        return redirect('/training')
                else:
                    return "Произошла ошибка!"
        except Exception as e:
            print(e)
    return render_template('index.html')

@app.route('/reg', methods=['GET', 'POST'])
def reg():
    if request.method == 'POST':
        email = request.form['email']
        name = request.form['name']
        age = request.form['age']
        password = request.form['password'].encode("utf-8")
        height = int(request.form['height'])
        weight = int(request.form['weight'])
        hash_password = bcrypt.hashpw(password,bcrypt.gensalt())
        print(hash_password)
        user = User(email=email,name=name,age=age,password=hash_password, height=height,weight=weight)
        try:
            if "register_btn" in request.form:
                db.session.add(user)
                db.session.commit()
                id_user = User.query.filter_by(email=email).first()
                weeklyprogramUser = WeeklyProgram(id_user.id)
                db.session.add(weeklyprogramUser)
                db.session.commit()
                return redirect('/')
        except Exception as e:
            print(e)

    else:
        return render_template('reg.html')

@app.route('/training',methods=['GET', 'POST'])
def training():
    data_user = session['user']
    total_water = session.get('total_water', 0)
    total_calories = session.get('total_calories', 0)
    user = User(data_user['name'], data_user['age'], data_user['email'], data_user['password'], data_user['height'], data_user['weight'])
    normal_water = 30*user.weight
    normal_calories:int = 10*int(user.weight)+6.25*int(user.height)-5*int(user.age)+5
    if request.method == 'POST':
        if "button_test" in request.form:
            return redirect('/test_train')
        elif "button_train" in request.form:
            return redirect('/train')
        elif "button_addWater" in request.form:
            return redirect('/add_water')
        elif "button_addCalories" in request.form:
            return redirect('/add_calories')
        elif "button_profile" in request.form:
            return redirect('/profile')
        elif "button_main" in request.form:
            return redirect('/training')
        elif "button_addtrain" in request.form:
            return redirect('/train')
    else:
        return render_template('training.html',normal_water=normal_water,total_water=total_water,total_calories=total_calories,normal_calories=normal_calories)

@app.route('/userstable')
def userstable():
    users = User.query.all()
    users_list = []
    for user in users:
        users_list.append(f"ID:{user.id} EMAIL:{user.email} NAME:{user.name} AGE:{user.age} PASSWORD:{user.password} HEIGHT:{user.height} WEIGHT:{user.weight}")
    return jsonify(users_list)

@app.route('/users_water')
def users_water_table():
    users_water = WaterUser.query.all()
    water_list = []
    for user_water in users_water:
        water_list.append(f"ID:{user_water.id} ID USER: {user_water.user_id} DATE: {user_water.date} COUNT: {user_water.count}")
    return jsonify(water_list)

@app.route('/users_calories')
def users_calories_table():
    users_calories = CaloriesUser.query.all()
    calories_list = []
    for user_water in users_calories:
        calories_list.append(f"ID:{user_water.id} ID USER: {user_water.user_id} DATE: {user_water.date} COUNT: {user_water.count}")
    return jsonify(calories_list)

@app.route('/test_train',methods=['GET', 'POST'])
def test_train():
    if request.method == 'POST':
        if "button_addTest" in request.form:
            answer1 = request.form['answer1']
            answer2 = request.form['answer2']
            answer3 = request.form['answer3']
            data = session.get('user')
            id_user = data['id']
            test_user = TestAnswer(id_user, answer1, answer2, answer3)
            workout_planUser = get_train(data['height'], data['weight'],answer1,answer2,answer3)
            weeklyprogramUser = WeeklyProgram.query.filter_by(id_user=id_user).first()
            for day in workout_planUser:
                training_day = TrainingDay(weeklyprogramUser.id, day['day'])
                db.session.add(training_day)
                db.session.commit()
                for exercise in day['exercises']:
                    exercise_train = Exercise(training_day.id, exercise['name'],exercise['sets'],exercise['reps'])
                    db.session.add(exercise_train)
                    db.session.commit()
            try:
                db.session.add(test_user)
                db.session.commit()
                return redirect('/training')
            except Exception as e:
                return jsonify(e)
    return render_template('test_train.html')

@app.route('/train',methods=['GET', 'POST'])
def train():
    pages = {'train1':'block','train2':'none','train3':'none'}
    if request.method == 'POST':
        if "button_train1" in request.form:
            name = 'train1'
            if name in pages:
                pages[name] = 'block'
                pages['train2'] = 'none'
                pages['train3'] = 'none'
            list_exercises = Exercise.query.filter_by()
            return render_template('train.html', **pages)
        elif "button_train2" in request.form:
            name = 'train2'
            if name in pages:
                pages[name] = 'block'
                pages['train1'] = 'none'
                pages['train3'] = 'none'
            return render_template('train.html', **pages)
        elif "button_train3" in request.form:
            name = 'train3'
            if name in pages:
                pages[name] = 'block'
                pages['train1'] = 'none'
                pages['train2'] = 'none'
            return render_template('train.html', **pages)
        elif "button_profile" in request.form:
            return redirect('/profile')
        elif "button_main" in request.form:
            return redirect('/training')
        elif "button_addtrain" in request.form:
            return redirect('/train')
    else:
        return render_template('train.html',**pages)
@app.route('/profile',methods=['GET', 'POST'])
def profile():
    data = session.get('user')
    user = User(data['name'], data['age'], data['email'], data['password'], data['height'], data['weight'])
    if request.method == 'POST':
        if "button_main" in request.form:
            return render_template('training.html')
        elif "button_train" in request.form:
            return redirect('/train')
        if "button_exit" in request.form:
            session.clear()
            return redirect('/')
    else:
        return render_template('profile.html',username= user.name,email=user.email,age=user.age,height=user.height,weight=user.weight)

@app.route('/add_water',methods=['GET', 'POST'])
def add_water():
    if request.method == 'POST':
        if "button_addWater" in request.form:
            data = session.get('user')
            user_id = data['id']
            date_water = datetime.now()
            water_count = request.form.get('count_water')
            water_user = WaterUser(user_id,date_water,water_count)
            session['water_user'] = {
                'user_id': user_id,
                'date_water': date_water,
                'water_count': water_count
            }
            try:
                db.session.add(water_user)
                db.session.commit()
                return redirect('/training')
            except Exception as e:
                return jsonify(e)
    else:
        return render_template('water.html')

@app.route('/add_calories',methods=['GET', 'POST'])
def add_calories():
    if request.method == 'POST':
        if "button_addCalories" in request.form:
            data = session.get('user')
            user_id = data['id']
            date_calories = datetime.now()
            calories_count = request.form.get('count_calories')
            calories_user = CaloriesUser(user_id,date_calories,calories_count)
            try:
                db.session.add(calories_user)
                db.session.commit()
                return redirect('/training')
            except Exception as e:
                return jsonify(e)
    else:
        return render_template('callories.html')

def get_train(height, weight, answer1, answer2, answer3):
    prompt = {
        "modelUri": "gpt://b1gc2itrie9cbggfhprv/yandexgpt-lite",
        "completionOptions": {
            "stream": False,
            "temperature": 0.6,
            "maxTokens": "1000"
        },
        "messages": [
            {
                "role": "system",
                "text": "Ты ассистент подбора тренировки на неделю."
            },
            {
                "role": "user",
                "text": f"Выведи ответ в виде компактного однострочного списка на Python без пробелов и переносов, чтобы его можно было сразу вставить в код. Составь план тренировок на 3 дня по 5 упражений на день на основе следующих данных:"
                        f"- Рост: {height} см"
                        f"- Вес: {weight} кг"
                        f"- Цель тренировок: {answer1}"
                        f"- Уровень физической подготовки: {answer2}"
                        f"- Ограничения по здоровью или травмы: {answer3}"
                        f"Выведи результат строго в виде списка Python-словарей. Каждый день — отдельный элемент списка."
                        f"Внутри каждого словаря должен быть ключ day (номер дня: 1, 2 или 3) и ключ exercises, значение которого — список упражнений."
                        f" Каждое упражнение — это словарь с ключами: name (название упражнения), sets (количество подходов), reps (количество повторений на подход)."
                        f"Не добавляй пояснений, комментариев или дополнительного текста — только валидный Python-список."
                        f"Пример как надо сделать:"
                        f"Формат ответа должен быть валидным Python-литералом, как в этом примере:"
                        f"["
                        f"{{"
                        f"day: 1,"
                        f"exercises: ["
                        f"{{name: Отжимания, sets: 3, reps: 12}},"
                        f"{{name: Приседания, sets: 4, reps: 15}}"
                        f"]"
                        f"}}"
                        f"]"
                        f"Не добавляй текст до или после — только список."
            }
        ]
    }
    url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Api-Key"
    }
    response = requests.post(url, json=prompt, headers=headers)
    response_text = json.loads(response.text)
    raw_text = response_text["result"]["alternatives"][0]["message"]["text"]
    if raw_text.startswith("```") and raw_text.endswith("```"):
        code_str = raw_text[3:-3].strip()
    else:
        code_str = raw_text.strip()
    workout_plan = ast.literal_eval(code_str)
    return workout_plan

if __name__ == '__main__':
    get_train(170,60,"Для набора мышечной массы","Нет","Нет")
    app.run(debug=True)
