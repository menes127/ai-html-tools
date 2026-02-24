create extension if not exists pgcrypto;

create table if not exists public.filings (
  accession_number text primary key,
  filing_date date not null,
  accepted_datetime timestamptz,
  filing_url text not null,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.transactions (
  id uuid primary key default gen_random_uuid(),
  accession_number text not null references public.filings(accession_number),
  transaction_date date not null,
  filing_date date not null,
  insider_name text not null,
  insider_title text,
  relationship text[] not null default '{}',
  security_title text not null,
  code text not null,
  shares numeric,
  price numeric,
  acquired_disposed text,
  shares_owned_after numeric,
  ownership_nature text,
  is_10b5_1 boolean not null default false,
  footnote_hint text,
  filing_url text not null,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (accession_number, transaction_date, insider_name, code, shares, price)
);

create index if not exists idx_transactions_transaction_date on public.transactions (transaction_date desc);
create index if not exists idx_transactions_insider_name on public.transactions (insider_name);
create index if not exists idx_transactions_code on public.transactions (code);
create index if not exists idx_transactions_is_10b5_1 on public.transactions (is_10b5_1);

create or replace view public.v_summary as
with totals as (
  select
    count(*)::bigint as total_transactions,
    max(transaction_date) as latest_transaction_date,
    coalesce(sum(case when code = 'P' then coalesce(shares, 0) * coalesce(price, 0) else 0 end), 0) as buy_amount,
    coalesce(sum(case when code = 'S' then coalesce(shares, 0) * coalesce(price, 0) else 0 end), 0) as sell_amount
  from public.transactions
),
code_counts as (
  select coalesce(jsonb_object_agg(code, cnt), '{}'::jsonb) as codes
  from (
    select code, count(*)::bigint as cnt
    from public.transactions
    group by code
    order by code
  ) c
)
select
  t.total_transactions,
  t.latest_transaction_date,
  t.buy_amount,
  t.sell_amount,
  (t.sell_amount - t.buy_amount) as net_amount,
  c.codes
from totals t
cross join code_counts c;

create or replace view public.v_years as
select
  extract(year from transaction_date)::int as year,
  count(*)::bigint as count,
  max(transaction_date) as latest_transaction_date
from public.transactions
group by 1
order by 1 desc;

create or replace view public.v_transactions as
select
  transaction_date,
  filing_date,
  insider_name,
  insider_title,
  relationship,
  security_title,
  code,
  shares,
  price,
  acquired_disposed,
  shares_owned_after,
  ownership_nature,
  is_10b5_1,
  footnote_hint,
  accession_number,
  filing_url
from public.transactions;

alter table public.filings enable row level security;
alter table public.transactions enable row level security;

revoke all on public.filings from anon;
revoke all on public.transactions from anon;

grant usage on schema public to anon;
grant select on public.v_summary to anon;
grant select on public.v_years to anon;
grant select on public.v_transactions to anon;
