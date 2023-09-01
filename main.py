# import pymysql
import sqlite3

from sqlalchemy.engine import result

conn = sqlite3.connect('chatbot_database')
cur = conn.cursor()
try:
    cur.execute('''CREATE TABLE doctor (
   id integer Primary key  AUTOINCREMENT,
   name varchar(20),
   email varchar(50),
   password varchar(20),
   gender varchar(10),
   specialist varchar(50),
   avaliability tinyint(1),
   address varchar(100))''')

    cur.execute('''CREATE TABLE user (
     name varchar(20) DEFAULT NULL,
      email varchar(50) DEFAULT NULL,
     password varchar(20) DEFAULT NULL,
     gender varchar(10) DEFAULT NULL,
     age int(11) DEFAULT NULL)''')

    cur.execute('''CREATE TABLE appointment (
           name varchar(20) DEFAULT NULL,
           doctor_name varchar(50) DEFAULT NULL,
           date_time varchar(20) DEFAULT NULL,
           hospital varchar(10) DEFAULT NULL)''')

    cur.execute('''CREATE TABLE previous_history (
           name varchar(20) DEFAULT NULL,
           age varchar(20) DEFAULT NULL,
          itching varchar(20) DEFAULT NULL,
          skin_rash varchar(20) DEFAULT NULL,
          nodal_skin_eruptions varchar(20) DEFAULT NULL,
          continuous_sneezing varchar(20) DEFAULT NULL,
          shivering varchar(20) DEFAULT NULL,
          chills varchar(20) DEFAULT NULL,
          joint_pain varchar(20) DEFAULT NULL,
          stomach_pain varchar(20) DEFAULT NULL,
          acidity varchar(20) DEFAULT NULL,
          ulcers_on_tongue varchar(20) DEFAULT NULL,
          muscle_wasting varchar(20) DEFAULT NULL,
          vomiting varchar(20) DEFAULT NULL,
          burning_micturition varchar(20) DEFAULT NULL,
          result varchar(20) DEFAULT NULL
         )''')
except:
    pass

import pandas as pd

df = pd.read_csv("Training1.csv", encoding='unicode_escape')
from sklearn.preprocessing import LabelEncoder

le = LabelEncoder()
df.Medicine = le.fit_transform(df.Medicine)

from sklearn.model_selection import train_test_split

predictors = df.drop("Medicine", axis=1)
target = df["Medicine"]
X_train, X_test, Y_train, Y_test = train_test_split(predictors, target, test_size=0.20, random_state=0)

from sklearn.naive_bayes import BernoulliNB
from sklearn.metrics import accuracy_score

BernNB = BernoulliNB(binarize=.1)
BernNB.fit(X_train, Y_train)
print(BernNB)
y_expect = Y_test
y_pred = BernNB.predict(X_test)
print(accuracy_score(y_expect, y_pred) * 100)
score_nb = accuracy_score(y_expect, y_pred) * 100

from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score

clf_entropy = DecisionTreeClassifier(criterion="entropy", random_state=100, max_depth=5, min_samples_leaf=3)
clf_entropy.fit(X_train, Y_train)
y_pred_en = clf_entropy.predict(X_test)
assert isinstance(y_pred_en, object)
y_pred_en
print(accuracy_score(y_expect, y_pred) * 100)
score_dt = accuracy_score(Y_test, y_pred_en) * 100

scores = [score_dt, score_nb]
algorithems = ['Decision Tree', 'navie bayes']

for i in range(len(algorithems)):
    print('the accuracy score achieved using' + algorithems[i] + 'is :' + str(scores[i]) + " %")

#######################################Flask########################################################################33333
import os
from flask import Flask, render_template, url_for, request, flash, redirect, session

from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer

filenumber = int(os.listdir('saved_conversations')[-1])
filenumber = filenumber + 1
file = open('saved_conversations/' + str(filenumber), "w+")
file.write(
    'bot : Hi There! I am a medical chatbot. You can begin conversation by typing in a message and pressing enter.\n')
file.close()

app = Flask(__name__)
app.config['SECRET_KEY'] = '881e69e15e7a528830975467b9d87a98'

english_bot = ChatBot('Bot',
                      storage_adapter='chatterbot.storage.SQLStorageAdapter',
                      logic_adapters=[
                          {
                              'import_path': 'chatterbot.logic.BestMatch'
                          },

                      ],
                      trainer='chatterbot.trainers.ListTrainer')
english_bot.set_trainer(ListTrainer)


