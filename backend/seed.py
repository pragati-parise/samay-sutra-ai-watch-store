from sqlalchemy.orm import Session
from .models import Category, Product
PRODUCT_SEED = [("Rajwadi Chronograph","Titan","Luxury",18999,"/static/images/rajwadi-chronograph.png","A polished steel chronograph built for refined festive and formal looks.","Steel","Silver"),("Noor Rose","Fastrack","Women",7999,"/static/images/noor-rose.png","Rose-gold detailing and a slim dial for an elegant everyday Indian style.","Mesh","Rose Gold"),("Goa Diver","Sonata","Sport",11999,"/static/images/goa-diver.png","A rugged diver-inspired watch with luminous markers and bold weekend energy.","Rubber","Blue"),("Kohinoor Automatic","Titan","Luxury",19999,"/static/images/kohinoor-automatic.png","Automatic movement, matte black dial, and a refined leather strap for premium dressing.","Leather","Black"),("Monsoon Field","Maxima","Casual",3999,"/static/images/monsoon-field.png","A reliable field watch with crisp numerals and a durable strap for daily wear.","Canvas","Olive"),("Metro Digital","boAt","Smart",6499,"/static/images/metro-digital.png","A hybrid digital watch for fitness tracking and clean urban styling.","Silicone","Black"),("Darbar Classic","HMT","Formal",9499,"/static/images/darbar-classic.png","Minimal dial design with timeless proportions for office-ready wear.","Leather","Brown"),("Delhi Edge Carbon","Fire-Boltt","Sport",13999,"/static/images/delhi-edge-carbon.png","Carbon-texture dial and performance strap for a fast, athletic feel.","Silicone","Black")]
def seed_products(db: Session):
    if db.query(Product).count(): return
    cats = {}
    for name, brand, category, price, image, description, strap, color in PRODUCT_SEED:
        cat = cats.get(category)
        if not cat:
            cat = Category(name=category); db.add(cat); db.flush(); cats[category] = cat
        db.add(Product(name=name, brand=brand, category_id=cat.id, price=price, image=image, description=description, strap=strap, color=color))
    db.commit()
