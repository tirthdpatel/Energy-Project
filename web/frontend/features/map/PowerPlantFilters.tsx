"use client";

import { useState, useEffect, useCallback } from "react";
import { fetchPowerPlantStats } from "@/lib/api";
import type { PowerPlantFilterStats, PowerPlantFilters } from "@/types";

/** Color map for energy types */
const TYPE_COLORS: Record<string, string> = {
    coal: "#ef4444",
    solar: "#eab308",
    hydro: "#3b82f6",
    wind: "#22c55e",
    nuclear: "#a855f7",
    gas: "#f97316",
    biomass: "#84cc16",
    other: "#94a3b8",
    unknown: "#64748b",
};

interface Props {
    filters: PowerPlantFilters;
    onFiltersChange: (filters: PowerPlantFilters) => void;
    plantCount: number;
    visible: boolean;
    onToggleVisible: () => void;
}

export default function PowerPlantFilterPanel({
    filters,
    onFiltersChange,
    plantCount,
    visible,
    onToggleVisible,
}: Props) {
    const [stats, setStats] = useState<PowerPlantFilterStats | null>(null);
    const [stateSearch, setStateSearch] = useState("");
    const [showStateDropdown, setShowStateDropdown] = useState(false);

    useEffect(() => {
        fetchPowerPlantStats()
            .then(setStats)
            .catch((err) => console.error("Failed to load power-plant stats:", err));
    }, []);

    const toggleType = useCallback(
        (type: string) => {
            const next = filters.types.includes(type)
                ? filters.types.filter((t) => t !== type)
                : [...filters.types, type];
            onFiltersChange({ ...filters, types: next });
        },
        [filters, onFiltersChange]
    );

    const toggleState = useCallback(
        (state: string) => {
            const next = filters.states.includes(state)
                ? filters.states.filter((s) => s !== state)
                : [...filters.states, state];
            onFiltersChange({ ...filters, states: next });
        },
        [filters, onFiltersChange]
    );

    const resetFilters = useCallback(() => {
        onFiltersChange({ states: [], types: [], minCapacity: 0 });
    }, [onFiltersChange]);

    const selectAllTypes = useCallback(() => {
        if (!stats) return;
        onFiltersChange({ ...filters, types: [...stats.types] });
    }, [filters, onFiltersChange, stats]);

    const selectNoTypes = useCallback(() => {
        onFiltersChange({ ...filters, types: [] });
    }, [filters, onFiltersChange]);

    const selectAllStates = useCallback(() => {
        if (!stats) return;
        onFiltersChange({ ...filters, states: [...stats.states] });
    }, [filters, onFiltersChange, stats]);

    const selectNoStates = useCallback(() => {
        onFiltersChange({ ...filters, states: [] });
    }, [filters, onFiltersChange]);

    if (!stats) return null;

    const filteredStates = stats.states.filter((s) =>
        s.toLowerCase().includes(stateSearch.toLowerCase())
    );

    const hasFilters =
        filters.states.length > 0 ||
        filters.types.length > 0 ||
        filters.minCapacity > 0;

    return (
        <div className="absolute top-16 right-3 z-40 flex flex-col items-end gap-2">
            {/* Toggle button */}
            <button
                onClick={onToggleVisible}
                className="flex items-center gap-2 px-3 py-2 rounded-lg
                           bg-slate-900/80 backdrop-blur-md border border-slate-700/50
                           text-slate-200 text-sm font-medium
                           hover:bg-slate-800/90 transition-colors shadow-lg"
            >
                <svg
                    className="w-4 h-4"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                    strokeWidth={2}
                >
                    <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        d="M12 3c2.755 0 5.455.232 8.083.678.533.09.917.556.917 1.096v1.044a2.25 2.25 0 01-.659 1.591l-5.432 5.432a2.25 2.25 0 00-.659 1.591v2.927a2.25 2.25 0 01-1.244 2.013L9.75 21v-6.568a2.25 2.25 0 00-.659-1.591L3.659 7.409A2.25 2.25 0 013 5.818V4.774c0-.54.384-1.006.917-1.096A48.32 48.32 0 0112 3z"
                    />
                </svg>
                Filters
                <span className="px-1.5 py-0.5 rounded-full bg-cyan-500/20 text-cyan-300 text-xs font-semibold">
                    {plantCount}
                </span>
                {hasFilters && (
                    <span className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse" />
                )}
            </button>

            {/* Filter panel */}
            {visible && (
                <div
                    className="w-80 rounded-xl bg-slate-900/90 backdrop-blur-xl
                                border border-slate-700/50 shadow-2xl overflow-hidden"
                >
                    {/* Header */}
                    <div className="px-4 py-3 border-b border-slate-700/50 flex items-center justify-between">
                        <h3 className="text-sm font-semibold text-slate-200">
                            Power Plant Filters
                        </h3>
                        {hasFilters && (
                            <button
                                onClick={resetFilters}
                                className="text-xs text-cyan-400 hover:text-cyan-300 transition-colors"
                            >
                                Reset all
                            </button>
                        )}
                    </div>

                    <div className="p-4 space-y-4 max-h-[60vh] overflow-y-auto custom-scrollbar">
                        {/* Energy Type */}
                        <div>
                            <div className="flex items-center justify-between mb-2">
                                <label className="text-xs font-medium text-slate-400 uppercase tracking-wider">
                                    Energy Type
                                    {filters.types.length === 0 && (
                                        <span className="ml-1.5 normal-case tracking-normal text-slate-500">· all shown</span>
                                    )}
                                </label>
                                <div className="flex gap-1.5">
                                    <button
                                        onClick={selectAllTypes}
                                        className="text-[10px] px-1.5 py-0.5 rounded bg-slate-800/60 text-cyan-400 hover:bg-slate-700/60 transition-colors"
                                    >
                                        All
                                    </button>
                                    <button
                                        onClick={selectNoTypes}
                                        className="text-[10px] px-1.5 py-0.5 rounded bg-slate-800/60 text-slate-400 hover:bg-slate-700/60 transition-colors"
                                    >
                                        Clear
                                    </button>
                                </div>
                            </div>
                            <div className="grid grid-cols-2 gap-1.5">
                                {stats.types.map((type) => {
                                    const active = filters.types.includes(type);
                                    const color =
                                        TYPE_COLORS[type] || TYPE_COLORS.other;
                                    return (
                                        <button
                                            key={type}
                                            onClick={() => toggleType(type)}
                                            className={`flex items-center gap-2 px-2.5 py-1.5 rounded-lg text-xs font-medium transition-all ${active
                                                ? "bg-slate-700/80 text-white ring-1 ring-cyan-500/50"
                                                : "bg-slate-800/50 text-slate-400 hover:bg-slate-700/50 hover:text-slate-300"
                                                }`}
                                        >
                                            <span
                                                className="w-2.5 h-2.5 rounded-full flex-shrink-0"
                                                style={{
                                                    backgroundColor: color,
                                                    opacity: active ? 1 : 0.5,
                                                }}
                                            />
                                            {type.charAt(0).toUpperCase() +
                                                type.slice(1)}
                                        </button>
                                    );
                                })}
                            </div>
                        </div>

                        {/* State Filter */}
                        <div>
                            <div className="flex items-center justify-between mb-2">
                                <label className="text-xs font-medium text-slate-400 uppercase tracking-wider">
                                    State
                                    {filters.states.length === 0 && (
                                        <span className="ml-1.5 normal-case tracking-normal text-slate-500">· all shown</span>
                                    )}
                                    {filters.states.length > 0 && (
                                        <span className="ml-2 text-cyan-400 normal-case">
                                            ({filters.states.length} selected)
                                        </span>
                                    )}
                                </label>
                                <div className="flex gap-1.5">
                                    <button
                                        onClick={selectAllStates}
                                        className="text-[10px] px-1.5 py-0.5 rounded bg-slate-800/60 text-cyan-400 hover:bg-slate-700/60 transition-colors"
                                    >
                                        All
                                    </button>
                                    <button
                                        onClick={selectNoStates}
                                        className="text-[10px] px-1.5 py-0.5 rounded bg-slate-800/60 text-slate-400 hover:bg-slate-700/60 transition-colors"
                                    >
                                        Clear
                                    </button>
                                </div>
                            </div>
                            <div className="relative">
                                <input
                                    type="text"
                                    placeholder="Search states..."
                                    value={stateSearch}
                                    onChange={(e) => setStateSearch(e.target.value)}
                                    onFocus={() => setShowStateDropdown(true)}
                                    className="w-full px-3 py-2 rounded-lg bg-slate-800/60 border border-slate-700/50
                                               text-sm text-slate-200 placeholder-slate-500
                                               focus:outline-none focus:ring-1 focus:ring-cyan-500/50"
                                />
                                {showStateDropdown && (
                                    <div className="absolute top-full left-0 right-0 mt-1 max-h-40 overflow-y-auto
                                                    rounded-lg bg-slate-800 border border-slate-700/50 shadow-xl z-30
                                                    custom-scrollbar">
                                        {filteredStates.map((state) => {
                                            const active =
                                                filters.states.includes(state);
                                            return (
                                                <button
                                                    key={state}
                                                    onClick={() =>
                                                        toggleState(state)
                                                    }
                                                    className={`w-full text-left px-3 py-1.5 text-xs transition-colors ${active
                                                        ? "bg-cyan-500/10 text-cyan-300"
                                                        : "text-slate-300 hover:bg-slate-700/50"
                                                        }`}
                                                >
                                                    {active ? "✓ " : "  "}
                                                    {state}
                                                </button>
                                            );
                                        })}
                                        {filteredStates.length === 0 && (
                                            <div className="px-3 py-2 text-xs text-slate-500">
                                                No matching states
                                            </div>
                                        )}
                                    </div>
                                )}
                            </div>
                            {/* Selected state pills */}
                            {filters.states.length > 0 && (
                                <div className="flex flex-wrap gap-1 mt-2">
                                    {filters.states.map((state) => (
                                        <button
                                            key={state}
                                            onClick={() => toggleState(state)}
                                            className="flex items-center gap-1 px-2 py-0.5 rounded-full
                                                       bg-cyan-500/15 text-cyan-300 text-xs
                                                       hover:bg-red-500/15 hover:text-red-300 transition-colors"
                                        >
                                            {state}
                                            <span className="text-[10px]">×</span>
                                        </button>
                                    ))}
                                </div>
                            )}
                        </div>

                        {/* Capacity filter */}
                        <div>
                            <label className="block text-xs font-medium text-slate-400 mb-2 uppercase tracking-wider">
                                Min Capacity:{" "}
                                <span className="text-slate-200 normal-case">
                                    {filters.minCapacity > 0
                                        ? `${filters.minCapacity} MW`
                                        : "All"}
                                </span>
                            </label>
                            <input
                                type="range"
                                min={0}
                                max={Math.min(stats.max_capacity, 5000)}
                                step={10}
                                value={filters.minCapacity}
                                onChange={(e) =>
                                    onFiltersChange({
                                        ...filters,
                                        minCapacity: Number(e.target.value),
                                    })
                                }
                                className="w-full h-1.5 rounded-full bg-slate-700 appearance-none cursor-pointer
                                           [&::-webkit-slider-thumb]:appearance-none
                                           [&::-webkit-slider-thumb]:w-4 [&::-webkit-slider-thumb]:h-4
                                           [&::-webkit-slider-thumb]:rounded-full
                                           [&::-webkit-slider-thumb]:bg-cyan-400
                                           [&::-webkit-slider-thumb]:shadow-lg
                                           [&::-webkit-slider-thumb]:cursor-pointer"
                            />
                            <div className="flex justify-between text-[10px] text-slate-500 mt-1">
                                <span>0 MW</span>
                                <span>{Math.min(stats.max_capacity, 5000)} MW</span>
                            </div>
                        </div>
                    </div>

                    {/* Footer */}
                    <div className="px-4 py-2.5 border-t border-slate-700/50 bg-slate-900/50">
                        <div className="text-xs text-slate-400 text-center">
                            Showing{" "}
                            <span className="text-cyan-300 font-semibold">
                                {plantCount}
                            </span>{" "}
                            of {stats.total_plants} power plants
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
