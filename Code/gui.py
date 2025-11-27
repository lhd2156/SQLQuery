import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox

# create_tables() function hmmm i wonder what this function does
def create_tables():
    conn = sqlite3.connect("lbms.db")
    cursor = conn.cursor()

    # Create tables
    cursor.execute('''CREATE TABLE IF NOT EXISTS PUBLISHER(
                    publisher_name TEXT PRIMARY KEY,
                    phone TEXT NOT NULL,
                    address TEXT NOT NULL
                    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS LIBRARY_BRANCH(
                    branch_id INTEGER PRIMARY KEY,
                    branch_name TEXT NOT NULL,
                    branch_address TEXT NOT NULL
                    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS BORROWER(
                    card_no INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    address TEXT NOT NULL,
                    phone TEXT NOT NULL
                    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS BOOK(
                    book_id INTEGER PRIMARY KEY,
                    title TEXT NOT NULL,
                    book_publisher TEXT NOT NULL,
                    FOREIGN KEY(book_publisher) REFERENCES PUBLISHER(publisher_name)
                    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS BOOK_LOANS(
                    book_id INTEGER NOT NULL,
                    branch_id INTEGER NOT NULL,
                    card_no INTEGER NOT NULL,
                    date_out DATE NOT NULL,
                    due_date DATE NOT NULL,
                    Returned_date DATE,
                    PRIMARY KEY(book_id, branch_id, card_no),
                    FOREIGN KEY(book_id) REFERENCES BOOK(book_id),
                    FOREIGN KEY(branch_id) REFERENCES LIBRARY_BRANCH(branch_id),
                    FOREIGN KEY(card_no) REFERENCES BORROWER(card_no)
                    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS BOOK_COPIES(
                    book_id INTEGER NOT NULL,
                    branch_id INTEGER NOT NULL,
                    no_of_copies INTEGER NOT NULL,
                    PRIMARY KEY(book_id, branch_id),
                    FOREIGN KEY(book_id) REFERENCES BOOK(book_id),
                    FOREIGN KEY(branch_id) REFERENCES LIBRARY_BRANCH(branch_id)
                    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS BOOK_AUTHORS(
                    book_id INTEGER NOT NULL,
                    author_name TEXT NOT NULL,
                    PRIMARY KEY(book_id, author_name),
                    FOREIGN KEY(book_id) REFERENCES BOOK(book_id)
                    )''')

    conn.commit()
    conn.close()
    # # Debug Info
    # print("Tables created successfully!")

