CREATE DATABASE IF NOT EXISTS marketplace_db;
USE marketplace_db;

/* Ensure status lookup table exists before tables that reference it */
CREATE TABLE IF NOT EXISTS entity_statuses (
    status_id INT AUTO_INCREMENT PRIMARY KEY,
    # UNIQUE: Creates an implicit index on the column
    status_code VARCHAR(50) UNIQUE NOT NULL, -- e.g., 'active', 'inactive', 'banned'
    status_description TEXT
);

CREATE TABLE IF NOT EXISTS users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    user_email VARCHAR(100) UNIQUE NOT NULL,
    user_name VARCHAR(50) NOT NULL,
    user_password_hash VARCHAR(255) NOT NULL,
    user_phone VARCHAR(20) NOT NULL,
    user_status_id INT NOT NULL,
    # FOREIGN KEY constraint: Apart from the relationship, it creates an index on the column for most
    # DB systems suach as PostgreSQL and MySQL/MariaDB
    FOREIGN KEY (user_status_id) REFERENCES entity_statuses (status_id)
);

CREATE TABLE IF NOT EXISTS stores (
    store_id INT AUTO_INCREMENT PRIMARY KEY,
    store_email VARCHAR(100) UNIQUE NOT NULL,
    store_name VARCHAR(100) NOT NULL,
    store_description TEXT,
    store_phone VARCHAR(20),
    store_address TEXT NOT NULL,
    store_status_id INT NOT NULL,
    FOREIGN KEY (store_status_id) REFERENCES entity_statuses (status_id)
);

CREATE TABLE IF NOT EXISTS roles (
    role_id INT AUTO_INCREMENT PRIMARY KEY,
    role_code VARCHAR(50) UNIQUE NOT NULL,
    role_description TEXT
);

CREATE TABLE IF NOT EXISTS store_user_role (
    store_id INT NOT NULL,
    user_id INT NOT NULL,
    role_id INT NOT NULL,
    status_id INT NOT NULL,
    PRIMARY KEY (store_id, user_id),
    FOREIGN KEY (store_id) REFERENCES stores (store_id),
    FOREIGN KEY (user_id) REFERENCES users (user_id),
    FOREIGN KEY (role_id) REFERENCES roles (role_id),
    FOREIGN KEY (status_id) REFERENCES entity_statuses (status_id)
);

CREATE TABLE IF NOT EXISTS categories (
    category_id INT AUTO_INCREMENT PRIMARY KEY,
    category_name VARCHAR(100) UNIQUE NOT NULL,
    category_description TEXT,
    category_pic_path VARCHAR(255),
    category_status_id INT NOT NULL,
    FOREIGN KEY (category_status_id) REFERENCES entity_statuses (status_id)
);

CREATE TABLE IF NOT EXISTS products_services (
    product_service_id INT AUTO_INCREMENT PRIMARY KEY,
    product_service_name VARCHAR(100) UNIQUE NOT NULL,
    product_service_description TEXT,
    product_service_pic_path VARCHAR(255),
    product_service_category_id INT NOT NULL,
    product_service_status_id INT NOT NULL,
    FOREIGN KEY (product_service_category_id) REFERENCES categories (category_id),
    FOREIGN KEY (product_service_status_id) REFERENCES entity_statuses (status_id)
);

/* Composite PK was discarded as AI suggested it was best practice only for
   Pure join/association tables (many-to-many) and few other specific cases */
CREATE TABLE IF NOT EXISTS store_products_services (
    id INT AUTO_INCREMENT PRIMARY KEY,
    store_id INT NOT NULL,
    product_service_id INT NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    stock INT NOT NULL,
    UNIQUE KEY uk_store_product (store_id, product_service_id),
    INDEX idx_store (store_id),
    INDEX idx_product_service (product_service_id),
    status_id INT NOT NULL,
    FOREIGN KEY (status_id) REFERENCES entity_statuses (status_id),
    FOREIGN KEY (store_id) REFERENCES stores (store_id),
    FOREIGN KEY (product_service_id) REFERENCES products_services (product_service_id)
);

CREATE TABLE IF NOT EXISTS customers (
    customer_id INT AUTO_INCREMENT PRIMARY KEY,
    customer_email VARCHAR(100) UNIQUE NOT NULL,
    customer_name VARCHAR(100) NOT NULL,
    customer_password_hash VARCHAR(255) NOT NULL,
    customer_phone VARCHAR(20) NOT NULL,
    customer_status_id INT NOT NULL,
    FOREIGN KEY (customer_status_id) REFERENCES entity_statuses (status_id)
);

CREATE TABLE IF NOT EXISTS countries (
    country_id INT AUTO_INCREMENT PRIMARY KEY,
    country_name VARCHAR(100) NOT NULL,
    country_code VARCHAR(10) UNIQUE NOT NULL,
    country_status_id INT NOT NULL,
    FOREIGN KEY (country_status_id) REFERENCES entity_statuses (status_id)
);

CREATE TABLE IF NOT EXISTS states_regions (
    state_region_id INT AUTO_INCREMENT PRIMARY KEY,
    state_region_name VARCHAR(100) NOT NULL,
    state_region_code VARCHAR(10) UNIQUE NOT NULL,
    country_id INT NOT NULL,
    FOREIGN KEY (country_id) REFERENCES countries (country_id),
    state_region_status_id INT NOT NULL,
    FOREIGN KEY (state_region_status_id) REFERENCES entity_statuses (status_id)
);

CREATE TABLE IF NOT EXISTS cities (
    city_id INT AUTO_INCREMENT PRIMARY KEY,
    city_name VARCHAR(100) NOT NULL,
    state_region_id INT NOT NULL,
    FOREIGN KEY (state_region_id) REFERENCES states_regions (state_region_id),
    city_status_id INT NOT NULL,
    FOREIGN KEY (city_status_id) REFERENCES entity_statuses (status_id)
);

