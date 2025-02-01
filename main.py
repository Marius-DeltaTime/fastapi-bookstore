from fastapi import FastAPI, HTTPException
import sqlite3
from typing import List
from pydantic import BaseModel, Field
import random

class Book(BaseModel):
    title: str
    author: str
    genre: str
    price: float = Field(..., ge=0, description="Price must be non-negative")
    stock: int = Field(..., ge=0, description="Stock must be non-negative")

# Initialize the FastAPI app
app = FastAPI()

# Connect to the SQLite database
DATABASE = "bookstore.db"

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# Models for request validation and responses
class Book(BaseModel):
    book_id: int
    title: str
    author: str
    genre: str
    price: float
    stock: int

class Customer(BaseModel):
    customer_id: int
    name: str
    email: str
    phone: str

class Sale(BaseModel):
    book_id: int
    customer_id: int
    sale_date: str  # Use 'YYYY-MM-DD' format
    quantity: int
    total_amount: float

# Routes for Books
@app.get("/books", response_model=List[Book])
def get_books(limit: int = 10, offset: int = 0):
    conn = get_db_connection()
    books = conn.execute(
        "SELECT * FROM Books LIMIT ? OFFSET ?", (limit, offset)
    ).fetchall()
    conn.close()
    return [
        {
            "book_id": book["BookID"],
            "title": book["Title"],
            "author": book["Author"],
            "genre": book["Genre"],
            "price": book["Price"],
            "stock": book["Stock"],
        }
        for book in books
    ]

@app.post("/books")
def add_book(book: Book):
    conn = get_db_connection()
    conn.execute(
        "INSERT INTO Books (Title, Author, Genre, Price, Stock) VALUES (?, ?, ?, ?, ?)",
        (book.title, book.author, book.genre, book.price, book.stock),
    )
    conn.commit()
    conn.close()
    return {"message": "Book added successfully"}

@app.put("/books/{book_id}")
def update_book(book_id: int, book: Book):
    conn = get_db_connection()
    conn.execute(
        "UPDATE Books SET Title = ?, Author = ?, Genre = ?, Price = ?, Stock = ? WHERE BookID = ?",
        (book.title, book.author, book.genre, book.price, book.stock, book_id),
    )
    conn.commit()
    conn.close()
    return {"message": "Book updated successfully"}

@app.delete("/books/{book_id}")
def delete_book(book_id: int):
    conn = get_db_connection()
    conn.execute("DELETE FROM Books WHERE BookID = ?", (book_id,))
    conn.commit()
    conn.close()
    return {"message": "Book deleted successfully"}

# Routes for Customers
@app.get("/customers", response_model=List[Customer])
def get_customers(limit: int = 10, offset: int = 0):
    conn = get_db_connection()
    customers = conn.execute(
        "SELECT * FROM Customers LIMIT ? OFFSET ?", (limit, offset)
    ).fetchall()
    conn.close()
    return [
        {
            "customer_id": customer["CustomerID"],
            "name": customer["Name"],
            "email": customer["Email"],
            "phone": customer["Phone"],
        }
        for customer in customers
    ]

@app.post("/customers")
def add_customer(customer: Customer):
    conn = get_db_connection()
    conn.execute(
        "INSERT INTO Customers (Name, Email, Phone) VALUES (?, ?, ?)",
        (customer.name, customer.email, customer.phone),
    )
    conn.commit()
    conn.close()
    return {"message": "Customer added successfully"}

@app.put("/customers/{customer_id}")
def update_customer(customer_id: int, customer: Customer):
    conn = get_db_connection()
    conn.execute(
        "UPDATE Customers SET Name = ?, Email = ?, Phone = ? WHERE CustomerID = ?",
        (customer.name, customer.email, customer.phone, customer_id),
    )
    conn.commit()
    conn.close()
    return {"message": "Customer updated successfully"}

@app.delete("/customers/{customer_id}")
def delete_customer(customer_id: int):
    conn = get_db_connection()
    conn.execute("DELETE FROM Customers WHERE CustomerID = ?", (customer_id,))
    conn.commit()
    conn.close()
    return {"message": "Customer deleted successfully"}

# Routes for Sales
@app.post("/sales")
def add_sale(sale: Sale):
    conn = get_db_connection()
    # Check if the book exists and has enough stock
    book = conn.execute(
        "SELECT Stock FROM Books WHERE BookID = ?", (sale.book_id,)
    ).fetchone()

    if not book:
        conn.close()
        raise HTTPException(status_code=404, detail="Book not found.")

    if book["Stock"] < sale.quantity:
        conn.close()
        raise HTTPException(status_code=400, detail="Not enough stock available.")

    # Record the sale
    conn.execute(
        "INSERT INTO Sales (BookID, CustomerID, SaleDate, Quantity, TotalAmount) VALUES (?, ?, ?, ?, ?)",
        (sale.book_id, sale.customer_id, sale.sale_date, sale.quantity, sale.total_amount),
    )
    # Update the stock
    conn.execute(
        "UPDATE Books SET Stock = Stock - ? WHERE BookID = ?",
        (sale.quantity, sale.book_id),
    )
    conn.commit()
    conn.close()
    return {"message": "Sale recorded successfully, and stock updated."}

@app.get("/sales/book/{book_id}")
def get_total_sales_by_book(book_id: int):
    """
    Get the total sales revenue and quantity sold for a specific book.
    """
    conn = get_db_connection()
    sales = conn.execute
    (
        """
        SELECT SUM(S.Quantity) AS TotalQuantity, SUM(S.TotalAmount) AS TotalRevenue
        FROM Sales S
        WHERE S.BookID = ?
        """,
        (book_id,),
    ).fetchone()
    conn.close()

    if not sales or sales["TotalQuantity"] is None:
        raise HTTPException(status_code=404, detail="No sales found for this book.")

    return 
    {
        "book_id": book_id,
        "total_quantity_sold": sales["TotalQuantity"],
        "total_revenue": sales["TotalRevenue"],
    }

@app.get("/sales/top-books")
def get_top_selling_books(limit: int = 5):
    """
    Get the top-selling books based on total quantity sold.
    """
    conn = get_db_connection()
    books = conn.execute(
        """
        SELECT B.BookID, B.Title, B.Author, B.Genre, SUM(S.Quantity) AS TotalSold
        FROM Sales S
        JOIN Books B ON S.BookID = B.BookID
        GROUP BY B.BookID
        ORDER BY TotalSold DESC
        LIMIT ?
        """,
        (limit,),
    ).fetchall()
    conn.close()

    if not books:
        raise HTTPException(status_code=404, detail="No sales data available.")

    return [dict(book) for book in books]


