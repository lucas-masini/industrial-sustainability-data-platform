-- Créer la BDD

CREATE DATABASE IF NOT EXISTS helios_industrial_group;

USE helios_industrial_group;

/*==========================================================
  TABLES DE RÉFÉRENCE
==========================================================*/

-- Créer la table "site"

CREATE TABLE site (
    site_id INT AUTO_INCREMENT PRIMARY KEY,
    site_name VARCHAR(100) NOT NULL UNIQUE,
    city VARCHAR(100) NOT NULL,
    country VARCHAR(100) NOT NULL,
    surface_m2 INT NOT NULL,
    employees_count INT NOT NULL
);

-- Créer la table "product"

CREATE TABLE product (
    product_id INT AUTO_INCREMENT PRIMARY KEY,
    site_id INT NOT NULL,
    product_code VARCHAR(20) NOT NULL UNIQUE,
    product_name VARCHAR(100) NOT NULL,
    product_category VARCHAR(100) NOT NULL,

    CONSTRAINT fk_product_site
        FOREIGN KEY (site_id)
        REFERENCES site(site_id)
);

-- Créer la table "supplier"

CREATE TABLE supplier (
    supplier_id INT AUTO_INCREMENT PRIMARY KEY,
    supplier_code VARCHAR(20) NOT NULL UNIQUE,
    supplier_name VARCHAR(100) NOT NULL,
    country VARCHAR(100) NOT NULL,
    supplier_type VARCHAR(100) NOT NULL,
    iso14001_certified BOOLEAN NOT NULL,
    sustainability_score TINYINT NOT NULL,

    CONSTRAINT chk_supplier_score
        CHECK (sustainability_score BETWEEN 0 AND 100)
);

-- Créer la table "transport_company"

CREATE TABLE transport_company (
    transport_company_id INT AUTO_INCREMENT PRIMARY KEY,
    transport_company_code VARCHAR(20) NOT NULL UNIQUE,
    transport_company_name VARCHAR(100) NOT NULL,
    country VARCHAR(100) NOT NULL,
    transport_type VARCHAR(50) NOT NULL
);

-- Créer la table "energy_source"

CREATE TABLE energy_source (
    energy_source_id INT AUTO_INCREMENT PRIMARY KEY,
    energy_source_code VARCHAR(20) NOT NULL UNIQUE,
    energy_source_name VARCHAR(100) NOT NULL,
    renewable BOOLEAN NOT NULL
);

/*==========================================================
  TABLES DE FAITS
==========================================================*/

-- Créer la table "production"

CREATE TABLE production (
    production_id INT AUTO_INCREMENT PRIMARY KEY,
    site_id INT NOT NULL,
    product_id INT NOT NULL,
    production_date DATE NOT NULL,
    quantity_produced INT NOT NULL,
    production_duration_minutes INT NOT NULL,

    CONSTRAINT chk_quantity_produced
        CHECK (quantity_produced > 0),

    CONSTRAINT chk_production_duration
        CHECK (production_duration_minutes > 0),

    CONSTRAINT fk_production_site
        FOREIGN KEY (site_id)
        REFERENCES site(site_id),

    CONSTRAINT fk_production_product
        FOREIGN KEY (product_id)
        REFERENCES product(product_id)
);

-- Créer la table "energy"

CREATE TABLE energy (
    energy_id INT AUTO_INCREMENT PRIMARY KEY,
    site_id INT NOT NULL,
    energy_source_id INT NOT NULL,
    energy_date DATE NOT NULL,
    energy_consumption_kwh DECIMAL(10,2) NOT NULL,
    energy_cost DECIMAL(10,2) NOT NULL,

    CONSTRAINT chk_energy_consumption
        CHECK (energy_consumption_kwh >= 0),

    CONSTRAINT chk_energy_cost
        CHECK (energy_cost >= 0),

    CONSTRAINT fk_energy_site
        FOREIGN KEY (site_id)
        REFERENCES site(site_id),

    CONSTRAINT fk_energy_source
        FOREIGN KEY (energy_source_id)
        REFERENCES energy_source(energy_source_id)
);

-- Créer la table "water"

CREATE TABLE water (
    water_id INT AUTO_INCREMENT PRIMARY KEY,
    site_id INT NOT NULL,
    water_date DATE NOT NULL,
    water_consumption_m3 DECIMAL(10,2) NOT NULL,
    water_cost DECIMAL(10,2) NOT NULL,

    CONSTRAINT chk_water_consumption
        CHECK (water_consumption_m3 >= 0),

    CONSTRAINT chk_water_cost
        CHECK (water_cost >= 0),

    CONSTRAINT fk_water_site
        FOREIGN KEY (site_id)
        REFERENCES site(site_id)
);

-- Créer la table "waste"

CREATE TABLE waste (
    waste_id INT AUTO_INCREMENT PRIMARY KEY,
    site_id INT NOT NULL,
    waste_date DATE NOT NULL,
    waste_type VARCHAR(100) NOT NULL,
    waste_quantity_kg DECIMAL(10,2) NOT NULL,
    recyclable BOOLEAN NOT NULL,

    CONSTRAINT chk_waste_quantity
        CHECK (waste_quantity_kg >= 0),

    CONSTRAINT fk_waste_site
        FOREIGN KEY (site_id)
        REFERENCES site(site_id)
);

-- Créer la table "transport"

CREATE TABLE transport (
    transport_id INT AUTO_INCREMENT PRIMARY KEY,
    supplier_id INT NOT NULL,
    transport_company_id INT NOT NULL,
    site_id INT NOT NULL,
    transport_date DATE NOT NULL,
    distance_km DECIMAL(10,2) NOT NULL,
    co2_emissions_kg DECIMAL(10,2) NOT NULL,
    transport_cost DECIMAL(10,2) NOT NULL,
    transported_weight_kg DECIMAL(10,2) NOT NULL,

    CONSTRAINT chk_distance
        CHECK (distance_km >= 0),

    CONSTRAINT chk_co2_emissions
        CHECK (co2_emissions_kg >= 0),

    CONSTRAINT chk_transport_cost
        CHECK (transport_cost >= 0),

    CONSTRAINT chk_transported_weight
        CHECK (transported_weight_kg > 0),

    CONSTRAINT fk_transport_supplier
        FOREIGN KEY (supplier_id)
        REFERENCES supplier(supplier_id),

    CONSTRAINT fk_transport_company
        FOREIGN KEY (transport_company_id)
        REFERENCES transport_company(transport_company_id),

    CONSTRAINT fk_transport_site
        FOREIGN KEY (site_id)
        REFERENCES site(site_id)
);