# Query 1 gui function
def create_query1_gui(root, listing):
    frame = ttk.Frame(listing)
    listing.add(frame, text = "Query 1")

    # Add the query name
    ttk.Label(
        frame,
        text = "Query 1: Allow the user to check a book out",
        font = ("Arial", 12, "bold"),
        anchor = "center",
        justify = "center"
    ).grid(row = 0, column = 0, columnspan = 3, pady = 10)

    # Creates our labels and entry fields per usual yk as requested by the query
    ttk.Label(frame, text = "Card Number:", font = ("Arial", 10)).grid(row = 1, column = 0, padx = 5, pady = 3, sticky = tk.E)
    card_number_entry = ttk.Entry(frame, width = 30)
    card_number_entry.grid(row = 1, column = 1, padx = 5, pady = 3, sticky = tk.W)

    ttk.Label(frame, text = "Book Title:", font = ("Arial", 10)).grid(row = 2, column = 0, padx = 5, pady = 3, sticky = tk.E)
    book_title_combobox = ttk.Combobox(frame, width = 28)
    book_title_combobox.grid(row = 2, column = 1, padx = 5, pady = 3, sticky = tk.W)

    ttk.Label(frame, text="Date Out (YYYY-MM-DD):", font = ("Arial", 10)).grid(row = 3, column = 0, padx = 5, pady = 3, sticky = tk.E)
    date_out_entry = ttk.Entry(frame, width = 30)
    date_out_entry.grid(row = 3, column = 1, padx = 5, pady = 3, sticky = tk.W)

    ttk.Label(frame, text = "Due Date (YYYY-MM-DD):", font = ("Arial", 10)).grid(row = 4, column = 0, padx = 5, pady = 3, sticky = tk.E)
    due_date_entry = ttk.Entry(frame, width = 30)
    due_date_entry.grid(row = 4, column = 1, padx = 5, pady = 3, sticky = tk.W)

    ttk.Label(frame, text="Returned Date (YYYY-MM-DD):", font = ("Arial", 10)).grid(row = 5, column = 0, padx = 5, pady = 3, sticky = tk.E)
    returned_date_entry = ttk.Entry(frame, width = 30)
    returned_date_entry.grid(row = 5, column = 1, padx = 5, pady = 3, sticky = tk.W)


    # update_books() function actively updates the database at the start
    def update_books():
        # Connect to the database
        conn = sqlite3.connect("lbms.db")
        cursor = conn.cursor()

        # Grab book titles from the BOOK table and store
        cursor.execute("SELECT title FROM BOOK")
        books = [row[0] for row in cursor.fetchall()]

        # Close the connection
        conn.close()

        # Update the combobox (dropdown menu) with provided titles
        book_title_combobox["values"] = books


    # checkout_booK() function obviously checks the book out
    def checkout_book():
        # Get all needed input values from the fields
        card_number = card_number_entry.get()
        book_title = book_title_combobox.get()
        date_out = date_out_entry.get()
        due_date = due_date_entry.get()
        returned_date = returned_date_entry.get()

        # Have to make sure that all are filled in, otherwise it won't even run
        if not (card_number and book_title and date_out and due_date and returned_date):
            messagebox.showerror("Error", "All fields are required!")
            return

        try:
            # Connect to the database per usual
            conn = sqlite3.connect("lbms.db")
            cursor = conn.cursor()

            # Creating a trigger that takes one copy away
            cursor.execute('''
                    CREATE TRIGGER IF NOT EXISTS update_copies_after_checkout
                    AFTER INSERT ON BOOK_LOANS
                    BEGIN
                        UPDATE BOOK_COPIES
                        SET no_of_copies = no_of_copies - 1
                        WHERE book_id = NEW.book_id AND branch_id = NEW.branch_id;
                    END;
            ''')

            # Get the book_id for the selected book title (From the dropdown menu)
            cursor.execute("SELECT book_id FROM BOOK WHERE title = ?", (book_title,))
            book_id = cursor.fetchone()

            # Statement will check if a book is not found
            if not book_id:
                messagebox.showerror("Error", "Selected book not found")
                return
            # Return the data that the user decides to grab
            book_id = book_id[0]

            # Grabs all the branch with available copies
            cursor.execute("SELECT branch_id, no_of_copies FROM BOOK_COPIES WHERE book_id = ? AND no_of_copies > 0", (book_id,))
            branches = cursor.fetchall()

            # Statement checks when no copys are available
            if not branches:
                messagebox.showerror("Error", "No copies that're available for this book in any branch :(")
                return

            # Check if there are multiple branches with available copies
            if len(branches) > 1:
                # Open a new window with needed parameters
                branch_selection_window = tk.Toplevel(root)
                branch_selection_window.title("Select Branch")
                branch_selection_window.geometry("400x200")

                # Show a message in the pop-up that tells the user they gotta pick a branch
                ttk.Label(
                    branch_selection_window,
                    text = "Select a branch:",
                    font = ("Arial", 10)
                ).pack(pady = 10)

                # Create a menu with all of the branches and how many copies they have
                # Like we can take Branch 1 and their copies they have
                branch_menu = ttk.Combobox(
                    branch_selection_window,
                    values = [f"Branch {b[0]} (Copies: {b[1]})" for b in branches]
                )
                branch_menu.pack(pady = 10)

                # inner confirm_branch() just makes checks that they actually picked something when checking out
                def confirm_branch():
                    # Grab the selected input (branch in this case) that the user picked
                    branch_selected = branch_menu.get()
                    # Statement checks if a branch has been selected or not
                    if not branch_selected:
                        messagebox.showerror("Error", "You must select a branch!")
                        return
                    # Just grab the branch number (such as if we are given 1), cast that number to int
                    branch_id = int(branch_selected.split()[1])
                    # Provide an X (close) button that we can use to close the pop-up window
                    branch_selection_window.destroy()
                    # This is a nested function that is ACTUALLY checking something gets picked out
                    checkout_complete(book_id, branch_id, card_number, date_out, due_date, returned_date)

                # This button calls confirm_branch() func which then will call complete_checkout() func

                ttk.Button(branch_selection_window, text="Confirm", command=confirm_branch).pack(pady = 10)
            else:
                # Takes the branch ID, we can't take a tuple
                branch_id = branches[0][0]
                # Check it out per usual
                checkout_complete(book_id, branch_id, card_number, date_out, due_date, returned_date)

        except sqlite3.Error as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

        finally:
                # Close database lbms.db connection
                conn.close()

    # checkout_complete() function just will update it to the window
    def checkout_complete(book_id, branch_id, card_number, date_out, due_date, returned_date):
        try:
            conn = sqlite3.connect("lbms.db")
            cursor = conn.cursor()

            # Give parameters as needed to be shown to the user after a book is checked out
            cursor.execute("INSERT INTO BOOK_LOANS (book_id, branch_id, card_no, date_out, due_date, Returned_date) VALUES (?, ?, ?, ?, ?, ?)",
                           (book_id, branch_id, card_number, date_out, due_date, returned_date))
            conn.commit()
            messagebox.showinfo("Success", f"Book checked out from branch {branch_id}!")

            # Right after they finish clicking the ok button after the messagebox, display
            show_book_copies()
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"An error occurred: {e}")
        finally:
            conn.close()

    # show_book_loans() shows the book loans window
    def show_book_loans():
        # Create the window on top of the gui when the button gets clicked (Tk button at the end of the def func)
        loans_window = tk.Toplevel(root)
        loans_window.title("Book Loans")
        loans_window.geometry("1200x600")
        # The returned data type that we need that is gonna get displayed on the window
        loans_view = ttk.Treeview(loans_window, columns = ("book_id", "branch_id", "card_no", "date_out", "due_date", "returned_date"), show = "headings")
        loans_view.heading("book_id", text = "Book ID")
        loans_view.heading("branch_id", text = "Branch ID")
        loans_view.heading("card_no", text = "Card No")
        loans_view.heading("date_out", text = "Date Out")
        loans_view.heading("due_date", text = "Due Date")
        loans_view.heading("returned_date", text = "Returned Date")
        loans_view.pack(fill=tk.BOTH, expand = True, padx = 5, pady = 5)

        conn = sqlite3.connect("lbms.db")
        cursor = conn.cursor()
        # Grab all the data type being stored in BOOK_LOANS at this time
        cursor.execute("SELECT * FROM BOOK_LOANS")
        rows = cursor.fetchall()
        conn.close()

        # Any rows will get added to the end everytime as new rows
        if rows:
            for row in rows:
                loans_view.insert("", "end", values=row)
        else:
            messagebox.showinfo("No Data", "No book loans found.")

    # show_book_copies_window() function shows the book copies in a window like above^
    def show_book_copies():
        copies_window = tk.Toplevel(root)
        copies_window.title("Book Copies")
        copies_window.geometry("600x400")
        copies_view = ttk.Treeview(copies_window, columns = ("book_id", "branch_id", "no_of_copies"), show = "headings")
        copies_view.heading("book_id", text = "Book ID")
        copies_view.heading("branch_id", text = "Branch ID")
        copies_view.heading("no_of_copies", text = "No. of Copies")
        copies_view.pack(fill = tk.BOTH, expand = True, padx = 5, pady = 5)

        conn = sqlite3.connect("lbms.db")
        cursor = conn.cursor()
        cursor.execute("SELECT book_id, branch_id, no_of_copies FROM BOOK_COPIES")
        rows = cursor.fetchall()
        conn.close()

        if rows:
            for row in rows:
                copies_view.insert("", "end", values=row)
        else:
            messagebox.showinfo("No Data", "No book copies found.")

    # All the needed buttons that have their own function for QUERY 1
    ttk.Button(frame, text = "Checkout Book", command = checkout_book, width = 20).grid(row = 6, column = 0, padx = 10, pady = 10, columnspan = 1)
    ttk.Button(frame, text = "Show Book Loans", command = show_book_loans, width = 20).grid(row = 6, column = 1, padx = 10, pady = 10, columnspan = 1)
    ttk.Button(frame, text = "Show Book Copies", command = show_book_copies, width = 20).grid(row = 6, column = 2, padx = 10, pady = 10, columnspan = 1)

    # Gots to give the GUI the loaded book_titles at the given moment in time
    update_books()