CREATE TABLE IF NOT EXISTS customer_addresses (
    address_id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES customers (customer_id),
    address_line1 VARCHAR(255) NOT NULL,
    address_line2 VARCHAR(255),
    city_id INT NOT NULL,
    FOREIGN KEY (city_id) REFERENCES cities (city_id),
    google_maps_url VARCHAR(255) NOT NULL,
    address_status_id INT NOT NULL,
    FOREIGN KEY (address_status_id) REFERENCES entity_statuses (status_id),
    postal_code VARCHAR(20) NOT NULL
);

CREATE TABLE IF NOT EXISTS order_statuses (
    status_id INT AUTO_INCREMENT PRIMARY KEY,
    -- eg: 'open', 'paid', 'pending', 'filled', 'partial_filled', 'shipped', 'partial_shipped',
    --     'delivered', 'partial_delivered', 'canceled', 'partial_canceled', 'returned', 'partial_returned',
    --     'customer_accepted', 'refunded']
    status_code VARCHAR(50) UNIQUE NOT NULL,
    status_description TEXT
);

CREATE TABLE IF NOT EXISTS orders (
    order_id INT AUTO_INCREMENT PRIMARY KEY,
    order_tot_quantity INT NOT NULL,
    order_tot_price DECIMAL(10, 2) NOT NULL,
    customer_id INT NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES customers (customer_id),
    order_status_id INT NOT NULL,
    FOREIGN KEY (order_status_id) REFERENCES order_statuses (status_id)
);

CREATE TABLE IF NOT EXISTS order_details (
    order_id INT NOT NULL,
    store_product_service_id INT NOT NULL, -- references store_products_services.id
    PRIMARY KEY (order_id, store_product_service_id),
    product_service_quantity INT NOT NULL,
    product_service_price DECIMAL(10, 2) NOT NULL, -- price at the time of order
    product_service_tot_price DECIMAL(10, 2) NOT NULL, -- paid order total price 
    product_service_status_id INT NOT NULL,
    product_service_filled_quantity INT NOT NULL DEFAULT 0,
    product_service_filled_tot_price DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    FOREIGN KEY (product_service_status_id) REFERENCES order_statuses(status_id),
    FOREIGN KEY (order_id) REFERENCES orders(order_id),
    FOREIGN KEY (store_product_service_id) REFERENCES store_products_services(id)
);


/* It's possible to create dummy data for testing purposes using the following SQL commands.
INSERT INTO... */


/**
   Audit/History tables and triggers for all project tables
   Pattern: <table>_history (hist_id, <pk>, op_type, changed_by, changed_at, data_before, data_after)
   Triggers use COALESCE(@audit_user,'system') and JSON_OBJECT(...) snapshots.
*/

/* ---------------------- users ---------------------- */
CREATE TABLE IF NOT EXISTS users_history (
    hist_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    op_type ENUM('INSERT','UPDATE','DELETE') NOT NULL,
    changed_by VARCHAR(100), -- set from app via: SET @audit_user = 'user@example.com';
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data_before JSON,
    data_after JSON,
    INDEX idx_users_history_user (user_id),
    INDEX idx_users_history_time (changed_at)
);

-- Change the delimiter from ; to $$ because by default RDBMS executes a command at each ;
DELIMITER $$

CREATE TRIGGER trg_users_after_insert
AFTER INSERT ON users
FOR EACH ROW
BEGIN
  INSERT INTO users_history (user_id, op_type, changed_by, data_after)
  VALUES (
    NEW.user_id,
    'INSERT',
    COALESCE(@audit_user, 'system'), -- If no user is logged in, use 'system'
    JSON_OBJECT(
      'user_id', NEW.user_id,
      'user_email', NEW.user_email,
      'user_name', NEW.user_name,
      'user_phone', NEW.user_phone,
      'user_status_id', NEW.user_status_id
    )
  );
END$$

CREATE TRIGGER trg_users_before_update
BEFORE UPDATE ON users
FOR EACH ROW
BEGIN
  INSERT INTO users_history (user_id, op_type, changed_by, data_before, data_after)
  VALUES (
    OLD.user_id,
    'UPDATE',
    COALESCE(@audit_user, 'system'),
    JSON_OBJECT(
      'user_id', OLD.user_id,
      'user_email', OLD.user_email,
      'user_name', OLD.user_name,
      'user_phone', OLD.user_phone,
      'user_status_id', OLD.user_status_id
    ),
    JSON_OBJECT(
      'user_id', NEW.user_id,
      'user_email', NEW.user_email,
      'user_name', NEW.user_name,
      'user_phone', NEW.user_phone,
      'user_status_id', NEW.user_status_id
    )
  );
END$$

CREATE TRIGGER trg_users_before_delete
BEFORE DELETE ON users
FOR EACH ROW
BEGIN
  INSERT INTO users_history (user_id, op_type, changed_by, data_before)
  VALUES (
    OLD.user_id,
    'DELETE',
    COALESCE(@audit_user, 'system'),
    JSON_OBJECT(
      'user_id', OLD.user_id,
      'user_email', OLD.user_email,
      'user_name', OLD.user_name,
      'user_phone', OLD.user_phone,
      'user_status_id', OLD.user_status_id
    )
  );
END$$

DELIMITER ;

/* ---------------------- entity_statuses ---------------------- */
CREATE TABLE IF NOT EXISTS entity_statuses_history (
  hist_id BIGINT AUTO_INCREMENT PRIMARY KEY,
  status_id INT,
  op_type ENUM('INSERT','UPDATE','DELETE') NOT NULL,
  changed_by VARCHAR(100),
  changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  data_before JSON,
  data_after JSON,
  INDEX (status_id),
  INDEX (changed_at)
);

/* ---------------------- stores ---------------------- */
CREATE TABLE IF NOT EXISTS stores_history (
  hist_id BIGINT AUTO_INCREMENT PRIMARY KEY,
  store_id INT,
  op_type ENUM('INSERT','UPDATE','DELETE') NOT NULL,
  changed_by VARCHAR(100),
  changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  data_before JSON,
  data_after JSON,
  INDEX (store_id),
  INDEX (changed_at)
);

/* ---------------------- roles ---------------------- */
CREATE TABLE IF NOT EXISTS roles_history (
  hist_id BIGINT AUTO_INCREMENT PRIMARY KEY,
  role_id INT,
  op_type ENUM('INSERT','UPDATE','DELETE') NOT NULL,
  changed_by VARCHAR(100),
  changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  data_before JSON,
  data_after JSON,
  INDEX (role_id),
  INDEX (changed_at)
);

