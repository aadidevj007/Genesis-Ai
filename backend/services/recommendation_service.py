import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
from typing import List, Dict, Any, Optional
import random
from datetime import datetime, timedelta
from bson import ObjectId

class RecommendationService:
    def __init__(self, db):
        self.db = db
        self.vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        
    async def get_recommendations_for_user(self, user_id: str, limit: int = 10) -> Dict[str, Any]:
        """Get personalized recommendations for a user"""
        try:
            # Get user data
            user = await self.db.users.find_one({"_id": ObjectId(user_id)})
            if not user:
                return await self._get_random_recommendations(limit)
            
            # Get user's purchase history
            purchases = await self.db.purchases.find({"user_id": ObjectId(user_id)}).to_list(length=100)
            
            if not purchases:
                # New user - get recommendations based on persona
                return await self._get_persona_based_recommendations(user, limit)
            
            # Get collaborative filtering recommendations
            collaborative_recs = await self._get_collaborative_recommendations(user_id, limit)
            
            # Get content-based recommendations
            content_recs = await self._get_content_based_recommendations(user, purchases, limit)
            
            # Get trending products
            trending_recs = await self._get_trending_recommendations(limit // 2)
            
            # Combine and rank recommendations
            all_recommendations = self._combine_recommendations(
                collaborative_recs, content_recs, trending_recs, user
            )
            
            # Get offers for recommended products
            offers = await self._get_offers_for_products([rec["product_id"] for rec in all_recommendations[:limit]])
            
            return {
                "user_id": user_id,
                "recommendations": all_recommendations[:limit],
                "offers": offers,
                "recommendation_type": "personalized" if purchases else "persona_based",
                "generated_at": datetime.utcnow()
            }
            
        except Exception as e:
            print(f"Error in get_recommendations_for_user: {e}")
            return await self._get_random_recommendations(limit)

    async def _get_collaborative_recommendations(self, user_id: str, limit: int) -> List[Dict]:
        """Get recommendations based on similar users' behavior"""
        try:
            # Find users with similar purchase patterns
            user_purchases = await self.db.purchases.find({"user_id": ObjectId(user_id)}).to_list(length=50)
            
            if not user_purchases:
                return []
            
            # Get products purchased by current user
            user_product_ids = set()
            for purchase in user_purchases:
                for item in purchase["items"]:
                    user_product_ids.add(str(item["product_id"]))
            
            # Find users who bought similar products
            similar_users = await self.db.purchases.aggregate([
                {"$match": {"user_id": {"$ne": ObjectId(user_id)}}},
                {"$unwind": "$items"},
                {"$match": {"items.product_id": {"$in": [ObjectId(pid) for pid in user_product_ids]}}},
                {"$group": {"_id": "$user_id", "common_products": {"$addToSet": "$items.product_id"}}},
                {"$match": {"common_products": {"$size": {"$gte": 2}}}},
                {"$limit": 20}
            ]).to_list(length=20)
            
            # Get products bought by similar users but not by current user
            similar_user_ids = [user["_id"] for user in similar_users]
            recommended_products = await self.db.purchases.aggregate([
                {"$match": {"user_id": {"$in": similar_user_ids}}},
                {"$unwind": "$items"},
                {"$match": {"items.product_id": {"$nin": [ObjectId(pid) for pid in user_product_ids]}}},
                {"$group": {"_id": "$items.product_id", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}},
                {"$limit": limit}
            ]).to_list(length=limit)
            
            # Get product details
            product_ids = [rec["_id"] for rec in recommended_products]
            products = await self.db.products.find({"_id": {"$in": product_ids}}).to_list(length=limit)
            
            return [{"product_id": str(p["_id"]), "product": p, "score": rec["count"]} 
                   for p, rec in zip(products, recommended_products)]
            
        except Exception as e:
            print(f"Error in collaborative recommendations: {e}")
            return []

    async def _get_content_based_recommendations(self, user: Dict, purchases: List[Dict], limit: int) -> List[Dict]:
        """Get recommendations based on product content and user preferences"""
        try:
            # Get user's favorite categories and interests
            favorite_categories = user.get("favorite_categories", [])
            interests = user.get("interests", [])
            persona_type = user.get("persona_type", "")
            
            # Build query based on user preferences
            query = {}
            
            if favorite_categories:
                query["category"] = {"$in": favorite_categories}
            
            # Get products matching user preferences
            products = await self.db.products.find(query).to_list(length=100)
            
            if not products:
                return []
            
            # Score products based on user preferences
            scored_products = []
            for product in products:
                score = 0
                
                # Category match
                if product["category"] in favorite_categories:
                    score += 3
                
                # Interest match (using tags)
                for interest in interests:
                    if interest.lower() in [tag.lower() for tag in product.get("tags", [])]:
                        score += 2
                
                # Persona type match
                if persona_type == "budget_conscious" and product["price"] < 100:
                    score += 2
                elif persona_type == "luxury_lover" and product["price"] > 500:
                    score += 2
                elif persona_type == "tech_enthusiast" and product["category"] == "Electronics":
                    score += 3
                
                # Rating boost
                score += product.get("rating", 0) * 0.5
                
                scored_products.append({
                    "product_id": str(product["_id"]),
                    "product": product,
                    "score": score
                })
            
            # Sort by score and return top recommendations
            scored_products.sort(key=lambda x: x["score"], reverse=True)
            return scored_products[:limit]
            
        except Exception as e:
            print(f"Error in content-based recommendations: {e}")
            return []

    async def _get_trending_recommendations(self, limit: int) -> List[Dict]:
        """Get trending products based on recent sales and ratings"""
        try:
            # Get products with high sales in last 30 days
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            
            trending_products = await self.db.products.aggregate([
                {"$match": {"created_at": {"$gte": thirty_days_ago}}},
                {"$sort": {"total_sold": -1, "rating": -1}},
                {"$limit": limit}
            ]).to_list(length=limit)
            
            return [{"product_id": str(p["_id"]), "product": p, "score": p["total_sold"]} 
                   for p in trending_products]
            
        except Exception as e:
            print(f"Error in trending recommendations: {e}")
            return []

    async def _get_persona_based_recommendations(self, user: Dict, limit: int) -> List[Dict]:
        """Get recommendations for new users based on their persona"""
        try:
            persona_type = user.get("persona_type", "")
            income_level = user.get("income_level", "medium")
            
            query = {}
            
            # Adjust recommendations based on persona type
            if persona_type == "budget_conscious":
                query["price"] = {"$lt": 100}
            elif persona_type == "luxury_lover":
                query["price"] = {"$gt": 500}
            elif persona_type == "tech_enthusiast":
                query["category"] = "Electronics"
            elif persona_type == "fashion_forward":
                query["category"] = "Fashion"
            
            # Adjust for income level
            if income_level == "low":
                query["price"] = {"$lt": 50}
            elif income_level == "high":
                query["price"] = {"$gt": 200}
            
            products = await self.db.products.find(query).to_list(length=limit)
            
            return [{"product_id": str(p["_id"]), "product": p, "score": 1.0} 
                   for p in products]
            
        except Exception as e:
            print(f"Error in persona-based recommendations: {e}")
            return []

    async def _get_random_recommendations(self, limit: int) -> List[Dict]:
        """Get random recommendations as fallback"""
        try:
            products = await self.db.products.find().limit(limit).to_list(length=limit)
            return [{"product_id": str(p["_id"]), "product": p, "score": 0.5} 
                   for p in products]
        except Exception as e:
            print(f"Error in random recommendations: {e}")
            return []

    def _combine_recommendations(self, collaborative: List[Dict], content: List[Dict], 
                               trending: List[Dict], user: Dict) -> List[Dict]:
        """Combine different types of recommendations with weights"""
        all_recs = {}
        
        # Add collaborative recommendations (weight: 0.4)
        for rec in collaborative:
            product_id = rec["product_id"]
            if product_id not in all_recs:
                all_recs[product_id] = {"product": rec["product"], "score": 0}
            all_recs[product_id]["score"] += rec["score"] * 0.4
        
        # Add content-based recommendations (weight: 0.4)
        for rec in content:
            product_id = rec["product_id"]
            if product_id not in all_recs:
                all_recs[product_id] = {"product": rec["product"], "score": 0}
            all_recs[product_id]["score"] += rec["score"] * 0.4
        
        # Add trending recommendations (weight: 0.2)
        for rec in trending:
            product_id = rec["product_id"]
            if product_id not in all_recs:
                all_recs[product_id] = {"product": rec["product"], "score": 0}
            all_recs[product_id]["score"] += rec["score"] * 0.2
        
        # Convert to list and sort by score
        result = [{"product_id": pid, "product": data["product"], "score": data["score"]} 
                 for pid, data in all_recs.items()]
        result.sort(key=lambda x: x["score"], reverse=True)
        
        return result

    async def _get_offers_for_products(self, product_ids: List[str]) -> List[Dict]:
        """Get special offers for recommended products"""
        try:
            offers = []
            for product_id in product_ids:
                product = await self.db.products.find_one({"_id": ObjectId(product_id)})
                if product and product.get("discount_percentage", 0) > 0:
                    offers.append({
                        "product_id": product_id,
                        "product_name": product["name"],
                        "original_price": product["price"],
                        "discounted_price": round(product["price"] * (1 - product["discount_percentage"] / 100), 2),
                        "discount_percentage": product["discount_percentage"],
                        "offer_type": "discount"
                    })
                elif random.random() < 0.1:  # 10% chance of special offer
                    offers.append({
                        "product_id": product_id,
                        "product_name": product["name"],
                        "offer_type": "free_shipping",
                        "description": "Free shipping on this item!"
                    })
            
            return offers
            
        except Exception as e:
            print(f"Error getting offers: {e}")
            return []
