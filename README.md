uvicorn app.main:app --reload

venv\Scripts\activate

python -c "from app.database import Database; db1 = Database(); db2 = Database(); print(f'Singleton check: {db1 is db2}')"

python -m uvicorn app.main:app --reload

Composite pattern example:
python -c "from app.models.file_system_component_examples import build_sample_tree; tree = build_sample_tree(); print(tree.display())"
