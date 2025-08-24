from sqlalchemy import Column, Integer, String, ForeignKey, JSON, DateTime, Boolean
from sqlalchemy.orm import relationship
from backend.models.basic_model import db
from backend.models.base import Base
from datetime import datetime


class SlideType(Base):
    __tablename__ = "slide_type"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    deleted = Column(Boolean, default=False)

    def convert_json(self, entire=False):
        return {"id": self.id, "name": self.name}

    def add_commit(self):
        db.session.add(self)
        db.session.commit()

    def delete_commit(self):
        db.session.delete(self)
        db.session.commit()


class Slide(Base):
    __tablename__ = "slide"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    subject_id = Column(Integer, ForeignKey('subject.id'))
    subject = relationship("Subject", backref="slide")
    deleted = Column(Boolean, default=False)

    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship("User", backref="slide")
    order = Column(Integer)

    def convert_json(self, entire=False):
        return {"id": self.id, "name": self.name}


class SlideItem(Base):
    __tablename__ = "slide_item"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    slide_id = Column(Integer, ForeignKey('slide.id'))
    slide = relationship("Slide", backref="slide_item")
    slide_type_id = Column(Integer, ForeignKey('slide_type.id'))
    slide_type = relationship("SlideType", backref="slide_item")
    layout = Column(JSON)
    order = Column(Integer)

    def convert_json(self, entire=False):
        return {
            "id": self.id,
            "name": self.name,
            "layout": self.layout,
            "slide_type": self.slide_type.convert_json()
        }

    def add_commit(self):
        db.session.add(self)
        db.session.commit()

    def delete_commit(self):
        db.session.delete(self)
        db.session.commit()


class SlideExerciseType(Base):
    __tablename__ = "slide_exercise_type"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    slide_id = Column(Integer, ForeignKey('slide.id'))
    slide = relationship("Slide", backref="slide_exercise_type")

    def convert_json(self, entire=False):
        return {"id": self.id, "name": self.name}


class SlideExercise(Base):
    __tablename__ = "slide_exercise"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    exercise_type_id = Column(Integer, ForeignKey('slide_exercise_type.id'))
    exercise_type = relationship("SlideExerciseType", backref="slide_exercise")

    def convert_json(self, entire=False):
        return {"id": self.id, "name": self.name}


class SlideExerciseAnswer(Base):
    __tablename__ = "slide_exercise_answer"
    id = Column(Integer, primary_key=True)
    variant = Column(String)
    status = Column(String)
    exercise_id = Column(Integer, ForeignKey('slide_exercise.id'))
    exercise = relationship("SlideExercise", backref="slide_exercise_answer")

    def convert_json(self, entire=False):
        return {"id": self.id, "name": self.name}


class SlideBlock(Base):
    __tablename__ = "slide_block"
    id = Column(Integer, primary_key=True)
    heading = Column(String)
    subheading = Column(String)
    label = Column(String)
    slide_item_id = Column(Integer, ForeignKey('slide_item.id'))
    slide_item = relationship("SlideItem", backref="slide_block")
    slide_exercise_id = Column(Integer, ForeignKey('slide_exercise.id'))
    slide_exercise = relationship("SlideExercise", backref="slide_block")
    layout = Column(JSON)

    def convert_json(self, entire=False):
        return {
            "id": self.id,
            "heading": self.heading,
            "subheading": self.subheading,
            "label": self.label,
            "layout": self.layout,
            "slide_item": self.slide_item.convert_json(),
            "slide_exercise": self.slide_exercise.convert_json()
        }

    def add_commit(self):
        db.session.add(self)
        db.session.commit()

    def delete_commit(self):
        db.session.delete(self)
        db.session.commit()


class StudentSlide(Base):
    __tablename__ = "student_slide"
    id = Column(Integer, primary_key=True)
    slide_id = Column(Integer, ForeignKey('slide.id'))
    slide = relationship("Slide", backref="student_slide")
    student_id = Column(Integer, ForeignKey('student.id'))
    student = relationship("Student", backref="student_slide")
    date = Column(DateTime, default=datetime.now())

    def convert_json(self, entire=False):
        return {
            "id": self.id,
            "slide_block": self.slide_block.convert_json(),
            "student": self.student.convert_json()
        }


class StudentSlideBlock(Base):
    __tablename__ = "student_slide_block"
    id = Column(Integer, primary_key=True)
    slide_block_id = Column(Integer, ForeignKey('slide_block.id'))
    slide_block = relationship("SlideBlock", backref="student_slide_block")
    student_id = Column(Integer, ForeignKey('student.id'))
    student = relationship("Student", backref="student_slide_block")
    date = Column(DateTime, default=datetime.now())
    slide_id = Column(Integer, ForeignKey('slide.id'))
    slide = relationship("Slide", backref="student_slide_block")
    student_slide_id = Column(Integer, ForeignKey('student_slide.id'))
    student_slide = relationship("StudentSlide", backref="student_slide_block")
    true_answer = Column(Integer)
    percentage = Column(Integer)

    def convert_json(self, entire=False):
        return {
            "id": self.id,
            "slide_block": self.slide_block.convert_json(),
            "student": self.student.convert_json()
        }


class StudentSlideExercise(Base):
    __tablename__ = "student_slide_exercise"
    id = Column(Integer, primary_key=True)
    slide_exercise_id = Column(Integer, ForeignKey('slide_exercise.id'))
    slide_exercise = relationship("SlideExercise", backref="student_slide_exercise")
    student_id = Column(Integer, ForeignKey('student.id'))
    student = relationship("Student", backref="student_slide_exercise")
    date = Column(DateTime, default=datetime.now())
    slide_id = Column(Integer, ForeignKey('slide.id'))
    slide = relationship("Slide", backref="student_slide_exercise")
    student_slide_id = Column(Integer, ForeignKey('student_slide.id'))
    student_slide = relationship("StudentSlide", backref="student_slide_exercise")
    slide_block_id = Column(Integer, ForeignKey('slide_block.id'))
    slide_block = relationship("SlideBlock", backref="student_slide_exercise")
    true_answer = Column(Integer)
    percentage = Column(Integer)

    def convert_json(self, entire=False):
        return {
            "id": self.id,
        }
