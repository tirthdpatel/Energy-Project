"use client";

import { useState, useRef } from "react";
import type { StateDetail, PowerPlantProperties } from "@/types";
import TrendChart from "./TrendChart";
import StateCompareModal from "./StateCompareModal";
import html2canvas from "html2canvas";
import jsPDF from "jspdf";

interface Props {
    state: StateDetail | null;
    plant?: PowerPlantProperties | null;
    loading: boolean;
    onClose: () => void;
    selectedYear?: number;
}

export default function StatePanel({ state, plant, loading, onClose, selectedYear }: Props) {
    const [isCompareOpen, setIsCompareOpen] = useState(false);
    const panelRef = useRef<HTMLDivElement>(null);

    const exportToPDF = async () => {
        if (!panelRef.current) return;
        try {
            const canvas = await html2canvas(panelRef.current, { scale: 2, useCORS: true, backgroundColor: "#161A22" });
            const imgData = canvas.toDataURL("image/png");
            const pdf = new jsPDF("p", "pt", "a4");
            const pdfWidth = pdf.internal.pageSize.getWidth();
            const pdfHeight = (canvas.height * pdfWidth) / canvas.width;
            pdf.addImage(imgData, "PNG", 0, 0, pdfWidth, pdfHeight);
            pdf.save(`India_Energy_Atlas_${state?.name.replaceAll(" ", "_")}.pdf`);
        } catch (error) {
            console.error("PDF Export failed:", error);
        }
    };

    if (!state && !plant && !loading) return null;

    /* Compute quick derived values */
    const totalGW = state ? (state.capacity.total_mw / 1000).toFixed(1) : "—";
    const renewablePct = state
        ? Math.round(
            ((state.mix.find((m) => m.source === "Solar")?.value ?? 0) +
                (state.mix.find((m) => m.source === "Wind")?.value ?? 0)) /
            Math.max(state.mix.reduce((a, m) => a + m.value, 0), 1) *
            100
        )
        : 0;

    return (
        <aside ref={panelRef} className="w-80 bg-[#161A22] border-l border-[#262C3A] flex flex-col no-scrollbar overflow-y-auto shrink-0">
            {/* Header */}
            <div className="p-4 border-b border-[#262C3A] flex items-center justify-between sticky top-0 bg-[#161A22] z-10">
                <div>
                    <h2 className="text-lg font-bold">
                        {loading ? "Loading…" : plant ? plant.name : state?.name}
                    </h2>
                    <p className="text-[10px] text-slate-400 uppercase tracking-widest font-medium">
                        {plant ? "Power Plant Overview" : "State Overview"}
                    </p>
                </div>
                <button
                    onClick={onClose}
                    className="p-1 hover:bg-[#262C3A] rounded transition-colors"
                    aria-label="Close panel"
                >
                    <span className="material-symbols-outlined text-xl">close</span>
                </button>
            </div>

            {loading ? (
                <div className="flex items-center justify-center h-64">
                    <div className="w-10 h-10 border-4 border-[#20d3ee] border-t-transparent rounded-full animate-spin" />
                </div>
            ) : plant ? (
                <div className="p-5 flex flex-col gap-5 h-full">
                    {/* Basic Info */}
                    <div className="bg-[#0F1115]/50 border border-[#262C3A] rounded-lg p-4 flex flex-col gap-3 shadow-md">
                        <div className="flex items-center justify-between">
                            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Primary Fuel</span>
                            <span className="px-2 py-0.5 rounded text-[11px] font-bold bg-[#262C3A] border border-slate-600 shadow-sm text-slate-200">
                                {plant.type ? plant.type.charAt(0).toUpperCase() + plant.type.slice(1) : "Unknown"}
                            </span>
                        </div>
                        <div className="h-px bg-slate-800/50 w-full" />
                        <div className="flex items-center justify-between">
                            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Capacity</span>
                            <span className="text-base font-bold text-[#20d3ee]">
                                {plant.capacity_mw > 0 ? `${plant.capacity_mw.toLocaleString()} MW` : "Unknown"}
                            </span>
                        </div>
                    </div>

                    {/* Operational Details */}
                    <div>
                        <h3 className="text-xs font-bold uppercase tracking-wider text-slate-300 mb-3 ml-1">
                            Operational Details
                        </h3>
                        <div className="bg-[#0F1115]/30 border border-[#262C3A] rounded-lg px-4 py-3 flex flex-col gap-4">
                            <div className="flex flex-col">
                                <span className="text-[10px] uppercase text-slate-500 font-semibold mb-1">Operator / Owner</span>
                                <span className="text-sm font-medium text-slate-200 leading-snug">
                                    {plant.operator || "Unknown"}
                                </span>
                            </div>
                            <div className="h-px bg-[#262C3A]" />
                            <div className="flex flex-col">
                                <span className="text-[10px] uppercase text-slate-500 font-semibold mb-1">Location</span>
                                <span className="text-sm font-medium text-slate-200 leading-snug">
                                    {plant.state || "Unknown"}
                                </span>
                            </div>
                        </div>
                    </div>

                    <a
                        href={`https://www.openstreetmap.org/${plant.osm_id}`}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="mt-6 flex items-center justify-center gap-2 py-2.5 bg-[#20d3ee]/10 hover:bg-[#20d3ee]/20 border border-[#20d3ee]/30 text-[#20d3ee] rounded-md transition-colors text-xs font-semibold"
                    >
                        <span>View Source on OpenStreetMap</span>
                        <span className="material-symbols-outlined text-[14px]">open_in_new</span>
                    </a>
                </div>
            ) : state ? (
                <div className="p-4 flex flex-col gap-4">
                    {/* ── Stat Grid ── */}
                    <div className="grid grid-cols-2 gap-3">
                        <StatBox label="Total Capacity" value={`${totalGW}`} unit="GW" highlight />
                        <StatBox
                            label="Generation"
                            value={state.generation.total_gwh.toLocaleString()}
                            unit="GWh"
                        />
                        <StatBox
                            label="Renewable %"
                            value={`${renewablePct}%`}
                            highlight
                        />
                        <StatBox
                            label="Capacity (MW)"
                            value={state.capacity.total_mw.toLocaleString()}
                            unit="MW"
                        />
                    </div>

                    {/* ── Generation Trend ── */}
                    <div className="mt-4">
                        <div className="flex items-center justify-between mb-3">
                            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-300">
                                Generation Trend
                            </h3>
                            <span className="text-[10px] text-[#20d3ee]">GWh / Year</span>
                        </div>
                        <div className="rounded-md border border-[#262C3A] bg-[#0F1115]/30 p-3">
                            <TrendChart data={state.trend} />
                        </div>
                    </div>

                    {/* ── Energy Mix Composition ── */}
                    <div className="mt-4">
                        <h3 className="text-xs font-bold uppercase tracking-wider text-slate-300 mb-3">
                            Energy Mix Composition
                        </h3>
                        <div className="flex items-center gap-6 p-4 border border-[#262C3A] rounded-md bg-[#0F1115]/30">
                            {/* Donut chart via SVG */}
                            <div className="relative w-20 h-20 shrink-0">
                                <svg className="w-full h-full -rotate-90" viewBox="0 0 36 36">
                                    <circle
                                        cx="18" cy="18" r="16"
                                        fill="transparent"
                                        stroke="#262C3A"
                                        strokeWidth={4}
                                    />
                                    {/* Solar + Wind slice */}
                                    <circle
                                        cx="18" cy="18" r="16"
                                        fill="transparent"
                                        stroke="#20d3ee"
                                        strokeWidth={4}
                                        strokeDasharray={`${renewablePct}, 100`}
                                    />
                                </svg>
                                <div className="absolute inset-0 flex items-center justify-center">
                                    <span className="text-[10px] font-bold">RE</span>
                                </div>
                            </div>

                            {/* Legend */}
                            <div className="flex flex-col gap-2 flex-1">
                                {state.mix.map((m) => {
                                    const color =
                                        m.source === "Solar" || m.source === "Wind"
                                            ? "bg-[#20d3ee]"
                                            : m.source === "Hydro"
                                                ? "bg-[#0e5663]"
                                                : "bg-[#262C3A]";
                                    const pct = Math.round(
                                        (m.value / state.mix.reduce((a, s) => a + s.value, 1)) * 100
                                    );
                                    return (
                                        <div key={m.source} className="flex items-center gap-2">
                                            <div className={`w-2 h-2 rounded-full ${color}`} />
                                            <div className="flex-1 flex justify-between text-[10px]">
                                                <span className="text-slate-400">{m.source}</span>
                                                <span className="font-bold">{pct}%</span>
                                            </div>
                                        </div>
                                    );
                                })}
                            </div>
                        </div>
                    </div>

                    {/* ── Recent Policy Changes (static placeholder) ── */}
                    <div className="mt-4 pb-6">
                        <h3 className="text-xs font-bold uppercase tracking-wider text-slate-300 mb-3">
                            Recent Policy Changes
                        </h3>
                        <div className="flex flex-col gap-3">
                            <div className="p-3 border-l-2 border-[#20d3ee] bg-[#0F1115]/50">
                                <p className="text-[11px] font-medium leading-tight">
                                    State Solar Policy Amendment 2024 published for public review.
                                </p>
                                <span className="text-[9px] text-slate-500 mt-1 block">2 DAYS AGO</span>
                            </div>
                            <div className="p-3 border-l-2 border-[#262C3A] bg-[#0F1115]/50">
                                <p className="text-[11px] font-medium leading-tight text-slate-400">
                                    PPA targets for distributed wind projects updated.
                                </p>
                                <span className="text-[9px] text-slate-500 mt-1 block">1 WEEK AGO</span>
                            </div>
                        </div>
                    </div>

                    {/* Download button */}
                    <div className="flex gap-2 mt-auto mb-4">
                        <button
                            onClick={() => setIsCompareOpen(true)}
                            className="flex-1 py-2 bg-slate-800 border border-[#262C3A] hover:border-slate-500 text-slate-300 text-xs font-bold rounded transition-all uppercase tracking-widest flex justify-center items-center gap-2"
                        >
                            <span className="material-symbols-outlined text-[16px]">compare_arrows</span>
                            Compare
                        </button>
                        <button
                            onClick={exportToPDF}
                            className="flex-1 py-2 bg-[#20d3ee]/10 border border-[#20d3ee]/40 text-[#20d3ee] text-xs font-bold rounded hover:bg-[#20d3ee]/20 transition-all uppercase tracking-widest flex justify-center items-center gap-2"
                        >
                            <span className="material-symbols-outlined text-[16px]">download</span>
                            Export
                        </button>
                    </div>
                </div>
            ) : null}

            {isCompareOpen && state && (
                <StateCompareModal
                    baseStateId={state.id}
                    baseStateName={state.name}
                    selectedYear={selectedYear}
                    onClose={() => setIsCompareOpen(false)}
                />
            )}
        </aside>
    );
}

/* ── Simple Stat Box ─── */
function StatBox({
    label,
    value,
    unit,
    highlight,
}: {
    label: string;
    value: string;
    unit?: string;
    highlight?: boolean;
}) {
    return (
        <div className="p-3 border border-[#262C3A] rounded-md bg-[#0F1115]/30">
            <p className="text-[10px] text-slate-400 uppercase font-semibold mb-1">{label}</p>
            <p className={`text-lg font-bold ${highlight ? "text-[#20d3ee]" : "text-slate-100"}`}>
                {value}
                {unit && (
                    <span className="text-xs font-normal ml-1 opacity-60">{unit}</span>
                )}
            </p>
        </div>
    );
}
