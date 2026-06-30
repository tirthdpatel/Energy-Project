"use client";

import { useState } from "react";
import {
    ScatterChart,
    Scatter,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer,
    ZAxis,
} from "recharts";
import { motion } from "framer-motion";
import { useAnalyticsData } from "./hooks/useAnalyticsData";
import EmissionsTab from "./EmissionsTab";

/* ── Helpers ─── */

function downloadCSV(rows: Record<string, string | number>[], filename: string) {
    if (!rows.length) return;
    const headers = Object.keys(rows[0]);
    const csv = [
        headers.join(","),
        ...rows.map((r) =>
            headers
                .map((h) => {
                    const v = r[h];
                    return typeof v === "string" && v.includes(",") ? `"${v}"` : v;
                })
                .join(",")
        ),
    ].join("\n");
    const blob = new Blob([csv], { type: "text/csv" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
}

/* ── Sidebar items ─── */
type View = "map" | "simple" | "pro";

const NAV_ITEMS: { icon: string; label: string; view: View }[] = [
    { icon: "dashboard", label: "Dashboard", view: "map" },
    { icon: "analytics", label: "Pro Analytics", view: "pro" },
    { icon: "map", label: "Geospatial", view: "map" },
    { icon: "database", label: "Datasets", view: "simple" },
];
const REPORTS: { icon: string; label: string; view: View }[] = [
    { icon: "monitoring", label: "Efficiency Trends", view: "simple" },
    { icon: "description", label: "Policy Audit", view: "simple" },
];

// Removed static TABLE_DATA; data is now served live from backend metrics via fetchCorrelation.

/* ── Component ─── */

interface Props {
    onNavigate?: (view: "map" | "simple" | "pro") => void;
    onStateClick?: (stateId: string) => void;
}

export default function AnalyticsDashboard({ onNavigate, onStateClick }: Props = {}) {
    const {
        meta,
        year,
        setYear,
        marketData,
        loading,
        data,
        filteredData,
        scatterDataGDP,
        scatterDataEmissions,
        correlationIndex,
        energyIntensity,
        emissionsIntensity,
        renewableShare
    } = useAnalyticsData();

    const [filterText, setFilterText] = useState("");
    const [activeNav, setActiveNav] = useState(1);
    const [activeTab, setActiveTab] = useState<"overview" | "emissions">("overview");

    const filteredTable = filteredData.filter((r) =>
        r.state.toLowerCase().includes(filterText.toLowerCase())
    );

    if (loading && !data) {
        return (
            <div className="flex items-center justify-center h-full">
                <div className="w-10 h-10 border-4 border-[#20d3ee] border-t-transparent rounded-full animate-spin" />
            </div>
        );
    }

    return (
        <div className="flex h-full overflow-hidden">
            {/* ── Sidebar ── */}
            <aside className="w-64 bg-[#161A22] border-r border-[#262C3A] flex-col hidden lg:flex shrink-0">
                <div className="p-6 flex items-center gap-3">
                    <div className="w-8 h-8 rounded bg-[#20d3ee] flex items-center justify-center text-[#0F1115]">
                        <span className="material-symbols-outlined font-bold">bolt</span>
                    </div>
                    <div className="flex flex-col">
                        <h1 className="text-sm font-bold tracking-tight uppercase">India Energy Atlas</h1>
                        <span className="text-[10px] text-slate-400 font-medium">Institutional Pro v4.2</span>
                    </div>
                </div>

                <nav className="flex-1 px-4 py-2 space-y-1">
                    {NAV_ITEMS.map((item, idx) => (
                        <button
                            key={item.label}
                            onClick={() => {
                                setActiveNav(idx);
                                if (onNavigate) onNavigate(item.view);
                            }}
                            className={`flex items-center gap-3 w-full px-3 py-2 rounded text-sm font-medium transition-colors ${activeNav === idx
                                ? "bg-[#20d3ee]/10 text-[#20d3ee] border border-[#20d3ee]/20"
                                : "text-slate-400 hover:text-white hover:bg-white/5"
                                }`}
                        >
                            <span className="material-symbols-outlined text-[20px]">{item.icon}</span>
                            {item.label}
                        </button>
                    ))}

                    <div className="pt-4 pb-2 px-3">
                        <p className="text-[10px] font-bold text-slate-500 uppercase tracking-widest">Reports</p>
                    </div>

                    {REPORTS.map((r) => (
                        <button
                            key={r.label}
                            onClick={() => {
                                if (onNavigate) onNavigate(r.view);
                            }}
                            className="flex items-center gap-3 w-full px-3 py-2 text-slate-400 hover:text-white hover:bg-white/5 rounded transition-colors text-sm font-medium"
                        >
                            <span className="material-symbols-outlined text-[20px]">{r.icon}</span>
                            {r.label}
                        </button>
                    ))}
                </nav>

                {/* User card */}
                <div className="p-4 border-t border-[#262C3A]">
                    <div className="flex items-center gap-3 p-2 rounded-lg bg-[#0F1115]/50 border border-[#262C3A]">
                        <div className="w-8 h-8 rounded-full bg-slate-700 flex items-center justify-center border border-[#262C3A] text-xs font-bold text-[#20d3ee]">
                            OP
                        </div>
                        <div className="flex-1 overflow-hidden">
                            <p className="text-xs font-bold truncate">Om Patel</p>
                            <p className="text-[10px] text-slate-500 truncate">Energy Analyst</p>
                        </div>
                        <span className="material-symbols-outlined text-slate-500 text-sm">settings</span>
                    </div>
                </div>
            </aside>

            {/* ── Main content ── */}
            <main className="flex-1 flex flex-col min-w-0 overflow-hidden">
                {/* Sub-header with year / sector selectors */}
                <header className="h-14 border-b border-[#262C3A] bg-[#161A22]/50 backdrop-blur-md px-6 flex items-center justify-between shrink-0">
                    <div className="flex items-center gap-8 h-full">
                        <div className="flex items-center gap-4">
                            <div className="flex items-center gap-2">
                                <label className="text-[11px] text-slate-500 font-bold uppercase tracking-tighter">
                                    Fiscal Year
                                </label>
                                <select
                                    className="bg-[#0F1115] border-[#262C3A] text-xs rounded py-1 pl-2 pr-8 text-slate-200 focus:border-[#20d3ee] focus:ring-0"
                                    value={year}
                                    onChange={(e) => setYear(Number(e.target.value))}
                                >
                                    {meta?.years &&
                                        Array.from(
                                            { length: meta.years.max_year - meta.years.min_year + 1 },
                                            (_, i) => meta.years.min_year + i
                                        ).map((y) => (
                                            <option key={y} value={y}>
                                                FY {y}-{String(y + 1).slice(-2)}
                                            </option>
                                        ))}
                                </select>
                            </div>
                            <div className="flex items-center gap-2">
                                <label className="text-[11px] text-slate-500 font-bold uppercase tracking-tighter">
                                    Sector
                                </label>
                                <select className="bg-[#0F1115] border-[#262C3A] text-xs rounded py-1 pl-2 pr-8 text-slate-200 focus:border-[#20d3ee] focus:ring-0">
                                    <option>All Sectors</option>
                                    <option>Industrial</option>
                                    <option>Residential</option>
                                    <option>Agriculture</option>
                                </select>
                            </div>
                        </div>
                    </div>
                    <div className="flex items-center gap-3">
                        <button className="p-1.5 text-slate-400 hover:text-[#20d3ee] transition-colors">
                            <span className="material-symbols-outlined text-[20px]">notifications</span>
                        </button>
                        <button className="p-1.5 text-slate-400 hover:text-[#20d3ee] transition-colors">
                            <span className="material-symbols-outlined text-[20px]">search</span>
                        </button>
                    </div>
                </header>

                {/* ── Tab Bar ── */}
                <div className="flex items-center gap-1 px-6 py-2 border-b border-[#262C3A] bg-[#161A22] shrink-0">
                    {(["overview", "emissions"] as const).map(tab => (
                        <button
                            key={tab}
                            onClick={() => setActiveTab(tab)}
                            className={`px-4 py-1.5 rounded text-xs font-semibold capitalize transition-colors ${activeTab === tab
                                ? "bg-[#20d3ee]/10 text-[#20d3ee] border border-[#20d3ee]/20"
                                : "text-slate-400 hover:text-white hover:bg-white/5"
                                }`}
                        >
                            {tab === "emissions" ? "🌿 Carbon Emissions" : "📊 Overview"}
                        </button>
                    ))}
                </div>

                {/* Scrollable Content */}
                <div className="flex-1 overflow-y-auto p-6 space-y-6">
                    {activeTab === "emissions" ? (
                        <EmissionsTab year={year} />
                    ) : (
                        <>
                            {/* ── Metric Tiles ── */}
                            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                                <TileCard
                                    label="Correlation Index"
                                    value={correlationIndex.toFixed(2)}
                                    icon="info"
                                    changeVal="+2.1%"
                                    changeDir="up"
                                    barPct={correlationIndex * 100}
                                />
                                <TileCard
                                    label="Energy Intensity"
                                    value={`${energyIntensity}`}
                                    unit="MJ/GDP"
                                    icon="speed"
                                    changeVal="-1.4%"
                                    changeDir="down"
                                    barPct={42}
                                />
                                <TileCard
                                    label="Emissions Intensity"
                                    value={`${emissionsIntensity}`}
                                    unit="kg CO2"
                                    icon="co2"
                                    changeVal="-3.2%"
                                    changeDir="down"
                                    barPct={52}
                                />
                                <TileCard
                                    label="Renewable Share"
                                    value={`${renewableShare}%`}
                                    icon="eco"
                                    changeVal="+5.7%"
                                    changeDir="up"
                                    barPct={Number(renewableShare) || 25}
                                />
                            </div>

                            {/* ── Charts Row ── */}
                            <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
                                {/* Energy vs GDP Scatter */}
                                <div className="bg-[#161A22] border border-[#262C3A] rounded-lg p-5">
                                    <div className="flex items-center justify-between mb-6">
                                        <div>
                                            <h3 className="text-sm font-bold text-slate-200">Energy Consumption vs. GDP</h3>
                                            <p className="text-[11px] text-slate-500">
                                                Correlation by State (Linear regression r²={((correlationIndex ** 2) || 0.88).toFixed(2)})
                                            </p>
                                        </div>
                                        <button className="p-1 rounded bg-[#0F1115] text-slate-400 border border-[#262C3A] hover:text-[#20d3ee] transition-colors">
                                            <span className="material-symbols-outlined text-xs">fullscreen</span>
                                        </button>
                                    </div>
                                    <ResponsiveContainer width="100%" height={260}>
                                        <ScatterChart margin={{ top: 10, right: 10, bottom: 10, left: 10 }}>
                                            <CartesianGrid stroke="#262C3A" strokeDasharray="3 3" />
                                            <XAxis
                                                type="number"
                                                dataKey="x"
                                                name="GDP"
                                                tick={{ fill: "#475569", fontSize: 10 }}
                                                axisLine={{ stroke: "#262C3A" }}
                                                tickLine={false}
                                                label={{ value: "GDP (₹B)", position: "insideBottomRight", offset: -5, fill: "#475569", fontSize: 10 }}
                                            />
                                            <YAxis
                                                type="number"
                                                dataKey="y"
                                                name="Capacity"
                                                tick={{ fill: "#475569", fontSize: 10 }}
                                                axisLine={{ stroke: "#262C3A" }}
                                                tickLine={false}
                                                label={{ value: "Capacity (GW)", angle: -90, position: "insideLeft", fill: "#475569", fontSize: 10 }}
                                            />
                                            <ZAxis range={[40, 300]} />
                                            <Tooltip
                                                contentStyle={{
                                                    backgroundColor: "#0F1115",
                                                    border: "1px solid #262C3A",
                                                    borderRadius: "8px",
                                                    fontSize: 11,
                                                }}
                                                cursor={{ strokeDasharray: "3 3", stroke: "#20d3ee" }}
                                            />
                                            <Scatter data={scatterDataGDP} fill="#20d3ee" fillOpacity={0.6} stroke="#20d3ee" strokeWidth={1} />
                                        </ScatterChart>
                                    </ResponsiveContainer>
                                    <div className="mt-4 flex justify-center gap-6">
                                        <ChartLegend dot="bg-[#20d3ee]" label="Top Tier States" />
                                        <ChartLegend dot="bg-slate-600" label="Emerging Economies" />
                                    </div>
                                </div>

                                {/* Emissions vs RE Scatter */}
                                <div className="bg-[#161A22] border border-[#262C3A] rounded-lg p-5">
                                    <div className="flex items-center justify-between mb-6">
                                        <div>
                                            <h3 className="text-sm font-bold text-slate-200">Emissions vs. Renewable Adoption</h3>
                                            <p className="text-[11px] text-slate-500">Inversion trend analysis by regional cluster</p>
                                        </div>
                                        <button className="p-1 rounded bg-[#0F1115] text-slate-400 border border-[#262C3A] hover:text-[#20d3ee] transition-colors">
                                            <span className="material-symbols-outlined text-xs">tune</span>
                                        </button>
                                    </div>
                                    <ResponsiveContainer width="100%" height={260}>
                                        <ScatterChart margin={{ top: 10, right: 10, bottom: 10, left: 10 }}>
                                            <CartesianGrid stroke="#262C3A" strokeDasharray="3 3" />
                                            <XAxis
                                                type="number"
                                                dataKey="x"
                                                name="RE Share"
                                                tick={{ fill: "#475569", fontSize: 10 }}
                                                axisLine={{ stroke: "#262C3A" }}
                                                tickLine={false}
                                                label={{ value: "RE Share (%)", position: "insideBottomRight", offset: -5, fill: "#475569", fontSize: 10 }}
                                            />
                                            <YAxis
                                                type="number"
                                                dataKey="y"
                                                name="Emissions"
                                                tick={{ fill: "#475569", fontSize: 10 }}
                                                axisLine={{ stroke: "#262C3A" }}
                                                tickLine={false}
                                                label={{ value: "Emissions (Mt)", angle: -90, position: "insideLeft", fill: "#475569", fontSize: 10 }}
                                            />
                                            <ZAxis range={[50, 200]} />
                                            <Tooltip
                                                contentStyle={{
                                                    backgroundColor: "#0F1115",
                                                    border: "1px solid #262C3A",
                                                    borderRadius: "8px",
                                                    fontSize: 11,
                                                }}
                                                cursor={{ strokeDasharray: "3 3", stroke: "#f43f5e" }}
                                            />
                                            <Scatter
                                                data={scatterDataEmissions}
                                                fill="#f43f5e"
                                                fillOpacity={0.5}
                                                stroke="#f43f5e"
                                                strokeWidth={1}
                                            />
                                        </ScatterChart>
                                    </ResponsiveContainer>
                                    <div className="mt-4 flex justify-center gap-6">
                                        <ChartLegend dot="bg-rose-500" label="High Carbon Risk" />
                                        <ChartLegend dot="bg-[#20d3ee]" label="Decarbonized Zones" />
                                    </div>
                                </div>
                            </div>

                            {/* ── Data Table ── */}
                            <div className="bg-[#161A22] border border-[#262C3A] rounded-lg overflow-hidden">
                                <div className="px-6 py-4 border-b border-[#262C3A] flex items-center justify-between bg-[#161A22]/50">
                                    <div className="flex items-center gap-4">
                                        <h3 className="text-sm font-bold">State-wise Efficiency Benchmarks</h3>
                                        <div className="px-2 py-0.5 rounded bg-[#20d3ee]/10 border border-[#20d3ee]/20 text-[10px] font-bold text-[#20d3ee] uppercase">
                                            {filteredData.length || 32} Entities Loaded
                                        </div>
                                    </div>
                                    <div className="flex items-center gap-2">
                                        <div className="relative">
                                            <span className="material-symbols-outlined absolute left-2 top-1/2 -translate-y-1/2 text-slate-500 text-xs">
                                                search
                                            </span>
                                            <input
                                                className="bg-[#0F1115] border-[#262C3A] text-[11px] rounded py-1 pl-7 pr-3 text-slate-200 focus:border-[#20d3ee] focus:ring-0 w-48"
                                                placeholder="Filter states..."
                                                type="text"
                                                value={filterText}
                                                onChange={(e) => setFilterText(e.target.value)}
                                            />
                                        </div>
                                        <button
                                            onClick={() => {
                                                const rows = filteredTable.map((r) => {
                                                    const mPrice = marketData?.prices.find(p => p.state_id === r.state_id)?.price_inr_per_mwh;
                                                    return {
                                                        State: r.state,
                                                        "Capacity (GW)": (r.total_capacity_mw / 1000).toFixed(2),
                                                        "CO2 Output (Mt)": r.total_emissions_mt.toFixed(2),
                                                        "Efficiency Score": (r.renewable_share_percent / 100).toFixed(2),
                                                        "GDP (Billion INR)": r.gdp_billion_inr.toFixed(1),
                                                        "Live DAM (₹/MWh)": mPrice ? mPrice.toFixed(0) : "N/A"
                                                    };
                                                });
                                                downloadCSV(rows, "efficiency_benchmarks.csv");
                                            }}
                                            className="flex items-center gap-1.5 px-3 py-1 bg-transparent border border-[#262C3A] rounded text-[11px] font-bold text-slate-400 hover:text-white hover:border-slate-500 transition-all uppercase tracking-tight"
                                        >
                                            <span className="material-symbols-outlined text-[16px]">download</span>
                                            CSV Export
                                        </button>
                                    </div>
                                </div>

                                <div className="overflow-x-auto">
                                    <table className="w-full text-left border-collapse">
                                        <thead className="bg-[#0F1115]/30 text-[10px] font-bold text-slate-500 uppercase tracking-widest">
                                            <tr>
                                                <th className="px-6 py-3 border-b border-[#262C3A]">
                                                    <div className="flex items-center gap-1 cursor-pointer hover:text-[#20d3ee]">
                                                        Region/State
                                                        <span className="material-symbols-outlined text-[14px]">expand_more</span>
                                                    </div>
                                                </th>
                                                <th className="px-6 py-3 border-b border-[#262C3A]">GDP Class</th>
                                                <th className="px-6 py-3 border-b border-[#262C3A] text-right">Capacity (GW)</th>
                                                <th className="px-6 py-3 border-b border-[#262C3A] text-right">CO2 Output (Mt)</th>
                                                <th className="px-6 py-3 border-b border-[#262C3A] text-right">Efficiency (RE%)</th>
                                                <th className="px-6 py-3 border-b border-[#262C3A] text-right">GDP (B-INR)</th>
                                                <th className="px-6 py-3 border-b border-[#262C3A] text-right">Live DAM Price</th>
                                                <th className="px-6 py-3 border-b border-[#262C3A] text-center">Status</th>
                                            </tr>
                                        </thead>
                                        <tbody className="text-xs text-slate-300 divide-y divide-[#262C3A]/50 tabular-nums">
                                            {filteredTable.map((row) => {
                                                const effScore = row.renewable_share_percent;
                                                const statusColor =
                                                    effScore >= 40
                                                        ? "bg-emerald-500"
                                                        : effScore >= 20
                                                            ? "bg-amber-500"
                                                            : "bg-rose-500";
                                                const barColor = effScore >= 40 ? "bg-[#20d3ee]" : "bg-rose-500";

                                                return (
                                                    <motion.tr
                                                        key={row.state}
                                                        initial={{ opacity: 0, y: 10 }}
                                                        animate={{ opacity: 1, y: 0 }}
                                                        transition={{ duration: 0.3, delay: filteredTable.indexOf(row) * 0.05 }}
                                                        className="hover:bg-white/5 transition-colors cursor-pointer"
                                                        onClick={() => {
                                                            if (onStateClick) onStateClick(row.state_id);
                                                            if (onNavigate) onNavigate("map");
                                                        }}
                                                    >
                                                        <td className="px-6 py-2.5 font-medium text-slate-200">{row.state}</td>
                                                        <td className="px-6 py-2.5">
                                                            <span className="px-1.5 py-0.5 rounded bg-slate-800 text-[10px] text-slate-400 font-bold">
                                                                {row.gdp_billion_inr > 5000 ? "Top Tier" : "Emerging"}
                                                            </span>
                                                        </td>
                                                        <td className="px-6 py-2.5 text-right">{(row.total_capacity_mw / 1000).toFixed(2)}</td>
                                                        <td className="px-6 py-2.5 text-right">{row.total_emissions_mt.toFixed(2)}</td>
                                                        <td className="px-6 py-2.5 text-right">
                                                            <div className="flex items-center justify-end gap-2">
                                                                <span>{effScore}%</span>
                                                                <div className="w-12 h-1 bg-[#262C3A] rounded-full overflow-hidden">
                                                                    <div
                                                                        className={`${barColor} h-full`}
                                                                        style={{ width: `${effScore}%` }}
                                                                    />
                                                                </div>
                                                            </div>
                                                        </td>
                                                        <td className="px-6 py-2.5 text-right text-slate-300">
                                                            ₹{row.gdp_billion_inr.toFixed(1)}B
                                                        </td>
                                                        <td className="px-6 py-2.5 text-right font-mono text-[#20d3ee]">
                                                            {marketData?.prices.find(p => p.state_id === row.state_id)?.price_inr_per_mwh
                                                                ? `₹${marketData.prices.find(p => p.state_id === row.state_id)?.price_inr_per_mwh.toFixed(0)}`
                                                                : "—"}
                                                        </td>
                                                        <td className="px-6 py-2.5 text-center">
                                                            <span
                                                                className={`w-1.5 h-1.5 rounded-full ${statusColor} inline-block`}
                                                            />
                                                        </td>
                                                    </motion.tr>
                                                );
                                            })}
                                        </tbody>
                                    </table>
                                </div>

                                <div className="px-6 py-3 border-t border-[#262C3A] flex items-center justify-between text-[11px] text-slate-500">
                                    <p>Showing 1-{filteredTable.length} of 32 states</p>
                                    <div className="flex items-center gap-2">
                                        <button className="p-1 hover:text-white transition-colors disabled:opacity-30" disabled>
                                            <span className="material-symbols-outlined text-[16px]">chevron_left</span>
                                        </button>
                                        <span className="px-2 text-[#20d3ee] font-bold">1</span>
                                        <button className="p-1 hover:text-white transition-colors">
                                            <span className="material-symbols-outlined text-[16px]">chevron_right</span>
                                        </button>
                                    </div>
                                </div>
                            </div>
                        </>
                    )}
                </div>
            </main>
        </div>
    );
}

/* ── Metric Tile Card ─── */
function TileCard({
    label,
    value,
    unit,
    icon,
    changeVal,
    changeDir,
    barPct,
}: {
    label: string;
    value: string;
    unit?: string;
    icon: string;
    changeVal: string;
    changeDir: "up" | "down";
    barPct: number;
}) {
    const isUp = changeDir === "up";
    return (
        <div className="bg-[#161A22] border border-[#262C3A] p-4 rounded-lg flex flex-col gap-1">
            <div className="flex justify-between items-start">
                <p className="text-[11px] font-bold text-slate-500 uppercase tracking-wider">{label}</p>
                <span className={`material-symbols-outlined text-sm ${isUp ? "text-[#20d3ee]" : "text-slate-500"}`}>
                    {icon}
                </span>
            </div>
            <div className="flex items-end gap-3 mt-1">
                <p className="text-2xl font-bold tabular-nums tracking-tight">
                    {value}
                    {unit && <span className="text-xs font-normal text-slate-400 uppercase ml-1">{unit}</span>}
                </p>
                <p
                    className={`text-[11px] font-medium mb-1 flex items-center ${isUp ? "text-emerald-500" : "text-rose-500"
                        }`}
                >
                    <span className="material-symbols-outlined text-[14px]">
                        {isUp ? "trending_up" : "trending_down"}
                    </span>
                    {changeVal}
                </p>
            </div>
            <div className="w-full h-1 bg-[#262C3A] rounded-full mt-2 overflow-hidden">
                <div className="bg-[#20d3ee] h-full" style={{ width: `${Math.min(barPct, 100)}%` }} />
            </div>
        </div>
    );
}

/* ── Chart Legend ─── */
function ChartLegend({ dot, label }: { dot: string; label: string }) {
    return (
        <div className="flex items-center gap-2">
            <span className={`w-2 h-2 rounded-full ${dot}`} />
            <span className="text-[10px] text-slate-400 uppercase">{label}</span>
        </div>
    );
}