# I think you get the idea, this function just makes query 2
def create_query2_gui(root, listing):
    frame = ttk.Frame(listing)
    listing.add(frame, text = "Query 2")

    # Just like done in query 2, tell the user what they can do
    ttk.Label(
        frame,
        text = "Query 2: Let user add a new borrower",
        font = ("Arial", 12, "bold"),
        anchor = "center",
        justify = "center"
    ).grid(row = 0, column = 0, columnspan = 2, pady = 10)

    # The text labels and entry fields for Query 2 done the same as in Query 1
    ttk.Label(frame, text = "Name:", font = ("Arial", 10)).grid(row = 1, column = 0, padx = 5, pady = 3, sticky = tk.E)
    name_entry = ttk.Entry(frame, width = 30)
    name_entry.grid(row = 1, column = 1, padx = 5, pady = 3, sticky = tk.W)

    ttk.Label(frame, text = "Address:", font = ("Arial", 10)).grid(row = 2, column = 0, padx = 5, pady = 3, sticky = tk.E)
    address_entry = ttk.Entry(frame, width = 30)
    address_entry.grid(row = 2, column = 1, padx = 5, pady = 3, sticky = tk.W)

    ttk.Label(frame, text="Phone:", font = ("Arial", 10)).grid(row = 3, column = 0, padx = 5, pady = 3, sticky = tk.E)
    phone_entry = ttk.Entry(frame, width = 30)
    phone_entry.grid(row = 3, column = 1, padx = 5, pady = 3, sticky = tk.W)

    # add_borrower() adds a new borrower
    def add_borrower():
        # Gets the field wanted, and removes any spaces that aren't necessary
        name = name_entry.get().strip()
        address = address_entry.get().strip()
        phone = phone_entry.get().strip()

        # Make sure that all fields are input
        if not (name and address and phone):
            messagebox.showerror("Error", "All fields are required")
            return

        try:
            conn = sqlite3.connect("lbms.db")
            cursor = conn.cursor()

            # This will add a new borrower to the database
            cursor.execute(
                "INSERT INTO Borrower (name, address, phone) VALUES (?, ?, ?)",
                (name, address, phone),
            )
            conn.commit()

            # Gets the last row of the query, and stores that as the card number
            cursor.execute("SELECT last_insert_rowid();")
            card_no = cursor.fetchone()[0]

            # # Debug
            # print(f"Inserted borrower: {name}, {address}, {phone}")
            # print(f"Generated Card Number: {card_no}")

            # Format card# and give them a new card# to display
            messagebox.showinfo("Success", f"Borrower added successfully! Card Number: {card_no}")

            # Once they put a new borrower in the list, it will clear the input
            name_entry.delete(0, tk.END)
            address_entry.delete(0, tk.END)
            phone_entry.delete(0, tk.END)

        except sqlite3.Error as e:
            messagebox.showerror("Error", f"An error occurred: {e}")
        finally:
            conn.close()

    # Just like any show function we do the same and display as usual, this for borrowers
    def show_borrowers():
        borrowers_window = tk.Toplevel(root)
        borrowers_window.title("All Borrowers")
        borrowers_window.geometry("1000x600")
        # Displays each one as intended per usual like in query 1
        borrowers_view = ttk.Treeview(
            borrowers_window,
            columns = ("card_no", "name", "address", "phone"),
            show = "headings"
        )
        borrowers_view.heading("card_no", text = "Card No")
        borrowers_view.heading("name", text = "Name")
        borrowers_view.heading("address", text = "Address")
        borrowers_view.heading("phone", text = "Phone")
        borrowers_view.pack(fill = tk.BOTH, expand = True, padx = 5, pady = 5)

        try:
            conn = sqlite3.connect("lbms.db")
            cursor = conn.cursor()

            # Grab all of the borrowers, and filter them by ASC
            cursor.execute("SELECT card_no, name, address, phone FROM Borrower ORDER BY card_no ASC")
            rows = cursor.fetchall()

            # # Debug
            # print("Borrowers from database:")

            # for row in rows:
            #     print(row)

            # Go through each row of borrower table
            for row in rows:
                card_no = f"{row[0]:06d}" if row[0] is not None else "000000"
                borrowers_view.insert("", "end", values = (card_no, row[1], row[2], row[3]))
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"An error occurred: {e}")
        finally:
            conn.close()

    # Buttons for query 2
    ttk.Button(frame, text = "Add Borrower", command = add_borrower, width = 20).grid(row = 4, column = 0, padx = 5, pady = 10, sticky = tk.E)
    ttk.Button(frame, text = "Show Borrowers", command = show_borrowers, width = 20).grid(row = 4, column = 1, padx = 5, pady = 15, sticky = tk.W)

