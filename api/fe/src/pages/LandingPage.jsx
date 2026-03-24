import React from "react";
import { Link } from "react-router-dom";

export default function LandingPage() {
  return (
    <div className="bg-[#f6f7fb] pb-10 pt-6">
      <div className="mx-auto w-[95%] max-w-7xl">
        <header className="flex items-center justify-between rounded-2xl border border-slate-200 bg-white px-6 py-4">
          <div className="text-sm font-bold text-indigo-600 md:text-base">
            Sound Capture
          </div>

          <div className="flex items-center gap-4">
            <Link to="/login" className="text-sm font-semibold text-slate-700">
              Login
            </Link>
            <Link
              to="/dashboard"
              className="rounded-xl bg-indigo-600 px-4 py-2 text-sm font-semibold text-white shadow hover:bg-indigo-700"
            >
              Get Started
            </Link>
          </div>
        </header>

        <section className="mt-7 grid gap-8 rounded-3xl border border-slate-200 bg-white p-6 md:p-10 lg:grid-cols-2">
          <div className="flex flex-col justify-center">
            <h1 className="text-4xl font-black leading-tight text-slate-900 md:text-6xl">
              Transcribe,
              <br />
              Analyze, & Master
              <br />
              Your
              <br />
              <span className="text-indigo-600">Conversations</span>
            </h1>

            <p className="mt-6 max-w-xl text-base leading-7 text-slate-500">
              Experience the ethereal power of AI that does not just listen, but
              understands. Turn every meeting, interview, and voice note into a
              searchable, actionable database of intelligence.
            </p>

            <div className="mt-8 flex flex-wrap gap-4">
              <Link
                to="/dashboard"
                className="rounded-xl bg-indigo-600 px-5 py-3 font-semibold text-white shadow hover:bg-indigo-700"
              >
                Get Started Free
              </Link>
              <button className="rounded-xl bg-slate-100 px-5 py-3 font-semibold text-slate-700 hover:bg-slate-200">
                Learn More
              </button>
            </div>
          </div>

          <div className="flex items-center justify-center">
            <div className="flex w-full max-w-[520px] gap-4">
              <div className="flex-1 rounded-2xl bg-white p-4 shadow-xl ring-1 ring-slate-100">
                <div className="mb-4 space-y-2">
                  <div className="h-1.5 w-20 rounded-full bg-indigo-200" />
                  <div className="h-1.5 w-28 rounded-full bg-slate-200" />
                </div>
                <div className="h-52 rounded-xl bg-[radial-gradient(circle_at_center,_rgba(255,210,120,0.8),_rgba(80,70,220,0.35)_45%,_#111827_80%)]" />
              </div>

              <div className="flex w-[110px] flex-col gap-4">
                <div className="flex h-40 flex-col items-center justify-center rounded-2xl bg-indigo-100 text-center text-slate-500 shadow">
                  <i className="bi bi-stars text-xl text-indigo-500" />
                  <span className="mt-2 text-sm font-medium">AI Insights</span>
                </div>
                <div className="flex h-28 items-center justify-center rounded-2xl bg-indigo-600 text-white shadow">
                  <i className="bi bi-mic-fill text-xl" />
                </div>
              </div>
            </div>
          </div>
        </section>

        <section className="mt-8 rounded-3xl bg-[#f9fafe] px-4 py-14 md:px-8">
          <div className="text-center text-[11px] font-extrabold tracking-[0.25em] text-indigo-500">
            MAIN FEATURES
          </div>
          <h2 className="mt-3 text-center text-3xl font-black text-slate-900 md:text-4xl">
            Perfect for Business
          </h2>

          <div className="mt-10 grid gap-5 md:grid-cols-3">
            <div className="rounded-2xl border border-slate-200 bg-white p-6">
              <div className="mb-4 flex h-11 w-11 items-center justify-center rounded-xl bg-indigo-100 text-indigo-600">
                <i className="bi bi-file-earmark-text" />
              </div>
              <h3 className="text-lg font-bold">Crystal Clear Transcription</h3>
              <p className="mt-3 text-sm leading-6 text-slate-500">
                Capture every nuance with high accuracy. Handle complex accents,
                industry jargon, and multi-speaker environments with ease.
              </p>
            </div>

            <div className="rounded-2xl border border-slate-200 bg-white p-6">
              <div className="mb-4 flex h-11 w-11 items-center justify-center rounded-xl bg-sky-100 text-sky-600">
                <i className="bi bi-stars" />
              </div>
              <h3 className="text-lg font-bold">
                Deep Analysis & Summarization
              </h3>
              <p className="mt-3 text-sm leading-6 text-slate-500">
                Get automated summaries, sentiment analysis, and key takeaway
                extraction in seconds.
              </p>
            </div>

            <div className="rounded-2xl border border-slate-200 bg-white p-6">
              <div className="mb-4 flex h-11 w-11 items-center justify-center rounded-xl bg-slate-100 text-slate-600">
                <i className="bi bi-magic" />
              </div>
              <h3 className="text-lg font-bold">AI Editing Assistant</h3>
              <p className="mt-3 text-sm leading-6 text-slate-500">
                Transform spoken content into polished text. Clean filler words,
                improve clarity, and produce structured outputs.
              </p>
            </div>
          </div>
        </section>

        <section className="mt-8">
          <div className="rounded-[28px] bg-indigo-600 px-6 py-14 text-center text-white shadow-xl">
            <h2 className="text-3xl font-black leading-tight md:text-5xl">
              Ready to turn your audio into
              <br />
              your most valuable asset?
            </h2>

            <Link
              to="/login"
              className="mt-8 inline-block rounded-xl bg-white px-6 py-3 font-semibold text-indigo-600"
            >
              Create Your Free Account
            </Link>
          </div>
        </section>
      </div>
    </div>
  );
}
