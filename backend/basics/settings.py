import os
from werkzeug.utils import secure_filename
from backend.models.basic_model import User
from backend.pisa.api.utils import generate_unique_filename
from dotenv import load_dotenv

import uuid

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}




def check_file(filename):
    value = '.' in filename
    type_file = filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
    return value and type_file


def check_img_remove(img, File):
    img = File.query.filter(File.id == img).first()
    if not img:
        return
    has_links = any([
        img.subjects, img.exercise_answers, img.lesson_block,
        img.exercise_block, img.users, img.file_audio, img.file_img
    ])
    if not has_links:
        img_path = os.path.join("frontend", "build", img.url)
        if os.path.isfile(img_path):
            os.remove(img_path)


def save_img(photo, app, type_file=None):
    basedir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

    symbols = (u"абвгдеёжзийклмнопрстуфхцчшщъыьэюяАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ",
               u"abvgdeejzijklmnoprstufhzcss_y_euaABVGDEEJZIJKLMNOPRSTUFHZCSS_Y_EUA")
    tr = {ord(a): ord(b) for a, b in zip(*symbols)}

    file_name = secure_filename(photo.filename.translate(tr))
    original_name = photo.filename
    unique_name = generate_unique_filename(file_name)

    if type_file == "img":
        upload_folder = os.path.join(basedir, "frontend", "build", "static", "img")
        photo_url = f"static/img/{unique_name}"
    elif type_file == "audio":
        upload_folder = os.path.join(basedir, "frontend", "build", "static", "audio")
        photo_url = f"static/audio/{unique_name}"
    elif type_file == "file":
        upload_folder = os.path.join(basedir, "frontend", "build", "static", "files")
        photo_url = f"static/files/{unique_name}"
    else:
        raise ValueError("Invalid type_file")

    os.makedirs(upload_folder, exist_ok=True)
    photo.save(os.path.join(upload_folder, unique_name))
    return (photo_url, unique_name, original_name)


def add_file(photo, type_file, app, File):
    photo_url, file_name, original_name = save_img(photo, app, type_file=type_file)
    mb_size = str(define_size(f'frontend/build/{photo_url}'))

    img_add = File.query.filter(
        File.url == photo_url,
        File.size == mb_size,
        File.type_file == type_file,
        File.file_name == file_name,
        File.original_name == original_name

    ).first()

    if not img_add:
        img_add = File(
            url=photo_url,
            size=mb_size,
            type_file=type_file,
            file_name=file_name,
            original_name=original_name
        )
        img_add.add()

    return img_add.id


def define_size(url):
    byte_size = os.path.getsize(url)
    return byte_size / (1024 * 1024)


def img_folder():
    return 'frontend/build/static/img'


def img_url():
    return 'static/img'


def file_url():
    return 'static/files'


def file_folder():
    return 'frontend/build/static/files'


def audio_folder():
    return 'frontend/build/static/audio'


def audio_url():
    return "static/audio"


def create_msg(item, status, data=None):
    if status:
        msg = f"{item} muvaffaqiyatli yaratildi",
        success = "success"
    else:
        msg = f"{item} muvaffaqiyatsiz yaratildi",
        success = "danger"

    return {
        "msg": msg,
        "data": data,
        "status": success
    }


def edit_msg(item, status, data=None):
    if status:
        msg = f"{item} muvaffaqiyatli o'zgaritirildi",
        success = "success"
    else:
        msg = f"{item} muvaffaqiyatsiz o'zgartirildi",
        success = "danger"

    return {
        "msg": msg,
        "data": data,
        "status": success
    }


def del_msg(item, status, data=None):
    if status:
        success = "success"
        msg = f"{item} muvaffaqiyatli o'chirildi"
    else:
        msg = f"{item} o'chirilmadi"
        success = "danger"
    return {
        "msg": msg,
        "status": success,
        "data": data
    }


def check_exist_id(user_id=None):
    id = uuid.uuid1()
    user_id = id.hex[0:35] if not user_id else user_id
    exist_user = User.query.filter(User.user_id == user_id).first()
    while exist_user:
        id = uuid.uuid1()
        user_id = id.hex[0:35]
        exist_user = User.query.filter(User.user_id == user_id).first()
    return user_id


def check_exist_classroom_id(classroom_id=None):
    id = uuid.uuid1()
    classroom_id = id.hex[0:35] if not classroom_id else classroom_id
    exist_classroom = User.query.filter(User.classroom_user_id == classroom_id).first()
    while exist_classroom:
        id = uuid.uuid1()
        classroom_id = id.hex[0:35]
        exist_classroom = User.query.filter(User.classroom_user_id == classroom_id).first()
    return classroom_id
