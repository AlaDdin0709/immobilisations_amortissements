-- Schéma initial pour le projet Paris OpenData Analytics
CREATE DATABASE IF NOT EXISTS paris_immobilisations_db;
USE paris_immobilisations_db;

-- exemple de table générique pour les datasets OpenData Paris
CREATE TABLE IF NOT EXISTS paris_dataset (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  source_id VARCHAR(255) NOT NULL,
  properties JSON NULL,
  record_timestamp VARCHAR(100) NULL,
  fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  UNIQUE KEY uq_source_id (source_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- create index (MySQL does not support IF NOT EXISTS for CREATE INDEX)
CREATE INDEX idx_paris_dataset_fetched_at ON paris_dataset(fetched_at);

-- Table structurée pour Immobilisations - Etat des Amortissements
CREATE TABLE IF NOT EXISTS immobilisations_amortissements (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  ndeg_immobilisation VARCHAR(64) NOT NULL,
  publication VARCHAR(100),
  collectivite VARCHAR(80),
  nature VARCHAR(80),
  date_d_acquisition DATE,
  ndeg_subs VARCHAR(32),
  designation_des_ensembles TEXT,
  valeur_d_acquisition DECIMAL(14,2),
  duree_amort INT,
  cumul_amort_anterieurs DECIMAL(14,2),
  vnc_debut_exercice DECIMAL(14,2),
  amort_exercice DECIMAL(14,2),
  vnc_fin_exercice DECIMAL(14,2),
  source_id VARCHAR(255) NULL,
  properties JSON NULL,
  fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  UNIQUE KEY uq_ndeg (ndeg_immobilisation)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- create index for immobilisations (no IF NOT EXISTS)
CREATE INDEX idx_immob_fetched_at ON immobilisations_amortissements(fetched_at);
