"use client";

import { useEffect, useState } from "react";
import {
    LineChart, Line, BarChart, Bar,
    XAxis, YAxis, CartesianGrid, Tooltip,
    ResponsiveContainer, Cell, Legend,
} from "recharts";
import { motion } from "framer-motion";
import { fetchStateEmissions, fetchEmissionsTrend } from "@/lib/api";

interface StateEmission {
    state_id: string;
    state: string;
    year: number;
    total_emissions_mt: number;
    coal_emissions_mt: number;
    non_coal_emissions_mt: number;
    intensity_kg_kwh: number;
    renewable_share_percent: number;
    trend_pct: number;
}

interface TrendPoint {
    year: number;
    total_emissions_mt: number;
    coal_emissions_mt: number;
}

function intensityColor(val: number): string {
    // 0.0 → green, 0.4 → yellow, 0.8+ → red
    if (val < 0.2) return "#22c55e";
    if (val < 0.4) return "#86efac";
    if (val < 0.6) return "#facc15";
    if (val < 0.8) return "#f97316";
    return "#ef4444";
}

function trendIcon(pct: number) {
    if (pct > 0) return { icon: "trending_up", color: "#ef4444" };
    if (pct < 0) return { icon: "trending_down", color: "#22c55e" };
    return { icon: "trending_flat", color: "#94a3b8" };
}

interface Props {
    year: number;
}

