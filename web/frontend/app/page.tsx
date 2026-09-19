"use client";

import { useState, useCallback, Suspense } from "react";
import dynamic from "next/dynamic";
import { AnimatePresence, motion } from "framer-motion";
import ErrorBoundary from "@/components/ErrorBoundary";
import SettingsDialog from "@/components/SettingsDialog";
import HelpDialog from "@/components/HelpDialog";
import StatePanel from "@/features/state-panel/StatePanel";
import { fetchStateDetail } from "@/lib/api";
import { useSettings } from "@/lib/settings";
import type { Destination, ProSection, ProTab, View } from "@/lib/navigation";
import type { StateDetail, PowerPlantProperties } from "@/types";

/* ── Lazy-loaded views ─── */
const IndiaMap = dynamic(() => import("@/features/map/IndiaMap"), { ssr: false });
const AnalyticsDashboard = dynamic(() => import("@/features/analytics/AnalyticsDashboard"), { ssr: false });
const SimpleView = dynamic(() => import("@/features/analytics/SimpleView"), { ssr: false });
const DatasetsView = dynamic(() => import("@/features/datasets/DatasetsView"), { ssr: false });

const Spinner = (
  <div className="flex items-center justify-center h-full">
    <div className="w-10 h-10 border-4 border-[#20d3ee] border-t-transparent rounded-full animate-spin" />
  </div>
);

interface ShellState {
  view: View;
  layersOpen: boolean;
}

/* ── Left icon rail ───
 * Each icon has its own destination. Previously Dashboard and Layers both
 * opened the map, and Analytics and Database both opened Pro, so half the rail
 * did nothing once you were on the matching view. Highlighting is derived from
 * where the app actually is rather than tracked as a separate index.
 */
const RAIL: {
  icon: string;
  title: string;
  to: (s: ShellState) => Destination;
  isActive: (s: ShellState) => boolean;
}[] = [
    {
      icon: "dashboard",
      title: "Map",
      to: () => ({ view: "map", layers: false }),
      isActive: (s) => s.view === "map" && !s.layersOpen,
    },
    {
      icon: "layers",
      title: "Layers — power plant filters",
      // Toggles the panel when already open, like any panel button.
      to: (s) => ({ view: "map", layers: !(s.view === "map" && s.layersOpen) }),
      isActive: (s) => s.view === "map" && s.layersOpen,
    },
    {
      icon: "analytics",
      title: "Pro analytics",
      to: () => ({ view: "pro", proTab: "overview" }),
      isActive: (s) => s.view === "pro",
    },
    {
      icon: "description",
      title: "Sector reports",
      to: () => ({ view: "simple" }),
      isActive: (s) => s.view === "simple",
    },
    {
      icon: "database",
      title: "Datasets",
      to: () => ({ view: "datasets" }),
      isActive: (s) => s.view === "datasets",
    },
  ];

const TOOLBAR: { view: View; label: string }[] = [
  { view: "map", label: "Map" },
  { view: "simple", label: "Simple" },
  { view: "pro", label: "Pro" },
];

