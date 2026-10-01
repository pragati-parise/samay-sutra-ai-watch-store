from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session, joinedload
from ..auth import admin_user
from ..database import get_db
from ..models import Product
from ..schemas import AiAskIn, AiRecommendIn, DescriptionIn
from ..services.gemini import ask_gemini
router=APIRouter(prefix="/api/ai",tags=["AI"])
def catalogue(db):
    products=db.query(Product).options(joinedload(Product.category)).all()
    return "\n".join(f"ID {p.id}: {p.name} | {p.brand} | {p.category.name} | ₹{float(p.price):.0f} | {p.strap} strap | {p.color} | {p.description}" for p in products)
def store_prompt(request, products):
    return f"""You are the concise, helpful shopping assistant for a premium watch store.

Use only the catalogue below. Never invent a product, price, stock, rating, or specification. Mention product names exactly as shown. If no item fits, say so plainly.

RESPONSE RULES:
- Answer the customer's actual question first; do not list the full catalogue.
- For a broad question such as "best for a gift", "best for office", or "what should I buy", select ONE best matching watch and give its price plus one short reason based only on the catalogue.
- You may include at most TWO alternatives, each with a short reason.
- If a budget is given, do not recommend products over that budget as the best match. You may mention one over-budget alternative only when clearly labelled "Over budget".
- Use short, readable paragraphs. Keep the entire response under 90 words.
- Do not use Markdown headings, bullet symbols, or asterisks.

CATALOGUE:
{products}

CUSTOMER REQUEST: {request}"""
@router.post("/recommendations")
def recommend(data:AiRecommendIn,db:Session=Depends(get_db)):
    preferences=", ".join(x for x in [f"budget ₹{data.budget:.0f}" if data.budget else "",data.watch_type,data.style,data.occasion,data.strap,data.color] if x) or "general recommendation"
    return {"answer":ask_gemini(store_prompt(f"Recommend up to three watches for: {preferences}.",catalogue(db)))}
@router.post("/assistant")
def assistant(data:AiAskIn,db:Session=Depends(get_db)):
    return {"answer":ask_gemini(store_prompt(data.question.strip(),catalogue(db)))}
@router.post("/product-description")
def generate_description(data:DescriptionIn,_=Depends(admin_user)):
    prompt=f"Write one concise, polished product description (40-60 words) for this watch only. Do not claim specifications not supplied: {data.name}, brand {data.brand}, category {data.category}, {data.strap} strap, {data.color} color."
    return {"description":ask_gemini(prompt)}
