import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { PlusCircle, Search, ArrowRight, BarChart3 } from 'lucide-react';
import api from '../services/api';
import { Campaign } from '../types';
import clsx from 'clsx';

export default function Dashboard() {
  const [campaigns, setCampaigns] = useState<Campaign[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get('/campaigns')
      .then(res => setCampaigns(res.data))
      .catch(err => console.error(err))
      .finally(() => setLoading(false));
  }, []);

  const getStatusColor = (status: string) => {
    switch(status) {
      case 'completed': return 'text-emerald-400 bg-emerald-400/10';
      case 'running': 
      case 'stage_1':
      case 'stage_2':
      case 'stage_3':
      case 'stage_4': return 'text-brand-400 bg-brand-400/10 animate-pulse';
      case 'pending_approval': return 'text-amber-400 bg-amber-400/10';
      case 'failed': return 'text-rose-400 bg-rose-400/10';
      default: return 'text-slate-400 bg-slate-400/10';
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div className="flex justify-between items-center mb-10">
        <div>
          <h1 className="text-3xl font-bold text-slate-100">Campaigns</h1>
          <p className="text-slate-400 mt-2">Manage your automated outreach pipelines.</p>
        </div>
        <Link 
          to="/campaigns/new" 
          className="bg-brand-600 hover:bg-brand-500 text-white px-6 py-3 rounded-xl font-medium transition-colors flex items-center space-x-2"
        >
          <PlusCircle className="w-5 h-5" />
          <span>New Campaign</span>
        </Link>
      </div>

      <div className="glass-panel rounded-2xl overflow-hidden">
        {loading ? (
          <div className="p-12 text-center text-slate-500 flex flex-col items-center">
            <div className="w-8 h-8 border-4 border-slate-700 border-t-brand-500 rounded-full animate-spin mb-4" />
            Loading campaigns...
          </div>
        ) : campaigns.length === 0 ? (
          <div className="p-16 text-center">
            <div className="w-20 h-20 bg-slate-800 rounded-full flex items-center justify-center mx-auto mb-6">
              <Search className="w-10 h-10 text-slate-500" />
            </div>
            <h3 className="text-xl font-medium text-slate-200 mb-2">No campaigns yet</h3>
            <p className="text-slate-400 mb-8 max-w-sm mx-auto">Launch your first automated outreach campaign by entering a seed domain.</p>
            <Link to="/campaigns/new" className="text-brand-400 hover:text-brand-300 font-medium inline-flex items-center space-x-2">
              <span>Start Campaign</span>
              <ArrowRight className="w-4 h-4" />
            </Link>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-slate-800 bg-slate-900/50">
                  <th className="p-5 font-semibold text-slate-400 text-sm">Seed Domain</th>
                  <th className="p-5 font-semibold text-slate-400 text-sm">Status</th>
                  <th className="p-5 font-semibold text-slate-400 text-sm">Date</th>
                  <th className="p-5 font-semibold text-slate-400 text-sm">Metrics</th>
                  <th className="p-5 font-semibold text-slate-400 text-sm"></th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/50">
                {campaigns.map(campaign => (
                  <tr key={campaign.id} className="hover:bg-slate-800/30 transition-colors">
                    <td className="p-5">
                      <div className="font-medium text-slate-200">{campaign.seed_domain}</div>
                      <div className="text-xs text-slate-500 font-mono mt-1">{campaign.id.substring(0, 8)}</div>
                    </td>
                    <td className="p-5">
                      <span className={clsx("px-3 py-1 text-xs font-medium rounded-full", getStatusColor(campaign.status))}>
                        {campaign.status.replace('_', ' ').toUpperCase()}
                      </span>
                    </td>
                    <td className="p-5 text-sm text-slate-400">
                      {new Date(campaign.created_at).toLocaleDateString()}
                    </td>
                    <td className="p-5">
                      <div className="flex items-center space-x-4 text-sm">
                        <div title="Companies Found" className="flex items-center space-x-1 text-slate-300">
                          <BarChart3 className="w-4 h-4 text-slate-500" />
                          <span>{campaign.metrics?.companies_found || 0}</span>
                        </div>
                        <div title="Emails Sent" className="flex items-center space-x-1 text-slate-300">
                          <span className="w-2 h-2 rounded-full bg-brand-500" />
                          <span>{campaign.metrics?.emails_sent || 0}</span>
                        </div>
                      </div>
                    </td>
                    <td className="p-5 text-right">
                      <Link 
                        to={`/campaigns/${campaign.id}`}
                        className="text-sm font-medium text-brand-400 hover:text-brand-300 flex items-center justify-end space-x-1"
                      >
                        <span>View</span>
                        <ArrowRight className="w-4 h-4" />
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
