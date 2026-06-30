"use client";

import { useState, useCallback, Suspense, useEffect } from "react";
import dynamic from "next/dynamic";
import { AnimatePresence, motion } from "framer-motion";
import ErrorBoundary from "@/components/ErrorBoundary";
import StatePanel from "@/features/state-panel/StatePanel";
import { fetchStateDetail } from "@/lib/api";
import type { StateDetail, PowerPlantProperties } from "@/types";

/* ── Lazy-loaded views ─── */
const IndiaMap = dynamic(() => import("@/features/map/IndiaMap"), { ssr: false });
const AnalyticsDashboard = dynamic(() => import("@/features/analytics/AnalyticsDashboard"), { ssr: false });
const SimpleView = dynamic(() => import("@/features/analytics/SimpleView"), { ssr: false });

const Spinner = (
  <div className="flex items-center justify-center h-full">
    <div className="w-10 h-10 border-4 border-[#20d3ee] border-t-transparent rounded-full animate-spin" />
  </div>
);

type View = "map" | "simple" | "pro";

/* ── Left Icon Sidebar items ─── */
const SIDEBAR_ICONS: { icon: string; title: string; view: View }[] = [
  { icon: "dashboard", title: "Dashboard", view: "map" },
  { icon: "layers", title: "Layers", view: "map" },
  { icon: "analytics", title: "Analytics", view: "pro" },
  { icon: "description", title: "Reports", view: "simple" },
  { icon: "database", title: "Database", view: "pro" },
];

