from fastapi import FastAPI, Depends, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import models, schemas
from database import SessionLocal, engine, Base

# إنشاء الجداول في قاعدة البيانات
Base.metadata.create_all(bind=engine)

app = FastAPI()

# ربط مجلد static لملفات CSS
app.mount("/static", StaticFiles(directory="static"), name="static")
# إعداد Jinja2 لعرض القوالب
templates = Jinja2Templates(directory="templates")

# دالة لإنشاء جلسة اتصال بالقاعدة
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create: إضافة منتج جديد
@app.post("/products", response_model=schemas.ProductOut)
def create_product(product: schemas.ProductCreate, db: Session = Depends(get_db)):
    db_product = models.Product(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

# Read: استرجاع كل المنتجات (JSON)
@app.get("/products", response_model=list[schemas.ProductOut])
def read_products(db: Session = Depends(get_db)):
    return db.query(models.Product).all()

# Read (UI): عرض صفحة HTML بالقائمة
@app.get("/", response_class=templates.TemplateResponse)
def view_products(request: Request, db: Session = Depends(get_db)):
    products = db.query(models.Product).all()
    return templates.TemplateResponse("products.html", {"request": request, "products": products})

# Update: تعديل منتج موجود
@app.put("/products/{product_id}", response_model=schemas.ProductOut)
def update_product(product_id: int, updated: schemas.ProductCreate, db: Session = Depends(get_db)):
    prod = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not prod:
        raise HTTPException(status_code=404, detail="Product not found")
    prod.name        = updated.name
    prod.price       = updated.price
    prod.description = updated.description
    db.commit()
    db.refresh(prod)
    return prod

# Delete: حذف منتج
@app.delete("/products/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db)):
    prod = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not prod:
        raise HTTPException(status_code=404, detail="Product not found")
    db.delete(prod)
    db.commit()
    return {"message": "Product deleted"}
