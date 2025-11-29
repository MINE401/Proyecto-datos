-- =========================================
-- COMPANY (tabla principal)
-- =========================================
create table if not exists public.company (
  id uuid primary key default gen_random_uuid(),
  name varchar(255) not null,
  website varchar(255),
  num_locations_bands varchar,
  year_business_back varchar,
  employee_band varchar(50),
  revenue_band varchar(50),
  external_id integer
);

-- =========================================
-- INDUSTRY: tabla maestra
-- =========================================
create table if not exists public.industry_master (
  id uuid primary key default gen_random_uuid(),
  sector varchar(255) not null,
  detail varchar(255),
  unique (sector, detail)
);

-- =========================================
-- COMPANY ⇄ INDUSTRY (tabla pivote many-to-many)
-- =========================================
create table if not exists public.company_industry (
  company_id uuid not null references public.company(id) on delete cascade,
  industry_id uuid not null references public.industry_master(id) on delete cascade,
  primary key (company_id, industry_id)
);

create index if not exists idx_company_industry_company
  on public.company_industry(company_id);

create index if not exists idx_company_industry_industry
  on public.company_industry(industry_id);

-- =========================================
-- LOCATION: tabla maestra
-- =========================================
create table if not exists public.location_master (
  id uuid primary key default gen_random_uuid(),
  city varchar(255),
  global_region varchar(255),
  country varchar(255),
  state varchar(255),
  region varchar(255),
  unique (city, state, country)
);

-- =========================================
-- COMPANY ⇄ LOCATION (tabla pivote many-to-many)
-- =========================================
create table if not exists public.company_location (
  company_id uuid not null references public.company(id) on delete cascade,
  location_id uuid not null references public.location_master(id) on delete cascade,
  address_type varchar(50),  -- HQ, Branch, etc.
  primary key (company_id, location_id, address_type)
);

create index if not exists idx_company_location_company
  on public.company_location(company_id);

create index if not exists idx_company_location_location
  on public.company_location(location_id);

-- =========================================
-- PARTNER CLASSIFICATION (1–N contra company)
-- =========================================
create table if not exists public.partner_classification (
  id uuid primary key default gen_random_uuid(),
  company_id uuid not null references public.company(id) on delete cascade,
  classification varchar(255) not null
);

create index if not exists idx_partner_class_company
  on public.partner_classification(company_id);

-- =========================================
-- CLOUD (1–N contra company)
-- =========================================
create table if not exists public.cloud (
  id uuid primary key default gen_random_uuid(),
  company_id uuid not null references public.company(id) on delete cascade,
  coverage varchar(255)
);

create index if not exists idx_cloud_company
  on public.cloud(company_id);

-- =========================================
-- PARTNER_VENDOR (many-to-many entre companies)
-- =========================================
create table if not exists public.partner_vendor (
  partner_id uuid not null references public.company(id) on delete cascade,
  vendor_id uuid not null references public.company(id) on delete cascade,
  primary key (partner_id, vendor_id)
);

create index if not exists idx_partner_vendor_vendor
  on public.partner_vendor(vendor_id);

-- =========================================
-- TECHNOLOGY_SC (1–N contra company)
-- =========================================
create table if not exists public.technology_sc (
  id uuid primary key default gen_random_uuid(),
  company_id uuid not null references public.company(id) on delete cascade,
  scope varchar(255)
);

create index if not exists idx_tech_sc_company
  on public.technology_sc(company_id);

-- =========================================
-- TECHNOLOGY (1–N contra company)
-- =========================================
create table if not exists public.technology (
  id uuid primary key default gen_random_uuid(),
  company_id uuid not null references public.company(id) on delete cascade,
  tech_group varchar(255),
  technology varchar(255),
  detail varchar(255),
  category varchar(255)
);

create index if not exists idx_technology_company
  on public.technology(company_id);

-- =========================================
-- SCORE (1–N contra company)
-- =========================================
create table if not exists public.score (
  id uuid primary key default gen_random_uuid(),
  company_id uuid not null references public.company(id) on delete cascade,
  relevance numeric,
  vendors text,
  partner_classification text
);

create index if not exists idx_score_company
  on public.score(company_id);
