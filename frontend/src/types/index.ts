export interface User {
  id: string;
  email: string;
}

export interface Profile {
  id: string;
  full_name: string;
  role: UserRole;
  created_at: string;
}

export enum UserRole {
  ENGINEER = 'engineer',
  SECURITY = 'security',
  DIRECTOR = 'director',
  ACCOUNTANT = 'accountant',
  ADMIN = 'admin',
}

export enum RequestStatus {
  DRAFT = 'draft',
  PENDING_SECURITY = 'pending_security',
  PENDING_DIRECTOR = 'pending_director',
  APPROVED = 'approved',
  REJECTED = 'rejected',
  PAID = 'paid',
  COUNTERPARTY_REJECTED = 'counterparty_rejected',
}

export enum CounterpartyStatus {
  PENDING = 'pending',
  APPROVED = 'approved',
  REJECTED = 'rejected',
}

export interface Counterparty {
  id: string;
  name: string;
  inn: string;
  legal_address?: string;
  bank_name?: string;
  bik?: string;
  account_number?: string;
  status: CounterpartyStatus;
  created_by?: string;
  created_at: string;
  updated_at: string;
}

export interface Request {
  id: string;
  internal_number: string;
  project_name: string;
  deal_number: string;
  invoice_number: string;
  invoice_url: string;
  amount?: number;
  status: RequestStatus;
  created_by?: string;
  counterparty_id: string;
  paid_at?: string;
  created_at: string;
  updated_at: string;
}

export interface JournalEntry {
  id: string;
  user_id: string;
  action: string;
  details?: any;
  created_at: string;
}
