CREATE DATABASE IF NOT EXISTS aaitech_inventory;
USE aaitech_inventory;

CREATE TABLE IF NOT EXISTS inventory (
    item_id VARCHAR(50),
    product_name VARCHAR(100),
    location VARCHAR(50),
    quantity INT DEFAULT 0,
    PRIMARY KEY (item_id, location)
);



INSERT INTO inventory (item_id, product_name, location, quantity) VALUES
('LAP-001', 'Dell Inspiron Laptop', 'Bengaluru', 25),
('LAP-002', 'HP Pavilion Laptop', 'Mumbai', 15),
('LAP-003', 'Lenovo ThinkPad Laptop', 'Bengaluru', 10),
('LAP-004', 'Apple MacBook Air', 'Delhi', 8),
('LAP-005', 'Asus VivoBook', 'Mumbai', 12),
('LAP-006', 'Acer Aspire 7', 'Pune', 14),

('MOB-001', 'iPhone 14', 'Bengaluru', 40),
('MOB-002', 'Samsung Galaxy S23', 'Mumbai', 35),
('MOB-003', 'OnePlus 11', 'Delhi', 20),
('MOB-004', 'Google Pixel 7', 'Bengaluru', 18),
('MOB-005', 'Xiaomi Redmi Note 12', 'Mumbai', 22),
('MOB-006', 'Realme 12 Pro', 'Pune', 16),

('TAB-001', 'Apple iPad Air', 'Delhi', 14),
('TAB-002', 'Samsung Galaxy Tab S8', 'Bengaluru', 17),
('TAB-003', 'Lenovo Tab M10', 'Mumbai', 9),
('TAB-004', 'Microsoft Surface Go', 'Delhi', 11),
('TAB-005', 'Amazon Fire HD 10', 'Bengaluru', 13),
('TAB-006', 'iBall Slide', 'Pune', 8),

('ACC-001', 'Logitech Mouse', 'Mumbai', 50),
('ACC-002', 'Dell Keyboard', 'Delhi', 45),
('ACC-003', 'HP USB-C Dock', 'Bengaluru', 60),
('ACC-004', 'Samsung 25W Charger', 'Mumbai', 30),
('ACC-005', 'Apple AirPods', 'Delhi', 55),
('ACC-006', 'Boat Headphones', 'Pune', 20);