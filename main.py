from fastapi import FastAPI, HTTPException
# Needs further testing
# Should ensure that any book created or updated via the API will have a price of at least 0 and a stock of at least 0
from pydantic import BaseModel, Field

class Book(BaseModel):
    title: str
    author: str
    genre: str
    price: float = Field(..., ge=0, description="Price must be non-negative")
    stock: int = Field(..., ge=0, description="Stock must be non-negative")

import sqlite3
from typing import List

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
def get_books():
    conn = get_db_connection()
    books = conn.execute("SELECT * FROM Books").fetchall()
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
def get_customers():
    conn = get_db_connection()
    customers = conn.execute("SELECT * FROM Customers").fetchall()
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

# Routes for Sales
@app.post("/sales")
def add_sale(sale: Sale):
    conn = get_db_connection()
    conn.execute(
        "INSERT INTO Sales (BookID, CustomerID, SaleDate, Quantity, TotalAmount) VALUES (?, ?, ?, ?, ?)",
        (sale.book_id, sale.customer_id, sale.sale_date, sale.quantity, sale.total_amount),
    )
    conn.commit()
    conn.close()
    return {"message": "Sale recorded successfully"}

@app.get("/sales/total-by-genre")
def total_sales_by_genre():
    conn = get_db_connection()
    sales = conn.execute(
        """
        SELECT Genre, SUM(S.TotalAmount) AS TotalSales
        FROM Sales S
        JOIN Books B ON S.BookID = B.BookID
        GROUP BY Genre
        """
    ).fetchall()
    conn.close()
    return [dict(sale) for sale in sales]

@app.get("/books/search")
def search_books(query: str):
    """
    Search for books by title or author.
    :param query: The search term.
    :return: A list of books that match the query.
    """
    conn = get_db_connection()
    books = conn.execute(
        """
        SELECT * FROM Books
        WHERE Title LIKE ? OR Author LIKE ?
        """,
        (f"%{query}%", f"%{query}%"),
    ).fetchall()
    conn.close()

    if not books:
        raise HTTPException(status_code=404, detail="No books found matching the query.")

    return [dict(book) for book in books]

@app.get("/books/genre/{genre}", response_model=List[Book])
def get_books_by_genre(genre: str):
    conn = get_db_connection()
    books = conn.execute(
        "SELECT * FROM Books WHERE Genre = ?", (genre,)
    ).fetchall()
    conn.close()
    return [dict(book) for book in books]



# Run the application using Uvicorn
# Command: uvicorn script_name:app --reload
