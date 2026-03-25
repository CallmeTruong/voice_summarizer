import React from "react";
import { NavLink } from "react-router-dom";

const navItemBase =
  "flex items-center gap-3 rounded-xl px-4 py-3 text-[15px] font-medium transition";
const navItemIdle = "text-slate-500 hover:bg-slate-100";
const navItemActive = "bg-indigo-50 text-indigo-600";

export default function AppSidebar() {
  return (
    <aside className="hidden md:flex md:w-[250px] flex-col justify-between border-r border-slate-200 bg-white p-5">
      <div>
        <div className="mb-8 flex items-center gap-3 px-2">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-indigo-600 text-white">
            <i className="bi bi-record-circle text-lg" />
          </div>
          <div>
            <div className="font-extrabold text-slate-800">The Archivist</div>
            <div className="text-[11px] font-semibold tracking-wide text-slate-400">
              INTELLIGENCE ENGINE
            </div>
          </div>
        </div>

        <nav className="space-y-2">
          <NavLink
            to="/dashboard"
            className={({ isActive }) =>
              `${navItemBase} ${isActive ? navItemActive : navItemIdle}`
            }
          >
            <i className="bi bi-grid" />
            <span>Dashboard</span>
          </NavLink>

          <NavLink
            to="/library"
            className={({ isActive }) =>
              `${navItemBase} ${isActive ? navItemActive : navItemIdle}`
            }
          >
            <i className="bi bi-collection-play" />
            <span>Library</span>
          </NavLink>

          <NavLink
            to="/assistant"
            className={({ isActive }) =>
              `${navItemBase} ${isActive ? navItemActive : navItemIdle}`
            }
          >
            <i className="bi bi-stars" />
            <span>AI Assistant</span>
          </NavLink>
        </nav>
      </div>

      <div className="space-y-2">
        <a href="#" className={`${navItemBase} ${navItemIdle}`}>
          <i className="bi bi-question-circle" />
          <span>Support</span>
        </a>
      </div>
    </aside>
  );
}
