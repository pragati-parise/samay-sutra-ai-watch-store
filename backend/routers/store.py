from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, or_
from sqlalchemy.orm import Session, joinedload
from ..auth import admin_user, create_token, current_user, hash_password, verify_password
from ..database import get_db
from ..models import Cart, CartItem, Category, Order, OrderItem, Product, Review, User, WishlistItem
from ..schemas import CartIn, DescriptionUpdateIn, LoginIn, QuantityIn, RegisterIn, ReviewIn
router = APIRouter(prefix="/api", tags=["store"])
def product_data(product):
    rating = sum(r.rating for r in product.reviews) / len(product.reviews) if product.reviews else None
    return {"id":product.id,"name":product.name,"brand":product.brand,"category":product.category.name,"price":float(product.price),"image":product.image,"description":product.description,"stock":product.stock,"strap":product.strap,"color":product.color,"rating":round(rating,1) if rating else None,"reviewCount":len(product.reviews)}
def cart_data(user, db):
    cart = user.cart
    if not cart: return {"items":[],"subtotal":0,"itemCount":0}
    items=[]; subtotal=0
    for item in cart.items:
        p=item.product; line=float(p.price)*item.quantity; subtotal+=line
        items.append({"id":p.id,"name":p.name,"brand":p.brand,"price":float(p.price),"image":p.image,"quantity":item.quantity,"lineTotal":round(line,2)})
    return {"items":items,"subtotal":round(subtotal,2),"itemCount":sum(i["quantity"] for i in items)}
@router.post("/auth/register", status_code=201)
@router.post("/register", status_code=201)
def register(data: RegisterIn, db: Session = Depends(get_db)):
    if db.query(User).filter_by(email=data.email.lower()).first(): raise HTTPException(409,"An account with that email already exists.")
    user=User(name=data.name.strip(),email=data.email.lower(),password_hash=hash_password(data.password),address=data.address.strip(),contact_number=data.contact_number.strip())
    db.add(user); db.commit(); db.refresh(user)
    return {"message":"Account created successfully.","access_token":create_token(user),"token_type":"bearer","user":{"id":user.id,"name":user.name,"email":user.email,"isAdmin":user.is_admin}}
@router.post("/auth/login")
@router.post("/login")
def login(data: LoginIn, db: Session = Depends(get_db)):
    user=db.query(User).filter_by(email=data.email.lower()).first()
    if not user or not verify_password(data.password,user.password_hash): raise HTTPException(401,"Invalid email or password.")
    return {"message":"Logged in successfully.","access_token":create_token(user),"token_type":"bearer","user":{"id":user.id,"name":user.name,"email":user.email,"isAdmin":user.is_admin}}
@router.post("/auth/logout")
@router.post("/logout")
def logout(): return {"message":"Logged out successfully. Remove the JWT from the client."}
@router.get("/auth/me")
@router.get("/session")
def me(user: User = Depends(current_user)): return {"authenticated":True,"user":{"id":user.id,"name":user.name,"email":user.email,"isAdmin":user.is_admin}}
@router.get("/products")
def products(search:str="",category:str="",brand:str="",sort:str="",db:Session=Depends(get_db)):
    q=db.query(Product).options(joinedload(Product.category),joinedload(Product.reviews))
    if search.strip():
        # Search should match category names too. The aliases make natural searches
        # such as "Sports" find the catalogue's "Sport" category.
        search_text = search.strip().lower()
        aliases = {"sports": "sport", "smartwatches": "smart", "womens": "women", "women's": "women"}
        search_terms = {search_text, aliases.get(search_text, search_text)}
        conditions = []
        for value in search_terms:
            term = f"%{value}%"
            conditions.extend((Product.name.ilike(term), Product.brand.ilike(term), Product.description.ilike(term), Category.name.ilike(term)))
        q=q.join(Category).filter(or_(*conditions))
    if category: q=q.join(Category).filter(Category.name.ilike(category))
    if brand: q=q.filter(Product.brand.ilike(brand))
    q=q.order_by(Product.price.asc() if sort=="price_asc" else Product.price.desc() if sort=="price_desc" else Product.id.asc())
    all_products=q.all()
    return {"products":[product_data(p) for p in all_products],"categories":[x.name for x in db.query(Category).order_by(Category.name)],"brands":[x[0] for x in db.query(Product.brand).distinct().order_by(Product.brand)]}
@router.get("/products/{product_id}")
def product(product_id:int,db:Session=Depends(get_db)):
    p=db.query(Product).options(joinedload(Product.category),joinedload(Product.reviews)).get(product_id)
    if not p: raise HTTPException(404,"Product not found.")
    return product_data(p)
@router.patch("/admin/products/{product_id}/description")
def update_description(product_id:int,data:DescriptionUpdateIn,_=Depends(admin_user),db:Session=Depends(get_db)):
    p=db.get(Product,product_id)
    if not p: raise HTTPException(404,"Product not found.")
    p.description=data.description.strip(); db.commit()
    return {"message":"Description saved.","product":product_data(p)}
