from flask import Flask, render_template, request, redirect, url_for, session, flash
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

HOSTNAME = "127.0.0.1"
PORT = 3306
USERNAME = "root"
PASSWORD = "bqy040222"
DATABASE = "gu2"

app.config[
    "SQLALCHEMY_DATABASE_URI"] = f"mysql+pymysql://{USERNAME}:{PASSWORD}@{HOSTNAME}:{PORT}/{DATABASE}?charset=utf8"

db = SQLAlchemy(app)


class User(db.Model):
    iduser = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(45), unique=True, nullable=False)
    password = db.Column(db.String(45), nullable=False)
    gender = db.Column(db.String(45))
    birth = db.Column(db.Date)
    telephone = db.Column(db.String(45))
    email = db.Column(db.String(45), unique=True, nullable=False)
    applicationStatus = db.Column(db.String(45))
    asn = db.Column(db.Integer, default='0')
    major = db.Column(db.String(45), nullable=False)


class Admin(db.Model):
    idadmin = db.Column(db.Integer, primary_key=True, autoincrement=True)
    admin_name = db.Column(db.String(45), unique=True, nullable=False)
    admin_password = db.Column(db.String(45), nullable=False)


class Majors(db.Model):
    idmajor = db.Column(db.Integer, primary_key=True, autoincrement=True)
    major = db.Column(db.String(45), primary_key=True)


class ApplyTable(db.Model):
    idapply = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(45), db.ForeignKey('user.username'), nullable=False)
    name = db.Column(db.String(45), nullable=False)
    gender = db.Column(db.String(45), nullable=False)
    birth = db.Column(db.Date, nullable=False)
    IDnum = db.Column(db.String(12), nullable=False)
    studentNum = db.Column(db.String(45), nullable=False)
    faculty = db.Column(db.String(45), nullable=False)
    politicstatus = db.Column(db.String(45), nullable=False)
    nation = db.Column(db.String(45), nullable=False)
    timeofenrollment = db.Column(db.Date, nullable=False)
    scoreRanking = db.Column(db.Integer, nullable=False)
    NumberofCompulsoryCourses = db.Column(db.String(45), nullable=False)
    PassedNum = db.Column(db.String(45), nullable=False)
    AwardName = db.Column(db.String(45), nullable=False)
    ApplyDate = db.Column(db.Date, nullable=False)
    ApplyReason = db.Column(db.Text, nullable=False)


class Mentor(db.Model):
    idmentor = db.Column(db.Integer, primary_key=True)
    mentorname = db.Column(db.String(45))
    mpassword = db.Column(db.String(45))
    major = db.Column(db.String(45), db.ForeignKey('majors.major'))


class Faculty(db.Model):
    idfaculty = db.Column(db.Integer, primary_key=True, autoincrement=True)
    facultyname = db.Column(db.String(45))
    facultypassword = db.Column(db.String(45))


class College(db.Model):
    idcollege = db.Column(db.Integer, primary_key=True, autoincrement=True)
    collegename = db.Column(db.String(45))
    collegepassword = db.Column(db.String(45))


@app.route('/')
def home():
    return render_template('user_login.html')


@app.route('/college_login', methods=['GET', 'POST'])
def college_login():
    if request.method == 'POST':
        collegename = request.form['collegename']
        collegepassword = request.form['collegepassword']

        colleg = College.query.filter_by(collegename=collegename, collegepassword=collegepassword).first()

        if colleg:
            return redirect(url_for('college_page'))
        else:
            return 'Invalid username or password. Please try again.'
    else:
        return render_template('college_login.html')


@app.route('/college_page', methods=['GET', 'POST'])
def college_page():
    if request.method == 'POST':
        search_query = request.form.get('search_query')
        if search_query:
            passed_students = User.query.filter(User.username.like(f'%{search_query}%')).all()
        else:
            passed_students = User.query.filter_by(applicationStatus='faculty passed').all()
            # 排序，降序passed_students = User.query.filter_by(applicationStatus='faculty passed').order_by(User.username.desc()).all()

        applications = []

        for student in passed_students:
            application = ApplyTable.query.filter_by(username=student.username).first()
            if application:
                applications.append(application)

        return render_template('college_page.html', applications=applications)

    else:
        passed_students = User.query.filter_by(applicationStatus='faculty passed').all()

        applications = []

        for student in passed_students:
            application = ApplyTable.query.filter_by(username=student.username).first()
            if application:
                applications.append(application)

        return render_template('college_page.html', applications=applications)


