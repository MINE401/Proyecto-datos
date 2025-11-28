from sqlalchemy import (Column, String, Integer, ForeignKey, Numeric, Text,
                        Table)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid

from database import Base

# Tabla de asociación para la relación muchos-a-muchos entre partners y vendors
partner_vendor_association = Table(
    'partner_vendor', Base.metadata,
    Column('partner_id', UUID(as_uuid=True), ForeignKey('company.id'), primary_key=True),
    Column('vendor_id', UUID(as_uuid=True), ForeignKey('company.id'), primary_key=True)
)

class Company(Base):
    __tablename__ = 'company'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    website = Column(String(255))
    num_locations_bands = Column(Integer)
    year_business_back = Column(Integer)
    employee_band = Column(String(50))
    revenue_band = Column(String(50))

    # Relaciones One-to-Many
    industries = relationship("Industry", back_populates="company")
    classifications = relationship("PartnerClassification", back_populates="company")
    clouds = relationship("Cloud", back_populates="company")
    locations = relationship("Location", back_populates="company")
    technology_scs = relationship("TechnologySC", back_populates="company")
    technologies = relationship("Technology", back_populates="company")
    scores = relationship("Score", back_populates="company")

    # Relación Many-to-Many para vendors (compañías que son vendors de esta)
    vendors = relationship(
        "Company",
        secondary=partner_vendor_association,
        primaryjoin=id == partner_vendor_association.c.partner_id,
        secondaryjoin=id == partner_vendor_association.c.vendor_id,
        backref="partners"
    )

class Industry(Base):
    __tablename__ = 'industry'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey('company.id'), nullable=False)
    sector = Column(String(255), nullable=False)
    detail = Column(String(255))
    company = relationship("Company", back_populates="industries")

class PartnerClassification(Base):
    __tablename__ = 'partner_classification'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey('company.id'), nullable=False)
    classification = Column(String(255), nullable=False)
    company = relationship("Company", back_populates="classifications")

class Cloud(Base):
    __tablename__ = 'cloud'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey('company.id'), nullable=False)
    coverage = Column(String(255))
    company = relationship("Company", back_populates="clouds")

class Location(Base):
    __tablename__ = 'location'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey('company.id'), nullable=False)
    city = Column(String(255))
    global_region = Column(String(255))
    country = Column(String(255))
    state = Column(String(255))
    region = Column(String(255))
    address_type = Column(String(50))
    company = relationship("Company", back_populates="locations")

class TechnologySC(Base):
    __tablename__ = 'technology_sc'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey('company.id'), nullable=False)
    scope = Column(String(255))
    company = relationship("Company", back_populates="technology_scs")

class Technology(Base):
    __tablename__ = 'technology'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey('company.id'), nullable=False)
    tech_group = Column(String(255))
    technology = Column(String(255))
    detail = Column(String(255))
    category = Column(String(255))
    company = relationship("Company", back_populates="technologies")

class Score(Base):
    __tablename__ = 'score'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey('company.id'), nullable=False)
    relevance = Column(Numeric)
    vendors = Column(Text)
    partner_classification = Column(Text)
    company = relationship("Company", back_populates="scores")