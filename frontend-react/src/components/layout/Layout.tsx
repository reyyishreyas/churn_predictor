import React from 'react';
import { NavLink, Outlet } from 'react-router-dom';
import { LayoutDashboard, Users, LineChart, Sliders, UploadCloud, Bell, Search, Moon, Sun, UserCircle } from 'lucide-react';
import { Button } from '../ui/button';

export const Layout = () => {
  const [theme, setTheme] = React.useState('dark');

  React.useEffect(() => {
    document.documentElement.classList.toggle('dark', theme === 'dark');
  }, [theme]);

  const navItems = [
    { name: 'Dashboard', path: '/', icon: LayoutDashboard },
    { name: 'User Analysis', path: '/user-analysis', icon: Users },
    { name: 'Insights', path: '/insights', icon: LineChart },
    { name: 'Simulation', path: '/simulation', icon: Sliders },
    { name: 'Batch Upload', path: '/batch', icon: UploadCloud },
  ];

  return (
    <div className="flex h-screen bg-background overflow-hidden font-sans">
      {/* Sidebar */}
      <aside className="w-64 flex-shrink-0 border-r border-border bg-card/30 backdrop-blur-xl flex flex-col hidden md:flex relative z-10 transition-all duration-300">
        <div className="h-16 flex items-center px-6 border-b border-border/50">
          <div className="h-8 w-8 rounded-xl bg-gradient-to-br from-primary to-purple-500 shadow-soft-dark flex items-center justify-center font-bold text-white tracking-widest text-lg">
            C
          </div>
          <span className="ml-3 font-semibold text-foreground tracking-tight">Churn Intel</span>
        </div>
        
        <nav className="flex-1 overflow-y-auto py-6 px-3 space-y-1">
          {navItems.map((item) => (
            <NavLink
              key={item.name}
              to={item.path}
              className={({ isActive }) =>
                `group flex items-center px-3 py-2.5 text-sm font-medium rounded-xl transition-all duration-200 ease-in-out ${
                  isActive
                    ? 'bg-primary/10 text-primary shadow-sm ring-1 ring-primary/20'
                    : 'text-muted-foreground hover:bg-secondary/60 hover:text-foreground'
                }`
              }
            >
              <item.icon className="mr-3 h-5 w-5 flex-shrink-0 drop-shadow-sm transition-transform group-hover:scale-110" />
              {item.name}
            </NavLink>
          ))}
        </nav>
        
        <div className="p-4 border-t border-border/50">
          <div className="px-3 py-3 rounded-xl bg-gradient-to-br from-primary/10 to-transparent border border-primary/10 flex flex-col justify-center items-center text-center">
             <div className="h-2 w-2 rounded-full bg-green-500 animate-pulse mb-2"></div>
             <p className="text-xs font-medium text-foreground">API Connected</p>
             <p className="text-[10px] text-muted-foreground mt-0.5">Metrics synced live</p>
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col w-full min-w-0">
        {/* Top Header */}
        <header className="h-16 flex items-center justify-between px-6 border-b border-border/40 bg-background/50 backdrop-blur-sm z-10 w-full transition-colors">
          <div className="flex flex-1 items-center max-w-md">
            <div className="relative w-full">
              <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
              <input
                type="text"
                placeholder="Search metrics, users, or reports..."
                className="w-full h-9 pl-9 pr-4 rounded-full bg-secondary/50 border-none text-sm focus:outline-none focus:ring-1 focus:ring-primary/40 transition-all font-medium text-foreground placeholder-muted-foreground"
              />
            </div>
          </div>
          
          <div className="flex items-center space-x-2 ml-4">
            <Button variant="ghost" size="icon" className="rounded-full" onClick={() => setTheme(t => t === 'dark' ? 'light' : 'dark')}>
              {theme === 'dark' ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
            </Button>
            <Button variant="ghost" size="icon" className="rounded-full">
              <Bell className="h-4 w-4" />
            </Button>
            <Button variant="ghost" size="icon" className="rounded-full">
              <UserCircle className="h-5 w-5" />
            </Button>
          </div>
        </header>

        {/* Page Content */}
        <div className="flex-1 overflow-y-auto px-6 lg:px-10 py-8 scroll-smooth w-full relative">
          <Outlet />
        </div>
      </main>
    </div>
  );
};
