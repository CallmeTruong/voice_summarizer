import React from "react";
import AppSidebar from "../components/AppSidebar";
import { messages } from "../data/mockData";

export default function AssistantPage() {
  return (
    <div className="min-h-screen bg-[#f6f7fb] md:grid md:grid-cols-[250px_1fr]">
      <AppSidebar />

      <main className="grid min-h-screen lg:grid-cols-[1.2fr_420px]">
        <section className="flex flex-col border-r border-slate-200 bg-[#fbfcff] p-4 md:p-6">
          <div className="border-b border-slate-200 pb-4">
            <div className="flex items-center gap-3">
              <button className="rounded-xl p-2 text-slate-500 hover:bg-slate-100">
                <i className="bi bi-arrow-left" />
              </button>
              <div>
                <h2 className="text-lg font-bold text-slate-900">Meeting</h2>
                <p className="text-sm text-slate-500">
                  Recorded Oct 24, 2024 • 42:15
                </p>
              </div>
            </div>
          </div>

          <div className="flex-1 overflow-auto py-6">
            <div className="mb-6 text-center text-[11px] font-extrabold tracking-[0.18em] text-slate-400">
              START OF CONVERSATION
            </div>

            <div className="space-y-5">
              {messages.map((msg) => (
                <div
                  key={msg.id}
                  className={`flex gap-3 ${
                    msg.side === "right" ? "justify-end" : "justify-start"
                  }`}
                >
                  {msg.side === "left" && (
                    <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-indigo-100 text-xs font-bold text-indigo-600">
                      SA
                    </div>
                  )}

                  <div
                    className={`max-w-[560px] rounded-2xl border p-4 ${
                      msg.side === "right"
                        ? "border-indigo-100 bg-indigo-50"
                        : "border-slate-200 bg-white"
                    }`}
                  >
                    <div className="mb-2 flex items-center gap-2">
                      <strong className="text-sm text-slate-900">
                        {msg.speaker}
                      </strong>
                      <span className="text-xs text-slate-400">{msg.time}</span>
                    </div>
                    <p className="leading-7 text-slate-600">{msg.text}</p>

                    {msg.tag && (
                      <span className="mt-3 inline-block rounded-md bg-teal-500 px-2 py-1 text-[10px] font-extrabold text-white">
                        {msg.tag}
                      </span>
                    )}
                  </div>

                  {msg.side === "right" && (
                    <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-indigo-100 text-xs font-bold text-indigo-600">
                      SB
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>

          <div className="flex items-center gap-4 pt-3">
            <button className="flex h-11 w-11 items-center justify-center rounded-xl bg-indigo-600 text-white shadow">
              <i className="bi bi-play-fill" />
            </button>
            <div className="h-1.5 flex-1 rounded-full bg-slate-200">
              <div className="h-1.5 w-[42%] rounded-full bg-indigo-600" />
            </div>
          </div>
        </section>

        <aside className="flex flex-col bg-white p-5">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-bold text-slate-900">AI Assistant</h3>
            <button className="text-slate-400">
              <i className="bi bi-x-lg" />
            </button>
          </div>

          <div className="mt-6">
            <div className="mb-3 text-[11px] font-extrabold tracking-[0.15em] text-slate-400">
              SUGGESTIONS
            </div>

            <div className="space-y-2">
              <button className="w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-left text-sm hover:bg-slate-100">
                Summarize this call
              </button>
              <button className="w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-left text-sm hover:bg-slate-100">
                Highlight action items
              </button>
            </div>
          </div>

          <div className="mt-6 flex-1 space-y-4 overflow-auto">
            <div className="max-w-[90%] rounded-2xl bg-indigo-50 p-4 text-sm leading-6 text-slate-600">
              I have analyzed the conversation. Here are the key themes:
              <ul className="mt-2 list-disc pl-5">
                <li>Q3 audio processing improvements</li>
                <li>Rollout of The Archivist feature</li>
                <li>Contrast ratio accessibility audit</li>
              </ul>
            </div>

            <div className="ml-auto max-w-[86%] rounded-2xl bg-slate-100 p-4 text-sm text-slate-700">
              Can you extract the specific deadline mentioned for the design
              summary?
            </div>

            <div className="text-sm text-slate-400">
              Analyzing transcript...
            </div>
          </div>

          <div className="mt-4 flex gap-3">
            <input
              type="text"
              placeholder="Ask anything about the call..."
              className="h-12 flex-1 rounded-xl border border-slate-200 px-4 outline-none"
            />
            <button className="flex h-12 w-12 items-center justify-center rounded-xl bg-indigo-600 text-white">
              <i className="bi bi-send-fill" />
            </button>
          </div>
        </aside>
      </main>
    </div>
  );
}
