from flask import render_template, request, send_from_directory, make_response, jsonify
from flask import current_app as app

from PIL import Image
import uuid
import io
import json
import hashlib
import uuid
import re
import random

class DailyMonster:
    day = ""
    monster = None 

    @staticmethod
    def get_daily_monster():
        if not DailyMonster.day or date.today() != DailyMonster.day:
            rand = random.randrange(0, db.session.query(MonsterInfo).count())
            DailyMonster.daily_monster = db.session.query(MonsterInfo)[rand]
            DailyMonster.day = date.today()
        return DailyMonster.daily_monster



@app.route('/')
def index():
    return render_template('index.html')

@app.route('/manifest.json')
def manifest():
    return send_from_directory('../react/build', 'manifest.json')

@app.route('/logo192.png')
def logo192():
    return send_from_directory('../react/build', 'logo192.png')

@app.route('/logo512.png')
def logo512():
    return send_from_directory('../react/build', 'logo512.png')

@app.route('/favicon.ico')
def favicon():
    return send_from_directory('../react/build', 'favicon.ico')

@app.route('/titlelogo.png')
def titlelogo():
    return send_from_directory('../react/build', 'titlelogo.png')

@app.route('/loading.png')
def loading():
    return send_from_directory('../react/build', 'loading.png')

@app.route('/login')
def login():
    args = _get_request_args('username', 'password')
    if None in args:
        return _make_error_response('Missing URL Arguments')
    username, password = args
    if '' in (username, password):
        return _make_invalid_response('Username/password empty')
    find_user = User.query.filter_by(username=username).first()
    if not find_user:
        return _make_invalid_response('Incorrect Credentials')

    salt = find_user.salt
    hashed_password = _hash_password(password, salt)
    if find_user.password != hashed_password:
        return _make_invalid_response('Incorrect Credentials')

    return _make_json_response(_user_as_json(find_user))


@app.route('/register')
def register():
    args = _get_request_args('username', 'password')
    if None in args:
        return _make_error_response('Bad Request')

    username, password = args
    if not _valid_username(username) or not _valid_password(password):
        return _make_invalid_response('Invalid username or password')
    find_user = User.query.filter_by(username=username).first()
    if find_user:
        return _make_invalid_response('Username Taken')

        
    salt = _generate_salt()
    hashed_password = _hash_password(password, salt)
    user = User(username, hashed_password, salt)
    db.session.add(user)

    new_monster_info = MonsterInfo()
    db.session.add(new_monster_info)

    first_monster = Monster(user, new_monster_info)
    db.session.add(first_monster)

    db.session.commit()
    return _make_json_response(_user_as_json(user))


@app.route('/codes')
def codes():
    args = _get_request_args('userId', 'codes')
    if None in args:
        return _make_invalid_response('Bad Request')

    user_id, monster_codes = args
    if not user_id.isdigit():
        return _make_invalid_response(f'Invalid user id')

    monster_codes = monster_codes.split()

    user_id = int(user_id)
    user = User.query.get(user_id)
    if not user:
        return _make_invalid_response('User not found')

    log = []
    redeemed = []
    for monster_code in monster_codes:
        if not _valid_code(monster_code):
            log.append(f'Invalid code: {monster_code}')
            continue
        monster_info = MonsterInfo.query.filter_by(code=monster_code).first()
        if not monster_info:
            log.append(f'Code not found: {monster_code}')
            continue

        already_redeemed = False

        for monster in user.monsters:
            if monster.monster_info.code == monster_code:
                log.append(f'Code already redeemed: {monster_code}')
                already_redeemed = True
        if not already_redeemed:
            log.append(f'Redeemed code: {monster_code} Obtained {monster_info.name}')
            new_monster = Monster(user, monster_info)
            redeemed.append(new_monster)
            db.session.add(new_monster)

    db.session.commit()
    return _make_json_response({'user':_user_as_json(user), 'redeemed': redeemed, 'log':log})


@app.route('/create')
def create():
    args = _get_request_args('num')
    if None in args:
        return _make_invalid_response('No num given')
    num, = args
    if not num.isdigit():
        return _make_invalid_response(f'Invalid num')
    num = int(num)
    new_monsters = []
    for _ in range(num):
        new_monster = MonsterInfo()
        new_monsters.append(new_monster)
        db.session.add(new_monster)
    db.session.commit()

    return _make_json_response([_monster_info_as_json(monster) for monster in new_monsters])

@app.route('/images/<monster_info_id>')
def get_image(monster_info_id):
    if monster_info_id == None:
        return _make_error_response('No Monster Id')
    monster = MonsterInfo.query.get(monster_info_id)
    if not monster or not monster.image:
        return _make_invalid_response('No Monster Found')
    response = _make_response(monster.image, 200)
    response.headers['Content-Type'] = 'image/png'
    return response

def _get_request_args(*args):
    return [request.args.get(arg) for arg in args]

def _valid_username(username):
    return re.match(r'^[a-z0-9\-!@#$%^&*()]{3,64}$', username)


def _valid_password(password):
    return re.match(r'^[a-z0-9\-!@#$%^&*()]{3,64}$', password)


def _valid_code(code):
    return True


def _all_ints(*args):
    return all([arg.isdigit() for arg in args])


def _convert_to_ints(*args):
    return [int(arg) for arg in args]


def _generate_salt():
    return uuid.uuid4().hex


def _hash_password(password, salt):
    return hashlib.sha512(password.encode('utf-8')+salt.encode('utf-8')).hexdigest()

def _user_as_json(user):
    return {
        'id': user.id,
        'username': user.username,
        'created': str(user.created),
        'monsters': _get_user_monsters(user),
        'dailyMonster': _monster_info_as_json(DailyMonster.get_daily_monster())
    }


def _get_user_monsters(user):
    return [_monster_as_json(monster) for monster in user.monsters]


def _monster_as_json(monster):
    return {
        'id': monster.monster_info.id,
        'name': monster.monster_info.name,
        'code': monster.monster_info.code
    }

def _monster_info_as_json(monster_info):
    return {
        'id': monster_info.id,
        'name': monster_info.name,
        'code': monster_info.code
    }

def _image_to_bytes(image: Image):
    image = image.copy()
    image_bytes_array = io.BytesIO()
    image.save(image_bytes_array, format='PNG')
    image_bytes = image_bytes_array.getvalue()
    return image_bytes


def _make_error_response(error_message, *args, **kargs):
    return _make_json_response({'error': error_message}, 400, *args, **kargs)


def _make_invalid_response(invalid_message, *args, **kargs):
    return _make_json_response({'invalid': invalid_message}, 200, *args, **kargs)


def _make_json_response(body, *args, **kargs):
    response = jsonify(body, 200, *args, **kargs)
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response


def _make_response(*args, **kargs):
    response = make_response(*args, **kargs)
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response
