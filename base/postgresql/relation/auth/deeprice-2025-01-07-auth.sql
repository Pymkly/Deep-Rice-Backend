CREATE TABLE users (
    id SERIAL PRIMARY KEY, -- Unique identifier for the user
    first_name VARCHAR(100) NOT NULL, -- User's first name
    last_name VARCHAR(100) NOT NULL, -- User's last name
    email VARCHAR(150) NOT NULL UNIQUE, -- Unique email address
    password TEXT NOT NULL, -- Hashed password
    role VARCHAR(50) DEFAULT 'user', -- Role (e.g., admin, user)
    registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP -- Date of registration
);





