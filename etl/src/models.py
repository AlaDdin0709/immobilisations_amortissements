from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import (
    Column, BigInteger, String, VARCHAR, Text, Date, Integer, Numeric, DateTime, func
)

Base = declarative_base()


class Immobilisation(Base):
    __tablename__ = 'immobilisations_amortissements'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    # allow duplicates in the business key: do not enforce uniqueness here
    # allow NULLs for records that don't provide a business key
    ndeg_immobilisation = Column(String(64), nullable=True)
    publication = Column(String(100))
    collectivite = Column(String(80))
    nature = Column(String(80))
    date_d_acquisition = Column(Date)
    designation_des_ensembles = Column(Text)
    valeur_d_acquisition = Column(Numeric(14, 2))
    duree_amort = Column(Integer)
    cumul_amort_anterieurs = Column(Numeric(14, 2))
    vnc_debut_exercice = Column(Numeric(14, 2))
    amort_exercice = Column(Numeric(14, 2))
    vnc_fin_exercice = Column(Numeric(14, 2))
    fetched_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Derived / KPI columns
    taux_amortissement = Column(Numeric(12, 6))
    amortissement_total = Column(Numeric(14, 2))
    pct_valeur_restante = Column(Numeric(6, 2))
    age_immobilisation = Column(Numeric(6, 2))
    annee_acquisition = Column(Integer)
    mois_acquisition = Column(Integer)
    jour_acquisition = Column(Integer)
    trimestre_acquisition = Column(Integer)
