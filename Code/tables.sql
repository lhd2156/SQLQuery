CREATE TABLE IF NOT EXISTS PUBLISHER (
    publisher_name VARCHAR(255) PRIMARY KEY,
    phone VARCHAR(20) NOT NULL,
    address TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS LIBRARY_BRANCH (
    branch_id INTEGER PRIMARY KEY AUTOINCREMENT,
    branch_name VARCHAR(255) NOT NULL,
    branch_address TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS BORROWER (
    card_no INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(255) NOT NULL,
    address TEXT NOT NULL,
    phone VARCHAR(20) NOT NULL
);

CREATE TABLE IF NOT EXISTS BOOK (
    book_id INTEGER PRIMARY KEY AUTOINCREMENT,
    title VARCHAR(255) NOT NULL,
    book_publisher VARCHAR(255) NOT NULL,
    FOREIGN KEY(book_publisher) REFERENCES PUBLISHER(publisher_name)
);

CREATE TABLE IF NOT EXISTS BOOK_AUTHORS (
    book_id INTEGER NOT NULL,
    author_name VARCHAR(255) NOT NULL,
    PRIMARY KEY(book_id, author_name),
    FOREIGN KEY(book_id) REFERENCES BOOK(book_id)
);

CREATE TABLE IF NOT EXISTS BOOK_LOANS (
    book_id INTEGER NOT NULL,
    branch_id INTEGER NOT NULL,
    card_no INTEGER NOT NULL,
    date_out DATE NOT NULL,
    due_date DATE NOT NULL,
    returned_date DATE NOT NULL,
    PRIMARY KEY(book_id, branch_id, card_no),
    FOREIGN KEY(book_id) REFERENCES BOOK(book_id),
    FOREIGN KEY(branch_id) REFERENCES LIBRARY_BRANCH(branch_id),
    FOREIGN KEY(card_no) REFERENCES BORROWER(card_no)
);

CREATE TABLE IF NOT EXISTS BOOK_COPIES (
    book_id INTEGER NOT NULL,
    branch_id INTEGER NOT NULL,
    no_of_copies INTEGER NOT NULL,
    PRIMARY KEY(book_id, branch_id),
    FOREIGN KEY(book_id) REFERENCES BOOK(book_id),
    FOREIGN KEY(branch_id) REFERENCES LIBRARY_BRANCH(branch_id)
);