@app.route('/college_pass_verification', methods=['POST'])
def college_pass_verification():
    selected_students = request.form.getlist('selected_students')

    selected_students_set = set()

    selected_students_set.update(selected_students)

    for student_name in selected_students:
        student = User.query.filter_by(username=student_name).first()
        if student:
            student.applicationStatus = 'Congratulation! You have successfully applied for the scholarship!'
            student.asn = 4
            db.session.add(student)

    all_students = [student.username for student in User.query.all()]

    for student_name in all_students:
        if student_name not in selected_students_set:
            student = User.query.filter_by(username=student_name).first()
            if student and student.applicationStatus == 'mentor did not pass':
                student.applicationStatus = 'college did not pass'
                student.asn = 4
                db.session.add(student)

    db.session.commit()

    return '<script>alert("Students\' application status have been updated."); window.history.back();</script>'


@app.route('/mentor_login', methods=['GET', 'POST'])
def mentor_login():
    error_message = None

    if request.method == 'POST':
        mentorname = request.form['mentorname']
        mpassword = request.form['mpassword']

        mentor = Mentor.query.filter_by(mentorname=mentorname, mpassword=mpassword).first()

        if mentor:
            return redirect(url_for('mentor_page', mentorname=mentorname))
        else:
            error_message = 'Invalid username or password. Please try again.'

    return render_template('mentor_login.html', error_message=error_message)


@app.route('/mentor_page')
def mentor_page():
    mentorname = request.args.get('mentorname')
    mentor = Mentor.query.filter_by(mentorname=mentorname).first()

    if mentor:
        students = User.query.filter_by(major=mentor.major).all()
        applications = []
        for student in students:
            application = ApplyTable.query.filter_by(username=student.username).first()
            if application:
                applications.append(application)
        return render_template('mentor_page.html', applications=applications)
    else:
        return "Mentor not found."


@app.route('/mentor_pass_verification', methods=['POST'])
def mentor_pass_verification():
    selected_students = request.form.getlist('selected_students')

    selected_students_set = set()

    selected_students_set.update(selected_students)

    for student_name in selected_students:
        student = User.query.filter_by(username=student_name).first()
        if student:
            student.applicationStatus = 'mentor passed'
            student.asn = 2
            db.session.add(student)

    all_students = [student.username for student in User.query.all()]

    for student_name in all_students:
        if student_name not in selected_students_set:
            student = User.query.filter_by(username=student_name).first()
            if student and student.applicationStatus == 'applying':
                student.applicationStatus = 'mentor did not pass'
                student.asn = 2
                db.session.add(student)

    db.session.commit()

    return '<script>alert("Students\' application status have been updated."); window.history.back();</script>'


@app.route('/faculty_login', methods=['GET', 'POST'])
def faculty_login():
    if request.method == 'POST':
        facultyname = request.form['facultyname']
        facultypassword = request.form['facultypassword']

        faculty = Faculty.query.filter_by(facultyname=facultyname, facultypassword=facultypassword).first()

        if faculty:
            return redirect(url_for('faculty_page'))
        else:
            return 'Invalid username or password. Please try again.'
    else:
        return render_template('faculty_login.html')


@app.route('/faculty_page', methods=['GET', 'POST'])
def faculty_page():
    if request.method == 'GET':
        passed_students = User.query.filter_by(applicationStatus='mentor passed').all()

        applications = []

        for student in passed_students:
            application = ApplyTable.query.filter_by(username=student.username).first()
            if application:
                applications.append(application)
                print(application)

        if not applications:
            return 'No applications found.'

        return render_template('faculty_page.html', applications=applications)
    else:
        pass


@app.route('/faculty_pass_verification', methods=['POST'])
def faculty_pass_verification():
    selected_students = request.form.getlist('selected_students')

    selected_students_set = set()

    selected_students_set.update(selected_students)

    for student_name in selected_students:
        student = User.query.filter_by(username=student_name).first()
        if student:
            student.applicationStatus = 'faculty passed'
            student.asn = 2
            db.session.add(student)

    all_students = [student.username for student in User.query.all()]

    for student_name in all_students:
        if student_name not in selected_students_set:
            student = User.query.filter_by(username=student_name).first()
            if student and student.applicationStatus == 'mentor did not pass':
                student.applicationStatus = 'faculty did not pass'
                student.asn = 3
                db.session.add(student)

    db.session.commit()

    return '<script>alert("Students\' application status have been updated."); window.history.back();</script>'


