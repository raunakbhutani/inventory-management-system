# Inventory Management System

A simple inventory management system built with Python and MySQL.

## Overview

This project demonstrates how to create a database-driven application using MySQL and Python. The system allows users to:

- Add, update, and delete products
- Track inventory levels
- Record transactions (sales and restocks)
- Generate reports

## Technologies Used

- MySQL: Relational database for storing inventory data
- Python: Backend programming language
- mysql-connector-python: Python library for connecting to MySQL databases
- Tabulate: For formatting console output in a readable table format

## Setup Instructions

1. Install MySQL Server if not already installed
2. Install required Python packages: `pip install -r requirements.txt`
3. Run the setup script to create the database and tables: `python setup_database.py`
4. Run the main application: `python app.py`

## Database Schema

The database consists of the following tables:

- Products: Stores product information (ID, name, description, price)
- Inventory: Tracks current stock levels for each product
- Transactions: Records all inventory movements (sales, restocks)
- Categories: Product categorization

## Features

- User-friendly command-line interface
- Data validation and error handling
- Transaction logging
- Basic reporting capabilities