@router.get("/categories")
def categories(db:Session=Depends(get_db)): return [{"id":c.id,"name":c.name} for c in db.query(Category).order_by(Category.name)]
@router.get("/cart")
def get_cart(user:User=Depends(current_user),db:Session=Depends(get_db)): return cart_data(user,db)
@router.post("/cart")
def add_cart(data:CartIn,user:User=Depends(current_user),db:Session=Depends(get_db)):
    product=db.get(Product,data.productId)
    if not product: raise HTTPException(404,"Product not found.")
    if product.stock < 1: raise HTTPException(400,"This watch is out of stock.")
    if not user.cart: user.cart=Cart(user_id=user.id); db.add(user.cart); db.flush()
    item=next((x for x in user.cart.items if x.product_id==product.id),None)
    if item: item.quantity=min(20,item.quantity+data.quantity)
    else: db.add(CartItem(cart_id=user.cart.id,product_id=product.id,quantity=data.quantity))
    db.commit(); db.refresh(user); return {"message":"Item added to cart.",**cart_data(user,db)}
@router.patch("/cart/{product_id}")
def update_cart(product_id:int,data:QuantityIn,user:User=Depends(current_user),db:Session=Depends(get_db)):
    item=next((x for x in (user.cart.items if user.cart else []) if x.product_id==product_id),None)
    if not item: raise HTTPException(404,"Item is not in your cart.")
    if data.quantity==0: db.delete(item)
    else: item.quantity=data.quantity
    db.commit(); db.refresh(user); return {"message":"Cart updated.",**cart_data(user,db)}
@router.delete("/cart/{product_id}")
def remove_cart(product_id:int,user:User=Depends(current_user),db:Session=Depends(get_db)):
    item=next((x for x in (user.cart.items if user.cart else []) if x.product_id==product_id),None)
    if item: db.delete(item); db.commit(); db.refresh(user)
    return {"message":"Item removed from cart.",**cart_data(user,db)}
@router.post("/orders")
@router.post("/checkout")
def checkout(user:User=Depends(current_user),db:Session=Depends(get_db)):
    payload=cart_data(user,db)
    if not payload["items"]: raise HTTPException(400,"Your cart is empty.")
    order=Order(user_id=user.id,total=payload["subtotal"],status="Placed"); db.add(order); db.flush()
    for item in user.cart.items:
        if item.product.stock < item.quantity: raise HTTPException(400,f"Only {item.product.stock} left for {item.product.name}.")
        item.product.stock-=item.quantity; db.add(OrderItem(order_id=order.id,product_id=item.product_id,quantity=item.quantity,price=item.product.price)); db.delete(item)
    db.commit(); return {"message":"Order placed successfully.","orderId":order.id,"status":"Order placed"}
@router.get("/orders")
def orders(user:User=Depends(current_user),db:Session=Depends(get_db)):
    rows=db.query(Order).options(joinedload(Order.items).joinedload(OrderItem.product)).filter_by(user_id=user.id).order_by(Order.created_at.desc()).all()
    return {"orders":[{"id":o.id,"total":float(o.total),"status":o.status,"createdAt":o.created_at.isoformat(),"items":[{"name":x.product.name,"brand":x.product.brand,"image":x.product.image,"quantity":x.quantity,"price":float(x.price)} for x in o.items]} for o in rows]}
@router.get("/wishlist")
def wishlist(user:User=Depends(current_user),db:Session=Depends(get_db)): return {"products":[product_data(x.product) for x in db.query(WishlistItem).options(joinedload(WishlistItem.product).joinedload(Product.category),joinedload(WishlistItem.product).joinedload(Product.reviews)).filter_by(user_id=user.id)]}
@router.post("/wishlist/{product_id}",status_code=201)
def add_wishlist(product_id:int,user:User=Depends(current_user),db:Session=Depends(get_db)):
    if not db.get(Product,product_id): raise HTTPException(404,"Product not found.")
    if not db.query(WishlistItem).filter_by(user_id=user.id,product_id=product_id).first(): db.add(WishlistItem(user_id=user.id,product_id=product_id)); db.commit()
    return {"message":"Added to wishlist."}
@router.delete("/wishlist/{product_id}")
def remove_wishlist(product_id:int,user:User=Depends(current_user),db:Session=Depends(get_db)):
    row=db.query(WishlistItem).filter_by(user_id=user.id,product_id=product_id).first()
    if row: db.delete(row); db.commit()
    return {"message":"Removed from wishlist."}
@router.get("/products/{product_id}/reviews")
def reviews(product_id:int,db:Session=Depends(get_db)):
    return {"reviews":[{"id":r.id,"rating":r.rating,"comment":r.comment,"createdAt":r.created_at.isoformat()} for r in db.query(Review).filter_by(product_id=product_id).order_by(Review.created_at.desc())]}
@router.post("/products/{product_id}/reviews",status_code=201)
def review(product_id:int,data:ReviewIn,user:User=Depends(current_user),db:Session=Depends(get_db)):
    if not db.get(Product,product_id): raise HTTPException(404,"Product not found.")
    existing=db.query(Review).filter_by(product_id=product_id,user_id=user.id).first()
    if existing: existing.rating=data.rating; existing.comment=data.comment.strip()
    else: db.add(Review(product_id=product_id,user_id=user.id,rating=data.rating,comment=data.comment.strip()))
    db.commit(); return {"message":"Review saved."}
