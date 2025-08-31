from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List, Dict, Any
import asyncio

from app.database import connect_to_mongo, close_mongo_connection, get_database
from models.user import UserCreate, UserResponse
from models.product import ProductCreate, ProductResponse
from models.purchase import PurchaseCreate, PurchaseResponse
from services.recommendation_service import RecommendationService
from services.persona_service import PersonaService
from utils.data_generator import DataGenerator

app = FastAPI(title="Generative Recommendation Engine", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database connection
@app.on_event("startup")
async def startup_db_client():
    await connect_to_mongo()

@app.on_event("shutdown")
async def shutdown_db_client():
    await close_mongo_connection()

# Dependency to get database
async def get_db() -> AsyncIOMotorDatabase:
    return get_database()

# Initialize services
recommendation_service = None
persona_service = None

@app.on_event("startup")
async def initialize_services():
    global recommendation_service, persona_service
    db = get_database()
    recommendation_service = RecommendationService(db)
    persona_service = PersonaService(db)

# Health check
@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "Recommendation Engine is running"}

# User endpoints
@app.post("/users", response_model=UserResponse)
async def create_user(user: UserCreate, db: AsyncIOMotorDatabase = Depends(get_db)):
    """Create a new user"""
    try:
        user_dict = user.dict()
        user_dict["created_at"] = user_dict.get("created_at")
        user_dict["total_purchases"] = 0
        user_dict["total_spent"] = 0.0
        user_dict["favorite_categories"] = []
        
        result = await db.users.insert_one(user_dict)
        user_dict["_id"] = result.inserted_id
        
        return UserResponse(**user_dict)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: str, db: AsyncIOMotorDatabase = Depends(get_db)):
    """Get user by ID"""
    from bson import ObjectId
    try:
        user = await db.users.find_one({"_id": ObjectId(user_id)})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return UserResponse(**user)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/users", response_model=List[UserResponse])
async def get_users(skip: int = 0, limit: int = 100, db: AsyncIOMotorDatabase = Depends(get_db)):
    """Get all users with pagination"""
    try:
        users = await db.users.find().skip(skip).limit(limit).to_list(length=limit)
        return [UserResponse(**user) for user in users]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Product endpoints
@app.post("/products", response_model=ProductResponse)
async def create_product(product: ProductCreate, db: AsyncIOMotorDatabase = Depends(get_db)):
    """Create a new product"""
    try:
        product_dict = product.dict()
        product_dict["created_at"] = product_dict.get("created_at")
        product_dict["updated_at"] = product_dict.get("updated_at")
        product_dict["total_sold"] = 0
        product_dict["revenue_generated"] = 0.0
        
        result = await db.products.insert_one(product_dict)
        product_dict["_id"] = result.inserted_id
        
        return ProductResponse(**product_dict)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/products/{product_id}", response_model=ProductResponse)