# conn = pymysql.connect(host='127.0.0.1', user='root', password='root', database='xtipl')
# cur = conn.cursor()


@app.route('/user_login', methods=['POST', 'GET'])
def user_login():
    conn = sqlite3.connect('chatbot_database')
    cur = conn.cursor()
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['psw']
        count = cur.execute('SELECT * FROM user WHERE email = "%s" AND password = "%s"' % (email, password))
        # conn.commit()
        # cur.close()
        # print(count)
        if len(cur.fetchall()) == 1:
            session['logged_in'] = True
            cur.execute('select * from doctor where avaliability="true"')
            s = cur.fetchall()
            print(s)
            cur.execute('select * from doctor where avaliability="false"')
            # conn.commit()
            s1 = cur.fetchall()
            s2 = s + s1
            return render_template('user_account.html', data=s2)
        else:
            flash('invalid email and password!')
    return render_template('user_login.html')


@app.route('/user_register', methods=['POST', 'GET'])
def user_register():
    conn = sqlite3.connect('chatbot_database')
    cur = conn.cursor()
    if request.method == 'POST':
        name = request.form['uname']
        email = request.form['email']
        password = request.form['psw']
        gender = request.form['gender']
        age = request.form['age']

        cur.execute("insert into user(name,email,password,gender,age)values('%s','%s','%s','%s','%s')" % (
        name, email, password, gender, age))
        conn.commit()
        # cur.close()
        return redirect(url_for('user_login'))

    return render_template('user_register.html')


@app.route('/doctor_login', methods=['POST', 'GET'])
def doctor_login():
    conn = sqlite3.connect('chatbot_database')
    cur = conn.cursor()

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['psw']
        count = cur.execute('SELECT * FROM doctor WHERE email = "%s" AND password = "%s"' % (email, password))
        conn.commit()
        # cur.close()
        print(count)
        if len(cur.fetchall()) == 1:
            print(count)
            flash('{} You have been logged in!'.format(email), 'success')
            session['logged_in_d'] = True
            cur.execute("update doctor set avaliability='true' where email='%s'" % email)
            print("""update doctor set avaliability='true' where email='%s'" %email""")
            conn.commit()
            cur.execute('select * from doctor where email="%s"' % email)
            s = cur.fetchall()
            print(s)
            return render_template('doctor_account.html', a=email, b=s)
        else:
            flash('invalid email and password')
            return redirect(url_for('doctor_login'))
    return render_template('doctor_login.html')


@app.route('/disease_predictor')
def disease_predictor():
    return render_template('user_account.html')


@app.route('/medicine')
def medicine():
    global pname
    conn = sqlite3.connect('chatbot_database')
    cur = conn.cursor()
    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        itching = request.form['itching']
        skin_rash = request.form['skin_rash']
        nodal_skin_eruptions = request.form['nodal_skin_eruptions']
        continuous_sneezing = request.form['continuous_sneezing']
        shivering = request.form['shivering']
        chills = request.form['chills']
        joint_pain = request.form['joint_pain']
        stomach_pain = request.form['stomach_pain']
        acidity = request.form['acidity']
        ulcers_on_tongue = request.form['ulcers_on_tongue']
        muscle_wasting = request.form['muscle_wasting']
        vomiting = request.form['vomiting']
        burning_micturition = request.form['burning_micturition']

        cur.execute(
            "insert into previous_history(name,age,itching,skin_rash,nodal_skin_eruptions,continuous_sneezing,shivering,chills,joint_pain,stomach_pain,acidity,ulcers_on_tongue,muscle_wasting,vomiting,burning_micturition)values('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')" % (
                name, age, itching, skin_rash, nodal_skin_eruptions, continuous_sneezing, shivering, chills, joint_pain,
                stomach_pain, acidity, ulcers_on_tongue, muscle_wasting, vomiting, burning_micturition))
        cur.execute("insert into previous_history(name) values ('%s')" % (
            name))
        conn.commit()
        s = cur.fetchall()
        return render_template('previous_data.html', a=pname, b=s)
        # return redirect(url_for('user_login'))

    return render_template('user_account.html')


@app.route('/server')
def server():
    pass


@app.route('/livechat')
def livechat():
    # os.system('dir')
    os.system('python pythonchat/pyclient.py')
    return render_template('user_account.html')


@app.route('/doctor_livechat')
def doctor_livechat():
    # os.system('dir')
    os.system('python pythonchat/pyclient.py')
    return render_template('doctor_login.html')


