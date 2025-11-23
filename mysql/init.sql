-- Schéma initial pour le projet Paris OpenData Analytics
CREATE DATABASE IF NOT EXISTS paris_immobilisations_db;
USE paris_immobilisations_db;

-- (Removed) generic `paris_dataset` table: not used by this project.
-- The ETL writes directly to `immobilisations_amortissements`.

-- Table structurée pour Immobilisations - Etat des Amortissements
CREATE TABLE IF NOT EXISTS immobilisations_amortissements (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  ndeg_immobilisation VARCHAR(64) NOT NULL,
  publication VARCHAR(100),
  collectivite VARCHAR(80),
  nature VARCHAR(80),
  date_d_acquisition DATE,
  designation_des_ensembles TEXT,
  valeur_d_acquisition DECIMAL(14,2),
  duree_amort INT,
  cumul_amort_anterieurs DECIMAL(14,2),
  vnc_debut_exercice DECIMAL(14,2),
  amort_exercice DECIMAL(14,2),
  vnc_fin_exercice DECIMAL(14,2),
  -- legacy columns removed: source_id, properties
  fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  UNIQUE KEY uq_ndeg (ndeg_immobilisation)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- create index for immobilisations (no IF NOT EXISTS)
CREATE INDEX idx_immob_fetched_at ON immobilisations_amortissements(fetched_at);
