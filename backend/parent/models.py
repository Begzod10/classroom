from backend.models.basic_model import Column, Integer, db, String, ForeignKey, Boolean, desc, DateTime, relationship


class Parent(db.Model):
    __tablename__ = "parent"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    student_get = relationship("Student", secondary="parent_child", backref="parent", order_by="Student.id")

    def convert_json(self, entire=False):
        return {
            "parent_id": self.id,
            "id": self.user.id,
            "name": self.user.name,
            "surname": self.user.surname,
            "username": self.user.username,
            "phone": self.user.phone,
            "location": {
                "id": self.user.location_id,
                "name": self.user.location.name
            },
            'date': str(self.user.born_day) + '.' + str(self.user.born_month) + '.' + str(self.user.born_year),
            "children": [
                {
                    "id": st.id,
                    "user_id": st.user_id,
                    "name": st.user.name,
                    "username": st.user.username,
                    "surname": st.user.surname,
                    "balance": st.user.balance,
                    "subjects": [subject.subject.name for subject in st.studentsubject]
                } for st in self.student
            ]
        }

    def add(self):
        db.session.add(self)
        db.session.commit()


db.Table('parent_child',
         db.Column('parent_id', db.Integer, db.ForeignKey('parent.id')),
         db.Column('student_id', db.Integer, db.ForeignKey('student.id'))
         )
