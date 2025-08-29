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
    level_id = Column(Integer, ForeignKey('subject_level.id'))
    level = relationship("SubjectLevel", backref="slide")
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship("User", backref="slide")
    order = Column(Integer)

    def convert_json(self, entire=False):
        return {
            "id": self.id,
            "name": self.name,
            "order": self.order,
            "level": {
                "id": self.level.id if self.level else None,
                "name": self.level.name if self.level else None
            },
            "subject": {
                "id": self.subject.id if self.subject else None,
                "name": self.subject.name if self.subject else None
            },
            "user": {
                "id": self.user.id,
                "name": self.user.name
            },
            "system_name": self.level.system_name if self.level else None
        }


class SlideItem(Base):
    __tablename__ = "slide_item"
    id = Column(Integer, primary_key=True)
    heading = Column(String)
    subheading = Column(String)
    label = Column(String)
    image_type = Column(String)
    video = Column(String)
    file_id = Column(Integer, ForeignKey('file.id'))
    file = relationship("File", backref="slide_item")
    slide_id = Column(Integer, ForeignKey('slide.id'))
    slide = relationship("Slide", backref="slide_item")
    slide_type = Column(String)
    slide_exercise_id = Column(Integer, ForeignKey('slide_exercise.id'))
    slide_exercise = relationship("SlideExercise", backref="slide_item")
    design = Column(JSON)
    order = Column(Integer)
    extra_design = Column(JSON)

    def convert_json(self, entire=False):
        """
        Convert SlideItem to JSON representation.

        :param entire: bool - if True, include all nested details (like exercise, extraDesign)
        :return: dict
        """
        data = {
            "id": self.id,
            "slide_id": self.slide_id,
            "slide_type": self.slide_type,
            "heading": getattr(self, "heading", ""),
            "subheading": getattr(self, "subheading", ""),
            "image": getattr(self, "image", ""),
            "video": getattr(self, "video", ""),
            "imageType": getattr(self, "image_type", "center"),
            "label": getattr(self, "label", ""),
            "order": getattr(self, "order", 0),
            "design": getattr(self, "design", {})
        }

        if entire:
            # Optionally include any extra relationships or nested data here
            data["created_at"] = getattr(self, "created_at", None)
            data["updated_at"] = getattr(self, "updated_at", None)

        return data

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


class SlideBlock(Base):
    __tablename__ = "slide_block"
    id = Column(Integer, primary_key=True)

    slide_item_id = Column(Integer, ForeignKey('slide_item.id'))
    slide_item = relationship("SlideItem", backref="slide_block")

    layout = Column(JSON)


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
