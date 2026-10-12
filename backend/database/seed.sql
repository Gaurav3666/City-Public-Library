INSERT OR IGNORE INTO branches (branch_id, name, address) VALUES
(1, 'Central Library', 'Sector 17, Chandigarh'),
(2, 'North Branch', 'Sector 15, Chandigarh'),
(3, 'South Branch', 'Sector 34, Chandigarh');

INSERT OR IGNORE INTO books
    (book_id, title, isbn, published_year)
VALUES
(1, 'The Alchemist', '9780061122415', 1988),
(2, 'Wings of Fire', '9788173711466', 1999),
(3, 'Atomic Habits', '9780735211292', 2018),
(4, 'The Discovery of India', '9780143031031', 1946),
(5, 'Python Crash Course', '9781718502703', 2019);

INSERT OR IGNORE INTO authors (author_id, name) VALUES
(1, 'Paulo Coelho'),
(2, 'A. P. J. Abdul Kalam'),
(3, 'Arun Tiwari'),
(4, 'James Clear'),
(5, 'Jawaharlal Nehru'),
(6, 'Eric Matthes');

INSERT OR IGNORE INTO book_authors (book_id, author_id) VALUES
(1, 1),
(2, 2),
(2, 3),
(3, 4),
(4, 5),
(5, 6);

INSERT OR IGNORE INTO book_copies (copy_id, book_id, branch_id, status) VALUES
(1, 1, 1, 'available'),
(2, 1, 2, 'available'),
(3, 2, 1, 'available'),
(4, 2, 3, 'available'),
(5, 3, 2, 'available'),
(6, 3, 3, 'available'),
(7, 4, 1, 'available'),
(8, 5, 3, 'available');

-- Demo member accounts
INSERT OR IGNORE INTO members
    (member_id, name, email, password_hash, is_active)
VALUES
(1, 'Aarav Sharma', 'aarav@example.com', 'RESET_DEMO_PASSWORD', 1),
(2, 'Meera Verma', 'meera@example.com', 'RESET_DEMO_PASSWORD', 1),
(3, 'Kabir Singh', 'kabir@example.com', 'RESET_DEMO_PASSWORD', 1);

-- Demo staff accounts
INSERT OR IGNORE INTO staff
    (staff_id, name, email, password_hash, role, branch_id)
VALUES
(1, 'Priya Malhotra', 'librarian1@example.com',
 'RESET_DEMO_PASSWORD', 'librarian', 1),
(2, 'Rahul Kapoor', 'librarian2@example.com',
 'RESET_DEMO_PASSWORD', 'librarian', 2),
(3, 'Ananya Gupta', 'admin@example.com',
 'RESET_DEMO_PASSWORD', 'admin', 1);
