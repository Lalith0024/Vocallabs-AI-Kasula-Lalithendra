import StageCard from './StageCard';
import { CampaignStatus, CampaignMetrics } from '../types';

interface PipelineStatusProps {
  status: CampaignStatus;
  metrics: CampaignMetrics;
}

export default function PipelineStatus({ status, metrics }: PipelineStatusProps) {
  const getStageStatus = (stageNum: number): 'pending' | 'running' | 'completed' | 'failed' => {
    const statusMap: Record<CampaignStatus, number> = {
      pending: 0, running: 0,
      stage_1: 1, stage_2: 2, stage_3: 3,
      pending_approval: 4, stage_4: 4,
      completed: 5, failed: -1
    };
    const lvl = statusMap[status];
    if (status === 'failed') return 'failed';
    if (lvl > stageNum) return 'completed';
    if (lvl === stageNum && status !== 'pending_approval') return 'running';
    return 'pending';
  };

  return (
    <div className="max-w-2xl mx-auto mt-8 space-y-3">
      <StageCard stageNum={1} title="Find Lookalike Companies"   description="Ocean.io AI discovers companies similar to your seed domain."  status={getStageStatus(1)} count={metrics.companies_found} countLabel="Companies" />
      <StageCard stageNum={2} title="Extract Decision Makers"    description="Prospeo identifies C-suite and VP level contacts."            status={getStageStatus(2)} count={metrics.contacts_found}  countLabel="Prospects" />
      <StageCard stageNum={3} title="Resolve Verified Emails"    description="Prospeo email-finder verifies work email addresses."          status={getStageStatus(3)} count={metrics.emails_resolved} countLabel="Emails" />
      <StageCard stageNum={4} title="Personalised Email Outreach" description="Brevo sends tailored cold emails (max 20)."                  status={getStageStatus(4)} count={metrics.emails_sent}     countLabel="Sent" />
    </div>
  );
}
