-- Permanent Database Cleanup: German Cities Only
-- Run this once to clean your database and prevent future non-German entries

USE aaitech_inventory;

-- 1) Delete everything not in Germany
DELETE FROM inventory
WHERE location NOT IN (
  'Berlin','Munich','Hamburg','Frankfurt','Cologne',
  'Stuttgart','Dusseldorf','Dortmund','Essen','Leipzig',
  'Bremen','Dresden','Hanover','Nuremberg','Duisburg',
  'Bochum','Wuppertal','Bielefeld','Bonn','Munster'
);

-- 2) Create canonical locations table (Germany only)
DROP TABLE IF EXISTS locations;
CREATE TABLE locations (
  name VARCHAR(50) PRIMARY KEY
);

INSERT INTO locations (name) VALUES
('Berlin'),('Munich'),('Hamburg'),('Frankfurt'),('Cologne'),
('Stuttgart'),('Dusseldorf'),('Dortmund'),('Essen'),('Leipzig'),
('Bremen'),('Dresden'),('Hanover'),('Nuremberg'),('Duisburg'),
('Bochum','Wuppertal','Bielefeld','Bonn','Munster');

-- 3) Enforce: inventory.location must be a valid German city
-- Ensure column type matches
ALTER TABLE inventory MODIFY location VARCHAR(50) NOT NULL;

-- Drop any existing FK with same name if present (ignore error if none)
-- ALTER TABLE inventory DROP FOREIGN KEY fk_inventory_location;

ALTER TABLE inventory
  ADD CONSTRAINT fk_inventory_location
  FOREIGN KEY (location) REFERENCES locations(name)
  ON UPDATE CASCADE ON DELETE RESTRICT;

-- 4) Verify the cleanup
SELECT 'Cleanup completed. Current inventory:' as status;
SELECT location, COUNT(*) as item_count FROM inventory GROUP BY location ORDER BY item_count DESC;