export default function HomePage() {
  const [view, setView] = useState<View>("map");
  const [selectedYear, setSelectedYear] = useState(2026);
  const [selectedState, setSelectedState] = useState<StateDetail | null>(null);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [selectedPlant, setSelectedPlant] = useState<PowerPlantProperties | null>(null);
  const [loading, setLoading] = useState(false);
  const [activeSidebar, setActiveSidebar] = useState(0);

  // Sync sidebar highlight with view selection
  useEffect(() => {
    const currentIcon = SIDEBAR_ICONS[activeSidebar];
    if (currentIcon && currentIcon.view !== view) {
      const matchingIdx = SIDEBAR_ICONS.findIndex((item) => item.view === view);
      if (matchingIdx !== -1) {
        setActiveSidebar(matchingIdx);
      }
    }
  }, [view, activeSidebar]);

  const handleStateSelect = useCallback(
    async (stateId: string) => {
      setSelectedId(stateId);
      setSelectedPlant(null);
      setLoading(true);
      try {
        const data = await fetchStateDetail(stateId);
        setSelectedState(data);
      } catch (err) {
        console.error("Failed to load state data:", err);
        setSelectedState(null);
      } finally {
        setLoading(false);
      }
    },
    []
  );

  const handlePlantSelect = useCallback((plant: PowerPlantProperties) => {
    setSelectedPlant(plant);
    setView("map");
  }, []);

  const handleClose = useCallback(() => {
    setSelectedState(null);
    setSelectedId(null);
    setSelectedPlant(null);
  }, []);

  return (
    <ErrorBoundary>
      <div className="flex flex-col h-screen overflow-hidden bg-[#0F1115] text-slate-100">
        {/* ── Top Header ── */}
        <header className="h-14 border-b border-[#262C3A] flex items-center justify-between px-4 bg-[#161A22] z-50 shrink-0">
          {/* Logo */}
          <div className="flex items-center gap-3">
            <div className="text-[#20d3ee]">
              <span className="material-symbols-outlined text-3xl">energy_program_saving</span>
            </div>
            <h1 className="text-lg font-bold tracking-tight">
              INDIA ENERGY <span className="text-[#20d3ee]">ATLAS</span>
            </h1>
          </div>

          {/* Right: View Tabs + Settings + Avatar */}
          <div className="flex items-center gap-3">
            <div className="flex bg-[#0F1115] border border-[#262C3A] p-1 rounded">
              {(["map", "simple", "pro"] as View[]).map((v) => (
                <button
                  key={v}
                  onClick={() => setView(v)}
                  className={`px-4 py-1 text-xs font-medium rounded-sm transition-all capitalize ${view === v
                    ? "bg-[#262C3A] text-white"
                    : "text-slate-400 hover:text-[#20d3ee]"
                    }`}
                >
                  {v === "pro" ? "Pro" : v === "simple" ? "Simple" : "Map"}
                </button>
              ))}
            </div>
            <div className="h-8 w-px bg-[#262C3A] mx-1" />
            <button className="text-slate-400 hover:text-white transition-colors">
              <span className="material-symbols-outlined">settings</span>
            </button>
            <div className="w-8 h-8 rounded-full bg-[#20d3ee]/20 border border-[#20d3ee]/40 flex items-center justify-center text-[#20d3ee] text-xs font-bold">
              OP
            </div>
          </div>
        </header>

        {/* ── Body: Sidebar + Content ── */}
        <div className="flex-1 flex overflow-hidden">
          {/* Left Icon Sidebar — always visible */}
          <aside className="w-16 flex flex-col items-center py-4 gap-4 bg-[#161A22] border-r border-[#262C3A] shrink-0">
            <div className="flex flex-col gap-1 w-full">
              {SIDEBAR_ICONS.map((item, idx) => (
                <button
                  key={item.icon}
                  onClick={() => {
                    setActiveSidebar(idx);
                    setView(item.view);
                  }}
                  title={item.title}
                  className={`w-full h-12 flex items-center justify-center transition-colors ${activeSidebar === idx
                    ? "sidebar-active text-[#20d3ee]"
                    : "text-slate-400 hover:text-white"
                    }`}
                >
                  <span className="material-symbols-outlined">{item.icon}</span>
                </button>
              ))}
            </div>
            <div className="mt-auto flex flex-col gap-4">
              <button className="text-slate-400 hover:text-white" title="Help">
                <span className="material-symbols-outlined">help</span>
              </button>
              <button className="text-slate-400 hover:text-white" title="Logout">
                <span className="material-symbols-outlined">logout</span>
              </button>
            </div>
          </aside>

          {/* Main Content Area — removed duplicate 'relative' */}
          <div className="flex-1 relative overflow-hidden">
            <Suspense fallback={Spinner}>
              <AnimatePresence mode="wait">
                {/* Map View */}
                {view === "map" && (
                  <motion.div
                    key="map"
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: 20 }}
                    transition={{ duration: 0.3 }}
                    className="absolute inset-0 flex h-full"
                  >
                    <div className="flex-1 relative bg-[#0B0D11]">
                      <IndiaMap
                        onStateSelect={handleStateSelect}
                        onPlantSelect={handlePlantSelect}
                        selectedStateId={selectedId}
                        selectedYear={selectedYear}
                        onYearChange={setSelectedYear}
                      />
                    </div>
                    <StatePanel
                      state={selectedState}
                      plant={selectedPlant}
                      loading={loading}
                      onClose={handleClose}
                      selectedYear={selectedYear}
                    />
                  </motion.div>
                )}

                {/* Simple View */}
                {view === "simple" && (
                  <motion.div
                    key="simple"
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: 20 }}
                    transition={{ duration: 0.3 }}
                    className="absolute inset-0 h-full overflow-y-auto"
                  >
                    <SimpleView />
                  </motion.div>
                )}

                {/* Pro View */}
                {view === "pro" && (
                  <motion.div
                    key="pro"
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: 20 }}
                    transition={{ duration: 0.3 }}
                    className="absolute inset-0 h-full overflow-y-auto"
                  >
                    <AnalyticsDashboard onNavigate={setView} onStateClick={(id) => handleStateSelect(id)} />
                  </motion.div>
                )}
              </AnimatePresence>
            </Suspense>
          </div>
        </div>
      </div>
    </ErrorBoundary>
  );
}
