import { Link, useLocation } from 'react-router-dom';
import { Rocket, LayoutDashboard, PlusCircle } from 'lucide-react';
import clsx from 'clsx';

export default function Navbar() {
  const location = useLocation();

  const navItems = [
    { name: 'Dashboard', path: '/', icon: LayoutDashboard },
    { name: 'New Campaign', path: '/campaigns/new', icon: PlusCircle },
  ];

  return (
    <nav className="border-b border-slate-800 bg-slate-900/50 backdrop-blur-md sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex items-center space-x-3">
            <div className="bg-brand-500/20 p-2 rounded-xl">
              <Rocket className="h-6 w-6 text-brand-500" />
            </div>
            <span className="text-xl font-bold bg-gradient-to-r from-slate-100 to-slate-400 bg-clip-text text-transparent">
              OutreachAutomator
            </span>
          </div>
          
          <div className="flex items-center space-x-8">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = location.pathname === item.path;
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  className={clsx(
                    "flex items-center space-x-2 text-sm font-medium transition-colors",
                    isActive 
                      ? "text-brand-400" 
                      : "text-slate-400 hover:text-slate-200"
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
