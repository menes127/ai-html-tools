create extension if not exists pgcrypto;

create table if not exists public.filings (
  accession_number text primary key,
  issuer_ticker text not null default 'AMD',
  issuer_cik text not null default '0000002488',
  issuer_name text,
  filing_date date not null,
  accepted_datetime timestamptz,
  filing_url text not null,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.transactions (
  id uuid primary key default gen_random_uuid(),
  accession_number text not null references public.filings(accession_number),
  issuer_ticker text not null default 'AMD',
  issuer_cik text not null default '0000002488',
  issuer_name text,
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
  unique (issuer_cik, accession_number, transaction_date, insider_name, code, shares, price)
);

alter table public.filings add column if not exists issuer_ticker text not null default 'AMD';
alter table public.filings add column if not exists issuer_cik text not null default '0000002488';
alter table public.filings add column if not exists issuer_name text;
alter table public.transactions add column if not exists issuer_ticker text not null default 'AMD';
alter table public.transactions add column if not exists issuer_cik text not null default '0000002488';
alter table public.transactions add column if not exists issuer_name text;

do $$
declare
  cname text;
begin
  for cname in
    select c.conname
    from pg_constraint c
    join pg_class t on t.oid = c.conrelid
    join pg_namespace n on n.oid = t.relnamespace
    where n.nspname = 'public'
      and t.relname = 'transactions'
      and c.contype = 'u'
      and c.conname <> 'uq_transactions_conflict_key'
      and pg_get_constraintdef(c.oid) like '%accession_number%transaction_date%insider_name%code%shares%price%'
  loop
    execute format('alter table public.transactions drop constraint %I', cname);
  end loop;
end $$;

alter table public.transactions
  drop constraint if exists uq_transactions_conflict_key;
alter table public.transactions
  add constraint uq_transactions_conflict_key
  unique (issuer_cik, accession_number, transaction_date, insider_name, code, shares, price);

create index if not exists idx_transactions_transaction_date on public.transactions (transaction_date desc);
create index if not exists idx_transactions_issuer_ticker on public.transactions (issuer_ticker);
create index if not exists idx_transactions_issuer_cik on public.transactions (issuer_cik);
create index if not exists idx_transactions_insider_name on public.transactions (insider_name);
create index if not exists idx_transactions_code on public.transactions (code);
create index if not exists idx_transactions_is_10b5_1 on public.transactions (is_10b5_1);

create or replace view public.v_summary as
with totals as (
  select
    issuer_ticker,
    issuer_cik,
    max(issuer_name) as issuer_name,
    count(*)::bigint as total_transactions,
    max(transaction_date) as latest_transaction_date,
    coalesce(sum(case when code = 'P' then coalesce(shares, 0) * coalesce(price, 0) else 0 end), 0) as buy_amount,
    coalesce(sum(case when code = 'S' then coalesce(shares, 0) * coalesce(price, 0) else 0 end), 0) as sell_amount
  from public.transactions
  group by issuer_ticker, issuer_cik
),
code_counts as (
  select
    issuer_ticker,
    issuer_cik,
    coalesce(jsonb_object_agg(code, cnt), '{}'::jsonb) as codes
  from (
    select issuer_ticker, issuer_cik, code, count(*)::bigint as cnt
    from public.transactions
    group by issuer_ticker, issuer_cik, code
    order by issuer_ticker, issuer_cik, code
  ) c
  group by issuer_ticker, issuer_cik
)
select
  t.issuer_ticker,
  t.issuer_cik,
  t.issuer_name,
  t.total_transactions,
  t.latest_transaction_date,
  t.buy_amount,
  t.sell_amount,
  (t.sell_amount - t.buy_amount) as net_amount,
  c.codes
from totals t
left join code_counts c on c.issuer_ticker = t.issuer_ticker and c.issuer_cik = t.issuer_cik;

create or replace view public.v_years as
select
  issuer_ticker,
  issuer_cik,
  max(issuer_name) as issuer_name,
  extract(year from transaction_date)::int as year,
  count(*)::bigint as count,
  max(transaction_date) as latest_transaction_date
from public.transactions
group by issuer_ticker, issuer_cik, extract(year from transaction_date)::int
order by issuer_ticker, year desc;

create or replace view public.v_transactions as
select
  issuer_ticker,
  issuer_cik,
  issuer_name,
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
