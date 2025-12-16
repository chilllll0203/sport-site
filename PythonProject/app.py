from flask import Flask, render_template,url_for,request,redirect,jsonify
from flask_sqlalchemy import SQLAlchemy

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

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "age": self.age,
            "email": self.email,
            "height": self.height,
            "weight": self.weight
        }

@app.route('/',methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        try:
            if "sum_btn" in request.form:
                is_User = User.query.filter_by(email=email, password=password).first()
                if is_User:
                    return redirect('/training')
                else:
                    return "Произошла ошибка!"
        except Exception as e:
            return e
    return render_template('index.html')

@app.route('/reg', methods=['GET', 'POST'])
def reg():
    if request.method == 'POST':
        email = request.form['email']
        name = request.form['name']
        age = request.form['age']
        password = request.form['password']

        user = User(email=email,name=name,age=age,password=password)
        try:
            if "register_btn" in request.form:
                db.session.add(user)
                db.session.commit()
                return redirect('/')
        except Exception as e:
            return e

    else:
        return render_template('reg.html')

@app.route('/training',methods=['GET', 'POST'])
def training():
    if request.method == 'POST':
        pass
    else:
        return render_template('training.html')

@app.route('/userstable')
def userstable():
    users = User.query.all()
    return jsonify([user.to_dict() for user in users])

if __name__ == '__main__':
    app.run(debug=True)