import React from "react";
import AppSidebar from "../components/AppSidebar";
import AppTopbar from "../components/AppTopbar";
import MeetingCard from "../components/MeetingCard";
import { recordings } from "../data/mockData";

export default function LibraryPage() {
  return (
    <div className="min-h-screen bg-[#f6f7fb] md:grid md:grid-cols-[250px_1fr]">
      <AppSidebar />

      <main className="p-4 md:p-7">
        <AppTopbar
          title="Library"
          subtitle="Browse your recorded conversations and transcripts"
        />

        <div className="mb-6 grid overflow-hidden rounded-2xl border border-slate-200 bg-white md:grid-cols-3">
          <div className="border-b border-slate-200 p-6 md:border-b-0 md:border-r">
            <div className="text-xs font-extrabold tracking-[0.12em] text-slate-500">
              TOTAL RECORDINGS
            </div>
            <div className="mt-2 text-4xl font-black text-slate-900">5</div>
          </div>
          <div className="border-b border-slate-200 p-6 md:border-b-0 md:border-r">
            <div className="text-xs font-extrabold tracking-[0.12em] text-slate-500">
              TOTAL DURATION
            </div>
            <div className="mt-2 text-4xl font-black text-slate-900">
              2h 20m
            </div>
          </div>
          <div className="p-6">
            <div className="text-xs font-extrabold tracking-[0.12em] text-slate-500">
              THIS WEEK
            </div>
            <div className="mt-2 text-4xl font-black text-slate-900">3</div>
          </div>
        </div>

        <div className="space-y-5">
          {recordings.map((item) => (
            <MeetingCard key={item.id} item={item} />
          ))}
        </div>
      </main>
    </div>
  );
}
