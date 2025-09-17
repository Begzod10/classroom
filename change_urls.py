from sqlalchemy import create_engine, Table, MetaData, update, func
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql://postgres:or9T#u-x5PZo--@localhost:5432/classroom"

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

metadata = MetaData()
metadata.reflect(bind=engine)

file_table = metadata.tables['file']

stmt = (
    update(file_table)
    .where(file_table.c.url.like('static/%'))  # faqat static bilan boshlanadiganlar
    .values(url=func.replace(file_table.c.url, 'static/', 'staticfiles/'))
)

# Execute
with engine.begin() as conn:
    result = conn.execute(stmt)
    print(f"{result.rowcount} qator yangilandi")

session.close()
