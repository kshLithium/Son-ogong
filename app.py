import cv2

from flask import Flask, render_template, Response, redirect, url_for, request, session
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "fjsadfisdfn13958smdsdk@4"  # Flask-Login을 위한 시크릿 키 설정

app.config['SEND_FILE_MAX_AGE_DEFAULT']=0

login_manager = LoginManager()
login_manager.init_app(app)

# 간단한 사용자 클래스 정의
class User(UserMixin):
    pass

# 사용자 데이터베이스
users = {}
# 텍스트 파일에서 사용자 정보를 읽어옴
with open('users.txt', 'r') as file:
    for line in file:
        username, password = line.strip().split(':')
        username = str(username)
        password = generate_password_hash(password)

        # print(type(password))
        
        users[username] = {'username': username, 'password': password}


@login_manager.user_loader
def load_user(user_id):
    user = User()
    user.id = user_id
    return user


# 웹캠으로부터 영상을 가져오는 함수
def generate_frames():
    webcam = cv2.VideoCapture(0)
    while True:
        success, frame = webcam.read()
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/clear_session')
def clear_session():
    session.clear()
    return 'Session cleared'

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        # print(username)
        password = request.form['password']
        # print(password)

        # print(users)

        # print("username in users : ")
        # print(username in users)
        # print("check_password_hash(users[username]['password'], password)")
        # print(check_password_hash(users[username]['password'], password))
        
        if username in users and check_password_hash(users[username]['password'], password) :
            print("login ok")
            
            user = User()
            user.id = username
            login_user(user)
            return redirect(url_for('cctv'))
    return render_template('login.html')

@app.route('/cctv')
@login_required
def cctv():
    return render_template('cctv.html')

@app.route('/video_feed')
@login_required
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
