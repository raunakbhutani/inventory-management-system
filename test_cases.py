"""
Test cases for the Inventory Management System
This script demonstrates how the application would work with three test cases
without requiring an actual MySQL connection.
"""

from tabulate import tabulate

class MockInventorySystem:
    def __init__(self):
        # Mock data for demonstration
        self.products = [
            {"product_id": 1, "name": "Laptop", "description": "High-performance laptop with 16GB RAM", 
             "price": 1200.00, "category": "Electronics", "quantity": 20},
            {"product_id": 2, "name": "Smartphone", "description": "Latest model with 128GB storage", 
             "price": 800.00, "category": "Electronics", "quantity": 30},
            {"product_id": 3, "name": "T-shirt", "description": "Cotton t-shirt, available in multiple colors", 
             "price": 25.99, "category": "Clothing", "quantity": 100}
        ]
        
        self.categories = [
            {"category_id": 1, "name": "Electronics", "description": "Electronic devices and accessories", "product_count": 2},
            {"category_id": 2, "name": "Clothing", "description": "Apparel and fashion items", "product_count": 1}
        ]
        
        self.transactions = []
    
    def display_products(self):
        """Display all products"""
        print("\n===== Product List =====")
        headers = ["ID", "Name", "Description", "Price", "Category", "In Stock"]
        table_data = [
            [p["product_id"], p["name"], p["description"][:30] + "..." if len(p["description"]) > 30 else p["description"], 
             f"${p['price']:.2f}", p["category"], p["quantity"]]
            for p in self.products
        ]
        print(tabulate(table_data, headers=headers, tablefmt="grid"))
    
    def add_product(self, name, description, price, category, quantity):
        """Add a new product"""
        product_id = len(self.products) + 1
        self.products.append({
            "product_id": product_id,
            "name": name,
            "description": description,
            "price": price,
            "category": category,
            "quantity": quantity
        })
        print(f"\nProduct '{name}' added successfully with ID: {product_id}")
        return product_id
    
    def update_inventory(self, product_id, quantity_change, transaction_type, notes=None):
        """Update inventory and record transaction"""
        # Find the product
        product = next((p for p in self.products if p["product_id"] == product_id), None)
        if not product:
            print(f"Product with ID {product_id} not found.")
            return False
        
        # Update quantity
        current_quantity = product["quantity"]
        new_quantity = current_quantity + quantity_change
        
        if transaction_type == "sale" and new_quantity < 0:
            print(f"Error: Not enough inventory. Current: {current_quantity}")
            return False
        
        product["quantity"] = new_quantity
        
        # Record transaction
        transaction_id = len(self.transactions) + 1
        self.transactions.append({
            "transaction_id": transaction_id,
            "product_id": product_id,
            "product_name": product["name"],
            "quantity": abs(quantity_change),
            "transaction_type": transaction_type,
            "notes": notes
        })
        
        print(f"\nTransaction recorded: {transaction_type.capitalize()} of {abs(quantity_change)} units of {product['name']}")
        print(f"New inventory level: {new_quantity}")
        return True
    
    def display_transactions(self):
        """Display transaction history"""
        if not self.transactions:
            print("\nNo transactions recorded yet.")
            return
        
        print("\n===== Transaction History =====")
        headers = ["ID", "Product", "Quantity", "Type", "Notes"]
        table_data = [
            [t["transaction_id"], t["product_name"], t["quantity"], 
             t["transaction_type"].capitalize(), t["notes"] if t["notes"] else ""]
            for t in self.transactions
        ]
        print(tabulate(table_data, headers=headers, tablefmt="grid"))
    
    def generate_low_stock_report(self, threshold=30):
        """Generate a report of products with low stock"""
        low_stock = [p for p in self.products if p["quantity"] <= threshold]
        
        if not low_stock:
            print(f"\nNo products with stock below {threshold} units.")
            return
        
        print(f"\n===== Low Stock Report (Below {threshold} units) =====")
        headers = ["ID", "Product", "Current Stock", "Price"]
        table_data = [
            [p["product_id"], p["name"], p["quantity"], f"${p['price']:.2f}"]
            for p in low_stock
        ]
        print(tabulate(table_data, headers=headers, tablefmt="grid"))


def test_case_1():
    """Test Case 1: Adding a new product and viewing products"""
    print("\n" + "="*50)
    print("TEST CASE 1: Adding a new product and viewing all products")
    print("="*50)
    
    ims = MockInventorySystem()
    
    print("\nInitial product list:")
    ims.display_products()
    
    print("\nAdding a new product...")
    ims.add_product(
        name="Coffee Maker",
        description="Automatic coffee maker with timer",
        price=89.99,
        category="Home & Kitchen",
        quantity=15
    )
    
    print("\nUpdated product list:")
    ims.display_products()


def test_case_2():
    """Test Case 2: Recording sales transactions and viewing inventory changes"""
    print("\n" + "="*50)
    print("TEST CASE 2: Recording sales transactions and inventory updates")
    print("="*50)
    
    ims = MockInventorySystem()
    
    print("\nInitial product list:")
    ims.display_products()
    
    print("\nRecording a sale of 5 laptops...")
    ims.update_inventory(
        product_id=1,
        quantity_change=-5,  # Negative for sales
        transaction_type="sale",
        notes="Customer order #12345"
    )
    
    print("\nRecording a restock of 10 smartphones...")
    ims.update_inventory(
        product_id=2,
        quantity_change=10,  # Positive for restocks
        transaction_type="restock",
        notes="Weekly inventory replenishment"
    )
    
    print("\nAttempting to sell more t-shirts than in stock...")
    ims.update_inventory(
        product_id=3,
        quantity_change=-150,  # More than available
        transaction_type="sale",
        notes="Bulk order"
    )
    
    print("\nTransaction history:")
    ims.display_transactions()
    
    print("\nUpdated product list:")
    ims.display_products()


def test_case_3():
    """Test Case 3: Generating inventory reports"""
    print("\n" + "="*50)
    print("TEST CASE 3: Generating inventory reports")
    print("="*50)
    
    ims = MockInventorySystem()
    
    # Adjust some inventory levels for demonstration
    ims.products[0]["quantity"] = 8  # Set laptops to low stock
    ims.products[2]["quantity"] = 25  # Set t-shirts to low stock
    
    print("\nCurrent product list:")
    ims.display_products()
    
    # Generate low stock report
    ims.generate_low_stock_report(threshold=30)
    
    # Calculate total inventory value
    total_value = sum(p["price"] * p["quantity"] for p in ims.products)
    
    print(f"\nTotal Inventory Value: ${total_value:.2f}")


if __name__ == "__main__":
    print("Running test cases for Inventory Management System")
    
    test_case_1()
    test_case_2()
    test_case_3()
    
    print("\nAll test cases completed successfully!")
