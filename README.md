# Bookstore API

![License](https://img.shields.io/badge/license-MIT-green)
![Build](https://img.shields.io/badge/build-passing-brightgreen)

## Introduction

The **Bookstore API** is a FastAPI-based system for managing books, customers, and sales. It provides endpoints for CRUD operations on book inventory, customer data, and sales records. Additionally, it allows viewing total sales grouped by book genres.

## Features

- **Books**: Add, update, delete, and fetch books.
- **Customers**: Manage customer details.
- **Sales**: Record and retrieve sales transactions.
- **Sales Insights**: View total sales grouped by book genres.

## Prerequisites

Before running this project, ensure you have the following installed:

- **Python 3.9+**
- **SQLite**

## Installation

1. **Clone the repository**:
```
   git clone https://github.com/Marius-DeltaTime/fastapi-bookstore.git
   cd fastapi-bookstore
```

2.  **Set up a virtual environment (optional but recommended)**:
```
python -m venv env
source env/bin/activate  
```
  On Windows, use `env\Scripts\activate`

3. **Install dependencies**:
```
pip install -r requirements.txt
```

4. **Create the SQLite database**: Ensure the bookstore.db file exists. If not, initialize it with the following SQL:
```
CREATE TABLE Books (
    BookID INTEGER PRIMARY KEY,
    Title TEXT NOT NULL,
    Author TEXT NOT NULL,
    Genre TEXT NOT NULL,
    Price REAL NOT NULL,
    Stock INTEGER NOT NULL
);

CREATE TABLE Customers (
    CustomerID INTEGER PRIMARY KEY,
    Name TEXT NOT NULL,
    Email TEXT NOT NULL,
    Phone TEXT NOT NULL
);

CREATE TABLE Sales (
    SaleID INTEGER PRIMARY KEY,
    BookID INTEGER NOT NULL,
    CustomerID INTEGER NOT NULL,
    SaleDate TEXT NOT NULL,
    Quantity INTEGER NOT NULL,
    TotalAmount REAL NOT NULL,
    FOREIGN KEY (BookID) REFERENCES Books (BookID),
    FOREIGN KEY (CustomerID) REFERENCES Customers (CustomerID)
);
```
5. **Run the application**:
```
    uvicorn main:app --reload
```

## Usage

Access the API at [http://127.0.0.1:8000](http://127.0.0.1:8000/docs#/). Use tools like Postman, cURL, or a browser to test the endpoints.

### Example Endpoints

* **Get all books**:
  `GET /books`
  
* **Add a new book**:
  `POST /books`
```
  {
      "title": "New Book",
      "author": "Author Name",
      "genre": "Genre",
      "price": 10.99,
      "stock": 20
  }
```
* **View sales by genre**:
  `GET /sales/total-by-genre`
