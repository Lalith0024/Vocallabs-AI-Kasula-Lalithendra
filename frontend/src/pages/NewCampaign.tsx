import { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import DomainInput from '../components/DomainInput';
import PipelineStatus from '../components/PipelineStatus';
import SummaryModal from '../components/SummaryModal';
import api from '../services/api';
import { useWebSocket } from '../hooks/useWebSocket';
import { AlertCircle } from 'lucide-react';

export default function NewCampaign() {
  const navigate = useNavigate();
  const [campaignId, setCampaignId] = useState<string | null>(null);
  const [seedDomain, setSeedDomain] = useState<string>('');
  const [isLoading, setIsLoading] = useState(false);

  const wsData = useWebSocket(campaignId);
  const redirectTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    if (wsData?.status === 'completed') {
      redirectTimerRef.current = setTimeout(() => {
        navigate(`/campaigns/${campaignId}`);
      }, 2500);
    }
    return () => {
      if (redirectTimerRef.current !== null) {
        clearTimeout(redirectTimerRef.current);
        redirectTimerRef.current = null;
      }
    };
  }, [wsData?.status, navigate, campaignId]);

  const handleLaunch = async (domain: string) => {
    setIsLoading(true);
    setSeedDomain(domain);
    try {
      const res = await api.post('/campaigns', { seed_domain: domain });
      setCampaignId(res.data.id);
    } catch (err) {
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleApprove = async () => {
    if (!campaignId) return;
    setIsLoading(true);
    try {
      await api.post(`/campaigns/${campaignId}/approve-send`);
    } catch (err) {
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {!campaignId ? (
        <DomainInput onSubmit={handleLaunch} isLoading={isLoading} />
      ) : (
        <div className="animate-fade-in">
          {/* Campaign header */}
          <div className="text-center mb-6">
            <div className="inline-flex items-center gap-2 text-xs font-medium text-gray-400 bg-gray-50 border border-gray-100 rounded-full px-3 py-1.5 mb-4">
              <span className="font-mono">{campaignId}</span>
            </div>
            <h2 className="text-2xl font-bold text-gray-900">
              Running Pipeline
            </h2>
            <p className="text-gray-500 mt-1 text-sm">
              Seed domain: <span className="font-semibold text-gray-700">{seedDomain}</span>
            </p>
          </div>

          <PipelineStatus
            status={wsData?.status || 'pending'}
            metrics={wsData?.metrics || {}}
          />

          {/* Error state */}
          {wsData?.error_message && (
            <div className="mt-6 flex items-start gap-3 bg-red-50 border border-red-200 rounded-xl p-4 animate-slide-up">
              <AlertCircle className="w-5 h-5 text-red-500 shrink-0 mt-0.5" />
              <div>
                <p className="text-sm font-semibold text-red-700">Pipeline Failed</p>
                <p className="text-sm text-red-600 mt-0.5">{wsData.error_message}</p>
              </div>
            </div>
          )}

          {/* Completion redirect notice */}
          {wsData?.status === 'completed' && (
            <div className="mt-6 text-center animate-slide-up">
              <p className="text-sm text-gray-500">Redirecting to campaign details…</p>
            </div>
          )}
        </div>
      )}

      {/* Safety checkpoint modal */}
      {wsData?.status === 'pending_approval' && (
        <SummaryModal
          metrics={wsData.metrics}
          seedDomain={seedDomain}
          onApprove={handleApprove}
          onCancel={() => navigate('/')}
          isLoading={isLoading}
        />
      )}
    </div>
  );
}
