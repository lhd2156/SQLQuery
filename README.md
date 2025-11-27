# Library Management Base System (LMS)

A simple Library Management System built with SQLite and Python.  
The project includes:
- A SQLite database with tables for books, borrowers, branches, authors, and loans.
- CSV data import to populate all tables.
- SQL queries to support book checkouts, returns, late tracking, and reporting.
- A Python GUI to interact with the LMS database.

## Features
- Add borrowers, books, and authors.
- Checkout books and update available copies.
- Track due dates, return dates, and compute late fees.
- View book information, borrower information, and loan history.
- Query loans within date ranges and display late returns.

## How to Run
1. Build the database:
```
sqlite3
.open lbms.db
.read tables.sql
.mode csv
.read load.sql
.read task1.sql
.quit
```

2. Run the GUI:
```
python gui.py
```

## Project Structure
- tables.sql — Creates all LMS tables  
- load.sql — Imports CSV data  
- task1.sql — SQL enhancements and view creation  
- gui.py — Python application interface  
- LMSDataset/ — Folder containing all CSV files  

This project demonstrates SQL database design, Python integration, and GUI-based interaction with a relational database.
