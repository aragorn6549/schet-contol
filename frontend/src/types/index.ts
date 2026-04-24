export interface User {
  id: number;
  login: string;
  is_active: boolean;
  created_at: string;
}

export interface Profile {
  id: number;
  user_id: number;
  full_name: string;
  role: UserRole;
  created_at: string;
  updated_at: string;
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
  id: number;
  name: string;
  inn: string;
  kpp?: string;
  legal_address?: string;
  bank_name?: string;
  bik?: string;
  checking_account?: string;
  correspondent_account?: string;
  status: CounterpartyStatus;
  checked_by_id?: number;
  checked_at?: string;
  created_at: string;
  updated_at: string;
}

export interface Request {
  id: number;
  internal_number: string;
  project_name: string;
  deal_number: string;
  invoice_number: string;
  invoice_url: string;
  amount?: number;
  status: RequestStatus;
  created_by_id: number;
  counterparty_id: number;
  approved_by_id?: number;
  approved_at?: string;
  paid_at?: string;
  created_at: string;
  updated_at: string;
}

export interface JournalEntry {
  id: number;
  action: string;
  description?: string;
  entity_type?: string;
  entity_id?: number;
  performed_by_id: number;
  performer_full_name?: string;
  performed_at: string;
}

export interface Token {
  access_token: string;
  token_type: string;
}
