import { useState } from 'react';
import { CampaignMetrics } from '../types';
import { Send, X, ChevronDown, ChevronUp, Mail, ShieldCheck, AlertTriangle } from 'lucide-react';

interface SummaryModalProps {
  metrics: CampaignMetrics;
  seedDomain: string;
  onApprove: () => void;
  onCancel: () => void;
  isLoading?: boolean;
}

export default function SummaryModal({ metrics, seedDomain, onApprove, onCancel, isLoading }: SummaryModalProps) {
  const [showPreview, setShowPreview] = useState(false);

  const emailCount = metrics.emails_resolved || 0;
  const cappedCount = Math.min(emailCount, 20);
  const successRate = metrics.contacts_found
    ? Math.round((emailCount / metrics.contacts_found) * 100)
    : 0;

  return (
    <div className="fixed inset-0 z-50 flex items-end sm:items-center justify-center p-4 bg-black/30 backdrop-blur-sm animate-fade-in">
      <div className="bg-white rounded-2xl shadow-modal w-full max-w-lg overflow-hidden animate-slide-up">

        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-gray-100">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 bg-amber-50 rounded-lg flex items-center justify-center">
              <ShieldCheck className="w-4 h-4 text-amber-600" />
            </div>
            <div>
              <h2 className="font-bold text-gray-900 text-sm">Safety Checkpoint</h2>
              <p className="text-xs text-gray-400">Review before sending</p>
            </div>
          </div>
          <button
            onClick={onCancel}
            className="w-8 h-8 flex items-center justify-center rounded-lg text-gray-400 hover:text-gray-600 hover:bg-gray-100 transition-all"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Body */}
        <div className="px-6 py-5">
          <p className="text-sm text-gray-600 mb-5">
            Pipeline extraction complete for <span className="font-semibold text-gray-900">{seedDomain}</span>.
            {cappedCount < emailCount && (
              <span className="text-amber-600"> Capped at 20 emails to prevent billing overruns.</span>
            )}
          </p>

          {/* Stats grid */}
          <div className="grid grid-cols-4 gap-3 mb-5">
            {[
              { label: 'Companies', value: metrics.companies_found || 0, color: 'text-gray-900' },
              { label: 'Contacts',  value: metrics.contacts_found  || 0, color: 'text-gray-900' },
              { label: 'Emails',    value: cappedCount,                  color: 'text-blue-600'  },
              { label: 'Match',     value: `${successRate}%`,            color: 'text-emerald-600' },
            ].map(s => (
              <div key={s.label} className="bg-gray-50 rounded-xl p-3 text-center border border-gray-100">
                <div className={`text-xl font-bold ${s.color}`}>{s.value}</div>
                <div className="text-[10px] text-gray-400 uppercase tracking-wider mt-0.5 font-medium">{s.label}</div>
              </div>
            ))}
          </div>

          {/* 20 email cap notice */}
          {emailCount > 20 && (
            <div className="flex items-start gap-2.5 bg-amber-50 border border-amber-200 rounded-xl p-3 mb-4">
              <AlertTriangle className="w-4 h-4 text-amber-500 shrink-0 mt-0.5" />
              <p className="text-xs text-amber-700">
                <span className="font-semibold">{emailCount} emails found</span>, but only the first 20 will be sent to stay within free API limits.
              </p>
            </div>
          )}

          {/* Email preview accordion */}
          <div className="border border-gray-200 rounded-xl overflow-hidden mb-5">
            <button
              onClick={() => setShowPreview(!showPreview)}
              className="w-full flex items-center justify-between px-4 py-3 bg-gray-50 hover:bg-gray-100 text-sm font-medium text-gray-700 transition-colors"
            >
              <div className="flex items-center gap-2">
                <Mail className="w-4 h-4 text-gray-400" />
                Email Preview
              </div>
              {showPreview ? <ChevronUp className="w-4 h-4 text-gray-400" /> : <ChevronDown className="w-4 h-4 text-gray-400" />}
            </button>
            {showPreview && (
              <div className="px-4 py-4 bg-white border-t border-gray-100 text-xs text-gray-600 space-y-2 animate-slide-down">
                <p><span className="text-gray-400">Subject:</span> Partnership Opportunity — {'{company_name}'} &amp; {seedDomain}</p>
                <div className="bg-gray-50 rounded-lg p-3 space-y-2 leading-relaxed text-gray-700 border border-gray-100">
                  <p>Hi {'{first_name}'},</p>
                  <p>I came across {'{company_name}'} while researching companies in the {'{industry}'} space — impressive work you're doing there.</p>
                  <p>I'm reaching out because we help companies like yours streamline recurring costs…</p>
                  <p className="text-gray-400 italic">(Dynamic variables will be injected before sending.)</p>
                </div>
              </div>
            )}
          </div>

          {/* Actions */}
          <div className="flex gap-3">
            <button onClick={onCancel} disabled={isLoading} className="btn-secondary flex-1">
              Cancel
            </button>
            <button
              onClick={onApprove}
              disabled={isLoading}
              className="btn-success flex-[2] flex items-center justify-center gap-2"
            >
              {isLoading ? (
                <><div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" /> Sending…</>
              ) : (
                <><Send className="w-4 h-4" /> Approve &amp; Send {cappedCount} Emails</>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
