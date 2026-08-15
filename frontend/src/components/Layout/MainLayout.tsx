import React from 'react';
import { Outlet, Link, useLocation } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';

export default function MainLayout() {
  const auth = useAuth();
  const location = useLocation();

  const navItems = [
    { label: 'Dashboard', path: '/' },
    { label: 'New Analysis', path: '/new-analysis' },
    { label: 'Previous Reports', path: '/reports' },
    { label: 'Dataset', path: '/dataset' },
    { label: 'Model Performance', path: '/model-performance' },
    { label: 'About', path: '/about' },
  ];

  return (
    <div className="flex h-screen bg-gray-50">
      <aside className="w-64 bg-white shadow-md p-4">
        <h2 className="text-xl font-bold text-blue-800 mb-6">ReAlux</h2>
        <nav className="space-y-2">
          {navItems.map((item) => (
            <Link
              key={item.path}
              to={item.path}
              className={`block px-4 py-2 rounded hover:bg-blue-50 ${
                location.pathname === item.path ? 'bg-blue-100 text-blue-700' : 'text-gray-700'
              }`}
            >
              {item.label}
            </Link>
          ))}
        </nav>
        <div className="mt-8 pt-4 border-t">
          <div className="text-sm text-gray-600">Signed in as {auth?.user?.name}</div>
          <button
            onClick={auth?.logout}
            className="mt-2 text-sm text-red-600 hover:text-red-800"
          >
            Logout
          </button>
        </div>
      </aside>
      <main className="flex-1 overflow-y-auto p-6">
        <Outlet />
      </main>
    </div>
  );
}
