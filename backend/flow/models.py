from backend.models.basic_model import *



# Aloqa jadvali (Flow - Student M2M uchun)
student_flow = Table(
    'student_flow',
    db.Model.metadata,
    Column('flow_id', Integer, ForeignKey('flow.id'), primary_key=True),
    Column('student_id', Integer, ForeignKey('student.id'), primary_key=True)
)


class Flow(db.Model):
    __tablename__ = "flow"

    id = Column(Integer, primary_key=True)
    turon_id = Column(Integer, unique=True, nullable=True)  # Django ID saqlash uchun

    name = Column(String, nullable=False)
    desc = Column(String, nullable=True)
    activity = Column(Boolean, default=False)

    # ForeignKey lar
    subject_id = Column(Integer, ForeignKey('subject.id'), nullable=True)
    teacher_id = Column(Integer, ForeignKey('teacher.id'), nullable=True)
    level_id = Column(Integer, ForeignKey('subject_level.id'), nullable=True)
    branch_id = Column(Integer, ForeignKey('branch.id'), nullable=True)

    # JSONField
    classes = Column(JSON, nullable=True)

    # Relationships
    subject = relationship("Subject", backref="flows", lazy="select")
    teacher = relationship("Teacher", backref="flows", lazy="select")
    level = relationship("SubjectLevel", backref="flows", lazy="select")
    branch = relationship("Branch", backref="flows", lazy="select")
    # timetables = db.relationship("ClassTimeTable", backref="flow", lazy=True)
    # Many-to-Many
    students = relationship(
        "Student",
        secondary=student_flow,
        backref="flows",
        order_by="Student.id"
    )

    def __repr__(self):
        return f"<Flow {self.name}>"
