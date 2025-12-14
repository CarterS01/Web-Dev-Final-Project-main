from flask import Flask, render_template, request, jsonify, redirect, url_for
import bcrypt
import sqlite3
import json
from urllib.parse import urlencode

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/admin')
def admin():

    students = []

    with sqlite3.connect('data.db') as con:
        cur = con.cursor()

    cur.execute(''' SELECT *
                    FROM students''')
    
    for row in cur:
        stu_id, stu_name = row
        stu_info = (stu_id, stu_name)
        students.append(stu_info)

    cur.close()
    return render_template('admin.html', students=students)

@app.route('/student')
def student():
    grades_param = request.args.get('grades')
    gpa_param = request.args.get('gpa')
    grades = json.loads(grades_param) if grades_param else None
    grades[0].append('Science')
    grades[1].append('Math')
    print(grades)
    #print("stupid")
    gpa = float(gpa_param) if gpa_param else None
    classes = ['Science', 'Math']
    #print(gpa)
    return render_template('student.html', grades=grades, gpa=gpa)


@app.route('/select_a_student')
def select_a_student():

    students = []

    with sqlite3.connect('data.db') as con:
        cur = con.cursor()

    cur.execute(''' SELECT *
                    FROM students''')
    
    for row in cur:
        stu_id, stu_name = row
        stu_info = (stu_id, stu_name)
        students.append(stu_info)

    cur.close()
    return render_template('select.html', students=students)

@app.route('/submit_grades', methods=['POST'])
def submit_grades():
    s_grades = []
    s_nums = []
    m_grades = []
    m_nums = []
    json_data = request.get_json()
    stu_id = json_data['stu_id']
    s_grades.append(json_data['sg1'])
    s_grades.append(json_data['sg2'])
    s_grades.append(json_data['sg3'])
    s_grades.append(json_data['sg4'])
    m_grades.append(json_data['mg1'])
    m_grades.append(json_data['mg2'])
    m_grades.append(json_data['mg3'])
    m_grades.append(json_data['mg4'])

    for i in s_grades:
        if i == 'A':
            s_nums.append(4)
        elif i == 'B':
            s_nums.append(3)
        elif i == 'C':
            s_nums.append(2)
        elif i == 'D':
            s_nums.append(1)
        else:
            s_nums.append(0)

    for j in m_grades:
        if j == 'A':
            m_nums.append(4)
        elif j == 'B':
            m_nums.append(3)
        elif j == 'C':
            m_nums.append(2)
        elif j == 'D':
            m_nums.append(1)
        else:
            m_nums.append(0)

    with sqlite3.connect('data.db') as con:
        cur = con.cursor()

    cur.execute(''' UPDATE grades
                    SET grade1=?, grade2=?, grade3=?, grade4=?
                    WHERE stu_id=? AND class_id=1''',
                    (s_nums[0], s_nums[1], s_nums[2], s_nums[3], stu_id))
    con.commit()

    cur.execute(''' UPDATE grades
                    SET grade1=?, grade2=?, grade3=?, grade4=?
                    WHERE stu_id=? AND class_id=2''',
                    (m_nums[0], m_nums[1], m_nums[2], m_nums[3], stu_id))
    con.commit()

    cur.close()
    return jsonify(json_data)

@app.route('/get_grades', methods=['GET', 'POST'])
def get_grades():
    grades = []
    json_data = request.get_json()
    if not json_data:
        return jsonify({'error': 'expected JSON body with stu_id'}), 400
    stu_id = json_data['stu_id']

    with sqlite3.connect('data.db') as con:
        cur = con.cursor()

    cur.execute(''' SELECT *
                    FROM grades
                    WHERE stu_id=?''',
                    (stu_id,))

    for row in cur:
        id, stu_id, class_id, grade1, grade2, grade3, grade4 = row
        grades_by_class = (grade1, grade2, grade3, grade4)
        grades.append(grades_by_class)

    gpa = (sum(grades[0]) + sum(grades[1]))/(len(grades[0]) + len(grades[1]))

    params = urlencode({'grades': json.dumps(grades), 'gpa': gpa})
    redirect_url = url_for('student') + '?' + params
    # Return the URL so the client can navigate
    return jsonify({'redirect_url': redirect_url})

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/get_login', methods=['GET', 'POST'])
def get_login():
    json_data = request.get_json()
    if not json_data:
        return jsonify({'error': 'expected JSON body with stu_id'}), 400
    username = json_data['username']
    password = json_data['password']

    with sqlite3.connect('data.db') as con:
        cur = con.cursor()

    cur.execute(''' SELECT username
                    FROM user
                    WHERE username=?''',
                    (username,))
    
    if cur.fetchone():
        new_pass = password.encode('utf-8')

        cur.execute(''' SELECT password_hash
                        FROM user
                        WHERE username=?''',
                        (username,))
        
        hashed = str(cur.fetchall()).strip('[(,\')]')

        if bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8')):
            redirect_url = url_for('admin')
            cur.close()
            return jsonify({'redirect_url': redirect_url})
        else:
            redirect_url = url_for('login') + '?' + 'incorrect_password'
            cur.close()
            return jsonify({'redirect_url': redirect_url})
    else:
        redirect_url = url_for('login') + '?' + 'no_user_found'
        cur.close()
        return jsonify({'redirect_url': redirect_url})

if __name__ == "__main__":
    app.run(debug=True)