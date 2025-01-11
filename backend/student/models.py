import datetime

from backend.models.basic_model import db, Column, relationship, Integer, String, ForeignKey, Float, Boolean, JSON, \
    func, DateTime


class StudentCommentForLesson(db.Model):
    __tablename__ = "student_comment_for_lesson"
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey('student.id'))
    lesson_id = Column(Integer, ForeignKey("lesson.id"))
    group_id = Column(Integer, ForeignKey('group.id'))
    student_lesson_id = Column(Integer, ForeignKey('student_lesson.id'))
    comment = Column(String)
    ball = Column(Integer, default=0)
    date = Column(DateTime, default=datetime.datetime.now())

    def add(self):
        db.session.add(self)
        db.session.commit()

    def convert_json(self, entire=False):
        return {
            "id": self.id,
            "student_id": self.student_id,
            "lesson_id": self.lesson_id,
            "comment": self.comment,
            "ball": self.ball,
            "date": self.date,
        }

    @staticmethod
    def calculate_total_ball_by_group(group_id):
        """Calculate the total ball for all comments in a given group."""
        total_ball = db.session.query(func.sum(StudentCommentForLesson.ball)).filter_by(group_id=group_id).scalar()
        return total_ball or 0

    @staticmethod
    def calculate_average_ball_by_group(group_id):
        """Calculate the average ball for all comments in a given group."""
        average_ball = db.session.query(func.avg(StudentCommentForLesson.ball)).filter_by(group_id=group_id).scalar()
        return average_ball or 0

    @staticmethod
    def calculate_total_ball_by_student(student_id):
        """Calculate the total ball for all comments by a given student."""
        total_ball = db.session.query(func.sum(StudentCommentForLesson.ball)).filter_by(student_id=student_id).scalar()
        return total_ball or 0

    @staticmethod
    def calculate_average_ball_by_student(student_id):
        """Calculate the average ball for all comments by a given student."""
        average_ball = db.session.query(func.avg(StudentCommentForLesson.ball)).filter_by(
            student_id=student_id).scalar()
        return average_ball or 0