@app.route('/doctor_register', methods=['POST', 'GET'])
def doctor_register():
    conn = sqlite3.connect('chatbot_database')
    cur = conn.cursor()
    if request.method == 'POST':
        name = request.form['uname']
        email = request.form['email']
        password = request.form['psw']
        gender = request.form['gender']
        specialist = request.form['specialist']
        address = request.form['address']
        cur.execute(
            "insert into doctor(name,email,password,gender,specialist,avaliability,address)values('%s','%s','%s','%s','%s','false','%s')" % (
            name, email, password, gender, specialist, address))
        conn.commit()
        # cur.close()

        return redirect(url_for('doctor_login'))

    return render_template('doctor_register.html')


@app.route('/user_account', methods=['POST', 'GET'])
def user_account():
    return render_template('user_account.html')


@app.route('/doctor_account', methods=['POST', 'GET'])
def doctor_account():
    if request.method == 'POST':
        email = request.form['email']
        return render_template('doctor_account_edit.html', em=email)


@app.route('/doctor_edit', methods=['POST', 'GET'])
def doctor_edit():
    conn = sqlite3.connect('chatbot_database')
    cur = conn.cursor()
    if request.method == 'POST':
        name = request.form['uname']
        email = request.form['email']
        password = request.form['psw']
        gender = request.form['gender']
        specialist = request.form['specialist']
        address = request.form['address']
        em = request.form['em']

        cur.execute(
            "update doctor set name='%s', email='%s',password='%s',gender='%s',specialist='%s',address='%s' where email='%s'" %
            (name, email, password, gender, specialist, address, em))
        conn.commit()

        return redirect('doctor_login')


@app.route('/')
@app.route('/home')
def home():
    if not session.get('logged_in'):
        return render_template('home.html')
    else:
        return redirect(url_for('user_account'))


@app.route('/chatbot')
def chatbot():
    return render_template('index.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/predict', methods=['POST', 'GET'])
def predict(age=int):
    itching = request.form['itching']
    skin_rash = request.form['skin_rash']
    nodal_skin_eruptions = request.form['nodal_skin_eruptions']
    continuous_sneezing = request.form['continuous_sneezing']
    shivering = request.form['shivering']
    chills = request.form['chills']
    joint_pain = request.form['joint_pain']
    stomach_pain = request.form['stomach_pain']
    acidity = request.form['acidity']
    ulcers_on_tongue = request.form['ulcers_on_tongue']
    muscle_wasting = request.form['muscle_wasting']
    vomiting = request.form['vomiting']
    burning_micturition = request.form['burning_micturition']
    global clf_entropy
    if request.method == 'POST':
        res = clf_entropy.predict(
            [[float(itching), float(skin_rash), float(nodal_skin_eruptions), float(continuous_sneezing)
                 , float(shivering), float(chills), float(joint_pain), float(stomach_pain),
              float(acidity), float(ulcers_on_tongue), float(muscle_wasting), float(vomiting),
              float(burning_micturition)]])
        print(res)
        if res[0] == 0:
            print('abacavir Triumeq® Epzicom® acyclovir')
            flash(f'abacavir Triumeq® Epzicom® acyclovir')
        elif res[0] == 1:
            print('alemtuzumab amikacin amitriptyline')
            flash(f'alemtuzumab amikacin amitriptyline')
        elif res[0] == 2:
            print('Augmentin® amphotericin B ampicillin')
            flash(f'Augmentin® amphotericin B ampicillin')
        elif res[0] == 3:
            print('alemtuzumab amikacin amitriptyline')
            flash(f'alemtuzumab amikacin amitriptyline')
        elif res[0] == 4:
            print('baclofen bleomycin bortezomib')
            flash(f'baclofen bleomycin bortezomib')
        elif res[0] == 5:
            print('calcium bosentan')
            flash(f'calcium bosentan')
        elif res[0] == 6:
            print('codeine crizanlizumab cyclosporine')
            flash(f'codeine crizanlizumab cyclosporine')
        elif res[0] == 7:
            print('dapsone desmopressin cytarabine')
            flash(f'dapsone desmopressin cytarabine')
        elif res[0] == 8:
            print('cytarabine efavirenz Genvoya®')
            flash(f'cytarabine efavirenz Genvoya®')
        elif res[0] == 9:
            print('Genvoya® emtricitabine')
            flash(f'Genvoya® emtricitabine')
        elif res[0] == 10:
            print('cytarabine efavirenz Genvoya®')
            flash(f'cytarabine efavirenz Genvoya®')
        return render_template('medicine.html')
    conn = sqlite3.connect('chatbot_database')
    cur = conn.cursor()
    cur.execute("""UPDATE previous_history SET age = '{}', itching = '{}' ,
                                                  skin_rash = '{}', nodal_skin_eruptions = '{}' ,
                                                  continuous_sneezing = '{}', shivering = '{}',
                                                  chills = '{}', joint_pain = '{}' ,
                                                  stomach_pain = '{}', acidity = '{}',ulcers_on_tongue = '{}', muscle_wasting = '{}' ,
                                                  vomiting = '{}', burning_micturition = '{}', result = '{}'  WHERE name ='{}'""".format(
        age,
        itching,
        skin_rash,
        nodal_skin_eruptions,
        continuous_sneezing,
        shivering,
        chills,
        joint_pain,
        stomach_pain,
        acidity,
        ulcers_on_tongue,
        muscle_wasting,
        vomiting,
        burning_micturition,
        result))

    print("""UPDATE previous_history SET age = '{}', itching = '{}' ,
                                                  skin_rash = '{}', nodal_skin_eruptions = '{}' ,
                                                  continuous_sneezing = '{}', shivering = '{}',
                                                  chills = '{}', joint_pain = '{}' ,
                                                  stomach_pain = '{}',acidity = '{}',
                                                  ulcers_on_tongue = '{}', muscle_wasting = '{}' ,
                                                  vomiting = '{}', burning_micturition= '{}',
                                                  result = '{}'  WHERE name ='{}'""".format(age,
                                                                                            itching,
                                                                                            skin_rash,
                                                                                            nodal_skin_eruptions,
                                                                                            continuous_sneezing,
                                                                                            shivering,
                                                                                            chills,
                                                                                            joint_pain,
                                                                                            stomach_pain,
                                                                                            acidity,
                                                                                            ulcers_on_tongue,
                                                                                            muscle_wasting,
                                                                                            vomiting,
                                                                                            burning_micturition,
                                                                                            result
                                                                                            ))
    print('data updated')
    conn.commit()
    return render_template('user_account.html')


