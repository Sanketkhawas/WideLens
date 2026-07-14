-- ==========================
-- USERS TABLE
-- ==========================

CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- ==========================
-- CUSTOMERS TABLE
-- ==========================

CREATE TABLE customers (
    customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    customer_name VARCHAR(100) NOT NULL,
    age INTEGER,
    gender VARCHAR(10),
    city VARCHAR(100),
    area VARCHAR(100),
    latitude REAL,
    longitude REAL,
    purchase_frequency INTEGER,
    total_spent REAL,

    FOREIGN KEY (user_id)
        REFERENCES users(id)
);

-- ==========================
-- SALES TABLE
-- ==========================

CREATE TABLE sales (
    sale_id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER NOT NULL,
    product VARCHAR(100) NOT NULL,
    quantity INTEGER NOT NULL,
    amount REAL NOT NULL,
    sale_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    payment_method VARCHAR(50),

    FOREIGN KEY (customer_id)
        REFERENCES customers(customer_id)
);

-- ==========================
-- COMPETITORS TABLE
-- ==========================

CREATE TABLE competitors (
    competitor_id INTEGER PRIMARY KEY AUTOINCREMENT,
    business_name VARCHAR(150) NOT NULL,
    category VARCHAR(100),
    city VARCHAR(100),
    area VARCHAR(100),
    latitude REAL,
    longitude REAL,
    rating REAL
);

-- ==========================
-- LOCATIONS TABLE
-- ==========================

CREATE TABLE locations (
    location_id INTEGER PRIMARY KEY AUTOINCREMENT,
    city VARCHAR(100) NOT NULL,
    area VARCHAR(100) NOT NULL,
    latitude REAL,
    longitude REAL,
    population INTEGER,
    average_rent REAL,
    customer_density REAL,
    competitor_count INTEGER
);