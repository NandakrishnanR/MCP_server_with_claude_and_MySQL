CREATE DATABASE IF NOT EXISTS aaitech_inventory;
USE aaitech_inventory;

CREATE TABLE IF NOT EXISTS inventory (
    item_id VARCHAR(50),
    product_name VARCHAR(100),
    location VARCHAR(50),
    quantity INT DEFAULT 0,
    PRIMARY KEY (item_id, location)
);



INSERT IGNORE INTO inventory (item_id, product_name, location, quantity) VALUES
('LAP-001', 'Dell Inspiron Laptop', 'Berlin', 25),
('LAP-002', 'HP Pavilion Laptop', 'Munich', 15),
('LAP-003', 'Lenovo ThinkPad Laptop', 'Berlin', 10),
('LAP-004', 'Apple MacBook Air', 'Hamburg', 8),
('LAP-005', 'Asus VivoBook', 'Munich', 12),
('LAP-006', 'Acer Aspire 7', 'Frankfurt', 14),

('MOB-001', 'iPhone 14', 'Berlin', 40),
('MOB-002', 'Samsung Galaxy S23', 'Munich', 35),
('MOB-003', 'OnePlus 11', 'Hamburg', 20),
('MOB-004', 'Google Pixel 7', 'Berlin', 18),
('MOB-005', 'Xiaomi Redmi Note 12', 'Munich', 22),
('MOB-006', 'Realme 12 Pro', 'Frankfurt', 16),

('TAB-001', 'Apple iPad Air', 'Hamburg', 14),
('TAB-002', 'Samsung Galaxy Tab S8', 'Berlin', 17),
('TAB-003', 'Lenovo Tab M10', 'Munich', 9),
('TAB-004', 'Microsoft Surface Go', 'Hamburg', 11),
('TAB-005', 'Amazon Fire HD 10', 'Berlin', 13),
('TAB-006', 'iBall Slide', 'Frankfurt', 8),

('ACC-001', 'Logitech Mouse', 'Munich', 50),
('ACC-002', 'Dell Keyboard', 'Hamburg', 45),
('ACC-003', 'HP USB-C Dock', 'Berlin', 60),
('ACC-004', 'Samsung 25W Charger', 'Munich', 30),
('ACC-005', 'Apple AirPods', 'Hamburg', 55),
('ACC-006', 'Boat Headphones', 'Frankfurt', 20);