/* ---------------------- store_user_role ---------------------- */
CREATE TABLE IF NOT EXISTS store_user_role_history (
  hist_id BIGINT AUTO_INCREMENT PRIMARY KEY,
  store_id INT,
  user_id INT,
  role_id INT,
  op_type ENUM('INSERT','UPDATE','DELETE') NOT NULL,
  changed_by VARCHAR(100),
  changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  data_before JSON,
  data_after JSON,
  INDEX (store_id),
  INDEX (user_id),
  INDEX (changed_at)
);

/* ---------------------- categories ---------------------- */
CREATE TABLE IF NOT EXISTS categories_history (
  hist_id BIGINT AUTO_INCREMENT PRIMARY KEY,
  category_id INT,
  op_type ENUM('INSERT','UPDATE','DELETE') NOT NULL,
  changed_by VARCHAR(100),
  changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  data_before JSON,
  data_after JSON,
  INDEX (category_id),
  INDEX (changed_at)
);

/* ---------------------- products_services ---------------------- */
CREATE TABLE IF NOT EXISTS products_services_history (
  hist_id BIGINT AUTO_INCREMENT PRIMARY KEY,
  product_service_id INT,
  op_type ENUM('INSERT','UPDATE','DELETE') NOT NULL,
  changed_by VARCHAR(100),
  changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  data_before JSON,
  data_after JSON,
  INDEX (product_service_id),
  INDEX (changed_at)
);

/* ---------------------- store_products_services ---------------------- */
CREATE TABLE IF NOT EXISTS store_products_services_history (
  hist_id BIGINT AUTO_INCREMENT PRIMARY KEY,
  id INT,
  store_id INT,
  product_service_id INT,
  op_type ENUM('INSERT','UPDATE','DELETE') NOT NULL,
  changed_by VARCHAR(100),
  changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  data_before JSON,
  data_after JSON,
  INDEX (id),
  INDEX (store_id),
  INDEX (product_service_id),
  INDEX (changed_at)
);

/* ---------------------- customers ---------------------- */
CREATE TABLE IF NOT EXISTS customers_history (
  hist_id BIGINT AUTO_INCREMENT PRIMARY KEY,
  customer_id INT,
  op_type ENUM('INSERT','UPDATE','DELETE') NOT NULL,
  changed_by VARCHAR(100),
  changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  data_before JSON,
  data_after JSON,
  INDEX (customer_id),
  INDEX (changed_at)
);

/* ---------------------- countries ---------------------- */
CREATE TABLE IF NOT EXISTS countries_history (
  hist_id BIGINT AUTO_INCREMENT PRIMARY KEY,
  country_id INT,
  op_type ENUM('INSERT','UPDATE','DELETE') NOT NULL,
  changed_by VARCHAR(100),
  changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  data_before JSON,
  data_after JSON,
  INDEX (country_id),
  INDEX (changed_at)
);

/* ---------------------- states_regions ---------------------- */
CREATE TABLE IF NOT EXISTS states_regions_history (
  hist_id BIGINT AUTO_INCREMENT PRIMARY KEY,
  state_region_id INT,
  op_type ENUM('INSERT','UPDATE','DELETE') NOT NULL,
  changed_by VARCHAR(100),
  changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  data_before JSON,
  data_after JSON,
  INDEX (state_region_id),
  INDEX (changed_at)
);

/* ---------------------- cities ---------------------- */
CREATE TABLE IF NOT EXISTS cities_history (
  hist_id BIGINT AUTO_INCREMENT PRIMARY KEY,
  city_id INT,
  op_type ENUM('INSERT','UPDATE','DELETE') NOT NULL,
  changed_by VARCHAR(100),
  changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  data_before JSON,
  data_after JSON,
  INDEX (city_id),
  INDEX (changed_at)
);

/* ---------------------- customer_addresses ---------------------- */
CREATE TABLE IF NOT EXISTS customer_addresses_history (
  hist_id BIGINT AUTO_INCREMENT PRIMARY KEY,
  address_id INT,
  customer_id INT,
  op_type ENUM('INSERT','UPDATE','DELETE') NOT NULL,
  changed_by VARCHAR(100),
  changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  data_before JSON,
  data_after JSON,
  INDEX (address_id),
  INDEX (customer_id),
  INDEX (changed_at)
);

/* ---------------------- order_statuses ---------------------- */
CREATE TABLE IF NOT EXISTS order_statuses_history (
  hist_id BIGINT AUTO_INCREMENT PRIMARY KEY,
  status_id INT,
  op_type ENUM('INSERT','UPDATE','DELETE') NOT NULL,
  changed_by VARCHAR(100),
  changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  data_before JSON,
  data_after JSON,
  INDEX (status_id),
  INDEX (changed_at)
);

/* ---------------------- orders ---------------------- */
CREATE TABLE IF NOT EXISTS orders_history (
  hist_id BIGINT AUTO_INCREMENT PRIMARY KEY,
  order_id INT,
  op_type ENUM('INSERT','UPDATE','DELETE') NOT NULL,
  changed_by VARCHAR(100),
  changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  data_before JSON,
  data_after JSON,
  INDEX (order_id),
  INDEX (changed_at)
);

/* ---------------------- order_details ---------------------- */
CREATE TABLE IF NOT EXISTS order_details_history (
  hist_id BIGINT AUTO_INCREMENT PRIMARY KEY,
  order_id INT,
  store_product_service_id INT,
  op_type ENUM('INSERT','UPDATE','DELETE') NOT NULL,
  changed_by VARCHAR(100),
  changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  data_before JSON,
  data_after JSON,
  INDEX (order_id),
  INDEX (store_product_service_id),
  INDEX (changed_at)
);


-- Create triggers for all tables (use one DELIMITER block)
DELIMITER $$

