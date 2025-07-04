from backend.models.basic_model import db, Column, String, Integer


class ClassTest(db.Model):
    __tablename__ = "class_test"
    id = Column(Integer, primary_key=True)
    number = Column()
