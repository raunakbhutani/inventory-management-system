import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv
from tabulate import tabulate
import sys

# Load environment variables from .env file if it exists
load_dotenv()

# Database configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'database': 'inventory_management',
    'charset': 'utf8mb4',
    'use_pure': True
}

class InventoryManagementSystem:
    def __init__(self):
        self.connection = self.create_connection()
    
    def create_connection(self):
        """Create a database connection to MySQL server"""
        conn = None
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            return conn
        except Error as e:
            print(f"Error connecting to MySQL: {e}")
            return None
    
    def execute_query(self, query, params=None, fetch=False):
        """Execute a query on the database"""
        if not self.connection:
            self.connection = self.create_connection()
            if not self.connection:
                return None
        
        cursor = self.connection.cursor(dictionary=True)
        result = None
        
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            if fetch:
                result = cursor.fetchall()
            else:
                self.connection.commit()
                result = cursor.rowcount
        except Error as e:
            print(f"Error executing query: {e}")
        finally:
            cursor.close()
        
        return result
    
    def display_menu(self):
        """Display the main menu options"""
        print("\n===== Inventory Management System =====")
        print("1. View Products")
        print("2. Add New Product")
        print("3. Update Product")
        print("4. Delete Product")
        print("5. View Inventory")
        print("6. Update Inventory")
        print("7. Record Transaction")
        print("8. View Transactions")
        print("9. View Categories")
        print("10. Add Category")
        print("11. Generate Reports")
        print("0. Exit")
        return input("Enter your choice: ")
    
    def view_products(self):
        """Display all products"""
        query = """
        SELECT p.product_id, p.name, p.description, p.price, c.name as category, i.quantity
        FROM products p
        LEFT JOIN categories c ON p.category_id = c.category_id
        LEFT JOIN inventory i ON p.product_id = i.product_id
        ORDER BY p.product_id
        """
        products = self.execute_query(query, fetch=True)
        
        if products:
            headers = ["ID", "Name", "Description", "Price", "Category", "In Stock"]
            table_data = [
                [p['product_id'], p['name'], p['description'][:30] + "..." if p['description'] and len(p['description']) > 30 else p['description'], 
                 f"${p['price']:.2f}", p['category'], p['quantity']]
                for p in products
            ]
            print("\n" + tabulate(table_data, headers=headers, tablefmt="grid"))
        else:
            print("No products found.")
    
    def add_product(self):
        """Add a new product"""
        name = input("Enter product name: ")
        description = input("Enter product description: ")
        
        # Validate price input
        while True:
            try:
                price = float(input("Enter product price: "))
                break
            except ValueError:
                print("Invalid price. Please enter a number.")
        
        # Get categories for selection
        categories = self.execute_query("SELECT category_id, name FROM categories", fetch=True)
        
        if not categories:
            print("No categories found. Please add a category first.")
            return
        
        print("\nAvailable Categories:")
        for cat in categories:
            print(f"{cat['category_id']}. {cat['name']}")
        
        # Validate category selection
        while True:
            try:
                category_id = int(input("Select category ID: "))
                if any(cat['category_id'] == category_id for cat in categories):
                    break
                print("Invalid category ID. Please select from the list.")
            except ValueError:
                print("Invalid input. Please enter a number.")
        
        # Insert the product
        query = """
        INSERT INTO products (name, description, price, category_id)
        VALUES (%s, %s, %s, %s)
        """
        result = self.execute_query(query, (name, description, price, category_id))
        
        if result:
            print(f"Product '{name}' added successfully.")
            
            # Get the new product ID
            product_id = self.execute_query(
                "SELECT product_id FROM products WHERE name = %s ORDER BY product_id DESC LIMIT 1",
                (name,), fetch=True
            )[0]['product_id']
            
            # Initialize inventory
            quantity = int(input("Enter initial stock quantity: "))
            self.execute_query(
                "INSERT INTO inventory (product_id, quantity) VALUES (%s, %s)",
                (product_id, quantity)
            )
            print(f"Initial inventory of {quantity} units recorded.")
        else:
            print("Failed to add product.")
    
    def update_product(self):
        """Update an existing product"""
        self.view_products()
        
        while True:
            try:
                product_id = int(input("\nEnter product ID to update (0 to cancel): "))
                if product_id == 0:
                    return
                
                # Check if product exists
                product = self.execute_query(
                    "SELECT * FROM products WHERE product_id = %s",
                    (product_id,), fetch=True
                )
                
                if not product:
                    print("Product not found.")
                    continue
                
                break
            except ValueError:
                print("Invalid input. Please enter a number.")
        
        product = product[0]
        print(f"\nUpdating Product: {product['name']}")
        
        name = input(f"Enter new name (current: {product['name']}, press Enter to keep current): ")
        name = name if name else product['name']
        
        description = input(f"Enter new description (press Enter to keep current): ")
        description = description if description else product['description']
        
        price_str = input(f"Enter new price (current: ${product['price']:.2f}, press Enter to keep current): ")
        price = float(price_str) if price_str else product['price']
        
        # Get categories for selection
        categories = self.execute_query("SELECT category_id, name FROM categories", fetch=True)
        current_category = self.execute_query(
            "SELECT c.name FROM categories c JOIN products p ON c.category_id = p.category_id WHERE p.product_id = %s",
            (product_id,), fetch=True
        )
        
        print(f"\nCurrent category: {current_category[0]['name'] if current_category else 'None'}")
        print("Available Categories:")
        for cat in categories:
            print(f"{cat['category_id']}. {cat['name']}")
        
        category_id_str = input("Select new category ID (press Enter to keep current): ")
        category_id = int(category_id_str) if category_id_str else product['category_id']
        
        # Update the product
        query = """
        UPDATE products
        SET name = %s, description = %s, price = %s, category_id = %s
        WHERE product_id = %s
        """
        result = self.execute_query(query, (name, description, price, category_id, product_id))
        
        if result:
            print(f"Product updated successfully.")
        else:
            print("Failed to update product.")
    
    def delete_product(self):
        """Delete a product"""
        self.view_products()
        
        while True:
            try:
                product_id = int(input("\nEnter product ID to delete (0 to cancel): "))
                if product_id == 0:
                    return
                
                # Check if product exists
                product = self.execute_query(
                    "SELECT name FROM products WHERE product_id = %s",
                    (product_id,), fetch=True
                )
                
                if not product:
                    print("Product not found.")
                    continue
                
                break
            except ValueError:
                print("Invalid input. Please enter a number.")
        
        confirm = input(f"Are you sure you want to delete '{product[0]['name']}'? (y/n): ").lower()
        
        if confirm == 'y':
            # First delete from inventory and transactions (due to foreign key constraints)
            self.execute_query("DELETE FROM inventory WHERE product_id = %s", (product_id,))
            self.execute_query("DELETE FROM transactions WHERE product_id = %s", (product_id,))
            
            # Then delete the product
            result = self.execute_query("DELETE FROM products WHERE product_id = %s", (product_id,))
            
            if result:
                print(f"Product '{product[0]['name']}' deleted successfully.")
            else:
                print("Failed to delete product.")
        else:
            print("Deletion cancelled.")
    
    def view_inventory(self):
        """Display current inventory levels"""
        query = """
        SELECT p.product_id, p.name, i.quantity, p.price, (p.price * i.quantity) as total_value
        FROM inventory i
        JOIN products p ON i.product_id = p.product_id
        ORDER BY i.quantity DESC
        """
        inventory = self.execute_query(query, fetch=True)
        
        if inventory:
            headers = ["ID", "Product", "Quantity", "Unit Price", "Total Value"]
            table_data = [
                [item['product_id'], item['name'], item['quantity'], f"${item['price']:.2f}", f"${item['total_value']:.2f}"]
                for item in inventory
            ]
            
            # Calculate total inventory value
            total_value = sum(item['total_value'] for item in inventory)
            
            print("\n" + tabulate(table_data, headers=headers, tablefmt="grid"))
            print(f"\nTotal Inventory Value: ${total_value:.2f}")
        else:
            print("No inventory data found.")
    
    def update_inventory(self):
        """Update inventory levels"""
        self.view_inventory()
        
        while True:
            try:
                product_id = int(input("\nEnter product ID to update inventory (0 to cancel): "))
                if product_id == 0:
                    return
                
                # Check if product exists in inventory
                inventory = self.execute_query(
                    """
                    SELECT i.quantity, p.name 
                    FROM inventory i 
                    JOIN products p ON i.product_id = p.product_id 
                    WHERE i.product_id = %s
                    """,
                    (product_id,), fetch=True
                )
                
                if not inventory:
                    print("Product not found in inventory.")
                    continue
                
                break
            except ValueError:
                print("Invalid input. Please enter a number.")
        
        current_quantity = inventory[0]['quantity']
        product_name = inventory[0]['name']
        
        print(f"\nUpdating inventory for: {product_name}")
        print(f"Current quantity: {current_quantity}")
        
        while True:
            update_type = input("Do you want to (a)dd to or (s)et the inventory? ").lower()
            
            if update_type in ['a', 's']:
                break
            print("Invalid choice. Please enter 'a' for add or 's' for set.")
        
        while True:
            try:
                if update_type == 'a':
                    quantity_change = int(input("Enter quantity to add (use negative for removal): "))
                    new_quantity = current_quantity + quantity_change
                else:  # 's'
                    new_quantity = int(input("Enter new quantity: "))
                
                if new_quantity < 0:
                    print("Inventory cannot be negative. Please enter a valid quantity.")
                    continue
                
                break
            except ValueError:
                print("Invalid input. Please enter a number.")
        
        # Update inventory
        result = self.execute_query(
            "UPDATE inventory SET quantity = %s WHERE product_id = %s",
            (new_quantity, product_id)
        )
        
        if result:
            print(f"Inventory updated successfully. New quantity: {new_quantity}")
            
            # Record transaction if it's an addition or removal
            if update_type == 'a' and quantity_change != 0:
                transaction_type = 'restock' if quantity_change > 0 else 'sale'
                quantity = abs(quantity_change)
                
                self.execute_query(
                    """
                    INSERT INTO transactions (product_id, quantity, transaction_type, notes)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (product_id, quantity, transaction_type, f"Manual {transaction_type}")
                )
                
                print(f"Transaction recorded: {transaction_type} of {quantity} units")
        else:
            print("Failed to update inventory.")
    
    def record_transaction(self):
        """Record a sale or restock transaction"""
        self.view_products()
        
        while True:
            try:
                product_id = int(input("\nEnter product ID for transaction (0 to cancel): "))
                if product_id == 0:
                    return
                
                # Check if product exists
                product = self.execute_query(
                    """
                    SELECT p.name, i.quantity 
                    FROM products p 
                    JOIN inventory i ON p.product_id = i.product_id 
                    WHERE p.product_id = %s
                    """,
                    (product_id,), fetch=True
                )
                
                if not product:
                    print("Product not found.")
                    continue
                
                break
            except ValueError:
                print("Invalid input. Please enter a number.")
        
        product_name = product[0]['name']
        current_quantity = product[0]['quantity']
        
        print(f"\nRecording transaction for: {product_name}")
        print(f"Current inventory: {current_quantity}")
        
        while True:
            transaction_type = input("Transaction type (s)ale or (r)estock: ").lower()
            
            if transaction_type in ['s', 'r']:
                transaction_type = 'sale' if transaction_type == 's' else 'restock'
                break
            print("Invalid choice. Please enter 's' for sale or 'r' for restock.")
        
        while True:
            try:
                quantity = int(input("Enter quantity: "))
                
                if quantity <= 0:
                    print("Quantity must be positive.")
                    continue
                
                if transaction_type == 'sale' and quantity > current_quantity:
                    print(f"Not enough inventory. Current stock: {current_quantity}")
                    continue
                
                break
            except ValueError:
                print("Invalid input. Please enter a number.")
        
        notes = input("Enter transaction notes (optional): ")
        
        # Record the transaction
        result = self.execute_query(
            """
            INSERT INTO transactions (product_id, quantity, transaction_type, notes)
            VALUES (%s, %s, %s, %s)
            """,
            (product_id, quantity, transaction_type, notes)
        )
        
        if result:
            # Update inventory
            new_quantity = current_quantity + quantity if transaction_type == 'restock' else current_quantity - quantity
            
            self.execute_query(
                "UPDATE inventory SET quantity = %s WHERE product_id = %s",
                (new_quantity, product_id)
            )
            
            print(f"Transaction recorded successfully.")
            print(f"New inventory for {product_name}: {new_quantity}")
        else:
            print("Failed to record transaction.")
    
    def view_transactions(self):
        """View transaction history"""
        query = """
        SELECT t.transaction_id, p.name as product, t.quantity, t.transaction_type,
               t.transaction_date, t.notes
        FROM transactions t
        JOIN products p ON t.product_id = p.product_id
        ORDER BY t.transaction_date DESC
        LIMIT 50
        """
        transactions = self.execute_query(query, fetch=True)
        
        if transactions:
            headers = ["ID", "Product", "Quantity", "Type", "Date", "Notes"]
            table_data = [
                [t['transaction_id'], t['product'], t['quantity'], 
                 t['transaction_type'].capitalize(), t['transaction_date'], 
                 t['notes'] if t['notes'] else '']
                for t in transactions
            ]
            
            print("\n" + tabulate(table_data, headers=headers, tablefmt="grid"))
            print("\nShowing the 50 most recent transactions.")
        else:
            print("No transactions found.")
    
    def view_categories(self):
        """View product categories"""
        query = """
        SELECT c.category_id, c.name, c.description, COUNT(p.product_id) as product_count
        FROM categories c
        LEFT JOIN products p ON c.category_id = p.category_id
        GROUP BY c.category_id
        ORDER BY c.name
        """
        categories = self.execute_query(query, fetch=True)
        
        if categories:
            headers = ["ID", "Name", "Description", "Product Count"]
            table_data = [
                [c['category_id'], c['name'], 
                 c['description'][:30] + "..." if c['description'] and len(c['description']) > 30 else c['description'], 
                 c['product_count']]
                for c in categories
            ]
            
            print("\n" + tabulate(table_data, headers=headers, tablefmt="grid"))
        else:
            print("No categories found.")
    
    def add_category(self):
        """Add a new product category"""
        name = input("Enter category name: ")
        description = input("Enter category description: ")
        
        query = "INSERT INTO categories (name, description) VALUES (%s, %s)"
        result = self.execute_query(query, (name, description))
        
        if result:
            print(f"Category '{name}' added successfully.")
        else:
            print("Failed to add category.")
    
    def generate_reports(self):
        """Generate various inventory reports"""
        print("\n===== Reports =====")
        print("1. Low Stock Items")
        print("2. High Value Items")
        print("3. Sales Summary")
        print("4. Category Summary")
        print("0. Back to Main Menu")
        
        choice = input("Select report: ")
        
        if choice == '1':
            # Low stock items (less than 10 units)
            query = """
            SELECT p.name, i.quantity, c.name as category
            FROM inventory i
            JOIN products p ON i.product_id = p.product_id
            JOIN categories c ON p.category_id = c.category_id
            WHERE i.quantity < 10
            ORDER BY i.quantity
            """
            items = self.execute_query(query, fetch=True)
            
            if items:
                headers = ["Product", "Quantity", "Category"]
                table_data = [[item['name'], item['quantity'], item['category']] for item in items]
                
                print("\n===== Low Stock Items (Less than 10 units) =====")
                print(tabulate(table_data, headers=headers, tablefmt="grid"))
            else:
                print("No low stock items found.")
                
        elif choice == '2':
            # High value items (top 10 by total value)
            query = """
            SELECT p.name, i.quantity, p.price, (p.price * i.quantity) as total_value
            FROM inventory i
            JOIN products p ON i.product_id = p.product_id
            ORDER BY total_value DESC
            LIMIT 10
            """
            items = self.execute_query(query, fetch=True)
            
            if items:
                headers = ["Product", "Quantity", "Unit Price", "Total Value"]
                table_data = [
                    [item['name'], item['quantity'], f"${item['price']:.2f}", f"${item['total_value']:.2f}"]
                    for item in items
                ]
                
                print("\n===== High Value Items (Top 10) =====")
                print(tabulate(table_data, headers=headers, tablefmt="grid"))
            else:
                print("No inventory data found.")
                
        elif choice == '3':
            # Sales summary (last 30 days)
            query = """
            SELECT p.name, SUM(t.quantity) as units_sold, 
                   SUM(t.quantity * p.price) as revenue
            FROM transactions t
            JOIN products p ON t.product_id = p.product_id
            WHERE t.transaction_type = 'sale'
            AND t.transaction_date >= DATE_SUB(CURRENT_DATE, INTERVAL 30 DAY)
            GROUP BY p.product_id
            ORDER BY revenue DESC
            """
            sales = self.execute_query(query, fetch=True)
            
            if sales:
                headers = ["Product", "Units Sold", "Revenue"]
                table_data = [
                    [sale['name'], sale['units_sold'], f"${sale['revenue']:.2f}"]
                    for sale in sales
                ]
                
                total_revenue = sum(sale['revenue'] for sale in sales)
                
                print("\n===== Sales Summary (Last 30 Days) =====")
                print(tabulate(table_data, headers=headers, tablefmt="grid"))
                print(f"\nTotal Revenue: ${total_revenue:.2f}")
            else:
                print("No sales data found for the last 30 days.")
                
        elif choice == '4':
            # Category summary
            query = """
            SELECT c.name as category, COUNT(p.product_id) as product_count,
                   SUM(i.quantity) as total_units,
                   SUM(p.price * i.quantity) as total_value
            FROM categories c
            LEFT JOIN products p ON c.category_id = p.category_id
            LEFT JOIN inventory i ON p.product_id = i.product_id
            GROUP BY c.category_id
            ORDER BY total_value DESC
            """
            categories = self.execute_query(query, fetch=True)
            
            if categories:
                headers = ["Category", "Products", "Total Units", "Total Value"]
                table_data = [
                    [cat['category'], cat['product_count'], 
                     cat['total_units'] if cat['total_units'] else 0,
                     f"${cat['total_value']:.2f}" if cat['total_value'] else "$0.00"]
                    for cat in categories
                ]
                
                print("\n===== Category Summary =====")
                print(tabulate(table_data, headers=headers, tablefmt="grid"))
            else:
                print("No category data found.")
    
    def run(self):
        """Run the main application loop"""
        while True:
            choice = self.display_menu()
            
            if choice == '1':
                self.view_products()
            elif choice == '2':
                self.add_product()
            elif choice == '3':
                self.update_product()
            elif choice == '4':
                self.delete_product()
            elif choice == '5':
                self.view_inventory()
            elif choice == '6':
                self.update_inventory()
            elif choice == '7':
                self.record_transaction()
            elif choice == '8':
                self.view_transactions()
            elif choice == '9':
                self.view_categories()
            elif choice == '10':
                self.add_category()
            elif choice == '11':
                self.generate_reports()
            elif choice == '0':
                print("Thank you for using the Inventory Management System. Goodbye!")
                break
            else:
                print("Invalid choice. Please try again.")
            
            input("\nPress Enter to continue...")
    
    def close_connection(self):
        """Close the database connection"""
        if self.connection:
            self.connection.close()

if __name__ == "__main__":
    print("Starting Inventory Management System...")
    
    # Check if database exists
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        conn.close()
    except Error as e:
        print("Database not set up. Please run setup_database.py first.")
        sys.exit(1)
    
    ims = InventoryManagementSystem()
    
    try:
        ims.run()
    except KeyboardInterrupt:
        print("\nProgram terminated by user.")
    finally:
        ims.close_connection()
