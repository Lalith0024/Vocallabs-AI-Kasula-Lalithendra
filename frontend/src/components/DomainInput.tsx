import { useState, FormEvent } from 'react';
import { ArrowRight, Globe, Zap } from 'lucide-react';
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
    if (!domain.trim()) {
      setError('Please enter a domain');
      return;
    }
    const regex = /^[a-zA-Z0-9][a-zA-Z0-9-]{1,61}[a-zA-Z0-9]\.[a-zA-Z]{2,}$/;
    if (!regex.test(domain.trim())) {
      setError('Please enter a valid domain (e.g., shopify.com)');
      return;
    }
    setError('');
    onSubmit(domain.trim().toLowerCase());
  };

  const examples = ['stripe.com', 'notion.so', 'linear.app', 'vercel.com'];

  return (
    <div className="max-w-2xl mx-auto pt-12 animate-slide-up">
      {/* Hero icon */}
      <div className="flex justify-center mb-7">
        <div className="w-14 h-14 bg-gray-900 rounded-2xl flex items-center justify-center shadow-lg">
          <Zap className="w-7 h-7 text-white" />
        </div>
      </div>

      <div className="text-center mb-8">
        <h2 className="text-3xl font-bold text-gray-900 mb-3">Start a New Campaign</h2>
        <p className="text-gray-500 max-w-md mx-auto leading-relaxed">
          Enter a seed company domain. Our AI finds lookalikes, extracts decision-makers,
          resolves verified emails, and prepares a personalised outreach sequence.
        </p>
      </div>

      <div className="card p-6 sm:p-8">
        <form onSubmit={handleSubmit}>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            <Globe className="inline w-4 h-4 mr-1.5 text-gray-400" />
            Seed Domain
          </label>
          <div className="flex gap-3">
            <input
              type="text"
              value={domain}
              onChange={e => { setDomain(e.target.value); setError(''); }}
              placeholder="e.g. shopify.com"
              disabled={isLoading}
              className={clsx(
                "input-field flex-1",
                error && "!border-red-300 focus:!ring-red-200 focus:!border-red-400"
              )}
            />
            <button
              type="submit"
              disabled={isLoading}
              className="btn-primary flex items-center gap-2 whitespace-nowrap"
            >
              {isLoading ? (
                <>
                  <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  Starting…
                </>
              ) : (
                <>
                  Launch
                  <ArrowRight className="w-4 h-4" />
                </>
              )}
            </button>
          </div>
          {error && (
            <p className="text-red-500 text-sm mt-2 animate-slide-down">{error}</p>
          )}
        </form>

        {/* Example domains */}
        <div className="mt-5 pt-5 border-t border-gray-100">
          <p className="text-xs text-gray-400 mb-3">Try an example domain:</p>
          <div className="flex flex-wrap gap-2">
            {examples.map(ex => (
              <button
                key={ex}
                type="button"
                onClick={() => { setDomain(ex); setError(''); }}
                className="px-3 py-1.5 text-xs font-medium text-gray-600 bg-gray-50 hover:bg-gray-100 border border-gray-200 hover:border-gray-300 rounded-lg transition-all duration-150"
              >
                {ex}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Info pills */}
      <div className="flex flex-wrap justify-center gap-3 mt-6">
        {['Ocean.io lookalikes', 'Prospeo contacts', 'Email verification', 'Brevo delivery'].map((step, i) => (
          <div key={step} className="flex items-center gap-1.5 text-xs text-gray-500">
            <span className="w-5 h-5 rounded-full bg-gray-100 text-gray-500 font-semibold flex items-center justify-center text-[10px]">{i + 1}</span>
            {step}
          </div>
        ))}
      </div>
    </div>
  );
}
