import { supabase } from '../lib/supabaseClient';
import { Counterparty, Request, JournalEntry, CounterpartyStatus, RequestStatus } from '../types';

export const counterpartiesApi = {
  getAll: async () => {
    const { data, error } = await supabase
      .from('counterparties')
      .select('*');
    if (error) throw error;
    return data as Counterparty[];
  },
  
  getById: async (id: string) => {
    const { data, error } = await supabase
      .from('counterparties')
      .select('*')
      .eq('id', id)
      .single();
    if (error) throw error;
    return data as Counterparty;
  },
  
  create: async (counterpartyData: Partial<Counterparty>) => {
    const { data, error } = await supabase
      .from('counterparties')
      .insert([counterpartyData])
      .select()
      .single();
    if (error) throw error;
    return data as Counterparty;
  },
  
  updateStatus: async (id: string, status: CounterpartyStatus) => {
    const { data, error } = await supabase
      .from('counterparties')
      .update({ status, updated_at: new Date().toISOString() })
      .eq('id', id)
      .select()
      .single();
    if (error) throw error;
    return data as Counterparty;
  },
};

export const requestsApi = {
  getAll: async () => {
    const { data, error } = await supabase
      .from('requests')
      .select('*');
    if (error) throw error;
    return data as Request[];
  },
  
  getById: async (id: string) => {
    const { data, error } = await supabase
      .from('requests')
      .select('*')
      .eq('id', id)
      .single();
    if (error) throw error;
    return data as Request;
  },
  
  create: async (requestData: Partial<Request>) => {
    const { data, error } = await supabase
      .from('requests')
      .insert([requestData])
      .select()
      .single();
    if (error) throw error;
    return data as Request;
  },
  
  update: async (id: string, requestData: Partial<Request>) => {
    const { data, error } = await supabase
      .from('requests')
      .update({ ...requestData, updated_at: new Date().toISOString() })
      .eq('id', id)
      .select()
      .single();
    if (error) throw error;
    return data as Request;
  },
  
  approve: async (id: string, approve: boolean) => {
    const status = approve ? RequestStatus.APPROVED : RequestStatus.REJECTED;
    const { data, error } = await supabase
      .from('requests')
      .update({ 
        status, 
        approved_at: approve ? new Date().toISOString() : null,
        updated_at: new Date().toISOString() 
      })
      .eq('id', id)
      .select()
      .single();
    if (error) throw error;
    return data as Request;
  },
  
  pay: async (id: string) => {
    const { data, error } = await supabase
      .from('requests')
      .update({ 
        status: RequestStatus.PAID,
        paid_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      })
      .eq('id', id)
      .select()
      .single();
    if (error) throw error;
    return data as Request;
  },
  
  getPpText: async (id: string) => {
    const request = await requestsApi.getById(id);
    return `Прошу оплатить счет №${request.invoice_number} по ссылке: ${request.invoice_url}`;
  },
};

export const journalApi = {
  getAll: async () => {
    const { data, error } = await supabase
      .from('journal')
      .select('*');
    if (error) throw error;
    return data as JournalEntry[];
  },
  
  create: async (action: string, details?: any) => {
    const { data, error } = await supabase
      .from('journal')
      .insert([{ action, details, user_id: (await supabase.auth.getUser()).data.user?.id }])
      .select()
      .single();
    if (error) throw error;
    return data as JournalEntry;
  },
};

export const profilesApi = {
  getMe: async () => {
    const { data: { user } } = await supabase.auth.getUser();
    if (!user) throw new Error('Not authenticated');
    
    const { data, error } = await supabase
      .from('profiles')
      .select('*')
      .eq('id', user.id)
      .single();
    if (error) throw error;
    return { ...data, email: user.email };
  },
  
  getAll: async () => {
    const { data, error } = await supabase
      .from('profiles')
      .select('*');
    if (error) throw error;
    return data;
  },
  
  update: async (id: string, data: { full_name?: string; role?: string }) => {
    const { data: result, error } = await supabase
      .from('profiles')
      .update(data)
      .eq('id', id)
      .select()
      .single();
    if (error) throw error;
    return result;
  },
};

export const authApi = {
  login: async (email: string, password: string) => {
    const { data, error } = await supabase.auth.signInWithPassword({
      email,
      password,
    });
    if (error) throw error;
    return data;
  },
  
  register: async (email: string, password: string, fullName: string) => {
    const { data, error } = await supabase.auth.signUp({
      email,
      password,
      options: {
        data: {
          full_name: fullName,
        },
      },
    });
    if (error) throw error;
    return data;
  },
  
  logout: async () => {
    const { error } = await supabase.auth.signOut();
    if (error) throw error;
  },
  
  getMe: async () => {
    const { data: { user } } = await supabase.auth.getUser();
    if (!user) throw new Error('Not authenticated');
    
    const { data, error } = await supabase
      .from('profiles')
      .select('*')
      .eq('id', user.id)
      .single();
    if (error) throw error;
    return { ...data, email: user.email };
  },
};