# same thing as usual
def create_query3_gui(root, listing):
    frame = ttk.Frame(listing)
    listing.add(frame, text = "Query 3")

    # same thing as usual
    ttk.Label(
        frame,
        text = "Query 3: User can add new book w/ publisher info. Gives 5 copies",
        font = ("Arial", 12, "bold"),
        anchor = "center",
        justify = "center"
    ).grid(row = 0, column = 0, columnspan = 2, pady = 10)


    # same thing as usual
    ttk.Label(frame, text = "Book Title:").grid(row = 1, column = 0, padx = 5, pady = 5, sticky = tk.E)
    book_title_entry = ttk.Entry(frame)
    book_title_entry.grid(row = 1, column = 1, padx = 5, pady = 5)

    ttk.Label(frame, text = "Book Publisher:").grid(row = 2, column = 0, padx = 5, pady = 5, sticky = tk.E)
    book_publisher_entry = ttk.Entry(frame)
    book_publisher_entry.grid(row = 2, column = 1, padx = 5, pady = 5)

    ttk.Label(frame, text = "Author Name:").grid(row = 3, column = 0, padx = 5, pady = 5, sticky = tk.E)
    author_name_entry = ttk.Entry(frame)
    author_name_entry.grid(row = 3, column = 1, padx = 5, pady = 5)


    # add_book() function just adds the book
    def add_book():
        book_title = book_title_entry.get().strip()
        book_publisher = book_publisher_entry.get().strip()
        author_name = author_name_entry.get().strip()

        # Check all fields/parameters are filled in like any other
        if not (book_title and book_publisher and author_name):
            messagebox.showerror("Error", "All fields required")
            return

        try:
            conn = sqlite3.connect("lbms.db")
            cursor = conn.cursor()

            # Inserts a new book title and publisher into BOOK
            cursor.execute("INSERT INTO BOOK(title, book_publisher) VALUES (?, ?)", (book_title, book_publisher))
            conn.commit()

            # Grab all the new book_id of the book that the user put in (new book user put)
            cursor.execute("SELECT book_id FROM BOOK WHERE title = ? AND book_publisher = ?", (book_title, book_publisher))
            selected_book_id = cursor.fetchone()[0]

            # Grab the new author of the book that the user put in
            cursor.execute("INSERT INTO BOOK_AUTHORS(book_id, author_name) VALUES (?, ?)", (selected_book_id, author_name))
            conn.commit()

            # Grabs all of the entireity of the LIBRARY_BRANCH
            cursor.execute("SELECT COUNT(*) FROM LIBRARY_BRANCH")
            # Take the new value that we get from the query result of user and store
            branch_count = cursor.fetchone()[0]

            # Statement provides query of 5 copys of a book for every single branch
            for i in range(1, branch_count + 1):
                cursor.execute("INSERT INTO BOOK_COPIES(book_id, branch_id, no_of_copies) VALUES (?, ?, ?)", (selected_book_id, i, 5))
            conn.commit()

            messagebox.showinfo("Success", f"Book '{book_title}' by {author_name} added successfully!")
            # After completing it all, empty out the spaces
            book_title_entry.delete(0, tk.END)
            book_publisher_entry.delete(0, tk.END)
            author_name_entry.delete(0, tk.END)

        except sqlite3.Error as e:
            messagebox.showerror("Error", f"An error occurred: {e}")
        finally:
            conn.close()

    # show_books_information() will show all the book info needed
    def show_books_information():
        try:
            conn = sqlite3.connect("lbms.db")
            cursor = conn.cursor()

            # this will make sure that we are grabbing the stuff, alias this too much stuff
            cursor.execute('''
                SELECT B.book_id, B.title, B.book_publisher, BA.author_name, BC.branch_id, BC.no_of_copies
                FROM BOOK B
                JOIN BOOK_AUTHORS BA ON B.book_id = BA.book_id
                JOIN BOOK_COPIES BC ON BC.book_id = B.book_id
            ''')
            rows = cursor.fetchall()
            conn.close()

            # Make sure that we have rows existing
            if rows:
                books_window = tk.Toplevel(root)
                books_window.title("Books Information")
                books_window.geometry("1200x600")

                # Create the Treeview per usual
                books_view = ttk.Treeview(books_window, columns = ("book_id", "title", "book_publisher", "author_name", "branch_id", "no_of_copies"), show = "headings")
                books_view.heading("book_id", text = "Book ID")
                books_view.heading("title", text = "Title")
                books_view.heading("book_publisher", text = "Publisher")
                books_view.heading("author_name", text = "Author")
                books_view.heading("branch_id", text = "Branch ID")
                books_view.heading("no_of_copies", text = "Available Copies")
                books_view.pack(fill = tk.BOTH, expand = True, padx = 5, pady = 5)


                # Grab rows and put them at the end per usual
                for row in rows:
                    books_view.insert("", "end", values=row)
            else:
                messagebox.showinfo("No Results", "No books found.")

        except sqlite3.Error as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    # Query 3 buttons per usual
    ttk.Button(frame, text = "Add Book", command = add_book).grid(row = 4, column = 0, padx = 5, pady = 10, sticky = tk.W)
    ttk.Button(frame, text = "Show Books Information", command = show_books_information).grid(row = 4, column = 1, padx = 5, pady = 10, sticky = tk.W)