/* ---------- entity_statuses triggers ---------- */
CREATE TRIGGER trg_entity_statuses_after_insert
AFTER INSERT ON entity_statuses
FOR EACH ROW
BEGIN
  INSERT INTO entity_statuses_history (status_id, op_type, changed_by, data_after)
  VALUES (
    NEW.status_id,
    'INSERT',
    COALESCE(@audit_user, 'system'),
    JSON_OBJECT(
      'status_id', NEW.status_id,
      'status_code', NEW.status_code,
      'status_description', NEW.status_description
    )
  );
END$$

CREATE TRIGGER trg_entity_statuses_before_update
BEFORE UPDATE ON entity_statuses
FOR EACH ROW
BEGIN
  INSERT INTO entity_statuses_history (status_id, op_type, changed_by, data_before, data_after)
  VALUES (
    OLD.status_id,
    'UPDATE',
    COALESCE(@audit_user, 'system'),
    JSON_OBJECT('status_id', OLD.status_id, 'status_code', OLD.status_code, 'status_description', OLD.status_description),
    JSON_OBJECT('status_id', NEW.status_id, 'status_code', NEW.status_code, 'status_description', NEW.status_description)
  );
END$$

CREATE TRIGGER trg_entity_statuses_before_delete
BEFORE DELETE ON entity_statuses
FOR EACH ROW
BEGIN
  INSERT INTO entity_statuses_history (status_id, op_type, changed_by, data_before)
  VALUES (
    OLD.status_id,
    'DELETE',
    COALESCE(@audit_user, 'system'),
    JSON_OBJECT('status_id', OLD.status_id, 'status_code', OLD.status_code, 'status_description', OLD.status_description)
  );
END$$

/* ---------- stores triggers ---------- */
CREATE TRIGGER trg_stores_after_insert
AFTER INSERT ON stores
FOR EACH ROW
BEGIN
  INSERT INTO stores_history (store_id, op_type, changed_by, data_after)
  VALUES (
    NEW.store_id,
    'INSERT',
    COALESCE(@audit_user, 'system'),
    JSON_OBJECT('store_id', NEW.store_id, 'store_email', NEW.store_email, 'store_name', NEW.store_name, 'store_description', NEW.store_description, 'store_phone', NEW.store_phone, 'store_address', NEW.store_address, 'store_status_id', NEW.store_status_id)
  );
END$$

CREATE TRIGGER trg_stores_before_update
BEFORE UPDATE ON stores
FOR EACH ROW
BEGIN
  INSERT INTO stores_history (store_id, op_type, changed_by, data_before, data_after)
  VALUES (
    OLD.store_id,
    'UPDATE',
    COALESCE(@audit_user, 'system'),
    JSON_OBJECT('store_id', OLD.store_id, 'store_email', OLD.store_email, 'store_name', OLD.store_name, 'store_description', OLD.store_description, 'store_phone', OLD.store_phone, 'store_address', OLD.store_address, 'store_status_id', OLD.store_status_id),
    JSON_OBJECT('store_id', NEW.store_id, 'store_email', NEW.store_email, 'store_name', NEW.store_name, 'store_description', NEW.store_description, 'store_phone', NEW.store_phone, 'store_address', NEW.store_address, 'store_status_id', NEW.store_status_id)
  );
END$$

CREATE TRIGGER trg_stores_before_delete
BEFORE DELETE ON stores
FOR EACH ROW
BEGIN
  INSERT INTO stores_history (store_id, op_type, changed_by, data_before)
  VALUES (
    OLD.store_id,
    'DELETE',
    COALESCE(@audit_user, 'system'),
    JSON_OBJECT('store_id', OLD.store_id, 'store_email', OLD.store_email, 'store_name', OLD.store_name, 'store_description', OLD.store_description, 'store_phone', OLD.store_phone, 'store_address', OLD.store_address, 'store_status_id', OLD.store_status_id)
  );
END$$

/* ---------- roles triggers ---------- */
CREATE TRIGGER trg_roles_after_insert
AFTER INSERT ON roles
FOR EACH ROW
BEGIN
  INSERT INTO roles_history (role_id, op_type, changed_by, data_after)
  VALUES (
    NEW.role_id,
    'INSERT',
    COALESCE(@audit_user, 'system'),
    JSON_OBJECT('role_id', NEW.role_id, 'role_code', NEW.role_code, 'role_description', NEW.role_description)
  );
END$$

CREATE TRIGGER trg_roles_before_update
BEFORE UPDATE ON roles
FOR EACH ROW
BEGIN
  INSERT INTO roles_history (role_id, op_type, changed_by, data_before, data_after)
  VALUES (
    OLD.role_id,
    'UPDATE',
    COALESCE(@audit_user, 'system'),
    JSON_OBJECT('role_id', OLD.role_id, 'role_code', OLD.role_code, 'role_description', OLD.role_description),
    JSON_OBJECT('role_id', NEW.role_id, 'role_code', NEW.role_code, 'role_description', NEW.role_description)
  );
END$$

CREATE TRIGGER trg_roles_before_delete
BEFORE DELETE ON roles
FOR EACH ROW
BEGIN
  INSERT INTO roles_history (role_id, op_type, changed_by, data_before)
  VALUES (
    OLD.role_id,
    'DELETE',
    COALESCE(@audit_user, 'system'),
    JSON_OBJECT('role_id', OLD.role_id, 'role_code', OLD.role_code, 'role_description', OLD.role_description)
  );
END$$

/* ---------- store_user_role triggers ---------- */
CREATE TRIGGER trg_store_user_role_after_insert
AFTER INSERT ON store_user_role
FOR EACH ROW
BEGIN
  INSERT INTO store_user_role_history (store_id, user_id, role_id, op_type, changed_by, data_after)
  VALUES (
    NEW.store_id,
    NEW.user_id,
    NEW.role_id,
    'INSERT',
    COALESCE(@audit_user, 'system'),
    JSON_OBJECT('store_id', NEW.store_id, 'user_id', NEW.user_id, 'role_id', NEW.role_id, 'status_id', NEW.status_id)
  );
END$$

