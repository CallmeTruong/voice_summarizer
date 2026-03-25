import React, { useEffect, useState } from "react";
import AppSidebar from "../components/AppSidebar";
import AppTopbar from "../components/AppTopbar";
import UserMenu from "../components/UserMenu";
import MeetingCard from "../components/MeetingCard";
import { recordings as mockRecordings } from "../data/mockData";

export default function LibraryPage() {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    try {
      setItems(mockRecordings);
    } catch (err) {
      console.error(err);
      setError("Failed to load recordings");
    } finally {
      setLoading(false);
    }
  }, []);

  return (
    <div className="min-h-screen bg-[#f6f7fb] md:grid md:grid-cols-[250px_1fr]">
      <AppSidebar />

      <main className="p-4 md:p-7">
        <div className="mb-6 flex items-center justify-between gap-4">
          <div>
            <h1 className="text-3xl font-extrabold text-slate-900 md:text-4xl">
              Library
            </h1>
            <p className="mt-2 text-slate-500">
              Your collection of recorded meetings and insights.
            </p>
          </div>

          <UserMenu />
        </div>

        {loading ? (
          <div className="mt-6 text-sm text-slate-500">Loading...</div>
        ) : error ? (
          <div className="mt-6 rounded-2xl bg-red-50 p-6 text-sm text-red-600 shadow">
            {error}
          </div>
        ) : items.length === 0 ? (
          <div className="mt-6 rounded-2xl bg-white p-6 text-sm text-slate-500 shadow">
            No recordings yet.
          </div>
        ) : (
          <div className="space-y-5">
            {items.map((item) => (
              <MeetingCard key={item.id} item={item} />
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
