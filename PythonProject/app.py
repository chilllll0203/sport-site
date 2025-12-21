from datetime import datetime
from io import BytesIO
from flask import Flask, render_template,url_for,request,redirect,jsonify,session,send_file
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import bcrypt
import os
from pyexpat.errors import messages

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
class WeeklyProgram(db.Model):
    __tablename__ = 'weekly_programs'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'),nullable=False)
    user = db.relationship('User',foreign_keys=[user_id])
class TrainingDay(db.Model):
    __tablename__ = 'training_days'
    id = db.Column(db.Integer, primary_key=True)
    program_id = db.Column(db.Integer, db.ForeignKey('weekly_programs.id'),nullable=False)
    day_of_week = db.Column(db.String(20),nullable=False)
    program = db.relationship('WeeklyProgram',foreign_keys=[program_id])
class Exercise(db.Model):
    __tablename__ = 'exercises'
    id = db.Column(db.Integer, primary_key=True)
    training_id = db.Column(db.Integer, db.ForeignKey('training_days.id'),nullable=False)
    name = db.Column(db.String(200),nullable=False)
    sets = db.Column(db.Integer,nullable=False)
    reps = db.Column(db.Integer,nullable=False)
    training_day = db.relationship('TrainingDay',foreign_keys=[training_id])

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
                    'age':is_User.age,
                    'email':is_User.email,
                    'password':is_User.password,
                    'height':is_User.height.decode("utf-8"),
                    'weight':is_User.weight.decode("utf-8"),
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
        height = request.form['height'].encode("utf-8")
        weight = request.form['weight'].encode("utf-8")
        hash_password = bcrypt.hashpw(password,bcrypt.gensalt())
        print(hash_password)
        user = User(email=email,name=name,age=age,password=hash_password, height=height,weight=weight)
        try:
            if "register_btn" in request.form:
                db.session.add(user)
                db.session.commit()
                return redirect('/')
        except Exception as e:
            print(e)

    else:
        return render_template('reg.html')

@app.route('/training',methods=['GET', 'POST'])
def training():
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
            return render_template('training.html')
        return None
    else:
        return render_template('training.html')

@app.route('/userstable')
def userstable():
    users = User.query.all()
    users_list = []
    for user in users:
        users_list.append(f"ID:{user.id} EMAIL:{user.email} NAME:{user.name} AGE:{user.age} PASSWORD:{user.password}")
    return jsonify(users_list)

@app.route('/users_water')
def users_water_table():
    users_water = WaterUser.query.all()
    water_list = []
    for user_water in users_water:
        water_list.append(f"ID:{user_water.id} ID USER: {user_water.user_id} DATE: {user_water.date} COUNT: {user_water.count}")
    return jsonify(water_list)
@app.route('/test_train',methods=['GET', 'POST'])
async def test_train():
    print("Вы перешли на страницу с тестом")
    return await jsonify("Вы перешли на страницу с тестом")

@app.route('/train',methods=['GET', 'POST'])
def train():
    print("Вы перешли на страницу с вашими тренировками")

@app.route('/profile',methods=['GET', 'POST'])
def profile():
    if request.method == 'POST':
        if "button_main" in request.form:
            return render_template('training.html')
        elif "button_train" in request.form:
            return redirect('/train')
        if "button_exit" in request.form:
            session.clear()
            return redirect('/')
    data = session.get('user')
    user = User(data['name'],data['age'],data['email'],data['password'],data['height'],data['weight'])
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
            try:
                db.session.add(water_user)
                db.session.commit()
                return redirect('/training')
            except Exception as e:
                return jsonify(e)
    return render_template('water.html')

@app.route('/add_calories',methods=['GET', 'POST'])
def add_calories():
    print("Вы перешли на страницу с добавление калорий")

if __name__ == '__main__':
    app.run(debug=True)