# same per usual as other querys
def create_query4_gui(root, listing):


    frame = ttk.Frame(listing)
    listing.add(frame, text = "Query 4")

   # per usual
    ttk.Label(
        frame,
        text = "Query 4: Allow user to loan a book of their choice ",
        font = ("Arial", 12, "bold"),
        anchor = "center",
        justify = "center"
    ).grid(row = 0, column = 0, columnspan = 2, pady = 10)

    # Label and entry field for Book Title input
    ttk.Label(frame, text = "Book Title:", font = ("Arial", 10)).grid(row = 1, column = 0, padx = 5, pady = 5, sticky = tk.E)
    book_menu = ttk.Combobox(frame, width = 30)
    book_menu.grid(row = 1, column = 1, padx = 5, pady = 5, sticky = tk.W)


    # Same as query1, have to update the stuff everytime
    def update_books():
        conn = sqlite3.connect("lbms.db")
        cursor = conn.cursor()
        cursor.execute("SELECT title FROM BOOK")
        books = [row[0] for row in cursor.fetchall()]
        conn.close()
        book_menu["values"] = books


    # The input the user selects will get stored here in select_book()
    book_menu.selected_book_title = None

    # select_book() function will select a book
    def select_book():
        # store the exact book that get into this variable
        book_menu.selected_book_title = book_menu.get()

        # You have to select a book title
        if not book_menu.selected_book_title:
            messagebox.showerror("Error", "Please select a book title")
            return
        
        messagebox.showinfo("Book Selected", f"Selected Book: {book_menu.selected_book_title}")

    # Like any show function, show_book_copies_loaned() you HAVE to select a book for it to be displayed
    def show_book_copies_loaned():
        # Gotta select a book
        if not book_menu.selected_book_title:
            messagebox.showerror("Error", "Please select a book first")
            return

        try:
            conn = sqlite3.connect("lbms.db")
            cursor = conn.cursor()

            # Select everything needed for query 4, use alias for long query
            cursor.execute('''SELECT Bk.book_id, Bk.title, B_L.branch_id, L_B.branch_name, COUNT(*) AS num_of_copies_loaned
                              FROM Book AS Bk
                              NATURAL JOIN Book_Loans AS B_L
                              NATURAL JOIN Library_Branch AS L_B
                              WHERE Bk.title = ? 
                              GROUP BY Bk.book_id, Bk.title, B_L.branch_id, L_B.branch_name''', (book_menu.selected_book_title,))
            # Usual, just  get all rows as tuples
            rows = cursor.fetchall()
            conn.close()

            # Check if rows exist in here per usual like in query 3
            if rows:
                # Same as any other
                loan_window = tk.Toplevel(root)
                loan_window.title("Book Copies Loaned")
                loan_window.geometry("1200x800")

                # Same as any other
                loan_view = ttk.Treeview(loan_window, columns = ("book_id", "title", "branch_id", "branch_name", "num_of_copies_loaned"), show = "headings")
                loan_view.heading("book_id", text = "Book ID")
                loan_view.heading("title", text = "Title")
                loan_view.heading("branch_id", text = "Branch ID")
                loan_view.heading("branch_name", text = "Branch Name")
                loan_view.heading("num_of_copies_loaned", text = "Copies Loaned")
                loan_view.pack(fill = tk.BOTH, expand = True, padx = 5, pady = 5)

                # Add the new rows to the end like the other
                for row in rows:
                    loan_view.insert("", "end", values=row)
            else:
                messagebox.showinfo("No Data", "No copies loaned found for this book title.")

        except sqlite3.Error as e:
            messagebox.showerror("Error", f"An error occurred: {e}")


    # Same as any other queries, have a set of buttons
    ttk.Button(frame, text = "Select Book", command = select_book, width = 20).grid(row = 2, column = 0, padx = 5, pady = 10, sticky = tk.E)
    ttk.Button(frame, text = "Show Book Copies Loaned", command = show_book_copies_loaned, width = 25).grid(row = 2, column = 1, padx = 5, pady = 10, sticky = tk.W)

   
    # Update consistently everytime ran
    update_books()