async def get_product(product_id: str, db: AsyncIOMotorDatabase = Depends(get_db)):
    """Get product by ID"""
    from bson import ObjectId
    try:
        product = await db.products.find_one({"_id": ObjectId(product_id)})
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        return ProductResponse(**product)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/products", response_model=List[ProductResponse])
async def get_products(
    skip: int = 0, 
    limit: int = 100, 
    category: str = None,
    min_price: float = None,
    max_price: float = None,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get products with filters"""
    try:
        query = {}
        if category:
            query["category"] = category
        if min_price is not None or max_price is not None:
            query["price"] = {}
            if min_price is not None:
                query["price"]["$gte"] = min_price
            if max_price is not None:
                query["price"]["$lte"] = max_price
        
        products = await db.products.find(query).skip(skip).limit(limit).to_list(length=limit)
        return [ProductResponse(**product) for product in products]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Purchase endpoints
@app.post("/purchases", response_model=PurchaseResponse)
async def create_purchase(purchase: PurchaseCreate, db: AsyncIOMotorDatabase = Depends(get_db)):
    """Create a new purchase"""
    try:
        purchase_dict = purchase.dict()
        purchase_dict["created_at"] = purchase_dict.get("created_at")
        
        result = await db.purchases.insert_one(purchase_dict)
        purchase_dict["_id"] = result.inserted_id
        
        # Update user statistics
        from bson import ObjectId
        await db.users.update_one(
            {"_id": ObjectId(purchase.user_id)},
            {
                "$inc": {
                    "total_purchases": 1,
                    "total_spent": purchase.final_amount
                }
            }
        )
        
        # Update product statistics
        for item in purchase.items:
            await db.products.update_one(
                {"_id": ObjectId(item.product_id)},
                {
                    "$inc": {
                        "total_sold": item.quantity,
                        "revenue_generated": item.total_price
                    }
                }
            )
        
        return PurchaseResponse(**purchase_dict)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/purchases/{user_id}", response_model=List[PurchaseResponse])
async def get_user_purchases(user_id: str, db: AsyncIOMotorDatabase = Depends(get_db)):
    """Get purchase history for a user"""
    from bson import ObjectId
    try:
        purchases = await db.purchases.find({"user_id": ObjectId(user_id)}).to_list(length=100)
        return [PurchaseResponse(**purchase) for purchase in purchases]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Recommendation endpoints
@app.get("/recommendations/{user_id}")
async def get_recommendations(user_id: str, limit: int = 10):
    """Get personalized recommendations for a user"""
    try:
        if not recommendation_service:
            raise HTTPException(status_code=500, detail="Recommendation service not initialized")
        
        recommendations = await recommendation_service.get_recommendations_for_user(user_id, limit)
        return recommendations
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/recommendations/new-user")
async def get_new_user_recommendations(limit: int = 10, db: AsyncIOMotorDatabase = Depends(get_db)):
    """Get recommendations for new users"""
    try:
        # Get random popular products
        products = await db.products.find({"is_featured": True}).limit(limit).to_list(length=limit)
        return {
            "recommendations": [{"product_id": str(p["_id"]), "product": p, "score": 1.0} for p in products],
            "recommendation_type": "new_user",
            "generated_at": datetime.utcnow()
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Persona and simulation endpoints
@app.get("/persona/shopping-session/{user_id}")
async def generate_shopping_session(user_id: str, duration_minutes: int = 30):
    """Generate a realistic shopping session for a user"""
    try:
        if not persona_service:
            raise HTTPException(status_code=500, detail="Persona service not initialized")
        
        session = await persona_service.generate_shopping_session(user_id, duration_minutes)
        return session
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/persona/analyze/{user_id}")
async def analyze_user_persona(user_id: str, db: AsyncIOMotorDatabase = Depends(get_db)):
    """Analyze user behavior and persona"""
    try:
        from bson import ObjectId
        
        # Get user data
        user = await db.users.find_one({"_id": ObjectId(user_id)})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get purchase history
        purchases = await db.purchases.find({"user_id": ObjectId(user_id)}).to_list(length=100)
        
        # Analyze spending patterns
        total_spent = sum(p["final_amount"] for p in purchases)
        avg_purchase_value = total_spent / len(purchases) if purchases else 0
        
        # Analyze category preferences
        category_counts = {}
        for purchase in purchases:
            for item in purchase["items"]:
                product = await db.products.find_one({"_id": ObjectId(item["product_id"])})
                if product:
                    category = product["category"]
                    category_counts[category] = category_counts.get(category, 0) + 1
        
        favorite_categories = sorted(category_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        
        # Determine persona type based on behavior
        persona_type = user.get("persona_type", "practical_buyer")
        
        analysis = {
            "user_id": user_id,
            "persona_type": persona_type,
            "total_purchases": len(purchases),
            "total_spent": total_spent,
            "avg_purchase_value": avg_purchase_value,
            "favorite_categories": [cat for cat, count in favorite_categories],
            "category_preferences": dict(favorite_categories),
            "shopping_frequency": len(purchases) / max(1, (datetime.utcnow() - user["created_at"]).days / 30),
            "analysis_date": datetime.utcnow()
        }
        
        return analysis
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Data generation endpoints
@app.post("/generate-data")
async def generate_sample_data(db: AsyncIOMotorDatabase = Depends(get_db)):
    """Generate sample data for the recommendation engine"""
    try:
        generator = DataGenerator()
        
        # Generate users
        users = []
        for _ in range(1000):
            user_data = generator.generate_user()
            result = await db.users.insert_one(user_data)
            user_data["_id"] = result.inserted_id
            users.append(user_data)
        
        # Generate products
        products = []
        for _ in range(1000):
            product_data = generator.generate_product()
            result = await db.products.insert_one(product_data)
            product_data["_id"] = result.inserted_id
            products.append(product_data)
        
        # Generate purchases
        purchases = []
        for user in users:
            num_purchases = random.randint(0, 10)
            for _ in range(num_purchases):
                purchase_data = generator.generate_purchase(str(user["_id"]), products)
                result = await db.purchases.insert_one(purchase_data)
                purchase_data["_id"] = result.inserted_id
                purchases.append(purchase_data)
        
        return {
            "message": "Sample data generated successfully",
            "users_created": len(users),
            "products_created": len(products),
            "purchases_created": len(purchases)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
