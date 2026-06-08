import { CampaignMetrics } from '../types';
import { Send, X } from 'lucide-react';

interface SummaryModalProps {
  metrics: CampaignMetrics;
  seedDomain: string;
  onApprove: () => void;
  onCancel: () => void;
  isLoading?: boolean;
}

export default function SummaryModal({ metrics, seedDomain, onApprove, onCancel, isLoading }: SummaryModalProps) {
  const successRate = metrics.contacts_found 
    ? Math.round(((metrics.emails_resolved || 0) / metrics.contacts_found) * 100) 
    : 0;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm">
      <div className="bg-slate-900 border border-slate-700 shadow-2xl rounded-3xl max-w-2xl w-full overflow-hidden animate-[slideUp_0.3s_ease-out]">
        
        <div className="p-6 border-b border-slate-800 flex justify-between items-center bg-slate-800/50">
          <h2 className="text-xl font-bold text-slate-100">Safety Checkpoint</h2>
          <button onClick={onCancel} className="text-slate-400 hover:text-slate-200 transition-colors">
            <X className="w-6 h-6" />
          </button>
        </div>
        
        <div className="p-8">
          <p className="text-slate-300 mb-8">
            Pipeline data extraction is complete for <span className="font-semibold text-white">{seedDomain}</span>. 
            Review the results before initiating the email sequence.
          </p>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
            <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-4 text-center">
              <span className="block text-3xl font-bold text-slate-100 mb-1">{metrics.companies_found || 0}</span>
              <span className="text-xs text-slate-400 uppercase tracking-wider">Companies</span>
            </div>
            <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-4 text-center">
              <span className="block text-3xl font-bold text-slate-100 mb-1">{metrics.contacts_found || 0}</span>
              <span className="text-xs text-slate-400 uppercase tracking-wider">Contacts</span>
            </div>
            <div className="bg-brand-500/10 border border-brand-500/20 rounded-xl p-4 text-center">
              <span className="block text-3xl font-bold text-brand-400 mb-1">{metrics.emails_resolved || 0}</span>
              <span className="text-xs text-brand-400/80 uppercase tracking-wider">Emails Found</span>
            </div>
            <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-4 text-center">
              <span className="block text-3xl font-bold text-slate-100 mb-1">{successRate}%</span>
              <span className="text-xs text-slate-400 uppercase tracking-wider">Match Rate</span>
            </div>
          </div>

          <div className="flex space-x-4">
            <button
              onClick={onCancel}
              disabled={isLoading}
              className="flex-1 bg-slate-800 hover:bg-slate-700 text-slate-200 py-3 rounded-xl font-medium transition-colors"
            >
              Cancel
            </button>
            <button
              onClick={onApprove}
              disabled={isLoading}
              className="flex-[2] bg-emerald-600 hover:bg-emerald-500 text-white py-3 rounded-xl font-medium transition-colors flex items-center justify-center space-x-2 disabled:opacity-50"
            >
              <span>{isLoading ? 'Sending...' : `Approve & Send ${metrics.emails_resolved || 0} Emails`}</span>
              {!isLoading && <Send className="w-4 h-4" />}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
