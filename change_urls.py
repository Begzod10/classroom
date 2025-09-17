from sqlalchemy import create_engine, MetaData, update, func
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql://postgres:or9T#u-x5PZo--@localhost:5432/classroom"

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

metadata = MetaData()
metadata.reflect(bind=engine)

tables_to_update = ["file", "pisafiletype"]

for table_name in tables_to_update:
    table = metadata.tables[table_name]

    stmt = (update(table).where(table.c.url.like('static/%')).values(
        url=func.replace(table.c.url, 'static/', 'staticfiles/')))

    with engine.begin() as conn:
        result = conn.execute(stmt)
        print(f"{table_name} jadvalida {result.rowcount} qator yangilandi")

session.close()