CREATE TRIGGER trg_store_user_role_before_update
BEFORE UPDATE ON store_user_role
FOR EACH ROW
BEGIN
  INSERT INTO store_user_role_history (store_id, user_id, role_id, op_type, changed_by, data_before, data_after)
  VALUES (
    OLD.store_id,
    OLD.user_id,
    OLD.role_id,
    'UPDATE',
    COALESCE(@audit_user, 'system'),
    JSON_OBJECT('store_id', OLD.store_id, 'user_id', OLD.user_id, 'role_id', OLD.role_id, 'status_id', OLD.status_id),
    JSON_OBJECT('store_id', NEW.store_id, 'user_id', NEW.user_id, 'role_id', NEW.role_id, 'status_id', NEW.status_id)
  );
END$$

CREATE TRIGGER trg_store_user_role_before_delete
BEFORE DELETE ON store_user_role
FOR EACH ROW
BEGIN
  INSERT INTO store_user_role_history (store_id, user_id, role_id, op_type, changed_by, data_before)
  VALUES (
    OLD.store_id,
    OLD.user_id,
    OLD.role_id,
    'DELETE',
    COALESCE(@audit_user, 'system'),
    JSON_OBJECT('store_id', OLD.store_id, 'user_id', OLD.user_id, 'role_id', OLD.role_id, 'status_id', OLD.status_id)
  );
END$$

/* ---------- categories triggers ---------- */
CREATE TRIGGER trg_categories_after_insert
AFTER INSERT ON categories
FOR EACH ROW
BEGIN
  INSERT INTO categories_history (category_id, op_type, changed_by, data_after)
  VALUES (
    NEW.category_id,
    'INSERT',
    COALESCE(@audit_user, 'system'),
    JSON_OBJECT('category_id', NEW.category_id, 'category_name', NEW.category_name, 'category_description', NEW.category_description, 'category_pic_path', NEW.category_pic_path, 'category_status_id', NEW.category_status_id)
  );
END$$

CREATE TRIGGER trg_categories_before_update
BEFORE UPDATE ON categories
FOR EACH ROW
BEGIN
  INSERT INTO categories_history (category_id, op_type, changed_by, data_before, data_after)
  VALUES (
    OLD.category_id,
    'UPDATE',
    COALESCE(@audit_user, 'system'),
    JSON_OBJECT('category_id', OLD.category_id, 'category_name', OLD.category_name, 'category_description', OLD.category_description, 'category_pic_path', OLD.category_pic_path, 'category_status_id', OLD.category_status_id),
    JSON_OBJECT('category_id', NEW.category_id, 'category_name', NEW.category_name, 'category_description', NEW.category_description, 'category_pic_path', NEW.category_pic_path, 'category_status_id', NEW.category_status_id)
  );
END$$

CREATE TRIGGER trg_categories_before_delete
BEFORE DELETE ON categories
FOR EACH ROW
BEGIN
  INSERT INTO categories_history (category_id, op_type, changed_by, data_before)
  VALUES (
    OLD.category_id,
    'DELETE',
    COALESCE(@audit_user, 'system'),
    JSON_OBJECT('category_id', OLD.category_id, 'category_name', OLD.category_name, 'category_description', OLD.category_description, 'category_pic_path', OLD.category_pic_path, 'category_status_id', OLD.category_status_id)
  );
END$$

/* ---------- products_services triggers ---------- */
CREATE TRIGGER trg_products_services_after_insert
AFTER INSERT ON products_services
FOR EACH ROW
BEGIN
  INSERT INTO products_services_history (product_service_id, op_type, changed_by, data_after)
  VALUES (
    NEW.product_service_id,
    'INSERT',
    COALESCE(@audit_user, 'system'),
    JSON_OBJECT('product_service_id', NEW.product_service_id, 'product_service_name', NEW.product_service_name, 'product_service_description', NEW.product_service_description, 'product_service_pic_path', NEW.product_service_pic_path, 'product_service_category_id', NEW.product_service_category_id, 'product_service_status_id', NEW.product_service_status_id)
  );
END$$

CREATE TRIGGER trg_products_services_before_update
BEFORE UPDATE ON products_services
FOR EACH ROW
BEGIN
  INSERT INTO products_services_history (product_service_id, op_type, changed_by, data_before, data_after)
  VALUES (
    OLD.product_service_id,
    'UPDATE',
    COALESCE(@audit_user, 'system'),
    JSON_OBJECT('product_service_id', OLD.product_service_id, 'product_service_name', OLD.product_service_name, 'product_service_description', OLD.product_service_description, 'product_service_pic_path', OLD.product_service_pic_path, 'product_service_category_id', OLD.product_service_category_id, 'product_service_status_id', OLD.product_service_status_id),
    JSON_OBJECT('product_service_id', NEW.product_service_id, 'product_service_name', NEW.product_service_name, 'product_service_description', NEW.product_service_description, 'product_service_pic_path', NEW.product_service_pic_path, 'product_service_category_id', NEW.product_service_category_id, 'product_service_status_id', NEW.product_service_status_id)
  );
END$$

CREATE TRIGGER trg_products_services_before_delete
BEFORE DELETE ON products_services
FOR EACH ROW
BEGIN
  INSERT INTO products_services_history (product_service_id, op_type, changed_by, data_before)
  VALUES (
    OLD.product_service_id,
    'DELETE',
    COALESCE(@audit_user, 'system'),
    JSON_OBJECT('product_service_id', OLD.product_service_id, 'product_service_name', OLD.product_service_name, 'product_service_description', OLD.product_service_description, 'product_service_pic_path', OLD.product_service_pic_path, 'product_service_category_id', OLD.product_service_category_id, 'product_service_status_id', OLD.product_service_status_id)
  );
END$$

/* ---------- store_products_services triggers ---------- */
CREATE TRIGGER trg_store_products_services_after_insert
AFTER INSERT ON store_products_services
FOR EACH ROW
BEGIN
  INSERT INTO store_products_services_history (id, store_id, product_service_id, op_type, changed_by, data_after)
  VALUES (
    NEW.id,
    NEW.store_id,
    NEW.product_service_id,
    'INSERT',
    COALESCE(@audit_user, 'system'),
    JSON_OBJECT('id', NEW.id, 'store_id', NEW.store_id, 'product_service_id', NEW.product_service_id, 'price', NEW.price, 'stock', NEW.stock, 'status_id', NEW.status_id)
  );
