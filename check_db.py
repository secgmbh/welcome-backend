import os
from sqlalchemy import create_engine, text

# Get database URL from Render
db_url = os.environ.get('DATABASE_URL', 'postgresql://npuqdy_1:jts0@jts0.your-database.de:5432/npuqdy_db1')
print(f'Connecting to: {db_url[:30]}...')

engine = create_engine(db_url)
with engine.connect() as conn:
    # Check existing columns
    result = conn.execute(text("""
        SELECT column_name FROM information_schema.columns 
        WHERE table_name = 'users'
    """))
    existing = [row[0] for row in result.fetchall()]
    print(f'Existing columns: {existing}')
