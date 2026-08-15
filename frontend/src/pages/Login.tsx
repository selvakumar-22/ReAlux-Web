import React, { useState } from 'react';
import { useAuth } from '../hooks/useAuth';
import { Navigate } from 'react-router-dom';

export default function Login() {
  const auth = useAuth();

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [name, setName] = useState('');
  const [isRegister, setIsRegister] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  if (auth?.user) {
    return <Navigate to="/" replace />;
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      if (isRegister) {
        await auth?.register(name, email, password);
      } else {
        await auth?.login(email, password);
      }
    } catch (err: any) {
      setError(
        err?.response?.data?.detail ||
        'Unable to complete the request. Please try again.'
      );
    } finally {
      setLoading(false);
    }
  };

  const toggleMode = () => {
    setIsRegister(!isRegister);
    setError('');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-indigo-50 flex items-center justify-center px-4 py-10">

      <div className="w-full max-w-5xl bg-white rounded-3xl shadow-xl overflow-hidden border border-gray-100">

        <div className="grid md:grid-cols-2">

          {/* LEFT SIDE */}
          <div className="hidden md:flex bg-gradient-to-br from-blue-600 to-indigo-700 text-white p-12 flex-col justify-between">

            <div>

              <div className="flex items-center gap-3 mb-10">
                <div className="w-12 h-12 bg-white/15 rounded-2xl flex items-center justify-center text-2xl font-bold">
                  R
                </div>

                <div>
                  <div className="text-2xl font-bold">
                    ReAlux
                  </div>

                  <div className="text-sm text-blue-100">
                    Analytics Platform
                  </div>
                </div>
              </div>

              <h2 className="text-4xl font-bold leading-tight">
                Aluminium Dross
                <br />
                Recovery Analysis
              </h2>

              <p className="mt-6 text-blue-100 leading-relaxed">
                Analyse material composition, estimate recovery
                performance, evaluate risk, and generate professional
                reports with ReAlux.
              </p>

            </div>

            <div className="space-y-4">

              <div className="flex items-center gap-3">
                <div className="w-9 h-9 rounded-lg bg-white/15 flex items-center justify-center">
                  ✓
                </div>
                <span className="text-sm">
                  AI-powered analysis
                </span>
              </div>

              <div className="flex items-center gap-3">
                <div className="w-9 h-9 rounded-lg bg-white/15 flex items-center justify-center">
                  ✓
                </div>
                <span className="text-sm">
                  Recovery performance insights
                </span>
              </div>

              <div className="flex items-center gap-3">
                <div className="w-9 h-9 rounded-lg bg-white/15 flex items-center justify-center">
                  ✓
                </div>
                <span className="text-sm">
                  Professional PDF reports
                </span>
              </div>

            </div>

          </div>

          {/* RIGHT SIDE */}
          <div className="p-8 sm:p-12">

            {/* Mobile Logo */}
            <div className="md:hidden text-center mb-8">

              <div className="inline-flex items-center gap-3">
                <div className="w-11 h-11 bg-blue-600 text-white rounded-xl flex items-center justify-center font-bold text-xl">
                  R
                </div>

                <span className="text-2xl font-bold text-gray-900">
                  ReAlux
                </span>
              </div>

            </div>

            {/* Heading */}
            <div className="mb-8">

              <h1 className="text-3xl font-bold text-gray-900">
                {isRegister
                  ? 'Create your account'
                  : 'Welcome back'}
              </h1>

              <p className="text-gray-500 mt-2">
                {isRegister
                  ? 'Create an account to start analysing aluminium dross.'
                  : 'Sign in to continue to your ReAlux dashboard.'}
              </p>

            </div>

            {/* Error */}
            {error && (
              <div className="mb-6 p-4 rounded-xl bg-red-50 border border-red-100 text-red-700 text-sm">
                <div className="font-semibold mb-1">
                  Something went wrong
                </div>
                {error}
              </div>
            )}

            {/* FORM */}
            <form onSubmit={handleSubmit} className="space-y-5">

              {/* Name */}
              {isRegister && (
                <div>

                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    Full Name
                  </label>

                  <input
                    type="text"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    placeholder="Enter your name"
                    className="w-full px-4 py-3 rounded-xl border border-gray-200 bg-gray-50 focus:bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition"
                    required
                  />

                </div>
              )}

              {/* Email */}
              <div>

                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Email Address
                </label>

                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="you@example.com"
                  autoComplete="email"
                  className="w-full px-4 py-3 rounded-xl border border-gray-200 bg-gray-50 focus:bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition"
                  required
                />

              </div>

              {/* Password */}
              <div>

                <div className="flex items-center justify-between mb-2">

                  <label className="block text-sm font-semibold text-gray-700">
                    Password
                  </label>

                </div>

                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Enter your password"
                  autoComplete={
                    isRegister ? 'new-password' : 'current-password'
                  }
                  className="w-full px-4 py-3 rounded-xl border border-gray-200 bg-gray-50 focus:bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition"
                  required
                />

              </div>

              {/* Submit */}
              <button
                type="submit"
                disabled={loading}
                className={`w-full py-3.5 rounded-xl font-semibold text-white transition shadow-sm ${
                  loading
                    ? 'bg-blue-400 cursor-not-allowed'
                    : 'bg-blue-600 hover:bg-blue-700 active:bg-blue-800'
                }`}
              >

                {loading ? (
                  <span className="flex items-center justify-center gap-2">
                    <span className="w-5 h-5 border-2 border-white/40 border-t-white rounded-full animate-spin"></span>
                    {isRegister
                      ? 'Creating account...'
                      : 'Signing in...'}
                  </span>
                ) : (
                  isRegister
                    ? 'Create Account'
                    : 'Sign In'
                )}

              </button>

            </form>

            {/* Toggle */}
            <div className="mt-8 text-center">

              <p className="text-sm text-gray-500">
                {isRegister
                  ? 'Already have an account?'
                  : "Don't have an account?"}
              </p>

              <button
                type="button"
                onClick={toggleMode}
                className="mt-2 text-blue-600 font-semibold hover:text-blue-700 hover:underline"
              >
                {isRegister
                  ? 'Sign in instead'
                  : 'Create a new account'}
              </button>

            </div>

            {/* Footer */}
            <div className="mt-10 pt-6 border-t border-gray-100 text-center">

              <p className="text-xs text-gray-400">
                ReAlux · Aluminium Dross Recovery Analytics
              </p>

            </div>

          </div>

        </div>

      </div>

    </div>
  );
}