END$$

CREATE TRIGGER trg_store_products_services_before_update
BEFORE UPDATE ON store_products_services
FOR EACH ROW
BEGIN
  INSERT INTO store_products_services_history (id, store_id, product_service_id, op_type, changed_by, data_before, data_after)
  VALUES (
    OLD.id,
    OLD.store_id,
    OLD.product_service_id,
    'UPDATE',
    COALESCE(@audit_user, 'system'),
    JSON_OBJECT('id', OLD.id, 'store_id', OLD.store_id, 'product_service_id', OLD.product_service_id, 'price', OLD.price, 'stock', OLD.stock, 'status_id', OLD.status_id),
    JSON_OBJECT('id', NEW.id, 'store_id', NEW.store_id, 'product_service_id', NEW.product_service_id, 'price', NEW.price, 'stock', NEW.stock, 'status_id', NEW.status_id)
  );
END$$

CREATE TRIGGER trg_store_products_services_before_delete
BEFORE DELETE ON store_products_services
FOR EACH ROW
BEGIN
  INSERT INTO store_products_services_history (id, store_id, product_service_id, op_type, changed_by, data_before)
  VALUES (
    OLD.id,
    OLD.store_id,
    OLD.product_service_id,
    'DELETE',
    COALESCE(@audit_user, 'system'),
    JSON_OBJECT('id', OLD.id, 'store_id', OLD.store_id, 'product_service_id', OLD.product_service_id, 'price', OLD.price, 'stock', OLD.stock, 'status_id', OLD.status_id)
  );
END$$

/* ---------- customers triggers ---------- */
CREATE TRIGGER trg_customers_after_insert
AFTER INSERT ON customers
FOR EACH ROW
BEGIN
  INSERT INTO customers_history (customer_id, op_type, changed_by, data_after)
  VALUES (
    NEW.customer_id,
    'INSERT',
    COALESCE(@audit_user, 'system'),
    JSON_OBJECT('customer_id', NEW.customer_id, 'customer_email', NEW.customer_email, 'customer_name', NEW.customer_name, 'customer_phone', NEW.customer_phone, 'customer_status_id', NEW.customer_status_id)
  );
END$$

CREATE TRIGGER trg_customers_before_update
BEFORE UPDATE ON customers
FOR EACH ROW
BEGIN
  INSERT INTO customers_history (customer_id, op_type, changed_by, data_before, data_after)
  VALUES (
    OLD.customer_id,
    'UPDATE',
    COALESCE(@audit_user, 'system'),
    JSON_OBJECT('customer_id', OLD.customer_id, 'customer_email', OLD.customer_email, 'customer_name', OLD.customer_name, 'customer_phone', OLD.customer_phone, 'customer_status_id', OLD.customer_status_id),
    JSON_OBJECT('customer_id', NEW.customer_id, 'customer_email', NEW.customer_email, 'customer_name', NEW.customer_name, 'customer_phone', NEW.customer_phone, 'customer_status_id', NEW.customer_status_id)
  );
END$$

CREATE TRIGGER trg_customers_before_delete
BEFORE DELETE ON customers
FOR EACH ROW
BEGIN
  INSERT INTO customers_history (customer_id, op_type, changed_by, data_before)
  VALUES (
    OLD.customer_id,
    'DELETE',
    COALESCE(@audit_user, 'system'),
    JSON_OBJECT('customer_id', OLD.customer_id, 'customer_email', OLD.customer_email, 'customer_name', OLD.customer_name, 'customer_phone', OLD.customer_phone, 'customer_status_id', OLD.customer_status_id)
  );
END$$

/* ---------- countries triggers ---------- */
CREATE TRIGGER trg_countries_after_insert
AFTER INSERT ON countries
FOR EACH ROW
BEGIN
  INSERT INTO countries_history (country_id, op_type, changed_by, data_after)
  VALUES (
    NEW.country_id,
    'INSERT',
    COALESCE(@audit_user, 'system'),
    JSON_OBJECT('country_id', NEW.country_id, 'country_name', NEW.country_name, 'country_code', NEW.country_code, 'country_status_id', NEW.country_status_id)
  );
END$$

CREATE TRIGGER trg_countries_before_update
BEFORE UPDATE ON countries
FOR EACH ROW
BEGIN
  INSERT INTO countries_history (country_id, op_type, changed_by, data_before, data_after)
  VALUES (
    OLD.country_id,
    'UPDATE',
    COALESCE(@audit_user, 'system'),
    JSON_OBJECT('country_id', OLD.country_id, 'country_name', OLD.country_name, 'country_code', OLD.country_code, 'country_status_id', OLD.country_status_id),
    JSON_OBJECT('country_id', NEW.country_id, 'country_name', NEW.country_name, 'country_code', NEW.country_code, 'country_status_id', NEW.country_status_id)
  );
END$$

CREATE TRIGGER trg_countries_before_delete
BEFORE DELETE ON countries
FOR EACH ROW
BEGIN
  INSERT INTO countries_history (country_id, op_type, changed_by, data_before)
  VALUES (
    OLD.country_id,
    'DELETE',
    COALESCE(@audit_user, 'system'),
    JSON_OBJECT('country_id', OLD.country_id, 'country_name', OLD.country_name, 'country_code', OLD.country_code, 'country_status_id', OLD.country_status_id)
  );
END$$

/* ---------- states_regions triggers ---------- */
CREATE TRIGGER trg_states_regions_after_insert
AFTER INSERT ON states_regions
FOR EACH ROW
BEGIN
  INSERT INTO states_regions_history (state_region_id, op_type, changed_by, data_after)
  VALUES (
    NEW.state_region_id,
    'INSERT',
    COALESCE(@audit_user, 'system'),
    JSON_OBJECT('state_region_id', NEW.state_region_id, 'state_region_name', NEW.state_region_name, 'state_region_code', NEW.state_region_code, 'country_id', NEW.country_id, 'state_region_status_id', NEW.state_region_status_id)
  );
END$$

