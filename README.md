# Inventory Management System

A comprehensive inventory management system built with Flask, SQLite, and MongoDB. The application helps track items across different departments including Accounts, Sales & Purchases, IT & Marketing, and Masters and Costings.

## Features

- Department-wise inventory tracking
- Item condition monitoring
- Real-time quantity updates
- Modern and responsive UI using Bootstrap
- Easy item addition and updates
- Department overview with total item counts

## Prerequisites

- Python 3.8 or higher
- MongoDB (running on localhost:27017)
- pip (Python package manager)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd inventory-management-system
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install the required packages:
```bash
pip install -r requirements.txt
```

4. Make sure MongoDB is running on your system.

## Running the Application

1. Start the Flask application:
```bash
python app.py
```

2. Open your web browser and navigate to:
```
http://localhost:5000
```

## Usage

1. The home page shows an overview of all departments
2. Click on a department to view its items
3. Use the "Add Item" button to add new items
4. Click the edit icon to update item details
5. Items are color-coded based on their condition:
   - Green: Good
   - Yellow: Fair
   - Red: Poor

## Database Structure

- SQLite: Stores department and item information
- MongoDB: Stores additional metadata and historical data

## Contributing

Feel free to submit issues and enhancement requests!

