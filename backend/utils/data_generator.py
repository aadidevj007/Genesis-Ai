import random
from faker import Faker
from typing import List, Dict, Any
import json
from datetime import datetime, timedelta

fake = Faker()

class DataGenerator:
    def __init__(self):
        self.categories = {
            "Electronics": ["Smartphones", "Laptops", "Tablets", "Accessories", "Gaming"],
            "Fashion": ["Men's Clothing", "Women's Clothing", "Shoes", "Accessories", "Jewelry"],
            "Home & Garden": ["Furniture", "Kitchen", "Decor", "Garden", "Tools"],
            "Books": ["Fiction", "Non-Fiction", "Academic", "Children's", "Cookbooks"],
            "Sports": ["Fitness", "Outdoor", "Team Sports", "Equipment", "Clothing"],
            "Beauty": ["Skincare", "Makeup", "Haircare", "Fragrances", "Tools"],
            "Toys": ["Educational", "Action Figures", "Board Games", "Puzzles", "Dolls"],
            "Automotive": ["Parts", "Accessories", "Tools", "Electronics", "Maintenance"]
        }
        
        self.brands = {
            "Electronics": ["Apple", "Samsung", "Sony", "LG", "Dell", "HP", "Asus", "Lenovo"],
            "Fashion": ["Nike", "Adidas", "Zara", "H&M", "Uniqlo", "Levi's", "Calvin Klein"],
            "Home & Garden": ["IKEA", "Home Depot", "Wayfair", "Target", "Walmart"],
            "Books": ["Penguin", "Random House", "HarperCollins", "Simon & Schuster"],
            "Sports": ["Nike", "Adidas", "Under Armour", "Puma", "Reebok"],
            "Beauty": ["L'Oreal", "Maybelline", "MAC", "Sephora", "Estee Lauder"],
            "Toys": ["LEGO", "Mattel", "Hasbro", "Fisher-Price", "Melissa & Doug"],
            "Automotive": ["Bosch", "NGK", "Mobil 1", "Castrol", "Michelin"]
        }
        
        self.persona_types = [
            "budget_conscious", "luxury_lover", "tech_enthusiast", 
            "fashion_forward", "practical_buyer", "impulse_shopper",
            "research_heavy", "brand_loyal", "trend_follower"
        ]
        
        self.income_levels = ["low", "medium", "high"]
        self.genders = ["male", "female", "other"]
        self.payment_methods = ["credit_card", "debit_card", "paypal", "cash_on_delivery"]

    def generate_user(self) -> Dict[str, Any]:
        """Generate a realistic user profile"""
        age = random.randint(18, 75)
        gender = random.choice(self.genders)
        income_level = random.choice(self.income_levels)
        persona_type = random.choice(self.persona_types)
        
        # Generate interests based on persona type
        interests = self._generate_interests(persona_type, age, gender)
        
        return {
            "name": fake.name(),
            "email": fake.email(),
            "age": age,
            "gender": gender,
            "location": fake.city(),
            "income_level": income_level,
            "interests": interests,
            "persona_type": persona_type,
            "created_at": fake.date_time_between(start_date="-2y", end_date="now"),
            "last_login": fake.date_time_between(start_date="-30d", end_date="now"),
            "total_purchases": random.randint(0, 50),
            "total_spent": round(random.uniform(0, 10000), 2),
            "favorite_categories": random.sample(list(self.categories.keys()), random.randint(1, 3))
        }

    def generate_product(self) -> Dict[str, Any]:
        """Generate a realistic product"""
        category = random.choice(list(self.categories.keys()))
        subcategory = random.choice(self.categories[category])
        brand = random.choice(self.brands[category])
        
        # Generate price based on category
        base_price = self._get_base_price(category)
        price = round(random.uniform(base_price * 0.5, base_price * 2), 2)
        
        # Generate rating and reviews
        rating = round(random.uniform(3.0, 5.0), 1)
        review_count = random.randint(0, 1000)
        
        # Generate stock quantity
        stock_quantity = random.randint(0, 500)
        
        # Generate discount (20% chance of having discount)
        discount_percentage = 0.0
        if random.random() < 0.2:
            discount_percentage = round(random.uniform(5.0, 50.0), 1)
        
        return {
            "name": fake.catch_phrase(),
            "category": category,
            "subcategory": subcategory,
            "price": price,
            "description": fake.text(max_nb_chars=200),
            "brand": brand,
            "tags": random.sample(self._get_tags_for_category(category), random.randint(2, 5)),
            "rating": rating,
            "review_count": review_count,
            "stock_quantity": stock_quantity,
            "is_featured": random.random() < 0.1,  # 10% chance of being featured
            "discount_percentage": discount_percentage,
            "created_at": fake.date_time_between(start_date="-1y", end_date="now"),
            "updated_at": fake.date_time_between(start_date="-30d", end_date="now"),
            "total_sold": random.randint(0, 1000),
            "revenue_generated": round(random.uniform(0, price * 1000), 2)
        }

    def generate_purchase(self, user_id: str, products: List[Dict]) -> Dict[str, Any]:
        """Generate a realistic purchase"""
        # Select 1-5 products for this purchase
        num_items = random.randint(1, min(5, len(products)))
        selected_products = random.sample(products, num_items)
        
        items = []
        total_amount = 0.0
        discount_amount = 0.0
        
        for product in selected_products:
            quantity = random.randint(1, 3)
            unit_price = product["price"]
            item_total = unit_price * quantity
            
            # Apply product discount if available
            product_discount = (unit_price * product.get("discount_percentage", 0) / 100) * quantity
            item_total -= product_discount
            
            items.append({
                "product_id": product["_id"],
                "product_name": product["name"],
                "quantity": quantity,
                "unit_price": unit_price,
                "total_price": item_total,
                "discount_applied": product_discount
            })
            
            total_amount += unit_price * quantity
            discount_amount += product_discount
        
        # Apply additional purchase-level discount (10% chance)
        purchase_discount = 0.0
        if random.random() < 0.1:
            purchase_discount = round(total_amount * random.uniform(0.05, 0.15), 2)
            discount_amount += purchase_discount
        
        final_amount = total_amount - discount_amount
        
        return {
            "user_id": user_id,
            "items": items,
            "total_amount": total_amount,
            "discount_amount": discount_amount,
            "final_amount": final_amount,
            "payment_method": random.choice(self.payment_methods),
            "shipping_address": fake.address(),
            "status": "completed",
            "created_at": fake.date_time_between(start_date="-6m", end_date="now"),
            "session_id": fake.uuid4()
        }

    def _generate_interests(self, persona_type: str, age: int, gender: str) -> List[str]:
        """Generate interests based on persona type, age, and gender"""
        all_interests = [
            "technology", "fashion", "sports", "cooking", "travel", "music", 
            "movies", "books", "fitness", "gaming", "photography", "art",
            "gardening", "DIY", "cars", "pets", "parenting", "business"
        ]
        
        # Filter interests based on persona type
        if persona_type == "tech_enthusiast":
            base_interests = ["technology", "gaming", "photography"]
        elif persona_type == "fashion_forward":
            base_interests = ["fashion", "beauty", "art"]
        elif persona_type == "budget_conscious":
            base_interests = ["DIY", "cooking", "gardening"]
        elif persona_type == "luxury_lover":
            base_interests = ["travel", "fashion", "cars"]
        else:
            base_interests = random.sample(all_interests, 3)
        
        # Add age and gender appropriate interests
        if age < 25:
            base_interests.extend(["gaming", "music", "social_media"])
        elif age > 50:
            base_interests.extend(["gardening", "parenting", "business"])
        
        return list(set(base_interests))

    def _get_base_price(self, category: str) -> float:
        """Get base price for category"""
        base_prices = {
            "Electronics": 500,
            "Fashion": 50,
            "Home & Garden": 100,
            "Books": 20,
            "Sports": 80,
            "Beauty": 30,
            "Toys": 25,
            "Automotive": 150
        }
        return base_prices.get(category, 50)

    def _get_tags_for_category(self, category: str) -> List[str]:
        """Get relevant tags for category"""
        tag_mapping = {
            "Electronics": ["wireless", "smart", "portable", "high-tech", "premium"],
            "Fashion": ["trendy", "comfortable", "stylish", "casual", "formal"],
            "Home & Garden": ["durable", "eco-friendly", "modern", "traditional", "space-saving"],
            "Books": ["bestseller", "award-winning", "educational", "entertaining", "inspirational"],
            "Sports": ["lightweight", "durable", "performance", "comfortable", "professional"],
            "Beauty": ["natural", "organic", "long-lasting", "hypoallergenic", "luxury"],
            "Toys": ["educational", "safe", "fun", "creative", "interactive"],
            "Automotive": ["reliable", "high-quality", "durable", "performance", "safety"]
        }
        return tag_mapping.get(category, ["quality", "popular", "trending"])