CREATE TRIGGER trg_states_regions_before_update
BEFORE UPDATE ON states_regions
FOR EACH ROW
BEGIN
  INSERT INTO states_regions_history (state_region_id, op_type, changed_by, data_before, data_after)
  VALUES (
    OLD.state_region_id,
    'UPDATE',
    COALESCE(@audit_user, 'system'),
    JSON_OBJECT('state_region_id', OLD.state_region_id, 'state_region_name', OLD.state_region_name, 'state_region_code', OLD.state_region_code, 'country_id', OLD.country_id, 'state_region_status_id', OLD.state_region_status_id),
    JSON_OBJECT('state_region_id', NEW.state_region_id, 'state_region_name', NEW.state_region_name, 'state_region_code', NEW.state_region_code, 'country_id', NEW.country_id, 'state_region_status_id', NEW.state_region_status_id)
  );
END$$

CREATE TRIGGER trg_states_regions_before_delete
BEFORE DELETE ON states_regions
FOR EACH ROW
BEGIN
  INSERT INTO states_regions_history (state_region_id, op_type, changed_by, data_before)
  VALUES (
    OLD.state_region_id,
    'DELETE',
    COALESCE(@audit_user, 'system'),
    JSON_OBJECT('state_region_id', OLD.state_region_id, 'state_region_name', OLD.state_region_name, 'state_region_code', OLD.state_region_code, 'country_id', OLD.country_id, 'state_region_status_id', OLD.state_region_status_id)
  );
END$$

/* ---------- cities triggers ---------- */
CREATE TRIGGER trg_cities_after_insert
AFTER INSERT ON cities
FOR EACH ROW
BEGIN
  INSERT INTO cities_history (city_id, op_type, changed_by, data_after)
  VALUES (
    NEW.city_id,
    'INSERT',
    COALESCE(@audit_user, 'system'),
    JSON_OBJECT('city_id', NEW.city_id, 'city_name', NEW.city_name, 'state_region_id', NEW.state_region_id, 'city_status_id', NEW.city_status_id)
  );
END$$

CREATE TRIGGER trg_cities_before_update
BEFORE UPDATE ON cities
FOR EACH ROW
BEGIN
  INSERT INTO cities_history (city_id, op_type, changed_by, data_before, data_after)
  VALUES (
    OLD.city_id,
    'UPDATE',
    COALESCE(@audit_user, 'system'),
    JSON_OBJECT('city_id', OLD.city_id, 'city_name', OLD.city_name, 'state_region_id', OLD.state_region_id, 'city_status_id', OLD.city_status_id),
    JSON_OBJECT('city_id', NEW.city_id, 'city_name', NEW.city_name, 'state_region_id', NEW.state_region_id, 'city_status_id', NEW.city_status_id)
  );
END$$

CREATE TRIGGER trg_cities_before_delete
BEFORE DELETE ON cities
FOR EACH ROW
BEGIN
  INSERT INTO cities_history (city_id, op_type, changed_by, data_before)
  VALUES (
    OLD.city_id,
    'DELETE',
    COALESCE(@audit_user, 'system'),
    JSON_OBJECT('city_id', OLD.city_id, 'city_name', OLD.city_name, 'state_region_id', OLD.state_region_id, 'city_status_id', OLD.city_status_id)
  );
END$$

/* ---------- customer_addresses triggers ---------- */
CREATE TRIGGER trg_customer_addresses_after_insert
AFTER INSERT ON customer_addresses
FOR EACH ROW
BEGIN
  INSERT INTO customer_addresses_history (address_id, customer_id, op_type, changed_by, data_after)
  VALUES (
    NEW.address_id,
    NEW.customer_id,
    'INSERT',
    COALESCE(@audit_user, 'system'),
    JSON_OBJECT('address_id', NEW.address_id, 'customer_id', NEW.customer_id, 'address_line1', NEW.address_line1, 'address_line2', NEW.address_line2, 'city_id', NEW.city_id, 'google_maps_url', NEW.google_maps_url, 'address_status_id', NEW.address_status_id, 'postal_code', NEW.postal_code)
  );
END$$

CREATE TRIGGER trg_customer_addresses_before_update
BEFORE UPDATE ON customer_addresses
FOR EACH ROW
BEGIN
  INSERT INTO customer_addresses_history (address_id, customer_id, op_type, changed_by, data_before, data_after)
  VALUES (
    OLD.address_id,
    OLD.customer_id,
    'UPDATE',
    COALESCE(@audit_user, 'system'),
    JSON_OBJECT('address_id', OLD.address_id, 'customer_id', OLD.customer_id, 'address_line1', OLD.address_line1, 'address_line2', OLD.address_line2, 'city_id', OLD.city_id, 'google_maps_url', OLD.google_maps_url, 'address_status_id', OLD.address_status_id, 'postal_code', OLD.postal_code),
    JSON_OBJECT('address_id', NEW.address_id, 'customer_id', NEW.customer_id, 'address_line1', NEW.address_line1, 'address_line2', NEW.address_line2, 'city_id', NEW.city_id, 'google_maps_url', NEW.google_maps_url, 'address_status_id', NEW.address_status_id, 'postal_code', NEW.postal_code)
  );
END$$

CREATE TRIGGER trg_customer_addresses_before_delete
BEFORE DELETE ON customer_addresses
FOR EACH ROW
BEGIN
  INSERT INTO customer_addresses_history (address_id, customer_id, op_type, changed_by, data_before)
  VALUES (
    OLD.address_id,
    OLD.customer_id,
    'DELETE',
    COALESCE(@audit_user, 'system'),
    JSON_OBJECT('address_id', OLD.address_id, 'customer_id', OLD.customer_id, 'address_line1', OLD.address_line1, 'address_line2', OLD.address_line2, 'city_id', OLD.city_id, 'google_maps_url', OLD.google_maps_url, 'address_status_id', OLD.address_status_id, 'postal_code', OLD.postal_code)
  );
END$$

