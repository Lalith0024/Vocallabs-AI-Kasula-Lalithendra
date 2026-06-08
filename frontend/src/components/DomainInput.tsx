import { useState, FormEvent } from 'react';
import { ArrowRight, Globe } from 'lucide-react';
import clsx from 'clsx';

interface DomainInputProps {
  onSubmit: (domain: string) => void;
  isLoading?: boolean;
}

export default function DomainInput({ onSubmit, isLoading }: DomainInputProps) {
  const [domain, setDomain] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    if (!domain) {
      setError('Please enter a domain');
      return;
    }
    // Basic domain regex
    const regex = /^[a-zA-Z0-9][a-zA-Z0-9-]{1,61}[a-zA-Z0-9]\.[a-zA-Z]{2,}$/;
    if (!regex.test(domain)) {
      setError('Please enter a valid domain (e.g., acme.com)');
      return;
    }
    setError('');
    onSubmit(domain);
  };

  return (
    <div className="glass-panel p-8 rounded-3xl max-w-2xl mx-auto text-center mt-12">
      <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-brand-500/20 text-brand-400 mb-6">
        <Globe className="w-8 h-8" />
      </div>
      <h2 className="text-3xl font-bold text-slate-100 mb-4">Start New Campaign</h2>
      <p className="text-slate-400 mb-8 max-w-md mx-auto">
        Enter a seed company domain. Our AI will automatically find lookalikes, extract decision-makers, resolve verified emails, and prepare outreach.
      </p>

      <form onSubmit={handleSubmit} className="relative max-w-lg mx-auto">
        <div className="relative flex items-center">
          <input
            type="text"
            value={domain}
            onChange={(e) => { setDomain(e.target.value); setError(''); }}
            placeholder="e.g. shopify.com"
            disabled={isLoading}
            className={clsx(
              "w-full bg-slate-900/50 border rounded-xl py-4 pl-6 pr-32 text-lg focus:outline-none focus:ring-2 focus:ring-brand-500/50 transition-all text-slate-100 placeholder-slate-500",
              error ? "border-rose-500" : "border-slate-700"
            )}
          />
          <button
            type="submit"
            disabled={isLoading}
            className="absolute right-2 top-2 bottom-2 bg-brand-600 hover:bg-brand-500 text-white rounded-lg px-6 font-medium transition-colors flex items-center space-x-2 disabled:opacity-50"
          >
            <span>{isLoading ? 'Starting...' : 'Launch'}</span>
            {!isLoading && <ArrowRight className="w-4 h-4" />}
          </button>
        </div>
        {error && <p className="text-rose-400 text-sm mt-2 text-left pl-4">{error}</p>}
      </form>
    </div>
  );
}
