import React, { useEffect, useState } from "react";
import { NavLink, useNavigate } from "react-router-dom";

const navItemBase =
  "flex items-center gap-3 rounded-xl px-4 py-3 text-[15px] font-medium transition";
const navItemIdle = "text-slate-500 hover:bg-slate-100";
const navItemActive = "bg-indigo-50 text-[#5B4CF5]";

export default function AppSidebar() {
  const [recordingCount, setRecordingCount] = useState(0);
  const navigate = useNavigate();

  useEffect(() => {
    const loadCount = () => {
      const data = JSON.parse(localStorage.getItem("recordings") || "[]");
      setRecordingCount(data.length);
    };

    loadCount();
    window.addEventListener("recordings-updated", loadCount);

    return () => {
      window.removeEventListener("recordings-updated", loadCount);
    };
  }, []);

  const handleOpenAssistant = () => {
    try {
      const saved = JSON.parse(localStorage.getItem("recordings") || "[]");

      if (!saved.length) {
        window.__toast?.("Chưa có recording nào", "error");
        return;
      }

      const latest = saved[0];

      if (!latest?.recordingId) {
        window.__toast?.("Recording không hợp lệ", "error");
        return;
      }

      navigate(`/assistant/${latest.recordingId}`);
    } catch (err) {
      console.error(err);
      window.__toast?.("Không mở được assistant", "error");
    }
  };

  return (
    <aside className="hidden md:flex md:w-[250px] flex-col border-r border-slate-200 bg-[#f6f7fb]">
      <div className="p-5">
        <div className="mb-8 flex items-center gap-3 px-2">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-[#5B4CF5] text-white">
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
              `flex items-center justify-between rounded-xl px-4 py-3 text-[15px] font-medium transition ${
                isActive
                  ? "bg-indigo-50 text-[#5B4CF5]"
                  : "text-slate-500 hover:bg-slate-100"
              }`
            }
          >
            <div className="flex items-center gap-3">
              <i className="bi bi-collection" />
              <span>Library</span>
            </div>

            <span className="inline-flex h-6 min-w-[24px] items-center justify-center rounded-full bg-[#5B4CF5] px-2 text-xs font-bold text-white">
              {recordingCount}
            </span>
          </NavLink>

          <button
            onClick={handleOpenAssistant}
            className={`${navItemBase} ${navItemIdle} w-full text-left`}
          >
            <i className="bi bi-stars" />
            <span>AI Assistant</span>
          </button>
        </nav>
      </div>

      <div className="mt-auto border-t border-slate-200 p-4">
        <button className="flex w-full items-center gap-3 rounded-xl px-3 py-3 text-left hover:bg-slate-100">
          <div className="flex h-9 w-9 items-center justify-center rounded-full bg-[#5B4CF5] text-sm font-bold text-white">
            K
          </div>
          <span className="text-sm font-medium text-slate-700">Account</span>
        </button>
      </div>
    </aside>
  );
}
