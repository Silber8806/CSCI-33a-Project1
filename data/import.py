import csv
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


def main():
    f = open("books.csv")
    reader = csv.reader(f)

    next(reader)

    print("Starting truncate and load procedure...")
    db.execute("TRUNCATE BOOKS_STG")

    i = 0
    print("Starting staging process...")
    for isbn, title, author, year in reader:
        # I did this, because it was demonstrated in class..
        # please for your own future benefit, use a loader and don't print to stdout...5000 rows...insane time.
        db.execute(
            "INSERT INTO BOOKS_STG (book_isbn, book_name, book_author, book_year) VALUES (:book_isbn, :book_name, :book_author, :book_year)",
            {"book_isbn": isbn, "book_name": title, "book_author": author, "book_year": year})
        i += 1
        print(f"Added row {i} {title},{isbn},{author},{year} to BOOKS_STG TABLE")

    print("Committed data...")
    db.commit()

    print("Merging data with final BOOK table...")
    # not happy with this, but not production...
    merge_sql = """
        INSERT INTO BOOKS (book_isbn, book_name, book_author, book_year)
        SELECT
            book_isbn,
            book_name,
            book_author,
            book_year
        from BOOKS_STG bs
        where not exists ( SELECT 1 
						    from BOOKS b where 
						       bs.book_isbn = b.book_isbn and
                               bs.book_name = b.book_name and
                               bs.book_author = b.book_author and
                               bs.book_year = b.book_year
                           )
    """

    db.execute(merge_sql)

    print("Committed data...")
    db.commit()


if __name__ == "__main__":
    main()
