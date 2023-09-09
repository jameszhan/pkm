




````bash
$ sqlite3 ptpress_origin_books.db ".dump book" > book.sql
$ sqlite3 ptpress_authors.db ".dump author" > author.sql
$ sqlite3 ptpress_authors.db ".dump book_author" > book_author.sql

$ sqlite3 ptpress.db < book.sql
$ sqlite3 ptpress.db < author.sql
$ sqlite3 ptpress.db < book_author.sql
````