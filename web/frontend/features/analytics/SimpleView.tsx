"use client";

import { useState, useEffect, useMemo } from "react";
import { fetchInsights } from "@/lib/api";
import type { InsightsResult } from "@/types";
import {
    LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip,
    ResponsiveContainer,
} from "recharts";

/* ── static sector sidebar items ─── */
const SECTORS = [
    { icon: "dashboard", label: "Overview" },
    { icon: "wb_sunny", label: "Solar Energy" },
    { icon: "air", label: "Wind Power" },
    { icon: "factory", label: "Coal & Thermal" },
    { icon: "grid_view", label: "National Grid" },
];

/* ── helper: mock monthly trend data ─── */
const MONTHS = [
    "OCT 23", "NOV 23", "DEC 23", "JAN 24", "FEB 24", "MAR 24",
    "APR 24", "MAY 24", "JUN 24", "JUL 24", "AUG 24", "SEP 24",
];

function buildTrendData() {
    let renewable = 32;
    let fossil = 112;
    return MONTHS.map((m) => {
        renewable += Math.random() * 6 + 1;
        fossil += (Math.random() - 0.5) * 4;
        return {
            month: m,
            Renewable: +renewable.toFixed(1),
            "Fossil Fuel": +fossil.toFixed(1),
        };
    });
}

