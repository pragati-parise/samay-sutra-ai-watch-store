"""One-time, explicit migration of legacy watch_store.db records into PostgreSQL.
Run only after setting DATABASE_URL and before first production use.
"""
import sqlite3
from datetime import datetime
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from backend.database import Base, SessionLocal, engine
from backend.models import Category, Order, OrderItem, Product, User
from backend.seed import seed_products

legacy = Path(__file__).resolve().parent.parent / "watch_store.db"
if not legacy.exists(): raise SystemExit("Legacy SQLite file was not found.")
Base.metadata.create_all(engine)
source = sqlite3.connect(legacy); source.row_factory = sqlite3.Row
db = SessionLocal()
try:
    categories = {}; product_map = {}; user_map = {}
    for row in source.execute("SELECT * FROM products"):
        category = categories.get(row["category"])
        if not category:
            category = db.query(Category).filter_by(name=row["category"]).first() or Category(name=row["category"])
            db.add(category); db.flush(); categories[row["category"]] = category
        target = db.query(Product).filter_by(name=row["name"], brand=row["brand"]).first()
        if not target:
            target=Product(name=row["name"],brand=row["brand"],category_id=category.id,price=row["price"],image=row["image"],description=row["description"]); db.add(target); db.flush()
        product_map[row["id"]]=target.id
    for row in source.execute("SELECT * FROM users"):
        target=db.query(User).filter_by(email=row["email"]).first()
        if not target:
            target=User(name=row["name"],email=row["email"],password_hash=row["password_hash"],address=row["address"] or "",contact_number=row["contact_number"] or ""); db.add(target); db.flush()
        user_map[row["id"]]=target.id
    for row in source.execute("SELECT * FROM orders"):
        if row["user_id"] not in user_map: continue
        created = datetime.fromisoformat(row["created_at"]) if row["created_at"] else datetime.utcnow()
        target=Order(user_id=user_map[row["user_id"]],total=row["total"],status=row["status"],created_at=created)
        db.add(target); db.flush()
        for item in source.execute("SELECT * FROM order_items WHERE order_id=?",(row["id"],)):
            if item["product_id"] in product_map: db.add(OrderItem(order_id=target.id,product_id=product_map[item["product_id"]],quantity=item["quantity"],price=item["price"]))
    db.commit()
    print("Legacy products, users, orders, and order items migrated to PostgreSQL.")
finally:
    source.close(); db.close()
