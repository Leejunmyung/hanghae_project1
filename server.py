from pymongo import MongoClient
import jwt
import datetime
import hashlib
import requests
from flask import Flask, render_template, jsonify, request, redirect, url_for
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta


app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True

SECRET_KEY = 'SPARTA'

client = MongoClient('localhost', 27017)
db = client.dbsparta_plus

# 홈화면 API
@app.route('/')
def home():
    # 토큰을 받는다
    token_receive = request.cookies.get('mytoken')
    # DB에서 영화목록을 가져온다
    movies = list(db.hangmovies.find({}, {'_id': False}))
    try:
        # 로그인된 jwt 토큰을 디코드하여 payload 설정
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        # 로그인 정보를 토대로 user_info 설정
        user_info = db.users.find_one({"username": payload["id"]})
        # 위에 설정이 완료되면 main.html로 전달(영화목록 데이터, 유저정보 데이터 포함)
        return render_template('main.html', movies=movies, user_info=user_info)
        # jwt 토큰 시간이 만료되면
    except jwt.ExpiredSignatureError:
        # 로그인 화면으로 이동
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
        # 유효화 실패 디코딩에러
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))

# 로그인 화면 이동
@app.route('/login')
def login():
    # msg request를 통해 받는다
    msg = request.args.get("msg")
    # hlogin.html로 msg와 함께 전달
    return render_template('hlogin.html', msg=msg)

# 상세페이지 API
@app.route('/detail/<name>')
def detail(name): # name 파라미터 받기
    token_receive = request.cookies.get('mytoken')
    # db 영화목록에서 name에 맞는 값 찾기
    movies = db.hangmovies.find_one({'name': name}, {'_id': False})
    # db 리뷰목록에서 name에 맞는 값들 불러오기
    reviews = list(db.posts.find({'title': name}, {'_id': False}))
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.users.find_one({"username": payload["id"]})
        return render_template('detail.html', movies=movies, reviews=reviews, user_info=user_info)
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))

# 리뷰 포스팅 API
@app.route('/posting', methods=['POST'])
def posting():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])

        user_info = db.users.find_one({'username' : payload['id']})
        # detail.html에서 comment,date,title 정보를 request로 받는다.
        comment_receive = request.form['comment_give']
        date_receive = request.form['date_give']
        title_receive = request.form['title_give']
        # 받은 정보를 doc에 담는다.
        doc = {
            "username" : user_info['username'],
            "comment" : comment_receive,
            "date" : date_receive,
            "title" : title_receive
        }
        # db 리뷰목록에 doc에 담은 정보를 넣는다.
        db.posts.insert_one(doc)
        return jsonify({"result": "success", 'msg' : '등록 완료!'})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))

# 로그인 API
@app.route('/sign_in', methods=['POST'])
def sign_in():
    # 로그인페이지에서 보낸 username, password를 request로 받는다.
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']

    # password를 해쉬함수로 암호화한다.
    pw_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    # 받은 username, password를 찾아서 result에 넣는다.
    result = db.users.find_one({'username': username_receive, 'password': pw_hash})

    # result값에 none이 아닐때
    if result is not None:
        # payload 변수에 id와 로그인 지속시간을 넣는다.
        payload = {
         'id': username_receive,
         'exp': datetime.utcnow() + timedelta(seconds=60*60)
        }
        # 정보를 암호화하여 토큰에 저장
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256').decode('utf-8')

        return jsonify({'result': 'success', 'token': token})
    else:
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})

# 회원가입 API
@app.route('/sign_up/save', methods=['POST'])
def sign_up():
    # 로그인페이지에서 보낸 username, password, email 정보를 request로 받는다.
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']
    email_receive = request.form['email_give']
    password_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    # DB에 저장
    doc = {
        "username": username_receive,  # 아이디
        "password": password_hash,  # 비밀번호
        "email": email_receive,
        "profile_name": username_receive,  # 프로필 이름 기본값은 아이디
    }
    db.users.insert_one(doc)
    return jsonify({'result': 'success'})

# 중복확인 API
@app.route('/sign_up/check_dup', methods=['POST'])
def check_dup(): # 아이디 중복확인
    # 로그인페이지에서 보낸 username 정보를 request로 받는다.
    username_receive = request.form['username_give']
    # 받은 username 정보를 db에 존재하는지 확인한다.
    exists = bool(db.users.find_one({"username": username_receive}))
    return jsonify({'result': 'success', 'exists': exists})


if __name__ == '__main__':
    app.run('127.0.0.1', port=5000, debug=True)