@app.route('/previous_data', methods=['POST', 'GET'])
def previous_data():
    # global pname
    conn = sqlite3.connect('chatbot_database')
    cur = conn.cursor()
    count = cur.execute('SELECT * FROM previous_history WHERE name = "%s"')
    conn.commit()
    print(count)
    s = cur.fetchall()
    print(s)
    return render_template('previous_data.html')
    return render_template('medicine.html')


@app.route("/logout")
def logout():
    session['logged_in'] = False
    return home()


@app.route("/logoutd", methods=['POST', 'GET'])
def logoutd():
    session['logged_in'] = False
    return home()


# def logoutd():
#    conn = sqlite3.connect('chatbot_database')
#    cur = conn.cursor()
#    print('doctor logout')
#    if request.method == 'POST':
#       email = request.form['email']
#       cur.execute('update doctor set avaliability="false" where email="%s"' %email)
#       conn.commit()
#       session['logged_in_d'] = False
#       return home()


@app.route("/get")
def get_bot_response():
    userText = request.args.get('msg')
    response = str(english_bot.get_response(userText))

    appendfile = os.listdir('saved_conversations')[-1]
    appendfile = open('saved_conversations/' + str(filenumber), "a")
    appendfile.write('user : ' + userText + '\n')
    appendfile.write('bot : ' + response + '\n')
    appendfile.close()

    return response


@app.route('/appoinment', methods=['POST', 'GET'])
def appoinment():
    conn = sqlite3.connect('chatbot_database')
    cur = conn.cursor()
    if request.method == 'POST':
        name = request.form['name']
        doctor = request.form['doctor']
        date_time = request.form['date_time']
        hospital = request.form['hospital']
        cur.execute("insert into appointment(name,doctor_name,date_time,hospital)values('%s','%s','%s','%s')" % (
        name, doctor, date_time, hospital))
        conn.commit()
        return redirect(url_for('user_login'))
    return render_template('appoinment.html')


@app.route('/appoinment_details', methods=['POST', 'GET'])
def appoinment_details():
    conn = sqlite3.connect('chatbot_database')
    cur = conn.cursor()
    # if request.method == 'POST':
    session['logged_in'] = True
    cur.execute('select * from appointment')
    s = cur.fetchall()
    return render_template('appoinment_details.html', data=s)
    # return render_template('doctor_account.html')


if __name__ == '__main__':
    app.secret_key = os.urandom(12)
    app.run(debug=True)
