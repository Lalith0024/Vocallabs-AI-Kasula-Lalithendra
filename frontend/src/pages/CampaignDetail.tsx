import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useCampaign } from '../hooks/useCampaign';
import { ArrowLeft, Building2, Users, Mail, CheckCircle2, XCircle, Send } from 'lucide-react';
import clsx from 'clsx';
import api from '../services/api';

export default function CampaignDetail() {
  const { id } = useParams<{ id: string }>();
  const { campaign, companies, contacts, emails, loading, refetch } = useCampaign(id);
  const [approving, setApproving] = useState(false);

  useEffect(() => {
    if (!campaign) return;
    if (campaign.status !== 'completed' && campaign.status !== 'failed') {
      const interval = setInterval(() => {
        refetch(false);
      }, 3000);
      return () => clearInterval(interval);
    }
  }, [campaign?.status, refetch]);

  const handleApprove = async () => {
    if (!campaign) return;
    setApproving(true);
    try {
      await api.post(`/campaigns/${campaign.id}/approve-send`);
      await refetch(false);
    } catch (error) {
      console.error('Failed to approve campaign', error);
      alert('Failed to approve campaign. Please check the console.');
    } finally {
      setApproving(false);
    }
  };

  if (loading && !campaign) {
    return (
      <div className="flex h-[50vh] items-center justify-center">
        <div className="w-8 h-8 border-4 border-gray-200 border-t-blue-600 rounded-full animate-spin" />
      </div>
    );
  }

  if (!campaign) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-12 text-center">
        <h2 className="text-2xl font-bold text-gray-900">Campaign not found</h2>
        <Link to="/" className="text-blue-600 mt-4 inline-block hover:underline font-medium">Return to Dashboard</Link>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <Link to="/" className="inline-flex items-center space-x-2 text-gray-500 hover:text-gray-900 mb-8 transition-colors font-medium">
        <ArrowLeft className="w-4 h-4" />
        <span>Back to Dashboard</span>
      </Link>

      <div className="card p-8 mb-8 flex flex-col md:flex-row justify-between items-start md:items-center gap-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Seed: <span className="text-blue-600">{campaign.seed_domain}</span>
          </h1>
          <div className="text-gray-500 text-sm font-mono bg-gray-100 px-3 py-1 rounded-md inline-block">ID: {campaign.id}</div>
        </div>
        <div className="flex flex-col items-end gap-3 w-full md:w-auto">
          <div className="text-right">
            <div className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-1">Status</div>
            <div className={clsx(
              "px-4 py-2 rounded-full font-bold inline-block text-sm border",
              campaign.status === 'completed' ? "bg-emerald-50 text-emerald-700 border-emerald-200" :
              campaign.status === 'failed' ? "bg-rose-50 text-rose-700 border-rose-200" :
              campaign.status === 'pending_approval' ? "bg-amber-50 text-amber-700 border-amber-200" :
              "bg-blue-50 text-blue-700 border-blue-200"
            )}>
              {campaign.status.replace('_', ' ').toUpperCase()}
            </div>
          </div>
          
          {campaign.status === 'pending_approval' && (
            <button
              onClick={handleApprove}
              disabled={approving || emails.length === 0}
              className="btn-primary w-full md:w-auto flex items-center justify-center gap-2"
            >
              <Send className="w-4 h-4" />
              {approving ? 'Approving...' : `Approve & Send ${emails.length} Emails`}
            </button>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* Companies Column */}
        <div className="card p-6">
          <div className="flex items-center space-x-3 mb-6 pb-4 border-b border-gray-100">
            <div className="p-2 bg-blue-50 text-blue-600 rounded-lg">
              <Building2 className="w-5 h-5" />
            </div>
            <h2 className="text-lg font-bold text-gray-900">Lookalike Companies</h2>
            <span className="ml-auto bg-gray-100 text-gray-700 px-3 py-1 rounded-full text-xs font-bold">
              {companies.length}
            </span>
          </div>
          <div className="space-y-3 max-h-[600px] overflow-y-auto pr-2 custom-scrollbar">
            {companies.length === 0 && !loading && (
              <div className="text-sm text-gray-500 text-center py-8">No companies found yet.</div>
            )}
            {companies.map(c => (
              <div key={c.id} className="bg-gray-50 p-4 rounded-xl border border-gray-100 hover:border-blue-200 hover:shadow-sm transition-all">
                <div className="font-semibold text-gray-900">{c.company_name || c.domain}</div>
                <div className="text-xs text-gray-500 mt-2 flex justify-between items-center">
                  <span className="bg-white px-2 py-1 rounded-md border border-gray-100">{c.industry || 'Unknown Industry'}</span>
                  <span className="font-medium text-blue-600 bg-blue-50 px-2 py-1 rounded-md">Score: {c.similarity_score ? Math.round(c.similarity_score * 100) + '%' : 'N/A'}</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Contacts Column */}
        <div className="card p-6">
          <div className="flex items-center space-x-3 mb-6 pb-4 border-b border-gray-100">
            <div className="p-2 bg-violet-50 text-violet-600 rounded-lg">
              <Users className="w-5 h-5" />
            </div>
            <h2 className="text-lg font-bold text-gray-900">Decision Makers</h2>
            <span className="ml-auto bg-gray-100 text-gray-700 px-3 py-1 rounded-full text-xs font-bold">
              {contacts.length}
            </span>
          </div>
          <div className="space-y-3 max-h-[600px] overflow-y-auto pr-2 custom-scrollbar">
            {contacts.length === 0 && !loading && (
              <div className="text-sm text-gray-500 text-center py-8">No contacts found yet.</div>
            )}
            {contacts.map(c => (
              <div key={c.id} className="bg-gray-50 p-4 rounded-xl border border-gray-100 hover:border-violet-200 hover:shadow-sm transition-all">
                <div className="font-semibold text-gray-900">{c.full_name}</div>
                <div className="text-xs text-violet-600 font-medium mt-1.5">{c.title}</div>
              </div>
            ))}
          </div>
        </div>

        {/* Emails Column */}
        <div className="card p-6">
          <div className="flex items-center space-x-3 mb-6 pb-4 border-b border-gray-100">
            <div className="p-2 bg-emerald-50 text-emerald-600 rounded-lg">
              <Mail className="w-5 h-5" />
            </div>
            <h2 className="text-lg font-bold text-gray-900">Email Delivery</h2>
            <span className="ml-auto bg-gray-100 text-gray-700 px-3 py-1 rounded-full text-xs font-bold">
              {emails.length}
            </span>
          </div>
          <div className="space-y-3 max-h-[600px] overflow-y-auto pr-2 custom-scrollbar">
            {emails.length === 0 && !loading && (
              <div className="text-sm text-gray-500 text-center py-8">No emails resolved yet.</div>
            )}
            {emails.map(e => (
              <div key={e.id} className="bg-gray-50 p-4 rounded-xl border border-gray-100 hover:border-emerald-200 hover:shadow-sm transition-all">
                <div className="flex justify-between items-start gap-3">
                  <div className="font-medium text-gray-900 text-sm break-all">{e.email_address}</div>
                  {e.status === 'sent' || e.status === 'delivered' ? (
                    <CheckCircle2 className="w-5 h-5 text-emerald-500 shrink-0 mt-0.5" />
                  ) : e.status === 'failed' || e.status === 'bounced' ? (
                    <XCircle className="w-5 h-5 text-rose-500 shrink-0 mt-0.5" />
                  ) : (
                    <span className="text-[10px] font-bold text-gray-500 uppercase tracking-wider shrink-0 mt-1 bg-white px-2 py-0.5 rounded border border-gray-200">{e.status}</span>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>

      </div>
    </div>
  );
}
