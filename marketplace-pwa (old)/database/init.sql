CREATE DATABASE IF NOT EXISTS marketplace_db;
USE marketplace_db;

CREATE TABLE IF NOT EXISTS users (
    user_email VARCHAR(100) PRIMARY KEY,
    user_name VARCHAR(50) NOT NULL,
    user_password_hash VARCHAR(255) NOT NULL,
);

CREATE TABLE IF NOT EXISTS stores (
    store_email VARCHAR(100) PRIMARY KEY,
    store_name VARCHAR(100) NOT NULL
    store_description TEXT,
    store_phone VARCHAR(20),
    store_address TEXT NOT NULL,
);

CREATE TABLE IF NOT EXISTS roles (
    role_id VARCHAR(50) PRIMARY KEY,
    role_name VARCHAR(50) UNIQUE NOT NULL,
    role_description TEXT,
);

CREATE TABLE IF NOT EXISTS store_user_role (
    store_id INT NOT NULL,
    user_email VARCHAR(100) NOT NULL,
    role_id VARCHAR(50) NOT NULL,
    PRIMARY KEY (store_id, user_email, role_id),
    FOREIGN KEY (store_id) REFERENCES stores(store_id),
    FOREIGN KEY (user_email) REFERENCES users(user_email),
    FOREIGN KEY (role_id) REFERENCES roles(role_id)
);

CREATE TABLE IF NOT EXISTS categories (
    category_id INT AUTO_INCREMENT PRIMARY KEY,
    category_name VARCHAR(100) UNIQUE NOT NULL,
    category_description TEXT,
    category_pic_path VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS products (
    product_id INT AUTO_INCREMENT PRIMARY KEY,
    product_name VARCHAR(100) UNIQUE NOT NULL,
    product_description TEXT,
    product_pic_path VARCHAR(255),
    category_id INT NOT NULL,
    FOREIGN KEY (category_id) REFERENCES categories(category_id)
);

CREATE TABLE IF NOT EXISTS store_products (
    store_id INT NOT NULL,
    product_id INT NOT NULL,
    PRIMARY KEY (store_id, product_id),
    price DECIMAL(10, 2) NOT NULL,
    stock INT NOT NULL,
    FOREIGN KEY (store_id) REFERENCES stores(store_id),
    FOREIGN KEY (product_id) REFERENCES master_products(product_id)
);

CREATE TABLE IF NOT EXISTS customers (
    customer_email VARCHAR(100) PRIMARY KEY,
    customer_name VARCHAR(100) NOT NULL,
    customer_password_hash VARCHAR(255) NOT NULL,
    customer_address TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS order_statuses (
    status_id VARCHAR(50) PRIMARY KEY,
    status VARCHAR(50) UNIQUE NOT NULL,
    status_description TEXT
);

CREATE TABLE IF NOT EXISTS orders (
    order_id INT AUTO_INCREMENT PRIMARY KEY,
    order_tot_quantity INT NOT NULL,
    order_tot_price DECIMAL(10, 2) NOT NULL,
    order_status_id INT NOT NULL,
    FOREIGN KEY (order_status_id) REFERENCES order_statuses(status_id),
);

CREATE TABLE IF NOT EXISTS order_customer_store (
    order_id INT NOT NULL,
    customer_email VARCHAR(100) NOT NULL,,
    store_id INT NOT NULL,
    PRIMARY KEY (order_id, customer_email, store_id),
    FOREIGN KEY (order_id) REFERENCES orders(order_id),
    FOREIGN KEY (customer_email) REFERENCES customers(customer_email),
    FOREIGN KEY (store_id) REFERENCES stores(store_id),
);

CREATE TABLE IF NOT EXISTS order_details (
    order_id INT NOT NULL,
    product_id INT NOT NULL,
    PRIMARY KEY (order_id, product_id),
    product_quantity INT NOT NULL,
    product_tot_price DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(order_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

CREATE TABLE IF NOT EXISTS order_status_history (
    order_id INT NOT NULL,
    status_id VARCHAR(50) NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(order_id),
    FOREIGN KEY (status_id) REFERENCES order_statuses(status_id)
);

/* It's possible to create dummy data for testing purposes using the following SQL commands.
INSERT INTO roles (role_name, role_keyword) VALUES ('Admin', 'admin');*/