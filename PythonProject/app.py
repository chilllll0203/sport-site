from flask import Flask, render_template,url_for,request,redirect,jsonify
from flask_sqlalchemy import SQLAlchemy
import bcrypt


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    age= db.Column(db.String(200))
    email= db.Column(db.String(200))
    password = db.Column(db.String(200))
    height = db.Column(db.Integer)
    weight = db.Column(db.Integer)

    def __repr__(self):
        return '<User %r>' % self.id

@app.route('/',methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        try:
            if "sum_btn" in request.form:
                is_User = User.query.filter_by(email=email).first()
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

        hash_password = bcrypt.hashpw(password,bcrypt.gensalt())
        print(hash_password)
        user = User(email=email,name=name,age=age,password=hash_password)
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
        render_template('training.html')
    else:
        return render_template('training.html')

@app.route('/userstable')
def userstable():
    users = User.query.all()
    users_list = []
    for user in users:
        users_list.append(f"ID:{user.id} NAME:{user.name} AGE:{user.age} PASSWORD:{user.password}")
    return jsonify(users_list)
if __name__ == '__main__':
    app.run(debug=True)