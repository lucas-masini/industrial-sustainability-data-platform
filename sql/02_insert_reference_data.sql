/*==========================================================
  INSERTION DES DONNÉES DE RÉFÉRENCE

  Ce script insère les données de référence utilisées par
  l'ensemble de la plateforme :
  - Sites industriels
  - Produits
  - Fournisseurs
  - Transporteurs
  - Sources d'énergie
==========================================================*/

USE helios_industrial_group;

/*==========================================================
  SITE
==========================================================*/

INSERT INTO site (
    site_name,
    city,
    country,
    surface_m2,
    employees_count
)
VALUES
('Helios Lyon', 'Lyon', 'France', 48000, 420),
('Helios Toulouse', 'Toulouse', 'France', 39000, 340),
('Helios Montpellier', 'Montpellier', 'France', 27000, 210),
('Helios Nantes', 'Nantes', 'France', 36000, 295),
('Helios Strasbourg', 'Strasbourg', 'France', 52000, 460);

/*==========================================================
  PRODUCT
==========================================================*/

INSERT INTO product (
    site_id,
    product_code,
    product_name,
    product_category
)
VALUES
(1, 'BAT-001', 'Industrial Battery', 'Energy Storage'),
(1, 'BAT-002', 'Residential Battery', 'Energy Storage'),
(2, 'WIN-001', 'Wind Turbine Blade', 'Wind Energy'),
(2, 'WIN-002', 'Wind Turbine Hub', 'Wind Energy'),
(3, 'SOL-001', 'Photovoltaic Structure', 'Solar Energy'),
(3, 'SOL-002', 'Solar Panel Support', 'Solar Energy'),
(4, 'ELE-001', 'Electrical Cabinet', 'Electrical Systems'),
(4, 'ELE-002', 'Electrical Distribution Panel', 'Electrical Systems'),
(5, 'REC-001', 'Recycled Aluminum Pellets', 'Recycling'),
(5, 'REC-002', 'Recycled Steel', 'Recycling');

/*==========================================================
  SUPPLIER
==========================================================*/

INSERT INTO supplier (
    supplier_code,
    supplier_name,
    country,
    supplier_type,
    iso14001_certified,
    sustainability_score
)
VALUES
('SUP-001', 'GreenSteel France', 'France', 'Raw Materials', TRUE, 92),
('SUP-002', 'SolarTech Europe', 'Germany', 'Renewable Components', TRUE, 95),
('SUP-003', 'EcoMetals Iberia', 'Spain', 'Metals', TRUE, 89),
('SUP-004', 'Nordic Components', 'Sweden', 'Renewable Components', TRUE, 97),
('SUP-005', 'PolyTech Industries', 'Italy', 'Plastics', FALSE, 72),
('SUP-006', 'Euro Cables', 'France', 'Electrical Components', TRUE, 91),
('SUP-007', 'MetalCore Belgium', 'Belgium', 'Metals', FALSE, 69),
('SUP-008', 'WindForce Materials', 'Denmark', 'Wind Components', TRUE, 96);

/*==========================================================
  TRANSPORT COMPANY
==========================================================*/

INSERT INTO transport_company (
    transport_company_code,
    transport_company_name,
    country,
    transport_type
)
VALUES
('TRP-001', 'Green Logistics France', 'France', 'Road'),
('TRP-002', 'Euro Freight Solutions', 'Germany', 'Road'),
('TRP-003', 'Nordic Transport Group', 'Sweden', 'Road'),
('TRP-004', 'Eco Rail Cargo', 'France', 'Rail'),
('TRP-005', 'Blue Shipping Lines', 'Netherlands', 'Maritime');

/*==========================================================
  ENERGY SOURCE
==========================================================*/

INSERT INTO energy_source (
    energy_source_code,
    energy_source_name,
    renewable
)
VALUES
('ENG-001', 'Electricity', FALSE),
('ENG-002', 'Natural Gas', FALSE),
('ENG-003', 'Solar', TRUE),
('ENG-004', 'Wind', TRUE),
('ENG-005', 'Hydroelectric', TRUE);