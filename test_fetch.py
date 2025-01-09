import sqlite3

# Database connection function
def get_db_connection():
    DATABASE = "bookstore.db"
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# Test function to fetch books
def test_get_books():
    conn = get_db_connection()
    books = conn.execute("SELECT * FROM Books").fetchall()
    conn.close()

    # Convert rows to dictionaries
    book_list = [dict(book) for book in books]
    return book_list

# Run the test
if __name__ == "__main__":
    try:
        books = test_get_books()
        print("Books fetched successfully:")
        for book in books:
            print(book)
    except Exception as e:
        print(f"An error occurred: {e}")
