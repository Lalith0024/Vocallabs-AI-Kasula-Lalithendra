import { useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useCampaign } from '../hooks/useCampaign';
import { ArrowLeft, Building2, Users, Mail, CheckCircle2, XCircle } from 'lucide-react';
import clsx from 'clsx';

export default function CampaignDetail() {
  const { id } = useParams<{ id: string }>();
  const { campaign, companies, contacts, emails, loading, refetch } = useCampaign(id);

  useEffect(() => {
    if (!campaign) return;
    if (campaign.status !== 'completed' && campaign.status !== 'failed') {
      const interval = setInterval(() => {
        refetch();
      }, 3000);
      return () => clearInterval(interval);
    }
  }, [campaign?.status, refetch]);

  if (loading) {
    return (
      <div className="flex h-[50vh] items-center justify-center">
        <div className="w-8 h-8 border-4 border-slate-700 border-t-brand-500 rounded-full animate-spin" />
      </div>
    );
  }

  if (!campaign) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-12 text-center">
        <h2 className="text-2xl font-bold text-slate-200">Campaign not found</h2>
        <Link to="/" className="text-brand-400 mt-4 inline-block hover:underline">Return to Dashboard</Link>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <Link to="/" className="inline-flex items-center space-x-2 text-slate-400 hover:text-slate-200 mb-8 transition-colors">
        <ArrowLeft className="w-4 h-4" />
        <span>Back to Dashboard</span>
      </Link>

      <div className="glass-panel p-8 rounded-3xl mb-8 flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-slate-100 mb-2">
            Seed: <span className="text-brand-400">{campaign.seed_domain}</span>
          </h1>
          <div className="text-slate-400 text-sm font-mono">ID: {campaign.id}</div>
        </div>
        <div className="text-right">
          <div className="text-sm text-slate-400 uppercase tracking-wider mb-1">Status</div>
          <div className={clsx(
            "px-4 py-2 rounded-full font-bold inline-block text-sm",
            campaign.status === 'completed' ? "bg-emerald-500/20 text-emerald-400" :
            campaign.status === 'failed' ? "bg-rose-500/20 text-rose-400" :
            "bg-brand-500/20 text-brand-400"
          )}>
            {campaign.status.toUpperCase()}
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* Companies Column */}
        <div className="glass-panel rounded-2xl p-6">
          <div className="flex items-center space-x-3 mb-6 pb-4 border-b border-slate-700">
            <div className="p-2 bg-slate-800 rounded-lg">
              <Building2 className="w-5 h-5 text-slate-300" />
            </div>
            <h2 className="text-xl font-bold text-slate-200">Lookalike Companies</h2>
            <span className="ml-auto bg-slate-800 text-slate-300 px-3 py-1 rounded-full text-xs font-bold">
              {companies.length}
            </span>
          </div>
          <div className="space-y-4 max-h-[600px] overflow-y-auto pr-2">
            {companies.length === 0 && !loading && (
              <div className="text-sm text-slate-500 text-center py-8">No companies found yet.</div>
            )}
            {companies.map(c => (
              <div key={c.id} className="bg-slate-800/50 p-4 rounded-xl border border-slate-700/50">
                <div className="font-medium text-slate-200">{c.company_name || c.domain}</div>
                <div className="text-xs text-slate-400 mt-1 flex justify-between">
                  <span>{c.industry || 'Unknown Industry'}</span>
                  <span>Score: {c.similarity_score ? Math.round(c.similarity_score * 100) + '%' : 'N/A'}</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Contacts Column */}
        <div className="glass-panel rounded-2xl p-6">
          <div className="flex items-center space-x-3 mb-6 pb-4 border-b border-slate-700">
            <div className="p-2 bg-slate-800 rounded-lg">
              <Users className="w-5 h-5 text-slate-300" />
            </div>
            <h2 className="text-xl font-bold text-slate-200">Decision Makers</h2>
            <span className="ml-auto bg-slate-800 text-slate-300 px-3 py-1 rounded-full text-xs font-bold">
              {contacts.length}
            </span>
          </div>
          <div className="space-y-4 max-h-[600px] overflow-y-auto pr-2">
            {contacts.length === 0 && !loading && (
              <div className="text-sm text-slate-500 text-center py-8">No contacts found yet.</div>
            )}
            {contacts.map(c => (
              <div key={c.id} className="bg-slate-800/50 p-4 rounded-xl border border-slate-700/50">
                <div className="font-medium text-slate-200">{c.full_name}</div>
                <div className="text-xs text-brand-400 font-medium mt-1">{c.title}</div>
              </div>
            ))}
          </div>
        </div>

        {/* Emails Column */}
        <div className="glass-panel rounded-2xl p-6">
          <div className="flex items-center space-x-3 mb-6 pb-4 border-b border-slate-700">
            <div className="p-2 bg-slate-800 rounded-lg">
              <Mail className="w-5 h-5 text-slate-300" />
            </div>
            <h2 className="text-xl font-bold text-slate-200">Email Delivery</h2>
            <span className="ml-auto bg-slate-800 text-slate-300 px-3 py-1 rounded-full text-xs font-bold">
              {emails.length}
            </span>
          </div>
          <div className="space-y-4 max-h-[600px] overflow-y-auto pr-2">
            {emails.length === 0 && !loading && (
              <div className="text-sm text-slate-500 text-center py-8">No emails resolved yet.</div>
            )}
            {emails.map(e => (
              <div key={e.id} className="bg-slate-800/50 p-4 rounded-xl border border-slate-700/50">
                <div className="flex justify-between items-start">
                  <div className="font-medium text-slate-200 text-sm break-all">{e.email_address}</div>
                  {e.status === 'sent' || e.status === 'delivered' ? (
                    <CheckCircle2 className="w-4 h-4 text-emerald-500 shrink-0 ml-2 mt-0.5" />
                  ) : e.status === 'failed' || e.status === 'bounced' ? (
                    <XCircle className="w-4 h-4 text-rose-500 shrink-0 ml-2 mt-0.5" />
                  ) : (
                    <span className="text-xs text-slate-500 uppercase shrink-0 ml-2">{e.status}</span>
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
