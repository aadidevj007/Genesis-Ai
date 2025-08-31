#!/usr/bin/env python3
"""
Data Generation Script for Recommendation Engine
This script generates realistic sample data for testing the recommendation engine.
"""

import asyncio
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../backend'))

from utils.data_generator import DataGenerator
from app.database import connect_to_mongo, close_mongo_connection, get_database
import random

async def generate_sample_data():
    """Generate comprehensive sample data"""
    print("Connecting to MongoDB...")
    await connect_to_mongo()
    db = get_database()
    
    print("Initializing data generator...")
    generator = DataGenerator()
    
    try:
        # Clear existing data
        print("Clearing existing data...")
        await db.users.delete_many({})
        await db.products.delete_many({})
        await db.purchases.delete_many({})
        
        # Generate users
        print("Generating 1000 users...")
        users = []
        for i in range(1000):
            if i % 100 == 0:
                print(f"Generated {i} users...")
            user_data = generator.generate_user()
            result = await db.users.insert_one(user_data)
            user_data["_id"] = result.inserted_id
            users.append(user_data)
        
        print(f"Generated {len(users)} users successfully")
        
        # Generate products
        print("Generating 1000 products...")
        products = []
        for i in range(1000):
            if i % 100 == 0:
                print(f"Generated {i} products...")
            product_data = generator.generate_product()
            result = await db.products.insert_one(product_data)
            product_data["_id"] = result.inserted_id
            products.append(product_data)
        
        print(f"Generated {len(products)} products successfully")
        
        # Generate purchases
        print("Generating purchase history...")
        total_purchases = 0
        for i, user in enumerate(users):
            if i % 100 == 0:
                print(f"Processing user {i}...")
            
            # Generate 0-15 purchases per user
            num_purchases = random.randint(0, 15)
            for _ in range(num_purchases):
                purchase_data = generator.generate_purchase(str(user["_id"]), products)
                result = await db.purchases.insert_one(purchase_data)
                total_purchases += 1
                
                # Update user statistics
                await db.users.update_one(
                    {"_id": user["_id"]},
                    {
                        "$inc": {
                            "total_purchases": 1,
                            "total_spent": purchase_data["final_amount"]
                        }
                    }
                )
                
                # Update product statistics
                for item in purchase_data["items"]:
                    await db.products.update_one(
                        {"_id": item["product_id"]},
                        {
                            "$inc": {
                                "total_sold": item["quantity"],
                                "revenue_generated": item["total_price"]
                            }
                        }
                    )
        
        print(f"Generated {total_purchases} purchases successfully")
        
        # Generate some statistics
        print("\nGenerating statistics...")
        user_count = await db.users.count_documents({})
        product_count = await db.products.count_documents({})
        purchase_count = await db.purchases.count_documents({})
        
        print(f"\nData Generation Complete!")
        print(f"Users: {user_count}")
        print(f"Products: {product_count}")
        print(f"Purchases: {purchase_count}")
        
        # Show some sample data
        print("\nSample User:")
        sample_user = await db.users.find_one()
        if sample_user:
            print(f"  Name: {sample_user['name']}")
            print(f"  Persona: {sample_user['persona_type']}")
            print(f"  Total Purchases: {sample_user['total_purchases']}")
            print(f"  Total Spent: ${sample_user['total_spent']:.2f}")
        
        print("\nSample Product:")
        sample_product = await db.products.find_one()
        if sample_product:
            print(f"  Name: {sample_product['name']}")
            print(f"  Category: {sample_product['category']}")
            print(f"  Price: ${sample_product['price']:.2f}")
            print(f"  Rating: {sample_product['rating']}/5")
        
        print("\nSample Purchase:")
        sample_purchase = await db.purchases.find_one()
        if sample_purchase:
            print(f"  Items: {len(sample_purchase['items'])}")
            print(f"  Total Amount: ${sample_purchase['total_amount']:.2f}")
            print(f"  Final Amount: ${sample_purchase['final_amount']:.2f}")
        
    except Exception as e:
        print(f"Error generating data: {e}")
        raise
    finally:
        await close_mongo_connection()

if __name__ == "__main__":
    asyncio.run(generate_sample_data())
