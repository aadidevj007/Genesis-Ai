import random
from typing import Dict, List, Any
from datetime import datetime, timedelta
import json

class PersonaService:
    def __init__(self, db):
        self.db = db
        
        # Define persona templates
        self.persona_templates = {
            "budget_conscious": {
                "price_range": (10, 100),
                "preferred_categories": ["Home & Garden", "Books", "Toys"],
                "shopping_behavior": "researches_before_buying",
                "discount_sensitivity": "high",
                "brand_preference": "value_brands"
            },
            "luxury_lover": {
                "price_range": (200, 2000),
                "preferred_categories": ["Fashion", "Electronics", "Beauty"],
                "shopping_behavior": "impulse_buyer",
                "discount_sensitivity": "low",
                "brand_preference": "premium_brands"
            },
            "tech_enthusiast": {
                "price_range": (50, 1500),
                "preferred_categories": ["Electronics", "Gaming", "Smart Home"],
                "shopping_behavior": "early_adopter",
                "discount_sensitivity": "medium",
                "brand_preference": "tech_brands"
            },
            "fashion_forward": {
                "price_range": (30, 500),
                "preferred_categories": ["Fashion", "Beauty", "Accessories"],
                "shopping_behavior": "trend_follower",
                "discount_sensitivity": "medium",
                "brand_preference": "trendy_brands"
            },
            "practical_buyer": {
                "price_range": (20, 300),
                "preferred_categories": ["Home & Garden", "Automotive", "Sports"],
                "shopping_behavior": "needs_based",
                "discount_sensitivity": "medium",
                "brand_preference": "reliable_brands"
            },
            "impulse_shopper": {
                "price_range": (5, 200),
                "preferred_categories": ["Toys", "Beauty", "Fashion"],
                "shopping_behavior": "impulse_buyer",
                "discount_sensitivity": "high",
                "brand_preference": "any_brand"
            },
            "research_heavy": {
                "price_range": (50, 800),
                "preferred_categories": ["Electronics", "Home & Garden", "Automotive"],
                "shopping_behavior": "researches_before_buying",
                "discount_sensitivity": "low",
                "brand_preference": "quality_brands"
            },
            "brand_loyal": {
                "price_range": (20, 600),
                "preferred_categories": ["Fashion", "Beauty", "Electronics"],
                "shopping_behavior": "brand_focused",
                "discount_sensitivity": "low",
                "brand_preference": "specific_brands"
            },
            "trend_follower": {
                "price_range": (15, 400),
                "preferred_categories": ["Fashion", "Beauty", "Toys"],
                "shopping_behavior": "trend_follower",
                "discount_sensitivity": "high",
                "brand_preference": "trendy_brands"
            }
        }

    async def generate_shopping_session(self, user_id: str, session_duration_minutes: int = 30) -> Dict[str, Any]:
        """Generate a realistic shopping session for a user"""
        try:
            user = await self.db.users.find_one({"_id": user_id})
            if not user:
                return {"error": "User not found"}
            
            persona_type = user.get("persona_type", "practical_buyer")
            persona_config = self.persona_templates.get(persona_type, self.persona_templates["practical_buyer"])
            
            # Generate session events
            session_events = self._generate_session_events(user, persona_config, session_duration_minutes)
            
            # Generate potential purchases
            potential_purchases = await self._generate_potential_purchases(user, persona_config)
            
            # Generate behavioral insights
            behavioral_insights = self._analyze_behavior(session_events, potential_purchases, persona_config)
            
            return {
                "user_id": str(user_id),
                "session_id": f"session_{user_id}_{datetime.utcnow().timestamp()}",
                "session_duration_minutes": session_duration_minutes,
                "persona_type": persona_type,
                "session_events": session_events,
                "potential_purchases": potential_purchases,
                "behavioral_insights": behavioral_insights,
                "generated_at": datetime.utcnow()
            }
            
        except Exception as e:
            print(f"Error generating shopping session: {e}")
            return {"error": str(e)}

    def _generate_session_events(self, user: Dict, persona_config: Dict, duration_minutes: int) -> List[Dict]:
        """Generate realistic session events based on persona"""
        events = []
        current_time = datetime.utcnow()
        
        # Number of events based on session duration and persona
        num_events = self._get_event_count(persona_config, duration_minutes)
        
        for i in range(num_events):
            event_time = current_time + timedelta(minutes=i * (duration_minutes / num_events))
            
            event_type = self._get_event_type(persona_config, i, num_events)
            
            event = {
                "timestamp": event_time,
                "event_type": event_type,
                "details": self._get_event_details(event_type, persona_config)
            }
            
            events.append(event)
        
        return events

    def _get_event_count(self, persona_config: Dict, duration_minutes: int) -> int:
        """Get number of events based on persona and session duration"""
        base_events = duration_minutes // 5  # One event every 5 minutes
        
        behavior = persona_config.get("shopping_behavior", "practical_buyer")
        
        if behavior == "impulse_buyer":
            return int(base_events * 1.5)
        elif behavior == "researches_before_buying":
            return int(base_events * 0.7)
        elif behavior == "trend_follower":
            return int(base_events * 1.2)
        else:
            return base_events

    def _get_event_type(self, persona_config: Dict, event_index: int, total_events: int) -> str:
        """Get event type based on persona and session progression"""
        behavior = persona_config.get("shopping_behavior", "practical_buyer")
        
        # Define event probabilities based on behavior
        if behavior == "impulse_buyer":
            event_types = ["browse", "view_product", "add_to_cart", "purchase"]
            weights = [0.2, 0.3, 0.3, 0.2]
        elif behavior == "researches_before_buying":
            event_types = ["search", "view_product", "read_reviews", "compare_products", "add_to_cart"]
            weights = [0.3, 0.2, 0.2, 0.2, 0.1]
        elif behavior == "trend_follower":
            event_types = ["browse", "view_product", "check_trends", "add_to_cart"]
            weights = [0.3, 0.3, 0.2, 0.2]
        else:
            event_types = ["browse", "view_product", "add_to_cart"]
            weights = [0.4, 0.4, 0.2]
        
        return random.choices(event_types, weights=weights)[0]

    def _get_event_details(self, event_type: str, persona_config: Dict) -> Dict:
        """Get detailed information for each event type"""
        if event_type == "search":
            return {
                "query": self._generate_search_query(persona_config),
                "filters_applied": self._generate_filters(persona_config)
            }
        elif event_type == "view_product":
            return {
                "product_category": random.choice(persona_config.get("preferred_categories", ["Electronics"])),
                "time_spent_seconds": random.randint(30, 300),
                "scrolled_to_reviews": random.random() < 0.7
            }
        elif event_type == "add_to_cart":
            return {
                "quantity": random.randint(1, 3),
                "price_range": persona_config.get("price_range", (20, 200))
            }
        elif event_type == "purchase":
            return {
                "payment_method": random.choice(["credit_card", "paypal", "debit_card"]),
                "total_amount": random.uniform(*persona_config.get("price_range", (20, 200)))
            }
        else:
            return {"duration_seconds": random.randint(10, 120)}

    def _generate_search_query(self, persona_config: Dict) -> str:
        """Generate realistic search queries based on persona"""
        categories = persona_config.get("preferred_categories", ["Electronics"])
        category = random.choice(categories)
        
        queries = {
            "Electronics": ["wireless headphones", "smartphone", "laptop", "tablet", "gaming console"],
            "Fashion": ["dress", "shoes", "jeans", "jacket", "accessories"],
            "Home & Garden": ["furniture", "kitchen appliances", "garden tools", "decor"],
            "Beauty": ["skincare", "makeup", "perfume", "hair products"],
            "Sports": ["fitness equipment", "running shoes", "sports clothing", "outdoor gear"]
        }
        
        return random.choice(queries.get(category, ["product"]))

    def _generate_filters(self, persona_config: Dict) -> Dict:
        """Generate filters based on persona preferences"""
        filters = {}
        
        # Price filter based on persona
        price_range = persona_config.get("price_range", (20, 200))
        filters["price_min"] = price_range[0]
        filters["price_max"] = price_range[1]
        
        # Category filter
        if random.random() < 0.7:
            filters["category"] = random.choice(persona_config.get("preferred_categories", ["Electronics"]))
        
        # Rating filter for research-heavy personas
        if persona_config.get("shopping_behavior") == "researches_before_buying":
            filters["min_rating"] = random.randint(3, 5)
        
        return filters

    async def _generate_potential_purchases(self, user: Dict, persona_config: Dict) -> List[Dict]:
        """Generate potential purchases based on persona"""
        try:
            # Get products matching persona preferences
            query = {
                "category": {"$in": persona_config.get("preferred_categories", ["Electronics"])},
                "price": {"$gte": persona_config.get("price_range", (20, 200))[0],
                         "$lte": persona_config.get("price_range", (20, 200))[1]}
            }
            
            products = await self.db.products.find(query).limit(20).to_list(length=20)
            
            potential_purchases = []
            for product in products:
                # Calculate purchase probability based on persona
                probability = self._calculate_purchase_probability(product, persona_config)
                
                if random.random() < probability:
                    potential_purchases.append({
                        "product_id": str(product["_id"]),
                        "product_name": product["name"],
                        "price": product["price"],
                        "purchase_probability": probability,
                        "reason": self._get_purchase_reason(product, persona_config)
                    })
            
            return potential_purchases[:10]  # Return top 10 potential purchases
            
        except Exception as e:
            print(f"Error generating potential purchases: {e}")
            return []

    def _calculate_purchase_probability(self, product: Dict, persona_config: Dict) -> float:
        """Calculate probability of purchase based on product and persona"""
        probability = 0.5  # Base probability
        
        # Price sensitivity
        price_range = persona_config.get("price_range", (20, 200))
        if price_range[0] <= product["price"] <= price_range[1]:
            probability += 0.2
        
        # Category preference
        if product["category"] in persona_config.get("preferred_categories", []):
            probability += 0.2
        
        # Rating influence
        if product.get("rating", 0) >= 4.0:
            probability += 0.1
        
        # Discount influence
        if persona_config.get("discount_sensitivity") == "high" and product.get("discount_percentage", 0) > 0:
            probability += 0.2
        
        return min(probability, 1.0)

    def _get_purchase_reason(self, product: Dict, persona_config: Dict) -> str:
        """Get reason for potential purchase based on persona"""
        reasons = {
            "budget_conscious": ["Good value for money", "On sale", "Essential item"],
            "luxury_lover": ["Premium quality", "Brand reputation", "Exclusive item"],
            "tech_enthusiast": ["Latest technology", "Innovative features", "High performance"],
            "fashion_forward": ["Trendy design", "Popular item", "Stylish appearance"],
            "practical_buyer": ["Durable", "Good reviews", "Practical use"]
        }
        
        persona_type = persona_config.get("persona_type", "practical_buyer")
        return random.choice(reasons.get(persona_type, ["Good product"]))

    def _analyze_behavior(self, session_events: List[Dict], potential_purchases: List[Dict], 
                         persona_config: Dict) -> Dict[str, Any]:
        """Analyze shopping behavior and provide insights"""
        total_events = len(session_events)
        purchase_events = [e for e in session_events if e["event_type"] == "purchase"]
        view_events = [e for e in session_events if e["event_type"] == "view_product"]
        
        # Calculate metrics
        conversion_rate = len(purchase_events) / max(total_events, 1)
        avg_time_per_product = sum(e["details"].get("time_spent_seconds", 0) for e in view_events) / max(len(view_events), 1)
        
        # Behavioral patterns
        behavior_patterns = {
            "shopping_style": persona_config.get("shopping_behavior", "practical_buyer"),
            "price_sensitivity": persona_config.get("discount_sensitivity", "medium"),
            "category_preference": persona_config.get("preferred_categories", ["Electronics"]),
            "conversion_rate": conversion_rate,
            "avg_time_per_product": avg_time_per_product,
            "total_products_viewed": len(view_events),
            "total_purchases": len(purchase_events)
        }
        
        return behavior_patterns
