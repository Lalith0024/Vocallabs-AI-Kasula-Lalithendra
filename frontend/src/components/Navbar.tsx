import { useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Zap, LayoutDashboard, PlusCircle, Wifi, WifiOff } from 'lucide-react';
import clsx from 'clsx';
import api from '../services/api';

export default function Navbar() {
  const location = useLocation();
  const [isLiveMode, setIsLiveMode] = useState<boolean | null>(null);

  useEffect(() => {
    api.get('/health')
      .then(res => setIsLiveMode(res.data.live_mode))
      .catch(() => setIsLiveMode(false));
  }, []);

  const navItems = [
    { name: 'Dashboard', path: '/', icon: LayoutDashboard },
    { name: 'New Campaign', path: '/campaigns/new', icon: PlusCircle },
  ];

  return (
    <nav className="bg-white border-b border-gray-100 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-14 items-center">
          {/* Logo */}
          <div className="flex items-center gap-6">
            <Link to="/" className="flex items-center gap-2.5 group">
              <div className="w-7 h-7 rounded-lg flex items-center justify-center overflow-hidden">
                <img src="/logo.png" alt="SubSpace Logo" className="w-full h-full object-cover" />
              </div>
              <span className="font-bold text-gray-900 text-sm tracking-tight hidden sm:block">SubSpace</span>
            </Link>

            {/* Mode badge */}
            {isLiveMode !== null && (
              <div className={clsx(
                "flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold border transition-all",
                isLiveMode
                  ? "bg-emerald-50 text-emerald-700 border-emerald-200"
                  : "bg-amber-50 text-amber-700 border-amber-200"
              )}>
                {isLiveMode
                  ? <><Wifi className="w-3 h-3" /> LIVE</>
                  : <><WifiOff className="w-3 h-3" /> MOCK</>
                }
              </div>
            )}
          </div>

          {/* Nav links */}
          <div className="flex items-center gap-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = location.pathname === item.path;
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  className={clsx(
                    "flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition-all duration-150",
                    isActive
                      ? "bg-gray-900 text-white"
                      : "text-gray-600 hover:bg-gray-100 hover:text-gray-900"
                  )}
                >
                  <Icon className="h-4 w-4" />
                  <span>{item.name}</span>
                </Link>
              );
            })}
          </div>
        </div>
      </div>
    </nav>
  );
}
