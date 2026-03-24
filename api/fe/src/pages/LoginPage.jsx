import React from "react";
import { Link } from "react-router-dom";

export default function LoginPage() {
  return (
    <div className="min-h-screen bg-[#f5f6fa] p-4 md:p-8">
      <div className="mx-auto grid min-h-[85vh] max-w-6xl overflow-hidden rounded-[28px] bg-white shadow-xl lg:grid-cols-[1.15fr_0.85fr]">
        <div className="relative hidden overflow-hidden bg-gradient-to-br from-indigo-500 to-indigo-700 lg:block">
          <div className="absolute left-10 top-10 z-10 text-4xl font-black text-white">
            Sound Capture
          </div>

          <div className="relative z-10 max-w-lg px-10 pt-48 text-white">
            <h1 className="text-6xl font-black leading-[0.95]">
              The Exquisite
              <br />
              Archivist.
            </h1>
            <p className="mt-6 text-lg leading-8 text-white/80">
              Transforming the fluid nature of audio into high-fidelity
              intelligence with editorial precision.
            </p>
          </div>

          <div className="absolute bottom-0 left-[18%] h-[60%] w-[80%] rounded-tl-[40px] bg-[linear-gradient(180deg,rgba(30,58,138,0.25),rgba(147,197,253,0.28))]" />
        </div>

        <div className="flex items-center justify-center px-6 py-10 md:px-12">
          <div className="w-full max-w-md">
            <h2 className="text-4xl font-black text-slate-900">Welcome Back</h2>
            <p className="mt-2 text-slate-500">
              Continue your auditory analysis journey.
            </p>

            <button className="mt-8 flex h-12 w-full items-center justify-center gap-2 rounded-xl border border-slate-200 bg-white font-semibold text-slate-700">
              <i className="bi bi-google" />
              Google
            </button>

            <div className="my-6 text-center text-xs font-bold tracking-[0.2em] text-slate-400">
              OR CONTINUE WITH EMAIL
            </div>

            <label className="mb-2 block text-xs font-extrabold tracking-[0.12em] text-slate-500">
              EMAIL ADDRESS
            </label>
            <input
              type="email"
              placeholder="name@company.com"
              className="mb-5 h-12 w-full rounded-xl border border-slate-200 px-4 outline-none"
            />

            <div className="mb-2 flex items-center justify-between">
              <label className="block text-xs font-extrabold tracking-[0.12em] text-slate-500">
                PASSWORD
              </label>
              <a href="#" className="text-sm font-semibold text-indigo-600">
                Forgot?
              </a>
            </div>

            <div className="relative">
              <input
                type="password"
                placeholder="••••••••"
                className="mb-5 h-12 w-full rounded-xl border border-slate-200 px-4 pr-10 outline-none"
              />
              <i className="bi bi-eye absolute right-4 top-3.5 text-slate-400" />
            </div>

            <div className="mb-5">
              <input type="checkbox" className="h-4 w-4 rounded" />
            </div>

            <Link
              to="/dashboard"
              className="flex h-12 w-full items-center justify-center rounded-xl bg-indigo-600 font-semibold text-white shadow hover:bg-indigo-700"
            >
              Sign In to Sound Capture
            </Link>

            <div className="mt-6 text-center text-sm text-slate-500">
              New to the us?
              <a href="#" className="ml-2 font-bold text-indigo-600">
                Create an account
              </a>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
