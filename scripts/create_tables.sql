-- COMPANY
create table if not exists public.company (
  id uuid primary key default gen_random_uuid(),
  name varchar(255) not null,
  website varchar(255),
  num_locations_bands integer,
  year_business_back integer,
  employee_band varchar(50),
  revenue_band varchar(50)
);

-- INDUSTRY 
create table if not exists public.industry (
  id uuid primary key default gen_random_uuid(),
  company_id uuid not null references public.company(id) on delete cascade,
  sector varchar(255) not null,
  detail varchar(255)
);
create index if not exists idx_industry_company on public.industry(company_id);

-- PARTNER CLASSIFICATION 
create table if not exists public.partner_classification (
  id uuid primary key default gen_random_uuid(),
  company_id uuid not null references public.company(id) on delete cascade,
  classification varchar(255) not null
);
create index if not exists idx_partner_class_company on public.partner_classification(company_id);

-- CLOUD 
create table if not exists public.cloud (
   id uuid primary key default gen_random_uuid(),
  company_id uuid not null references public.company(id) on delete cascade,
  coverage varchar(255)
);
create index if not exists idx_cloud_company on public.cloud(company_id);

-- LOCATION 
create table if not exists public.location (
  id uuid primary key default gen_random_uuid(),
  company_id uuid not null references public.company(id) on delete cascade,
  city varchar(255),
  global_region varchar(255),
  country varchar(255),
  state varchar(255),
  region varchar(255),
  address_type varchar(50)
);

-- PARTNER_VENDOR 
create table if not exists public.partner_vendor (
  partner_id uuid not null references public.company(id) on delete cascade,
  vendor_id uuid not null references public.company(id) on delete cascade
);

-- TECHNOLOGY_SC 
create table if not exists public.technology_sc (
   id uuid primary key default gen_random_uuid(),
  company_id uuid not null references public.company(id) on delete cascade,
  scope varchar(255)
);
create index if not exists idx_tech_sc_company on public.technology_sc(company_id);

-- TECHNOLOGY 
create table if not exists public.technology (
  id uuid primary key default gen_random_uuid(),
  company_id uuid not null references public.company(id) on delete cascade,
  tech_group varchar(255),
  technology varchar(255),
  detail varchar(255),
  category varchar(255)
);
create index if not exists idx_technology_company on public.technology(company_id);

-- SCORE 
create table if not exists public.score (
  id uuid primary key default gen_random_uuid(),
  company_id uuid not null references public.company(id) on delete cascade,
  relevance numeric,
  vendors text,
  partner_classification text
);
create index if not exists idx_score_company on public.score(company_id);
