import { useState, useEffect, useCallback } from 'react';
import api from '../services/api';
import { Campaign, Company, Contact, EmailRecord } from '../types';

export function useCampaign(id: string | undefined) {
  const [campaign, setCampaign] = useState<Campaign | null>(null);
  const [companies, setCompanies] = useState<Company[]>([]);
  const [contacts, setContacts] = useState<Contact[]>([]);
  const [emails, setEmails] = useState<EmailRecord[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchCampaignData = useCallback(async () => {
    if (!id) return;
    try {
      setLoading(true);
      const [campRes, compRes, contRes, emailRes] = await Promise.all([
        api.get(`/campaigns/${id}`),
        api.get(`/campaigns/${id}/companies`),
        api.get(`/campaigns/${id}/contacts`),
        api.get(`/campaigns/${id}/emails`),
      ]);
      setCampaign(campRes.data);
      setCompanies(compRes.data);
      setContacts(contRes.data);
      setEmails(emailRes.data);
    } catch (err) {
      console.error("Failed to fetch campaign data", err);
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => {
    fetchCampaignData();
  }, [fetchCampaignData]);

  return { campaign, companies, contacts, emails, loading, refetch: fetchCampaignData };
}