# As done in any other query
def create_query5_gui(root, listing):

    frame = ttk.Frame(listing)
    listing.add(frame, text = "Query 5")

    # per usual stuff
    ttk.Label(
        frame,
        text = "Query 5: Provide a date range, it will filter to books loaned in timeframe",
        font = ("Arial", 12, "bold"),
        anchor = "center",
        justify = "center"
    ).grid(row = 0, column = 0, columnspan = 2, pady = 10)

    # per usual stuff
    ttk.Label(frame, text = "Due Date 1:", font = ("Arial", 10)).grid(row = 1, column = 0, padx = 5, pady = 5, sticky = tk.E)
    first_due_date = ttk.Entry(frame, width = 20)
    first_due_date.grid(row = 1, column = 1, padx = 5, pady = 5)

    # per usual stuff
    ttk.Label(frame, text = "Due Date 2:", font = ("Arial", 10)).grid(row = 2, column = 0, padx = 5, pady = 5, sticky = tk.E)
    second_due_date = ttk.Entry(frame, width = 20)
    second_due_date.grid(row = 2, column = 1, padx = 5, pady = 5)


    # We're going to use this to store all of the date ranges that we are going to need
    date_due_range = []
    # submit_due_date_range() func will check the dates, checking if both have been submitted
    def submit_range_due():
        # Get the date that is entered
        date1 = first_due_date.get()
        date2 = second_due_date.get()

        # Statement checks if both dates are entered
        if not date1 and date2:
            messagebox.showerror("Error", "Both due dates required")
            return

        # clean the date range
        date_due_range.clear()
        # Now we add it onto the array using extend function
        date_due_range.extend([date1, date2])

        messagebox.showinfo("Success", "Due Date Range saved successfully")

    # show_book_loans_days_late() does as any other but just for the due_date's range
    def show_book_loans_days_late():
        # like any other statement, check if we got a due date range first
        if not date_due_range:
            messagebox.showerror("Error", "Please submit the due date range first")
            return

        # Store the first and second due date from the range (Entered by the user)
        date1 = date_due_range[0]
        date2 = date_due_range[1]

        try:
            conn = sqlite3.connect("lbms.db")
            cursor = conn.cursor()

            # Query that does required output for query5
            cursor.execute('''
                SELECT B_L.book_id, B_L.branch_id, B_L.card_no, B_L.date_out, B_L.due_date, B_L.Returned_date,
                CASE 
                    WHEN (B_L.Returned_date BETWEEN B_L.date_out AND B_L.due_date) THEN 0
                    ELSE CAST((JulianDay(B_L.Returned_date) - JulianDay(B_L.due_date)) AS INTEGER) 
                END AS num_of_days_late
                FROM Book_Loans AS B_L
                WHERE (B_L.due_date BETWEEN ? AND ?) AND (num_of_days_late != 0)
            ''', (date1, date2))
            # Grab all rows per usual
            rows = cursor.fetchall()

            # per usual, check rows
            if rows:
                # per usual stuff
                loans_window = tk.Toplevel(root)
                loans_window.title("Book Loans Days Late")
                loans_window.geometry("1200x800")

                # per usual stuff
                loans_view = ttk.Treeview(
                    loans_window,
                    columns = ("book_id", "branch_id", "card_no", "date_out", "due_date", "returned_date", "num_of_days_late"),
                    show = "headings"
                )
                loans_view.heading("book_id", text = "Book ID")
                loans_view.heading("branch_id", text = "Branch ID")
                loans_view.heading("card_no", text = "Card No")
                loans_view.heading("date_out", text = "Date Out")
                loans_view.heading("due_date", text = "Due Date")
                loans_view.heading("returned_date", text = "Returned Date")
                loans_view.heading("num_of_days_late", text = "Days Late")
                loans_view.pack(fill = tk.BOTH, expand = True, padx = 5, pady = 5)

                # Insert rows like any other we had in other stuff
                for row in rows:
                    loans_view.insert("", "end", values=row)
            else:
                messagebox.showinfo("No Data", "No book loans found for the given date range.")

        except sqlite3.Error as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

        finally:
            conn.close()

    # Per usual stuff
    ttk.Button(frame, text = "Submit Due Date Range", command = submit_range_due, width = 25).grid(row = 3, column = 0, padx = 5, pady = 10, sticky = tk.E)
    ttk.Button(frame, text = "Show Book Loans Days Late", command = show_book_loans_days_late, width = 25).grid(row = 3, column = 1, padx = 5, pady = 10, sticky = tk.W)