export default function HomePage() {
  const settings = useSettings();

  // The start view and year come from settings until the user picks their own.
  const [chosenView, setChosenView] = useState<View | null>(null);
  const [chosenYear, setChosenYear] = useState<number | null>(null);
  const view = chosenView ?? settings.startView;
  const selectedYear = chosenYear ?? settings.startYear;

  const [layersOpen, setLayersOpen] = useState(false);
  const [proTab, setProTab] = useState<ProTab>("overview");
  const [proSection, setProSection] = useState<{ id: ProSection; nonce: number } | null>(null);
  const [dialog, setDialog] = useState<"settings" | "help" | null>(null);

  const [selectedState, setSelectedState] = useState<StateDetail | null>(null);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [selectedPlant, setSelectedPlant] = useState<PowerPlantProperties | null>(null);
  const [loading, setLoading] = useState(false);

  const navigate = useCallback((to: Destination) => {
    setChosenView(to.view);
    if (to.proTab) setProTab(to.proTab);
    // A fresh nonce re-runs the scroll even when the same section is clicked again.
    if (to.section) setProSection({ id: to.section, nonce: Date.now() });
    if (to.layers !== undefined) setLayersOpen(to.layers);
  }, []);

  const openDialog = (which: "settings" | "help") => {
    // Pin the current view and year, so editing the start view or year in
    // Settings doesn't yank the page you're looking at.
    setChosenView(view);
    setChosenYear(selectedYear);
    setDialog(which);
  };

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
    setChosenView("map");
  }, []);

  const handleClose = useCallback(() => {
    setSelectedState(null);
    setSelectedId(null);
    setSelectedPlant(null);
  }, []);

  const shell: ShellState = { view, layersOpen };
  const transition = { duration: settings.reduceMotion ? 0 : 0.3 };
  const slide = settings.reduceMotion
    ? { initial: { opacity: 1, x: 0 }, animate: { opacity: 1, x: 0 }, exit: { opacity: 0, x: 0 } }
    : { initial: { opacity: 0, x: -20 }, animate: { opacity: 1, x: 0 }, exit: { opacity: 0, x: 20 } };

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

          {/* Right: View Tabs + Settings */}
          <div className="flex items-center gap-3">
            <div className="flex bg-[#0F1115] border border-[#262C3A] p-1 rounded">
              {TOOLBAR.map((t) => (
                <button
                  key={t.view}
                  onClick={() => navigate({ view: t.view })}
                  aria-current={view === t.view ? "page" : undefined}
                  className={`px-4 py-1 text-xs font-medium rounded-sm transition-all ${view === t.view
                    ? "bg-[#262C3A] text-white"
                    : "text-slate-400 hover:text-[#20d3ee]"
                    }`}
                >
                  {t.label}
                </button>
              ))}
            </div>
            <div className="h-8 w-px bg-[#262C3A] mx-1" />
            <button
              onClick={() => openDialog("settings")}
              title="Settings"
              aria-label="Settings"
              className="text-slate-400 hover:text-white transition-colors"
            >
              <span className="material-symbols-outlined">settings</span>
            </button>
          </div>
        </header>

        {/* ── Body: Sidebar + Content ── */}
        <div className="flex-1 flex overflow-hidden">
          {/* Left Icon Sidebar — always visible */}
          <aside className="w-16 flex flex-col items-center py-4 gap-4 bg-[#161A22] border-r border-[#262C3A] shrink-0">
            <div className="flex flex-col gap-1 w-full">
              {RAIL.map((item) => {
                const active = item.isActive(shell);
                return (
                  <button
                    key={item.icon}
                    onClick={() => navigate(item.to(shell))}
                    title={item.title}
                    aria-label={item.title}
                    aria-current={active ? "page" : undefined}
                    className={`w-full h-12 flex items-center justify-center transition-colors ${active
                      ? "sidebar-active text-[#20d3ee]"
                      : "text-slate-400 hover:text-white"
                      }`}
                  >
                    <span className="material-symbols-outlined">{item.icon}</span>
                  </button>
                );
              })}
            </div>
            <div className="mt-auto flex flex-col gap-4">
              <button
                onClick={() => openDialog("help")}
                title="Help"
                aria-label="Help"
                className="text-slate-400 hover:text-white transition-colors"
              >
                <span className="material-symbols-outlined">help</span>
              </button>
            </div>
          </aside>

          {/* Main Content Area */}
          <div className="flex-1 relative overflow-hidden">
            <Suspense fallback={Spinner}>
              {/* Not mode="wait": the outgoing view owns heavy resources (the
                  MapLibre canvas), and when its teardown interrupts the exit
                  animation the completion callback never fires, so "wait" would
                  block the incoming view from ever mounting. Each view is
                  absolutely positioned, so cross-fading them is safe. */}
              <AnimatePresence>
                {/* Map View */}
                {view === "map" && (
                  <motion.div key="map" {...slide} transition={transition} className="absolute inset-0 flex h-full">
                    <div className="flex-1 relative bg-[#0B0D11]">
                      <IndiaMap
                        onStateSelect={handleStateSelect}
                        onPlantSelect={handlePlantSelect}
                        selectedStateId={selectedId}
                        selectedYear={selectedYear}
                        onYearChange={setChosenYear}
                        filtersVisible={layersOpen}
                        onFiltersVisibleChange={setLayersOpen}
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
                  <motion.div key="simple" {...slide} transition={transition} className="absolute inset-0 h-full overflow-y-auto">
                    <SimpleView />
                  </motion.div>
                )}

                {/* Pro View */}
                {view === "pro" && (
                  <motion.div key="pro" {...slide} transition={transition} className="absolute inset-0 h-full overflow-y-auto">
                    <AnalyticsDashboard
                      onNavigate={navigate}
                      onStateClick={(id) => handleStateSelect(id)}
                      tab={proTab}
                      onTabChange={setProTab}
                      section={proSection}
                    />
                  </motion.div>
                )}

                {/* Datasets View */}
                {view === "datasets" && (
                  <motion.div key="datasets" {...slide} transition={transition} className="absolute inset-0 h-full">
                    <DatasetsView />
                  </motion.div>
                )}
              </AnimatePresence>
            </Suspense>
          </div>
        </div>
      </div>

      <SettingsDialog open={dialog === "settings"} onClose={() => setDialog(null)} />
      <HelpDialog open={dialog === "help"} onClose={() => setDialog(null)} onNavigate={navigate} />
    </ErrorBoundary>
  );
}
