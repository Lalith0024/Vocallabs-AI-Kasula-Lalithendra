import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { PlusCircle, ArrowRight, Building2, Mail, Clock, TrendingUp, Inbox } from 'lucide-react';
import api from '../services/api';
import { Campaign } from '../types';
import clsx from 'clsx';

function StatusBadge({ status }: { status: string }) {
  const configs: Record<string, { label: string; cls: string; dot?: boolean }> = {
    completed:       { label: 'Completed',        cls: 'badge-completed' },
    running:         { label: 'Running',           cls: 'badge-running', dot: true },
    stage_1:         { label: 'Stage 1 — Finding', cls: 'badge-running', dot: true },
    stage_2:         { label: 'Stage 2 — Contacts',cls: 'badge-running', dot: true },
    stage_3:         { label: 'Stage 3 — Emails',  cls: 'badge-running', dot: true },
    stage_4:         { label: 'Stage 4 — Sending', cls: 'badge-running', dot: true },
    pending_approval:{ label: 'Awaiting Approval', cls: 'badge-approval' },
    failed:          { label: 'Failed',            cls: 'badge-failed' },
    pending:         { label: 'Pending',           cls: 'badge-pending' },
  };
  const cfg = configs[status] ?? { label: status, cls: 'badge-pending' };
  return (
    <span className={cfg.cls}>
      {cfg.dot && <span className="w-1.5 h-1.5 rounded-full bg-blue-500 animate-pulse" />}
      {cfg.label}
    </span>
  );
}

export default function Dashboard() {
  const [campaigns, setCampaigns] = useState<Campaign[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get('/campaigns')
      .then(res => setCampaigns(res.data))
      .catch(err => console.error(err))
      .finally(() => setLoading(false));
  }, []);

  const stats = {
    total: campaigns.length,
    active: campaigns.filter(c => ['running','stage_1','stage_2','stage_3','stage_4'].includes(c.status)).length,
    completed: campaigns.filter(c => c.status === 'completed').length,
    emailsSent: campaigns.reduce((sum, c) => sum + (c.metrics?.emails_sent || 0), 0),
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">

      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-8">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Campaigns</h1>
          <p className="text-sm text-gray-500 mt-0.5">Manage your automated outreach pipelines</p>
        </div>
        <Link to="/campaigns/new" className="btn-primary flex items-center gap-2 w-fit">
          <PlusCircle className="w-4 h-4" />
          New Campaign
        </Link>
      </div>

      {/* Stats row */}
      {campaigns.length > 0 && (
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-8 animate-slide-up">
          {[
            { label: 'Total',     value: stats.total,     icon: Inbox,      color: 'text-gray-700' },
            { label: 'Active',    value: stats.active,    icon: TrendingUp, color: 'text-blue-600' },
            { label: 'Completed', value: stats.completed, icon: Building2,  color: 'text-emerald-600' },
            { label: 'Emails Sent', value: stats.emailsSent, icon: Mail,   color: 'text-violet-600' },
          ].map(s => (
            <div key={s.label} className="stat-card">
              <div className="flex items-center justify-between">
                <span className="text-xs font-medium text-gray-400 uppercase tracking-wider">{s.label}</span>
                <s.icon className={clsx("w-4 h-4", s.color)} />
              </div>
              <span className={clsx("text-3xl font-bold", s.color)}>{s.value}</span>
            </div>
          ))}
        </div>
      )}

      {/* Table */}
      <div className="card overflow-hidden animate-slide-up" style={{ animationDelay: '0.05s' }}>
        {loading ? (
          <div className="p-16 flex flex-col items-center gap-3">
            <div className="w-6 h-6 border-2 border-gray-200 border-t-gray-700 rounded-full animate-spin" />
            <span className="text-sm text-gray-400">Loading campaigns…</span>
          </div>
        ) : campaigns.length === 0 ? (
          <div className="p-16 text-center">
            <div className="w-16 h-16 bg-gray-50 rounded-2xl flex items-center justify-center mx-auto mb-5 border border-gray-100">
              <Inbox className="w-8 h-8 text-gray-300" />
            </div>
            <h3 className="text-base font-semibold text-gray-900 mb-1">No campaigns yet</h3>
            <p className="text-sm text-gray-500 mb-6 max-w-xs mx-auto">
              Launch your first automated outreach campaign by entering a seed domain.
            </p>
            <Link to="/campaigns/new" className="btn-primary inline-flex items-center gap-2">
              <PlusCircle className="w-4 h-4" />
              Start a Campaign
            </Link>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left">
              <thead>
                <tr className="border-b border-gray-100 bg-gray-50/50">
                  <th className="px-5 py-3 text-xs font-semibold text-gray-400 uppercase tracking-wider">Domain</th>
                  <th className="px-5 py-3 text-xs font-semibold text-gray-400 uppercase tracking-wider">Status</th>
                  <th className="px-5 py-3 text-xs font-semibold text-gray-400 uppercase tracking-wider hidden sm:table-cell">Date</th>
                  <th className="px-5 py-3 text-xs font-semibold text-gray-400 uppercase tracking-wider hidden md:table-cell">Metrics</th>
                  <th className="px-5 py-3" />
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-50">
                {campaigns.map((campaign, i) => (
                  <tr
                    key={campaign.id}
                    className="group hover:bg-gray-50/80 transition-colors duration-100 animate-fade-in"
                    style={{ animationDelay: `${i * 0.04}s` }}
                  >
                    <td className="px-5 py-4">
                      <div className="font-semibold text-gray-900 text-sm">{campaign.seed_domain}</div>
                      <div className="text-xs text-gray-400 font-mono mt-0.5">{campaign.id.substring(0, 8)}…</div>
                    </td>
                    <td className="px-5 py-4">
                      <StatusBadge status={campaign.status} />
                    </td>
                    <td className="px-5 py-4 text-sm text-gray-500 hidden sm:table-cell">
                      <div className="flex items-center gap-1.5">
                        <Clock className="w-3.5 h-3.5 text-gray-300" />
                        {new Date(campaign.created_at).toLocaleDateString('en-US', { month:'short', day:'numeric', year:'numeric' })}
                      </div>
                    </td>
                    <td className="px-5 py-4 hidden md:table-cell">
                      <div className="flex items-center gap-4 text-sm">
                        <div className="flex items-center gap-1.5 text-gray-600" title="Companies Found">
                          <Building2 className="w-3.5 h-3.5 text-gray-300" />
                          <span className="font-medium">{campaign.metrics?.companies_found ?? 0}</span>
                        </div>
                        <div className="flex items-center gap-1.5 text-gray-600" title="Emails Sent">
                          <Mail className="w-3.5 h-3.5 text-gray-300" />
                          <span className="font-medium">{campaign.metrics?.emails_sent ?? 0}</span>
                        </div>
                      </div>
                    </td>
                    <td className="px-5 py-4 text-right">
                      <Link
                        to={`/campaigns/${campaign.id}`}
                        className="inline-flex items-center gap-1.5 text-sm font-medium text-gray-700 hover:text-gray-900 group-hover:underline underline-offset-2 transition-colors"
                      >
                        View
                        <ArrowRight className="w-3.5 h-3.5 group-hover:translate-x-0.5 transition-transform" />
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