def create_query6a_gui(root, listing):
    frame = ttk.Frame(listing)
    listing.add(frame, text = "Query 6a")

    # per usual stuff
    ttk.Label(
        frame,
        text = "Query 6a: Check the Borrower Late Fee Balance",
        font = ("Arial", 12, "bold"),
        anchor = "center",
        justify = "center"
    ).grid(row = 0, column = 0, columnspan = 2, pady = 10)

    # per usual labels/entrys
    ttk.Label(frame, text = "Borrower Name:", font = ("Arial", 10)).grid(row = 1, column = 0, padx = 5, pady = 5, sticky = tk.E)
    borrower_name_entry = ttk.Entry(frame, width = 30)
    borrower_name_entry.grid(row = 1, column = 1, padx = 5, pady = 5, sticky = tk.W)

    # per usual labels/entrys
    ttk.Label(frame, text = "Card Number:", font = ("Arial", 10)).grid(row = 2, column = 0, padx = 5, pady = 5, sticky = tk.E)
    card_number_entry = ttk.Entry(frame, width = 30)
    card_number_entry.grid(row = 2, column = 1, padx = 5, pady = 5, sticky = tk.W)


    # show_late_fee_balances() func to show late fee balances based on the filter
    def show_late_fee_balances():
        # Gets the borrower and card number that gets typed in the box
        borrower_name = borrower_name_entry.get().strip()
        card_number = card_number_entry.get().strip()

        # Begin to build filter here.
        filter_query = ""
        filter_parameters = ()

        # Like we build two different versions of the same filter, one for SQL exec and the other for tuples like qu5
        if borrower_name and card_number:
            # ex would be borrower_name = Lebron and card_number = 123456
            filter_query = "WHERE [Borrower Name] LIKE ? AND Card_No = ?"
            filter_parameters = ('%' + borrower_name + '%', card_number)
        elif borrower_name:
            filter_query = "WHERE [Borrower Name] LIKE ?"
            filter_parameters = ('%' + borrower_name + '%',)
        elif card_number:
            filter_query = "WHERE Card_No = ?"
            filter_parameters = (card_number,)
        else:
            filter_query = ""  # No filter, display all borrowers

        conn = sqlite3.connect("lbms.db")
        cursor = conn.cursor()

        # Executes the query as given in q6
        # Check if correct TO TOMORROW!
        cursor.execute(f"""
                SELECT 
                    Card_No, 
                    [Borrower Name], 
                    CASE 
                        WHEN LateFeeBalance < 0 THEN 0
                        ELSE LateFeeBalance 
                    END AS LateFeeBalance
                FROM vBookLoanInfo
                {filter_query}
                ORDER BY Card_No;
        """, filter_parameters)

        # per usual stuff
        rows = cursor.fetchall()
        conn.close()

        # per usual stuff, check if we got rows
        if rows:
            # per usual stuff
            late_fees_window = tk.Toplevel(root)
            late_fees_window.title("Late Fee Balances")
            late_fees_window.geometry("600x500")

            # per usual stuff
            late_fee_view = ttk.Treeview(
                late_fees_window,
                columns = ("card_no", "borrower_name", "late_fee_balance"),
                show = "headings"
            )
            late_fee_view.heading("card_no", text = "Card No")
            late_fee_view.heading("borrower_name", text = "Borrower Name")
            late_fee_view.heading("late_fee_balance", text = "Late Fee Balance")
            late_fee_view.pack(fill = tk.BOTH, expand = True, padx = 5, pady = 5)

            # per usual stuff, format card number as intended
            for row in rows:
                card_no = f"{row[0]:06d}"
                borrower_name = row[1]
                late_bal = row[2]

                # this statement just checks we don't have any negatives
                if late_bal is None or late_bal < 0:
                    late_bal = 0
                # display as $#.##
                late_fee_balance_display = f"${late_bal:.2f}"
                late_fee_view.insert("", "end", values=(card_no, borrower_name, late_fee_balance_display))
        else:
            messagebox.showinfo("No Data", "No late fees found for the given borrower name or card number.")
    # per usual stuff
    ttk.Button(frame, text = "Show Late Fee Balance", command = show_late_fee_balances, width = 25).grid(row = 3, column = 0, columnspan = 2, pady = 10)

