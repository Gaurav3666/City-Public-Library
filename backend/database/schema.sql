
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS branches (
    branch_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    address TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS books (
    book_id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    isbn TEXT NOT NULL UNIQUE,
    published_year INTEGER,
    CHECK (
        published_year IS NULL
        OR published_year BETWEEN 1000 AND 2100
    )
);

CREATE TABLE IF NOT EXISTS authors (
    author_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS book_authors (
    book_id INTEGER NOT NULL,
    author_id INTEGER NOT NULL,
    PRIMARY KEY (book_id, author_id),
    FOREIGN KEY (book_id) REFERENCES books(book_id),
    FOREIGN KEY (author_id) REFERENCES authors(author_id)
);

CREATE TABLE IF NOT EXISTS book_copies (
    copy_id INTEGER PRIMARY KEY AUTOINCREMENT,
    book_id INTEGER NOT NULL,
    branch_id INTEGER NOT NULL,
    status TEXT NOT NULL DEFAULT 'available'
        CHECK (status IN ('available', 'issued', 'maintenance')),
    FOREIGN KEY (book_id) REFERENCES books(book_id),
    FOREIGN KEY (branch_id) REFERENCES branches(branch_id)
);

CREATE TABLE IF NOT EXISTS members (
    member_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE COLLATE NOCASE,
    password_hash TEXT NOT NULL,
    joined_at TEXT NOT NULL DEFAULT (date('now')),
    is_active INTEGER NOT NULL DEFAULT 1
        CHECK (is_active IN (0, 1))
);

CREATE TABLE IF NOT EXISTS staff (
    staff_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE COLLATE NOCASE,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('librarian', 'admin')),
    branch_id INTEGER,
    FOREIGN KEY (branch_id) REFERENCES branches(branch_id)
);

CREATE TABLE IF NOT EXISTS loans (
    loan_id INTEGER PRIMARY KEY AUTOINCREMENT,
    copy_id INTEGER NOT NULL,
    member_id INTEGER NOT NULL,
    staff_id INTEGER NOT NULL,
    checkout_date TEXT NOT NULL DEFAULT (date('now')),
    due_date TEXT NOT NULL,
    returned_at TEXT,
    FOREIGN KEY (copy_id) REFERENCES book_copies(copy_id),
    FOREIGN KEY (member_id) REFERENCES members(member_id),
    FOREIGN KEY (staff_id) REFERENCES staff(staff_id),
    CHECK (date(due_date) IS NOT NULL),
    CHECK (date(checkout_date) IS NOT NULL),
    CHECK (date(due_date) >= date(checkout_date)),
    CHECK (
        returned_at IS NULL
        OR (
            date(returned_at) IS NOT NULL
            AND date(returned_at) >= date(checkout_date)
        )
    )
);

CREATE TABLE IF NOT EXISTS fines (
    fine_id INTEGER PRIMARY KEY AUTOINCREMENT,
    loan_id INTEGER NOT NULL UNIQUE,
    amount REAL NOT NULL CHECK (amount >= 0),
    status TEXT NOT NULL DEFAULT 'unpaid'
        CHECK (status IN ('unpaid', 'paid')),
    created_at TEXT NOT NULL DEFAULT (date('now')),
    paid_at TEXT,
    FOREIGN KEY (loan_id) REFERENCES loans(loan_id),
    CHECK (
        (status = 'unpaid' AND paid_at IS NULL)
        OR (status = 'paid' AND paid_at IS NOT NULL)
    )
);

-- A physical copy cannot have more than one active loan.
CREATE UNIQUE INDEX IF NOT EXISTS idx_one_active_loan_per_copy
ON loans(copy_id)
WHERE returned_at IS NULL;

-- Indexes used by member loan history and overdue reports.
CREATE INDEX IF NOT EXISTS idx_loans_member_returned
ON loans(member_id, returned_at);

CREATE INDEX IF NOT EXISTS idx_loans_due_date
ON loans(due_date);

CREATE INDEX IF NOT EXISTS idx_fines_status
ON fines(status);

CREATE INDEX IF NOT EXISTS idx_copies_branch_status
ON book_copies(branch_id, status);

CREATE INDEX IF NOT EXISTS idx_book_authors_author
ON book_authors(author_id, book_id);


