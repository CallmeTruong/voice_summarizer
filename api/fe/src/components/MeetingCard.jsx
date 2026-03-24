import React from "react";

export default function MeetingCard({ item }) {
  return (
    <div className="flex flex-col gap-4 rounded-2xl border border-slate-200 bg-white p-6 shadow-sm lg:flex-row lg:items-start lg:justify-between">
      <div className="flex gap-4">
        <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl bg-indigo-100 text-indigo-600">
          <i className="bi bi-pause-fill text-lg" />
        </div>

        <div>
          <div className="flex flex-wrap items-center gap-3">
            <h3 className="text-2xl font-bold text-slate-900">{item.title}</h3>
            <span className="rounded-lg bg-sky-100 px-3 py-1 text-xs font-bold text-sky-600">
              {item.status}
            </span>
          </div>

          <p className="mt-2 text-slate-500">{item.desc}</p>

          <div className="mt-3 flex flex-wrap gap-5 text-sm text-slate-500">
            <span className="flex items-center gap-2">
              <i className="bi bi-calendar3" />
              {item.date}
            </span>
            <span className="flex items-center gap-2">
              <i className="bi bi-clock" />
              {item.time}
            </span>
            <span className="flex items-center gap-2">
              <i className="bi bi-people" />
              {item.participants} participants
            </span>
          </div>
        </div>
      </div>

      <button className="self-end rounded-xl p-2 text-slate-500 transition hover:bg-slate-100 lg:self-auto">
        <i className="bi bi-chevron-down" />
      </button>
    </div>
  );
}
