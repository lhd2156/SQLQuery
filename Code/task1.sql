-- q 1
ALTER TABLE Book_Loans
ADD Late INT;
UPDATE Book_Loans
SET Late = CASE
    WHEN Book_Loans.Returned_date BETWEEN 
    Book_Loans.date_out AND Book_Loans.due_date THEN 0
    ELSE 1
END;
SELECT * FROM Book_Loans;
-- SELECT COUNT(*) AS Total_Rows_Returned_Q1 FROM Book_Loans;

-- q 2
ALTER TABLE Library_Branch
ADD LateFee DECIMAL(10, 2);
UPDATE Library_Branch
SET LateFee = CASE
    WHEN Library_Branch.branch_id = 1 THEN 1.50
    WHEN Library_Branch.branch_id = 2 THEN 1.00
    WHEN Library_Branch.branch_id = 3 THEN 0.75
    ELSE 1.25
END;
SELECT * FROM Library_Branch;
-- SELECT COUNT(*) AS Total_Rows_Returned_Q2 FROM Library_Branch;

-- q 3
CREATE VIEW vBookLoanInfo AS
SELECT 
    BW.card_no AS Card_No,
    BW.name AS [Borrower Name],
    B_L.date_out AS Date_Out,
    B_L.due_date AS Due_Date,
    B_L.Returned_date AS Returned_Date,
    
    CAST(
        (JulianDay(B_L.Returned_date) - JulianDay(B_L.date_out)) AS INTEGER
    ) AS TotalDays,

    Bk.title AS [Book Title],
    
    CASE
        WHEN (B_L.Returned_date BETWEEN B_L.date_out AND B_L.due_date)
        THEN 0
        ELSE CAST(
            (JulianDay(B_L.Returned_date) - JulianDay(B_L.due_date)) AS INTEGER
        )
    END AS [Number of days returned late],

    L_B.branch_id AS [Branch ID],

    CASE
        WHEN (B_L.Returned_date BETWEEN B_L.date_out AND B_L.due_date)
        THEN 0
        ELSE L_B.LateFee * CAST(
            (JulianDay(B_L.Returned_date) - JulianDay(B_L.due_date)) AS INTEGER
        )
    END AS LateFeeBalance

FROM Borrower AS BW
JOIN Book_Loans AS B_L ON BW.card_no = B_L.card_no
JOIN Book AS Bk ON B_L.book_id = Bk.book_id
JOIN Library_Branch AS L_B ON B_L.branch_id = L_B.branch_id;

SELECT * FROM vBookLoanInfo;
-- SELECT COUNT(*) AS Total_Rows_Returned_Q3 FROM vBookLoanInfo;


