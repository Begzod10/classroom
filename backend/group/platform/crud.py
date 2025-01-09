from app import api, app, request, jsonify, db, contains_eager
from backend.models.basic_model import Group, Student, Teacher, User


@app.route(f'{api}/delete_student_from_group/<user_id>/<group_id>/<system_name>')
def delete_student_from_group(user_id, group_id, system_name):
    if system_name == "gennis":
        user = User.query.filter(User.platform_id == user_id).first()
        group = Group.query.filter(Group.platform_id == group_id).first()
    else:
        user = User.query.filter(User.turon_id == user_id).first()
        group = Group.query.filter(Group.turon_id == group_id).first()
    student = Student.query.filter(Student.user_id == user.id).first()
    group.students.remove(student)
    db.session.commit()
    return jsonify({"msg": "O'chirildi"})


@app.route(f'{api}/delete_teacher_from_group/<user_id>/<group_id>/<system_name>')
def delete_teacher_from_group(user_id, group_id, system_name):
    if system_name == "gennis":
        user = User.query.filter(User.platform_id == user_id).first()
        group = Group.query.filter(Group.platform_id == group_id).first()
    else:
        user = User.query.filter(User.turon_id == user_id).first()
        group = Group.query.filter(Group.turon_id == group_id).first()
    teacher = Teacher.query.filter(Teacher.user_id == user.id).first()
    group.teachers.remove(teacher)
    db.session.commit()
    return jsonify({"msg": "O'chirildi"})


@app.route(f'{api}/delete_group/<group_id>/<system_name>')
def delete_group(group_id, system_name):
    if system_name == "gennis":
        group = Group.query.filter(Group.platform_id == group_id).first()
    else:
        group = Group.query.filter(Group.turon_id == group_id).first()
    students = db.session.query(Student).join(Student.groups).options(contains_eager(Student.groups)).filter(
        Group.id == group.id).all()
    teacher = Teacher.query.filter(Teacher.id == group.teacher_id).first()
    group.teachers.remove(teacher)
    for student in students:
        student.groups.remove(group)
    db.session.delete(group)
    db.session.commit()
    return jsonify({"msg": "O'chirildi"})