export default function EmissionsTab({ year }: Props) {
    const [stateData, setStateData] = useState<StateEmission[]>([]);
    const [trend, setTrend] = useState<TrendPoint[]>([]);
    const [loading, setLoading] = useState(true);
    const [sortKey, setSortKey] = useState<keyof StateEmission>("total_emissions_mt");
    const [sortDir, setSortDir] = useState<"asc" | "desc">("desc");
    const [filter, setFilter] = useState("");

    useEffect(() => {
        setTimeout(() => setLoading(true), 0);
        Promise.all([
            fetchStateEmissions<StateEmission>(year),
            fetchEmissionsTrend<TrendPoint>(),
        ]).then(([stateRes, trendRes]) => {
            setStateData(stateRes.data ?? []);
            setTrend(trendRes.data ?? []);
            setLoading(false);
        }).catch(() => setLoading(false));
    }, [year]);

    const sortedData = [...stateData]
        .filter(r => r.state.toLowerCase().includes(filter.toLowerCase()))
        .sort((a, b) => {
            const av = a[sortKey] as number;
            const bv = b[sortKey] as number;
            return sortDir === "desc" ? bv - av : av - bv;
        });

    const topEmitters = sortedData.slice(0, 10);
    const nationalTotals = stateData.reduce(
        (acc, r) => ({ total: acc.total + r.total_emissions_mt, coal: acc.coal + r.coal_emissions_mt }),
        { total: 0, coal: 0 }
    );

    function toggleSort(key: keyof StateEmission) {
        if (sortKey === key) setSortDir(d => d === "desc" ? "asc" : "desc");
        else { setSortKey(key); setSortDir("desc"); }
    }

    if (loading) {
        return (
            <div className="flex items-center justify-center h-64">
                <div className="w-10 h-10 border-4 border-[#20d3ee] border-t-transparent rounded-full animate-spin" />
            </div>
        );
    }

    return (
        <div className="space-y-6">
            {/* KPI Tiles */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {[
                    { label: "National CO₂ (Mt)", value: nationalTotals.total.toFixed(1), icon: "cloud", color: "#ef4444" },
                    { label: "Coal Share", value: `${Math.round(nationalTotals.coal / nationalTotals.total * 100)}%`, icon: "co2", color: "#f97316" },
                    { label: "States Tracked", value: stateData.length, icon: "map", color: "#20d3ee" },
                    { label: "Cleanest State", value: sortedData[sortedData.length - 1]?.state ?? "—", icon: "eco", color: "#22c55e" }
                ].map(tile => (
                    <motion.div
                        key={tile.label}
                        initial={{ opacity: 0, y: 12 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="bg-[#161A22] border border-[#262C3A] rounded-lg p-4 flex flex-col gap-2"
                    >
                        <div className="flex items-center justify-between">
                            <span className="text-[10px] text-slate-400 uppercase tracking-widest font-semibold">{tile.label}</span>
                            <span className="material-symbols-outlined text-[18px]" style={{ color: tile.color }}>{tile.icon}</span>
                        </div>
                        <p className="text-2xl font-bold" style={{ color: tile.color }}>{tile.value}</p>
                    </motion.div>
                ))}
            </div>

            {/* Charts Row */}
            <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
                {/* National Trend Line */}
                <div className="bg-[#161A22] border border-[#262C3A] rounded-lg p-5">
                    <h3 className="text-sm font-bold mb-1">National CO₂ Trend</h3>
                    <p className="text-[11px] text-slate-400 mb-4">Million tonnes CO₂ per year (aggregated all states)</p>
                    <ResponsiveContainer width="100%" height={220}>
                        <LineChart data={trend}>
                            <CartesianGrid stroke="#1e293b" strokeDasharray="3 3" />
                            <XAxis dataKey="year" tick={{ fontSize: 11, fill: "#94a3b8" }} />
                            <YAxis tick={{ fontSize: 11, fill: "#94a3b8" }} />
                            <Tooltip
                                contentStyle={{ background: "#131720", border: "1px solid #262C3A", borderRadius: 8 }}
                                labelStyle={{ color: "#94a3b8" }}
                            />
                            <Legend wrapperStyle={{ fontSize: 11 }} />
                            <Line type="monotone" dataKey="total_emissions_mt" name="Total CO₂ (Mt)" stroke="#ef4444" strokeWidth={2} dot={false} />
                            <Line type="monotone" dataKey="coal_emissions_mt" name="Coal CO₂ (Mt)" stroke="#f97316" strokeWidth={2} dot={false} strokeDasharray="4 2" />
                        </LineChart>
                    </ResponsiveContainer>
                </div>

                {/* Top Emitters Bar */}
                <div className="bg-[#161A22] border border-[#262C3A] rounded-lg p-5">
                    <h3 className="text-sm font-bold mb-1">Top 10 Emitting States</h3>
                    <p className="text-[11px] text-slate-400 mb-4">Total CO₂ in million tonnes for FY {year}</p>
                    <ResponsiveContainer width="100%" height={220}>
                        <BarChart data={topEmitters} layout="vertical">
                            <CartesianGrid stroke="#1e293b" strokeDasharray="3 3" horizontal={false} />
                            <XAxis type="number" tick={{ fontSize: 10, fill: "#94a3b8" }} />
                            <YAxis type="category" dataKey="state" width={90} tick={{ fontSize: 10, fill: "#94a3b8" }} />
                            <Tooltip
                                contentStyle={{ background: "#131720", border: "1px solid #262C3A", borderRadius: 8 }}
                                formatter={(v?: number) => v != null ? [`${v.toFixed(1)} Mt`, "CO₂"] : ["—", "CO₂"]}
                            />
                            <Bar dataKey="total_emissions_mt" name="CO₂ (Mt)" radius={[0, 4, 4, 0]}>
                                {topEmitters.map((entry) => (
                                    <Cell key={entry.state_id} fill={intensityColor(entry.intensity_kg_kwh)} />
                                ))}
                            </Bar>
                        </BarChart>
                    </ResponsiveContainer>
                </div>
            </div>

            {/* State Table */}
            <div className="bg-[#161A22] border border-[#262C3A] rounded-lg p-5">
                <div className="flex items-center justify-between mb-4">
                    <div>
                        <h3 className="text-sm font-bold">Carbon Intensity by State</h3>
                        <p className="text-[11px] text-slate-400">Click column headers to sort</p>
                    </div>
                    <input
                        value={filter}
                        onChange={e => setFilter(e.target.value)}
                        placeholder="Search state…"
                        className="bg-[#0F1115] border border-[#262C3A] text-xs rounded px-3 py-1.5 text-slate-200 placeholder:text-slate-500 focus:outline-none focus:border-[#20d3ee] w-44"
                    />
                </div>
                <div className="overflow-x-auto">
                    <table className="w-full text-xs">
                        <thead>
                            <tr className="border-b border-[#262C3A]">
                                {[
                                    { key: "state", label: "State" },
                                    { key: "total_emissions_mt", label: "Total CO₂ (Mt)" },
                                    { key: "coal_emissions_mt", label: "Coal CO₂ (Mt)" },
                                    { key: "intensity_kg_kwh", label: "Intensity (kg/kWh)" },
                                    { key: "renewable_share_percent", label: "Renewable %" },
                                    { key: "trend_pct", label: "YoY Trend" },
                                ].map(col => (
                                    <th
                                        key={col.key}
                                        onClick={() => toggleSort(col.key as keyof StateEmission)}
                                        className="text-left py-2 px-3 text-slate-400 uppercase tracking-wider cursor-pointer hover:text-[#20d3ee] transition-colors select-none"
                                    >
                                        {col.label}
                                        {sortKey === col.key && (
                                            <span className="ml-1 material-symbols-outlined text-[10px]">
                                                {sortDir === "desc" ? "arrow_downward" : "arrow_upward"}
                                            </span>
                                        )}
                                    </th>
                                ))}
                            </tr>
                        </thead>
                        <tbody>
                            {sortedData.map((row, i) => {
                                const td = trendIcon(row.trend_pct);
                                return (
                                    <tr
                                        key={row.state_id}
                                        className={`border-b border-[#262C3A]/40 hover:bg-white/5 transition-colors ${i % 2 === 0 ? "" : "bg-white/[0.01]"}`}
                                    >
                                        <td className="py-2 px-3 font-medium text-slate-200">{row.state}</td>
                                        <td className="py-2 px-3 text-slate-300">{row.total_emissions_mt.toFixed(1)}</td>
                                        <td className="py-2 px-3 text-slate-300">{row.coal_emissions_mt.toFixed(1)}</td>
                                        <td className="py-2 px-3">
                                            <span
                                                className="px-2 py-0.5 rounded text-[10px] font-bold"
                                                style={{
                                                    color: intensityColor(row.intensity_kg_kwh),
                                                    background: `${intensityColor(row.intensity_kg_kwh)}20`,
                                                    border: `1px solid ${intensityColor(row.intensity_kg_kwh)}40`,
                                                }}
                                            >
                                                {row.intensity_kg_kwh.toFixed(3)}
                                            </span>
                                        </td>
                                        <td className="py-2 px-3 text-[#22c55e] font-semibold">
                                            {row.renewable_share_percent.toFixed(1)}%
                                        </td>
                                        <td className="py-2 px-3">
                                            <span className="flex items-center gap-1" style={{ color: td.color }}>
                                                <span className="material-symbols-outlined text-[14px]">{td.icon}</span>
                                                {row.trend_pct > 0 ? "+" : ""}{row.trend_pct}%
                                            </span>
                                        </td>
                                    </tr>
                                );
                            })}
                        </tbody>
                    </table>
                </div>

                {/* Legend */}
                <div className="mt-4 flex flex-wrap items-center gap-4 text-[10px] text-slate-500 border-t border-[#262C3A] pt-3">
                    <span className="font-bold text-slate-400">Intensity legend:</span>
                    {[
                        { color: "#22c55e", label: "< 0.2 Clean" },
                        { color: "#facc15", label: "0.4–0.6 Moderate" },
                        { color: "#f97316", label: "0.6–0.8 High" },
                        { color: "#ef4444", label: "> 0.8 Critical" },
                    ].map(l => (
                        <span key={l.label} className="flex items-center gap-1.5">
                            <span className="w-2.5 h-2.5 rounded-full inline-block" style={{ background: l.color }} />
                            {l.label}
                        </span>
                    ))}
                </div>
            </div>
        </div>
    );
}
