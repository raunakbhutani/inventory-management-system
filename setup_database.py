import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

# Database configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'charset': 'utf8mb4',
    'use_pure': True
}

# Database and table creation queries
CREATE_DB_QUERY = "CREATE DATABASE IF NOT EXISTS inventory_management"

CREATE_CATEGORIES_TABLE = """
CREATE TABLE IF NOT EXISTS categories (
    category_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
"""

CREATE_PRODUCTS_TABLE = """
CREATE TABLE IF NOT EXISTS products (
    product_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    price DECIMAL(10, 2) NOT NULL,
    category_id INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES categories(category_id)
)
"""

CREATE_INVENTORY_TABLE = """
CREATE TABLE IF NOT EXISTS inventory (
    inventory_id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT NOT NULL,
    quantity INT NOT NULL DEFAULT 0,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(product_id)
)
"""

CREATE_TRANSACTIONS_TABLE = """
CREATE TABLE IF NOT EXISTS transactions (
    transaction_id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT NOT NULL,
    quantity INT NOT NULL,
    transaction_type ENUM('sale', 'restock') NOT NULL,
    transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes TEXT,
    FOREIGN KEY (product_id) REFERENCES products(product_id)
)
"""

# Sample data
SAMPLE_CATEGORIES = [
    ("Electronics", "Electronic devices and accessories"),
    ("Clothing", "Apparel and fashion items"),
    ("Books", "Books and publications"),
    ("Home & Kitchen", "Home and kitchen appliances and accessories")
]

SAMPLE_PRODUCTS = [
    ("Laptop", "High-performance laptop with 16GB RAM", 1200.00, 1),
    ("Smartphone", "Latest model with 128GB storage", 800.00, 1),
    ("T-shirt", "Cotton t-shirt, available in multiple colors", 25.99, 2),
    ("Jeans", "Denim jeans, slim fit", 45.50, 2),
    ("Python Programming", "Comprehensive guide to Python", 35.00, 3),
    ("Coffee Maker", "Automatic coffee maker with timer", 89.99, 4)
]

SAMPLE_INVENTORY = [
    (1, 20),  # 20 Laptops
    (2, 30),  # 30 Smartphones
    (3, 100), # 100 T-shirts
    (4, 50),  # 50 Jeans
    (5, 25),  # 25 Python Programming books
    (6, 15)   # 15 Coffee Makers
]

def create_connection(db_name=None):
    """Create a database connection to MySQL server"""
    conn = None
    try:
        config = DB_CONFIG.copy()
        if db_name:
            config['database'] = db_name
        
        conn = mysql.connector.connect(**config)
        print(f"Connected to MySQL{'/' + db_name if db_name else ''}")
        return conn
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

def execute_query(connection, query, params=None):
    """Execute a query on the given connection"""
    cursor = connection.cursor()
    try:
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        connection.commit()
        return cursor
    except Error as e:
        print(f"Error executing query: {e}")
        return None
    finally:
        cursor.close()

def create_database():
    """Create the database if it doesn't exist"""
    conn = create_connection()
    if conn:
        execute_query(conn, CREATE_DB_QUERY)
        conn.close()

def create_tables():
    """Create tables in the database"""
    conn = create_connection("inventory_management")
    if conn:
        print("Creating tables...")
        execute_query(conn, CREATE_CATEGORIES_TABLE)
        execute_query(conn, CREATE_PRODUCTS_TABLE)
        execute_query(conn, CREATE_INVENTORY_TABLE)
        execute_query(conn, CREATE_TRANSACTIONS_TABLE)
        conn.close()
        print("Tables created successfully")

def insert_sample_data():
    """Insert sample data into the tables"""
    conn = create_connection("inventory_management")
    if conn:
        print("Inserting sample data...")
        
        # Insert categories
        for category in SAMPLE_CATEGORIES:
            execute_query(conn, "INSERT INTO categories (name, description) VALUES (%s, %s)", category)
        
        # Insert products
        for product in SAMPLE_PRODUCTS:
            execute_query(conn, "INSERT INTO products (name, description, price, category_id) VALUES (%s, %s, %s, %s)", product)
        
        # Insert inventory
        for item in SAMPLE_INVENTORY:
            execute_query(conn, "INSERT INTO inventory (product_id, quantity) VALUES (%s, %s)", item)
        
        conn.close()
        print("Sample data inserted successfully")

def main():
    print("Setting up the Inventory Management System database...")
    create_database()
    create_tables()
    
    # Ask user if they want to insert sample data
    choice = input("Do you want to insert sample data? (y/n): ").lower()
    if choice == 'y':
        insert_sample_data()
    
    print("Database setup completed!")

if __name__ == "__main__":
    main()
