import { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import DomainInput from '../components/DomainInput';
import PipelineStatus from '../components/PipelineStatus';
import SummaryModal from '../components/SummaryModal';
import api from '../services/api';
import { useWebSocket } from '../hooks/useWebSocket';

export default function NewCampaign() {
  const navigate = useNavigate();
  const [campaignId, setCampaignId] = useState<string | null>(null);
  const [seedDomain, setSeedDomain] = useState<string>('');
  const [isLoading, setIsLoading] = useState(false);
  
  // Connect WebSocket if campaign is created
  const wsData = useWebSocket(campaignId);

  const redirectTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  // If a status update indicates the campaign finished, redirect to the detail page
  useEffect(() => {
    if (wsData?.status === 'completed') {
      redirectTimerRef.current = setTimeout(() => {
        navigate(`/campaigns/${campaignId}`);
      }, 3000); // Wait 3s so user sees completion state before redirect
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
      // Handle error UI if needed
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

  const handleCancel = () => {
    navigate('/');
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      
      {!campaignId ? (
        <DomainInput onSubmit={handleLaunch} isLoading={isLoading} />
      ) : (
        <div>
          <div className="text-center mb-8">
            <h2 className="text-3xl font-bold text-slate-100">Pipeline Execution</h2>
            <p className="text-slate-400 mt-2 font-mono">ID: {campaignId}</p>
          </div>
          
          <PipelineStatus 
            status={wsData?.status || 'pending'} 
            metrics={wsData?.metrics || {}} 
          />
          
          {wsData?.error_message && (
            <div className="max-w-3xl mx-auto mt-8 p-4 bg-rose-500/10 border border-rose-500/20 rounded-xl text-rose-400 text-center">
              <span className="font-bold">Error:</span> {wsData.error_message}
            </div>
          )}

          {wsData?.status === 'pending_approval' && (
            <SummaryModal
              metrics={wsData.metrics}
              seedDomain={seedDomain}
              onApprove={handleApprove}
              onCancel={handleCancel}
              isLoading={isLoading}
            />
          )}
        </div>
      )}
    </div>
  );
}