@app.route('/user_login', methods=['GET', 'POST'])
def user_login():
    error_message = None

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username, password=password).first()

        if user:
            return redirect(url_for('user_page', username=username))
        else:
            error_message = 'Invalid username or password. Please try again.'

    return render_template('user_login.html', error_message=error_message)


@app.route('/user_page/<username>', methods=['GET', 'POST'])
def user_page(username):
    user = User.query.filter_by(username=username).first()
    if user:
        user_info = {
            'username': user.username,
            'password': user.password,
            'gender': user.gender,
            'birth': user.birth,
            'telephone': user.telephone,
            'email': user.email,
            'major': user.major
        }
        return render_template('user_page.html', **user_info)
    else:
        return 'User not found.'


@app.route('/application_status')
def application_status():
    username = request.args.get('username')
    user = User.query.filter_by(username=username).first()

    if user:
        application_status = user.applicationStatus
        return render_template('application_status.html', username=username, application_status=application_status)
    else:
        return 'User not found.'


@app.route('/user_register', methods=['GET', 'POST'])
def user_register():
    message = None

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        gender = request.form['gender']
        birth = request.form['birth']
        telephone = request.form['telephone']
        email = request.form['email']
        major = request.form['major']

        if password != confirm_password:
            message = 'Passwords do not match. Please try again.'
        else:
            if User.query.filter_by(username=username).first():
                message = 'Username already exists. Please choose a different username.'
            else:
                new_user = User(username=username, password=password, gender=gender, birth=birth,
                                telephone=telephone, email=email, major=major)

                db.session.add(new_user)
                db.session.commit()

                message = 'Registration successful! You can now log in.'

    return render_template('user_register.html', message=message)


@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        admin = Admin.query.filter_by(admin_name=username, admin_password=password).first()

        if admin:
            session['admin_id'] = admin.idadmin
            return redirect(url_for('admin_page'))
        else:
            return 'Invalid username or password. Please try again.'

    return render_template('admin_login.html')


@app.route('/admin_page')
def admin_page():
    if 'admin_id' in session:
        return render_template('admin_page.html')
    else:
        return redirect(url_for('admin_login'))


@app.route('/admin_add_user', methods=['GET', 'POST'])
def admin_add_user():
    message = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        gender = request.form['gender']
        birth = request.form['birth']
        telephone = request.form['telephone']
        email = request.form['email']
        major = request.form['major']

        if password != confirm_password:
            message = 'Passwords do not match. Please try again.'
        else:
            if User.query.filter_by(username=username).first():
                message = 'Username already exists. Please choose a different username.'
            else:
                new_user = User(username=username, password=password, gender=gender, birth=birth,
                                telephone=telephone, email=email, major=major)

                db.session.add(new_user)
                db.session.commit()

                message = 'Registration successful! You can now log in.'

    return render_template('admin_add_user.html', message=message)


@app.route('/admin_view_users')
def admin_view_users():
    users = User.query.all()

    return render_template('admin_view_users.html', users=users)


@app.route('/admin_delete_user', methods=['GET', 'POST'])
def admin_delete_user():
    if request.method == 'POST':
        username = request.form['username']

        # Retrieve the user from the database based on the provided username
        user = User.query.filter_by(username=username).first()

        if user:
            # Attempt to delete related data in the apply_table before deleting the user
            try:
                # Delete entries related to the user in the apply_table
                ApplyTable.query.filter_by(username=username).delete()
                db.session.commit()
            except IntegrityError:
                # If a foreign key constraint error occurs, rollback the session and display an error message
                db.session.rollback()
                return 'Error: Cannot delete user. Related data in apply_table exists.'

            # Delete the user from the user table
            db.session.delete(user)
            db.session.commit()

    # Retrieve the updated list of users from the database
    user_list = User.query.all()

    return render_template('admin_delete_user.html', user_list=user_list)


