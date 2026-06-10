import { useState, useEffect, useCallback } from 'react';
import api from '../services/api';
import { Campaign, Company, Contact, EmailRecord } from '../types';

export function useCampaign(id: string | undefined) {
  const [campaign, setCampaign] = useState<Campaign | null>(null);
  const [companies, setCompanies] = useState<Company[]>([]);
  const [contacts, setContacts] = useState<Contact[]>([]);
  const [emails, setEmails] = useState<EmailRecord[]>([]);
  const [loading, setLoading] = useState(true);

  // Bug 5 fix: isInitialLoad param prevents spinner on every 3s poll
  const fetchCampaignData = useCallback(async (isInitialLoad = true) => {
    if (!id) return;
    try {
      if (isInitialLoad) setLoading(true);
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
      if (isInitialLoad) setLoading(false);
    }
  }, [id]);

  useEffect(() => {
    fetchCampaignData(true);
  }, [fetchCampaignData]);

  return { campaign, companies, contacts, emails, loading, refetch: fetchCampaignData };
}