def create_query6b_gui(root, listing):
    # per usual stuff
    frame = ttk.Frame(listing)
    listing.add(frame, text = "Query 6b")

    # per usual stuff
    ttk.Label(
        frame,
        text = "Query 6b: Search Book Loan Information",
        font = ("Arial", 12, "bold"),
        anchor = "center"
    ).grid(row = 0, column = 0, columnspan = 2, pady = 10)

    # per usual stuff
    ttk.Label(frame, text = "Search by Borrower ID (DIGITS REQ):").grid(row = 1, column = 0, padx = 5, pady = 5, sticky = tk.E)
    borrower_id_entry = ttk.Entry(frame, width = 30)
    borrower_id_entry.grid(row = 1, column = 1, padx = 5, pady = 5, sticky = tk.W)

    # per usual stuff
    ttk.Label(frame, text = "Search by Book ID or Title:").grid(row = 2, column = 0, padx = 5, pady = 5, sticky = tk.E)
    filter_entry = ttk.Entry(frame, width = 30)
    filter_entry.grid(row = 2, column = 1, padx = 5, pady = 5, sticky = tk.W)

    # get_filtered_books() function gets the books when we filter it
    def select_Filtered_books():
        # per usual stuff, get the user input and remove any extra space
        borrower_id = borrower_id_entry.get().strip()
        input_filter = filter_entry.get().strip()

        # MUST have a borrower_id
        if not borrower_id:
            messagebox.showerror("Input Error", "Please enter Borrower ID.")
            return []

        try:
            conn = sqlite3.connect("lbms.db")
            cursor = conn.cursor()

            # Use the given value to store, filter is for matching and query version is for SQL
            filter_parameters = f"%{input_filter}%"
            query_parameters = [borrower_id]

            # Searching for partial and its a view so to lessen code, lets make one that repeatedly can be used
            query = '''
                        SELECT 
                            Bk.book_id AS "Book ID", 
                            vBLI.[Book Title] AS "Book Title", 
                            vBLI.Date_Out AS "Date Out", 
                            vBLI.Due_Date AS "Due Date", 
                            vBLI.Returned_date AS "Returned Date",
                            CASE 
                                WHEN vBLI.Due_Date IS NOT NULL THEN CAST((JulianDay(vBLI.Due_Date) - JulianDay(vBLI.Date_Out)) AS INTEGER)
                                ELSE 'N/A'
                            END AS "Total Days Loaned",
                            vBLI.[Number of days returned late] AS "Days Later Return",
                            vBLI.[Branch ID] AS "Branch ID",
                            CASE 
                                WHEN vBLI.LateFeeBalance IS NULL OR vBLI.LateFeeBalance <= 0 THEN 'Non-Applicable'
                                ELSE '$' || printf("%.2f", vBLI.LateFeeBalance)
                            END AS "Late Fee Balance"
                        FROM 
                            vBookLoanInfo AS vBLI
                        JOIN 
                            Book AS Bk ON vBLI.[Book Title] = Bk.title
                        WHERE 
                            vBLI.Card_No = ?
            '''

            # Check if filter_input got anything
            if input_filter:
                try:
                    # Add as needed for the query (BOOK ID)
                    book_id = int(input_filter)
                    query += " AND Bk.book_id = ?"
                    query_parameters.append(book_id)
                except ValueError:
                    # Add as needed for the query (PARTIAL BOOK TITLE)
                    query += " AND vBLI.[Book Title] LIKE ?"
                    query_parameters.append(filter_parameters)
            # FINALLY JUST ADD THE LATEFEE PUT IN HIGH VAL ORDER
            query += " ORDER BY vBLI.LateFeeBalance DESC;"

            # Query ran the same as usual, whatever is final, we also will take the SQL params as well.
            cursor.execute(query, tuple(query_parameters))
            records = cursor.fetchall()
            conn.close()
            return records

        except sqlite3.Error as e:
            messagebox.showerror("Error", f"An error occurred: {e}")
            return []

    # select_all_books() func to fetch all book info
    def select_all_books():
        try:
            conn = sqlite3.connect("lbms.db")
            cursor = conn.cursor()

            # Query to get all book information
            query = '''
                        SELECT 
                            Bk.book_id AS "Book ID", 
                            vBLI.[Book Title] AS "Book Title", 
                            vBLI.Date_Out AS "Date Out", 
                            vBLI.Due_Date AS "Due Date", 
                            vBLI.Returned_date AS "Returned Date",
                            CASE 
                                WHEN vBLI.Due_Date IS NOT NULL THEN CAST((JulianDay(vBLI.Due_Date) - JulianDay(vBLI.Date_Out)) AS INTEGER)
                                ELSE 'N/A'
                            END AS "Total Days Loaned",
                            vBLI.[Number of days returned late] AS "Days Returned Late",
                            vBLI.[Branch ID] AS "Branch ID",
                            CASE 
                                WHEN vBLI.LateFeeBalance IS NULL OR vBLI.LateFeeBalance <= 0 THEN 'Non-Applicable'
                                ELSE '$' || printf("%.2f", vBLI.LateFeeBalance)
                            END AS "Late Fee Balance"
                        FROM 
                            vBookLoanInfo AS vBLI
                        JOIN 
                            Book AS Bk ON vBLI.[Book Title] = Bk.title
                        ORDER BY 
                            vBLI.LateFeeBalance DESC;
            '''
            cursor.execute(query)
            records = cursor.fetchall()
            conn.close()

            return records

        except sqlite3.Error as e:
            messagebox.showerror("Error", f"An error occurred: {e}")
            return []

    # show_results(records) func will display the results using the records as params
    def show_results(records):
        # per usual stuff, check if records even exists
        if not records:
            messagebox.showinfo("No Results", "No books found.")
            return

        # per usual stuff
        results_window = tk.Toplevel(root)
        results_window.title("Books Information")
        results_window.geometry("1800x750")

        # per usual stuff
        books_view = ttk.Treeview(
            results_window,
            columns = ("book_id", "book_title", "date_out", "due_date", "returned_date",
                    "total_days_loaned", "days_returned_late", "branch_id", "late_fee_balance"),
            show = "headings"
        )
        books_view.heading("book_id", text = "Book ID")
        books_view.heading("book_title", text = "Book Title")
        books_view.heading("date_out", text = "Date Out")
        books_view.heading("due_date", text = "Due Date")
        books_view.heading("returned_date", text = "Returned Date")
        books_view.heading("total_days_loaned", text = "Total Days Loaned")
        books_view.heading("days_returned_late", text = "Days Returned Late")
        books_view.heading("branch_id", text = "Branch ID")
        books_view.heading("late_fee_balance", text = "Late Fee Balance")
        books_view.pack(fill = tk.BOTH, expand = True, padx = 5, pady = 5)

        # per usual stuff
        for record in records:
            books_view.insert("", "end", values = record)

    # per usual stuff but lambda is cause temporary stuff
    ttk.Button(frame, text = "Search Filtered View Book Information", command = lambda: show_results(select_Filtered_books())).grid(row = 3, column = 0, padx = 5, pady = 10, sticky = tk.E)
    ttk.Button(frame, text = "Show All View Book Information", command = lambda: show_results(select_all_books())).grid(row = 3, column = 1, padx = 5, pady = 10, sticky = tk.W)


def create_gui():
    root = tk.Tk()
    root.title("Library Management System")
    root.geometry("600x300")

    listing = ttk.Notebook(root)
    listing.pack(fill=tk.BOTH, expand=True)

    # create tables one by one :P
    create_query1_gui(root, listing)   # Query 1
    create_query2_gui(root, listing)   # Query 2
    create_query3_gui(root, listing)   # Query 3
    create_query4_gui(root, listing)   # Query 4
    create_query5_gui(root, listing)   # Query 5
    create_query6a_gui(root, listing)  # Query 6a
    create_query6b_gui(root, listing)  # Query 6b

    root.mainloop()

# Make sure the table get ran
create_tables()
create_gui()