@app.route('/user_apply/<username>', methods=['GET', 'POST'])
def user_apply(username):
    if request.method == 'POST':
        name = request.form['name']
        gender = request.form['gender']
        birth = request.form['birth']
        IDnum = request.form['IDnum']
        studentNum = request.form['studentNum']
        faculty = request.form['faculty']
        politicstatus = request.form['politicstatus']
        nation = request.form['nation']
        timeofenrollment = request.form['timeofenrollment']
        scoreRanking = request.form['scoreRanking']
        NumberofCompulsoryCourses = request.form['NumberofCompulsoryCourses']
        PassedNum = request.form['PassedNum']
        AwardName = request.form['AwardName']
        ApplyReason = request.form['ApplyReason']

        current_date = datetime.now().date()

        new_application = ApplyTable(
            username=username,
            name=name,
            gender=gender,
            birth=birth,
            IDnum=IDnum,
            studentNum=studentNum,
            faculty=faculty,
            politicstatus=politicstatus,
            nation=nation,
            timeofenrollment=timeofenrollment,
            scoreRanking=scoreRanking,
            NumberofCompulsoryCourses=NumberofCompulsoryCourses,
            PassedNum=PassedNum,
            AwardName=AwardName,
            ApplyDate=current_date,
            ApplyReason=ApplyReason,
        )
        db.session.add(new_application)
        db.session.commit()

        user = User.query.filter_by(username=username).first()
        if user:
            user.asn = 1
            user.applicationStatus = "applying"
            db.session.commit()

        return redirect(url_for('user_page', username=username))

    else:
        user = User.query.filter_by(username=username).first()
        if user and user.asn == 1:
            return render_template('already_applied.html', username=username)
        elif user and user.asn == 0:
            return render_template('user_apply.html', username=username)
        elif user and user.asn == 2 or 3 or 4:
            return '''
                           <script>
                               alert("The application is already under review and you cannot change the information");
                               window.location.href = "{0}";
                           </script>
                       '''.format(url_for('user_page', username=username))


@app.route('/already_applied/<username>')
def already_applied(username):
    return render_template('already_applied.html', username=username)


@app.route('/apply_update/<username>', methods=['GET', 'POST'])
def apply_update(username):
    if request.method == 'POST':
        name = request.form['name']
        gender = request.form['gender']
        birth = request.form['birth']
        IDnum = request.form['IDnum']
        studentNum = request.form['studentNum']
        faculty = request.form['faculty']
        politicstatus = request.form['politicstatus']
        nation = request.form['nation']
        timeofenrollment = request.form['timeofenrollment']
        scoreRanking = request.form['scoreRanking']
        NumberofCompulsoryCourses = request.form['NumberofCompulsoryCourses']
        PassedNum = request.form['PassedNum']
        AwardName = request.form['AwardName']
        ApplyReason = request.form['ApplyReason']

        current_date = datetime.now().date()

        application = ApplyTable.query.filter_by(username=username).first()
        if application:
            application.name = name
            application.gender = gender
            application.birth = birth
            application.IDnum = IDnum
            application.studentNum = studentNum
            application.faculty = faculty
            application.politicstatus = politicstatus
            application.nation = nation
            application.timeofenrollment = timeofenrollment
            application.scoreRanking = scoreRanking
            application.NumberofCompulsoryCourses = NumberofCompulsoryCourses
            application.PassedNum = PassedNum
            application.AwardName = AwardName
            application.ApllyDate = current_date
            application.ApplyReason = ApplyReason

            db.session.commit()

            return """
                            <script>
                                alert('Information updated successfully!');
                                window.location.href = '{}';
                            </script>
                        """.format(url_for('user_page', username=username))
        else:
            return 'Application not found.'

    return render_template('apply_update.html', username=username)


@app.route('/user_applyinfo/<username>')
def user_applyinfo(username):
    application = ApplyTable.query.filter_by(username=username).first()
    if application:
        return render_template('user_applyinfo.html', username=username, application=application)
    else:
        return """
                            <script>
                                alert('User request information not found.');
                                window.location.href = '{}';
                            </script>
                        """.format(url_for('user_page', username=username))


@app.route('/application_info/<username>', methods=['GET'])
def application_info(username):
    return render_template('application_info.html',username=username)


if __name__ == '__main__':
    app.run(debug=True)