export type CampaignStatus = 
  | 'pending'
  | 'running'
  | 'stage_1'
  | 'stage_2'
  | 'stage_3'
  | 'stage_4'
  | 'pending_approval'
  | 'completed'
  | 'failed';

export interface CampaignMetrics {
  companies_found?: number;
  contacts_found?: number;
  emails_resolved?: number;
  emails_sent?: number;
  emails_failed?: number;
}

export interface Campaign {
  id: string;
  seed_domain: string;
  status: CampaignStatus;
  created_at: string;
  started_at: string | null;
  completed_at: string | null;
  error_message: string | null;
  metrics: CampaignMetrics;
}

export interface Company {
  id: string;
  domain: string;
  company_name: string | null;
  industry: string | null;
  employee_count: number | null;
  similarity_score: number | null;
}

export interface Contact {
  id: string;
  first_name: string | null;
  last_name: string | null;
  full_name: string;
  title: string | null;
  linkedin_url: string | null;
}

export interface EmailRecord {
  id: string;
  email_address: string;
  verified: boolean;
  confidence: number | null;
  status: string;
  sent_at: string | null;
  opened_at: string | null;
}