export default function SimpleView() {
    const [data, setData] = useState<InsightsResult | null>(null);
    const [activeSector, setActiveSector] = useState(0);
    const trendData = useMemo(() => buildTrendData(), []);

    useEffect(() => {
        fetchInsights().then(setData).catch(console.error);
    }, []);

    /* derive headline numbers from insight cards */
    const totalCapacity = data?.insights?.[0];

    return (
        <div className="flex h-full overflow-hidden">
            {/* ── Sector Sidebar ── */}
            <aside className="w-64 border-r border-[#262C3A] flex flex-col py-6 shrink-0 overflow-y-auto">
                <div className="px-6 mb-6">
                    <p className="text-[10px] font-bold text-slate-500 uppercase tracking-widest">
                        Sectors
                    </p>
                </div>
                <div className="space-y-1">
                    {SECTORS.map((s, idx) => (
                        <button
                            key={s.label}
                            onClick={() => setActiveSector(idx)}
                            className={`flex items-center gap-3 w-full px-6 py-3 text-sm font-semibold transition-all ${activeSector === idx
                                ? "sidebar-active-right text-[#20d3ee]"
                                : "text-slate-400 hover:text-white hover:bg-[#161A22]"
                                }`}
                        >
                            <span className="material-symbols-outlined text-[20px]">{s.icon}</span>
                            {s.label}
                        </button>
                    ))}
                </div>

                {/* System Health badge */}
                <div className="mt-auto px-6 py-4 border-t border-[#262C3A]">
                    <div className="bg-[#161A22] p-4 rounded-lg border border-[#262C3A]">
                        <p className="text-xs text-slate-400 mb-2">Current System Health</p>
                        <div className="flex items-center gap-2">
                            <div className="h-2 w-2 rounded-full bg-[#20d3ee] animate-pulse" />
                            <span className="text-sm font-bold">Stable (50.02 Hz)</span>
                        </div>
                    </div>
                </div>
            </aside>

            {/* ── Main Content ── */}
            <main className="flex-1 p-8 lg:p-12 overflow-y-auto bg-[#0F1115]">
                {/* Headline */}
                <section className="max-w-6xl mx-auto mb-12">
                    <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-[#20d3ee]/10 border border-[#20d3ee]/20 text-[#20d3ee] text-[10px] font-bold uppercase tracking-wider mb-6">
                        <span className="material-symbols-outlined text-[14px]">auto_graph</span>
                        Q3 2024 Energy Report
                    </div>
                    <h2 className="text-4xl lg:text-5xl font-black text-white leading-[1.1] tracking-tight max-w-4xl">
                        India reaches a historic{" "}
                        <span className="text-[#20d3ee]">
                            {totalCapacity ? totalCapacity.body.split(" ")[0] : "180GW"}
                        </span>{" "}
                        of Renewable Energy capacity as of Q3 2024.
                    </h2>
                    <p className="mt-6 text-lg text-slate-400 max-w-2xl leading-relaxed">
                        A quarterly analysis of the nation&apos;s progress towards sustainable energy sovereignty,
                        tracking growth across solar, wind, and storage sectors.
                    </p>
                </section>

                {/* ── Insight Cards ── */}
                <section className="max-w-6xl mx-auto grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
                    {/* Total Capacity */}
                    <MetricCard
                        label="Total Capacity"
                        value="180 GW"
                        arrow="up"
                        change="15.2%"
                        sub="YoY Growth vs 2023"
                    />
                    <MetricCard
                        label="Solar Contribution"
                        value="72 GW"
                        arrow="up"
                        change="18.4%"
                        sub="40% of renewable mix"
                    />
                    <MetricCard
                        label="Carbon Intensity"
                        value="712"
                        unit="gCO2/kWh"
                        arrow="down"
                        change="4.1% reduction"
                    />
                    <MetricCard
                        label="Peak Demand"
                        value="243 GW"
                        arrow="up"
                        change="6.8%"
                        sub="All-time record high"
                    />
                </section>

                {/* ── Trend Chart ── */}
                <section className="max-w-6xl mx-auto">
                    <div className="bg-[#161A22] border border-[#262C3A] rounded-lg p-8">
                        <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 mb-10">
                            <div>
                                <h3 className="text-xl font-bold text-white mb-2">
                                    Renewable vs. Fossil Fuel Generation
                                </h3>
                                <p className="text-sm text-slate-400">
                                    Monthly energy mix comparison over the last 12 months (in TWh)
                                </p>
                            </div>
                            <div className="flex items-center gap-6">
                                <div className="flex items-center gap-2">
                                    <div className="h-1.5 w-6 bg-[#20d3ee] rounded-full" />
                                    <span className="text-xs font-semibold text-slate-300">Renewable</span>
                                </div>
                                <div className="flex items-center gap-2">
                                    <div className="h-1.5 w-6 bg-slate-600 rounded-full" />
                                    <span className="text-xs font-semibold text-slate-300">Fossil Fuel</span>
                                </div>
                            </div>
                        </div>

                        {/* Recharts Line Chart */}
                        <ResponsiveContainer width="100%" height={400}>
                            <LineChart data={trendData} margin={{ top: 5, right: 20, bottom: 5, left: 0 }}>
                                <CartesianGrid stroke="#262C3A" strokeDasharray="3 3" />
                                <XAxis
                                    dataKey="month"
                                    tick={{ fill: "#475569", fontSize: 10 }}
                                    axisLine={{ stroke: "#262C3A" }}
                                    tickLine={false}
                                />
                                <YAxis
                                    tick={{ fill: "#475569", fontSize: 10 }}
                                    axisLine={{ stroke: "#262C3A" }}
                                    tickLine={false}
                                    unit=" TWh"
                                />
                                <Tooltip
                                    contentStyle={{
                                        backgroundColor: "#0F1115",
                                        border: "1px solid #262C3A",
                                        borderRadius: "8px",
                                        fontSize: 12,
                                    }}
                                    labelStyle={{ color: "#94a3b8", fontWeight: 700, fontSize: 10, textTransform: "uppercase" }}
                                />
                                <Line
                                    type="monotone"
                                    dataKey="Fossil Fuel"
                                    stroke="#475569"
                                    strokeWidth={2.5}
                                    dot={false}
                                />
                                <Line
                                    type="monotone"
                                    dataKey="Renewable"
                                    stroke="#20d3ee"
                                    strokeWidth={3}
                                    dot={false}
                                />
                            </LineChart>
                        </ResponsiveContainer>

                        <div className="mt-8 pt-8 border-t border-[#262C3A] flex items-center justify-between text-slate-500 text-xs italic">
                            <p>Source: Central Electricity Authority (CEA) – Grid Real-time Data Platform</p>
                            <button className="flex items-center gap-2 hover:text-white transition-colors">
                                <span className="material-symbols-outlined text-sm">download</span>
                                Download Full Report (PDF)
                            </button>
                        </div>
                    </div>
                </section>
            </main>
        </div>
    );
}

/* ── Reusable Metric Card ─── */
function MetricCard({
    label,
    value,
    unit,
    arrow,
    change,
    sub,
}: {
    label: string;
    value: string;
    unit?: string;
    arrow: "up" | "down";
    change: string;
    sub?: string;
}) {
    return (
        <div className="bg-[#161A22] border border-[#262C3A] rounded-md p-6 relative overflow-hidden group">
            <div className="absolute left-0 top-0 bottom-0 w-1 bg-[#20d3ee]" />
            <p className="text-xs font-bold text-slate-500 uppercase tracking-widest mb-4">
                {label}
            </p>
            <div className="flex items-baseline gap-2">
                <span className="text-3xl font-bold text-white tracking-tight">{value}</span>
                {unit && <span className="text-xs text-slate-400 font-medium">{unit}</span>}
                <span className="text-[#20d3ee] text-xs font-bold flex items-center">
                    <span className="material-symbols-outlined text-[14px]">
                        {arrow === "up" ? "arrow_upward" : "arrow_downward"}
                    </span>
                    {change}
                </span>
            </div>
            {sub && <p className="text-[10px] text-slate-500 mt-2 italic">{sub}</p>}
        </div>
    );
}
