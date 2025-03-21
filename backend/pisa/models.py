import datetime

from backend.models.basic_model import db, Column, relationship, Integer, String, ForeignKey, Float, Boolean, JSON, \
    func, DateTime


class Pisa(db.Model):
    __tablename__ = "pisa"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    status = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    deleted = Column(Boolean, default=False)

    def add(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def convert_json(self, entire=False):
        return {"id": self.id, "name": self.name, "status": self.status, "created_at": self.created_at,
                "updated_at": self.updated_at, "deleted": self.deleted}


class PisaFileType(db.Model):
    __tablename__ = "pisa_file_type"
    id = Column(Integer, primary_key=True)
    url = Column(String)
    file_type = Column(String)
    block_texts = relationship('PisaBlockText', backref='file', order_by="PisaBlockText.index")
    options = relationship('PisaBlockQuestionOptions', backref='file', order_by="PisaBlockQuestionOptions.index")

    def add(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()


class PisaBlockText(db.Model):
    __tablename__ = "pisa_block_text"
    id = Column(Integer, primary_key=True)
    pisa_id = Column(Integer, ForeignKey('pisa.id'))
    file_id = Column(Integer, ForeignKey('pisa_file_type.id'))
    position = Column(String)
    index = Column(Integer)
    text = Column(String)
    type_block = Column(String)
    completed = Column(Boolean, default=False)
    words = Column(JSON)
    editorState = Column(JSON)
    typeVariants = Column(String)
    type_question = Column(String)
    video_url = Column(String)
    innerType = Column(String)

    def convert_json(self, entire=False):
        return {"id": self.id, "pisa_id": self.pisa_id, "file_id": self.file_id, "position": self.position,
                "index": self.index, "text": self.text, "type_block": self.type_block, "completed": self.completed,
                "words": self.words, "editorState": self.editorState, "typeVariants": self.typeVariants,
                "type_question": self.type_question, "video_url": self.video_url}

    def add(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()


class PisaBlockTextAnswer(db.Model):
    __tablename__ = "pisa_block_text_answer"
    id = Column(Integer, primary_key=True)
    pisa_block_id = Column(Integer, ForeignKey('pisa_block_text.id'))
    text = Column(String)
    statusWord = Column(String)
    type = Column(String)
    wrapped = Column(JSON)
    index = Column(Integer)

    def convert_json(self, entire=False):
        return {"id": self.id, "pisa_block_id": self.pisa_block_id, "text": self.text, "statusWord": self.statusWord,
                "type": self.type, "wrapped": self.wrapped, "index": self.index}

    def add(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()


class PisaBlockQuestionOptions(db.Model):
    __tablename__ = "pisa_block_question_options"
    id = Column(Integer, primary_key=True)
    pisa_block_id = Column(Integer, ForeignKey('pisa_block_text.id'))
    file_id = Column(Integer, ForeignKey('pisa_file_type.id'))
    index = Column(Integer)
    innerType = Column(String)
    isTrue = Column(Boolean, default=False)
    text = Column(String)
    answer = Column(String)

    def convert_json(self, entire=False):
        return {"id": self.id, "pisa_block_id": self.pisa_block_id, "file_id": self.file_id, "index": self.index,
                "image_url": self.file.url if self.file else None,
                "innerType": self.innerType, "isTrue": self.isTrue, "text": self.text, "answer": self.answer}

    def add(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()


class PisaStudent(db.Model):
    __tablename__ = "pisa_student"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    school = Column(String)
    grade = Column(String)
    address = Column(String)

    def add(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()


class PisaTest(db.Model):
    __tablename__ = "pisa_test"
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey('pisa_student.id'))
    pisa_id = Column(Integer, ForeignKey('pisa.id'))
    true_answers = Column(Integer)
    false_answers = Column(Integer)
    result = Column(Integer)
    test_date = Column(DateTime, default=datetime.datetime.utcnow)

    def add(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()


class PisaBlockOptionsStudent(db.Model):
    __tablename__ = "pisa_block_options_student"
    id = Column(Integer, primary_key=True)
    pisa_block_question_options_id = Column(Integer, ForeignKey('pisa_block_question_options.id'))
    pisa_test_id = Column(Integer, ForeignKey('pisa_test.id'))
    text = Column(String)
    answer = Column(String)

    def add(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()


class PisaBlockTextAnswerStudent(db.Model):
    __tablename__ = "pisa_block_text_answer_student"
    id = Column(Integer, primary_key=True)
    pisa_block_text_id = Column(Integer, ForeignKey('pisa_block_text.id'))
    pisa_test_id = Column(Integer, ForeignKey('pisa_test.id'))
    text = Column(String)
    statusWord = Column(String)
    type = Column(String)

    def add(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()
