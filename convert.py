from sqlalchemy import *
import pandas as pd
from os import listdir, remove
from os.path import isfile, join

DB_URI="postgres://sherry:sherry@localhost:5432/sherry"

def file_records_table(engine):
    metadata = MetaData()
    file_records = Table('file_records', metadata,
        Column('id', Integer, primary_key=True),
        Column('file_name', String, nullable=False),
        Column('create_date', DateTime, default=func.now())
    )
    metadata.create_all(engine)
    return file_records

def write_to_db(path):
    onlyfiles = [f for f in listdir(path) if isfile(join(path, f)) and f.endswith('.xlsx')]
    engine = create_engine(DB_URI)
    conn = engine.connect()
    
    for f in onlyfiles:
        conn.execute(file_records_table(engine).insert().values(file_name=f))
        excel_file = join(path, f)
        df = pd.read_excel(excel_file)
        df.to_sql('payment', engine, if_exists='append')
    conn.close()

def is_file_exists(filename):
    engine = create_engine(DB_URI)
    conn = engine.connect()
    table = file_records_table(engine)
    return conn.execute(table.select().where(table.c.file_name == filename)).fetchone() != None

def last_update():
    engine = create_engine(DB_URI)
    conn = engine.connect()
    table = file_records_table(engine)
    return conn.execute(table.select().order_by(table.c.create_date.desc())).fetchone()
    
def clean_files(path):
    onlyfiles = [f for f in listdir(path) if isfile(join(path, f)) and f.endswith('.xlsx')]
    for f in onlyfiles:
        print("Purging: %s" % f)
        remove(f)

def main():
    """Convert Excel file to DB

    Connecting to localhost/sherry, and save to 'payment' table
    """
    try:
        # conn = psycopg2.connect(DB_URI)
        write_to_db(conn)

    except Exception as e:
        print('An error occurred %s' % e)


if __name__ == '__main__':
    main()
