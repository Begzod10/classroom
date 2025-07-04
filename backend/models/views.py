from app import db, admin
from flask_admin.contrib.sqla import ModelView
from backend.models.basic_model import Subject, User, Role


class UserAdmin(ModelView):
    column_list = ['id', 'username', 'name', 'surname', 'phone', 'role_id', 'classroom_user_id']
    form_columns = ['username', 'name', 'surname', 'phone', 'password', 'role_id', 'system_name', 'password',
                    ]


class SubjectAdmin(ModelView):
    column_list = ['id', 'name']
    form_columns = ['name']


class RoleAdmin(ModelView):
    column_list = ['id', 'type', 'role']
    form_columns = ['type', 'role']


admin.add_view(UserAdmin(User, db.session))
admin.add_view(SubjectAdmin(Subject, db.session))
admin.add_view(RoleAdmin(Role, db.session))
