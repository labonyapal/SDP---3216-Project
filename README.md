uvicorn app.main:app --reload

venv\Scripts\activate

python -c "from app.database import Database; db1 = Database(); db2 = Database(); print(f'Singleton check: {db1 is db2}')"



python -m uvicorn app.main:app --reload