/* ---------- order_statuses triggers ---------- */
CREATE TRIGGER trg_order_statuses_after_insert
AFTER INSERT ON order_statuses
FOR EACH ROW
BEGIN
  INSERT INTO order_statuses_history (status_id, op_type, changed_by, data_after)
  VALUES (
    NEW.status_id,
    'INSERT',
    COALESCE(@audit_user, 'system'),
    JSON_OBJECT('status_id', NEW.status_id, 'status_code', NEW.status_code, 'status_description', NEW.status_description)
  );
END$$

CREATE TRIGGER trg_order_statuses_before_update
BEFORE UPDATE ON order_statuses
FOR EACH ROW
BEGIN
  INSERT INTO order_statuses_history (status_id, op_type, changed_by, data_before, data_after)
  VALUES (
    OLD.status_id,
    'UPDATE',
    COALESCE(@audit_user, 'system'),
    JSON_OBJECT('status_id', OLD.status_id, 'status_code', OLD.status_code, 'status_description', OLD.status_description),
    JSON_OBJECT('status_id', NEW.status_id, 'status_code', NEW.status_code, 'status_description', NEW.status_description)
  );
END$$

CREATE TRIGGER trg_order_statuses_before_delete
BEFORE DELETE ON order_statuses
FOR EACH ROW
BEGIN
  INSERT INTO order_statuses_history (status_id, op_type, changed_by, data_before)
  VALUES (
    OLD.status_id,
    'DELETE',
    COALESCE(@audit_user, 'system'),
    JSON_OBJECT('status_id', OLD.status_id, 'status_code', OLD.status_code, 'status_description', OLD.status_description)
  );
END$$

/* ---------- orders triggers ---------- */
CREATE TRIGGER trg_orders_after_insert
AFTER INSERT ON orders
FOR EACH ROW
BEGIN
  INSERT INTO orders_history (order_id, op_type, changed_by, data_after)
  VALUES (
    NEW.order_id,
    'INSERT',
    COALESCE(@audit_user, 'system'),
    JSON_OBJECT('order_id', NEW.order_id, 'order_tot_quantity', NEW.order_tot_quantity, 'order_tot_price', NEW.order_tot_price, 'customer_id', NEW.customer_id, 'order_status_id', NEW.order_status_id)
  );
END$$

CREATE TRIGGER trg_orders_before_update
BEFORE UPDATE ON orders
FOR EACH ROW
BEGIN
  INSERT INTO orders_history (order_id, op_type, changed_by, data_before, data_after)
  VALUES (
    OLD.order_id,
    'UPDATE',
    COALESCE(@audit_user, 'system'),
    JSON_OBJECT('order_id', OLD.order_id, 'order_tot_quantity', OLD.order_tot_quantity, 'order_tot_price', OLD.order_tot_price, 'customer_id', OLD.customer_id, 'order_status_id', OLD.order_status_id),
    JSON_OBJECT('order_id', NEW.order_id, 'order_tot_quantity', NEW.order_tot_quantity, 'order_tot_price', NEW.order_tot_price, 'customer_id', NEW.customer_id, 'order_status_id', NEW.order_status_id)
  );
END$$

CREATE TRIGGER trg_orders_before_delete
BEFORE DELETE ON orders
FOR EACH ROW
BEGIN
  INSERT INTO orders_history (order_id, op_type, changed_by, data_before)
  VALUES (
    OLD.order_id,
    'DELETE',
    COALESCE(@audit_user, 'system'),
    JSON_OBJECT('order_id', OLD.order_id, 'order_tot_quantity', OLD.order_tot_quantity, 'order_tot_price', OLD.order_tot_price, 'customer_id', OLD.customer_id, 'order_status_id', OLD.order_status_id)
  );
END$$

/* ---------- order_details triggers ---------- */
CREATE TRIGGER trg_order_details_after_insert
AFTER INSERT ON order_details
FOR EACH ROW
BEGIN
  INSERT INTO order_details_history (order_id, store_product_service_id, op_type, changed_by, data_after)
  VALUES (
    NEW.order_id,
    NEW.store_product_service_id,
    'INSERT',
    COALESCE(@audit_user, 'system'),
    JSON_OBJECT('order_id', NEW.order_id, 'store_product_service_id', NEW.store_product_service_id, 'product_service_quantity', NEW.product_service_quantity, 'product_service_price', NEW.product_service_price, 'product_service_tot_price', NEW.product_service_tot_price, 'product_service_status_id', NEW.product_service_status_id)
  );
END$$

CREATE TRIGGER trg_order_details_before_update
BEFORE UPDATE ON order_details
FOR EACH ROW
BEGIN
  INSERT INTO order_details_history (order_id, store_product_service_id, op_type, changed_by, data_before, data_after)
  VALUES (
    OLD.order_id,
    OLD.store_product_service_id,
    'UPDATE',
    COALESCE(@audit_user, 'system'),
    JSON_OBJECT('order_id', OLD.order_id, 'store_product_service_id', OLD.store_product_service_id, 'product_service_quantity', OLD.product_service_quantity, 'product_service_price', OLD.product_service_price, 'product_service_tot_price', OLD.product_service_tot_price, 'product_service_status_id', OLD.product_service_status_id),
    JSON_OBJECT('order_id', NEW.order_id, 'store_product_service_id', NEW.store_product_service_id, 'product_service_quantity', NEW.product_service_quantity, 'product_service_price', NEW.product_service_price, 'product_service_tot_price', NEW.product_service_tot_price, 'product_service_status_id', NEW.product_service_status_id)
  );
END$$

CREATE TRIGGER trg_order_details_before_delete
BEFORE DELETE ON order_details
FOR EACH ROW
BEGIN
  INSERT INTO order_details_history (order_id, store_product_service_id, op_type, changed_by, data_before)
  VALUES (
    OLD.order_id,
    OLD.store_product_service_id,
    'DELETE',
    COALESCE(@audit_user, 'system'),
    JSON_OBJECT('order_id', OLD.order_id, 'store_product_service_id', OLD.store_product_service_id, 'product_service_quantity', OLD.product_service_quantity, 'product_service_price', OLD.product_service_price, 'product_service_tot_price', OLD.product_service_tot_price, 'product_service_status_id', OLD.product_service_status_id)
  );
END$$


-- Reset delimiter back to default ';'
DELIMITER ;

-- End of init.sql
