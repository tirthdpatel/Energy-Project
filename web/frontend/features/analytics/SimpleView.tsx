"use client";

import { useState, useEffect } from "react";
import { fetchSectors, fetchSector } from "@/lib/api";
import type { SectorSummary, SectorDetail } from "@/types";
import {
    LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip,
    ResponsiveContainer,
} from "recharts";

/* Shown until the sector list arrives, so the sidebar never renders empty. */
const FALLBACK_SECTORS: SectorSummary[] = [
    { id: "overview", label: "Overview", icon: "dashboard" },
    { id: "solar", label: "Solar Energy", icon: "wb_sunny" },
    { id: "wind", label: "Wind Power", icon: "air" },
    { id: "coal", label: "Coal & Thermal", icon: "factory" },
    { id: "grid", label: "National Grid", icon: "grid_view" },
];

export default function SimpleView() {
    const [sectors, setSectors] = useState<SectorSummary[]>(FALLBACK_SECTORS);
    const [activeSector, setActiveSector] = useState("overview");
    const [detail, setDetail] = useState<SectorDetail | null>(null);
    const [failure, setFailure] = useState<{ sector: string; message: string } | null>(null);

    useEffect(() => {
        fetchSectors()
            .then((res) => setSectors(res.sectors))
            .catch(() => {
                /* keep the fallback list — the detail fetch reports the failure */
            });
    }, []);

    useEffect(() => {
        let cancelled = false;
        fetchSector(activeSector)
            .then((res) => {
                if (!cancelled) setDetail(res);
            })
            .catch((err: Error) => {
                if (!cancelled) setFailure({ sector: activeSector, message: err.message });
            });
        return () => {
            cancelled = true;
        };
    }, [activeSector]);

    // Derived rather than stored, so switching sectors shows the skeleton
    // immediately without a second render pass to reset the flags.
    const shown = detail?.id === activeSector ? detail : null;
    const error = failure?.sector === activeSector ? failure.message : null;
    const loading = !shown && !error;

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
                    {sectors.map((s) => (
                        <button
                            key={s.id}
                            onClick={() => setActiveSector(s.id)}
                            aria-current={activeSector === s.id ? "page" : undefined}
                            className={`flex items-center gap-3 w-full px-6 py-3 text-sm font-semibold transition-all ${activeSector === s.id
                                ? "sidebar-active-right text-[#20d3ee]"
                                : "text-slate-400 hover:text-white hover:bg-[#161A22]"
                                }`}
                        >
                            <span className="material-symbols-outlined text-[20px]">{s.icon}</span>
                            {s.label}
                        </button>
                    ))}
                </div>

                {/* Data currency badge */}
                <div className="mt-auto px-6 py-4 border-t border-[#262C3A]">
                    <div className="bg-[#161A22] p-4 rounded-lg border border-[#262C3A]">
                        <p className="text-xs text-slate-400 mb-2">Data current to</p>
                        <div className="flex items-center gap-2">
                            <div className="h-2 w-2 rounded-full bg-[#20d3ee] animate-pulse" />
                            <span className="text-sm font-bold">
                                {shown?.as_of ?? "—"}
                            </span>
                        </div>
                    </div>
                </div>
            </aside>

            {/* ── Main Content ── */}
            <main className="flex-1 p-8 lg:p-12 overflow-y-auto bg-[#0F1115]">
                {error && <SectorError message={error} />}
                {loading && <SectorSkeleton />}
                {shown && <SectorPanel detail={shown} />}
            </main>
        </div>
    );
}

/* ── One sector's dashboard ─── */
function SectorPanel({ detail }: { detail: SectorDetail }) {
    const { chart, table } = detail;

    return (
        <>
            {/* Headline */}
            <section className="max-w-6xl mx-auto mb-12">
                <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-[#20d3ee]/10 border border-[#20d3ee]/20 text-[#20d3ee] text-[10px] font-bold uppercase tracking-wider mb-6">
                    <span className="material-symbols-outlined text-[14px]">auto_graph</span>
                    {detail.label} · {detail.as_of}
                </div>
                <h2 className="text-4xl lg:text-5xl font-black text-white leading-[1.1] tracking-tight max-w-4xl">
                    {detail.headline}
                </h2>
                <p className="mt-6 text-lg text-slate-400 max-w-2xl leading-relaxed">
                    {detail.subtitle}
                </p>
            </section>

            {/* Metrics */}
            <section className="max-w-6xl mx-auto grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
                {detail.metrics.map((m) => (
                    <MetricCard key={m.label} metric={m} />
                ))}
            </section>

            {/* Trend chart */}
            <section className="max-w-6xl mx-auto mb-12">
                <div className="bg-[#161A22] border border-[#262C3A] rounded-lg p-8">
                    <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 mb-10">
                        <div>
                            <h3 className="text-xl font-bold text-white mb-2">{chart.title}</h3>
                            <p className="text-sm text-slate-400">{chart.subtitle}</p>
                        </div>
                        <div className="flex items-center gap-6">
                            {chart.series.map((s) => (
                                <div key={s.key} className="flex items-center gap-2">
                                    <div
                                        className="h-1.5 w-6 rounded-full"
                                        style={{ backgroundColor: s.color }}
                                    />
                                    <span className="text-xs font-semibold text-slate-300">
                                        {s.label}
                                    </span>
                                </div>
                            ))}
                        </div>
                    </div>

                    <ResponsiveContainer width="100%" height={400}>
                        <LineChart data={chart.data} margin={{ top: 5, right: 20, bottom: 5, left: 0 }}>
                            <CartesianGrid stroke="#262C3A" strokeDasharray="3 3" />
                            <XAxis
                                dataKey={chart.x_key}
                                tick={{ fill: "#475569", fontSize: 10 }}
                                axisLine={{ stroke: "#262C3A" }}
                                tickLine={false}
                                minTickGap={24}
                            />
                            <YAxis
                                tick={{ fill: "#475569", fontSize: 10 }}
                                axisLine={{ stroke: "#262C3A" }}
                                tickLine={false}
                                unit={chart.unit}
                                width={72}
                            />
                            <Tooltip
                                contentStyle={{
                                    backgroundColor: "#0F1115",
                                    border: "1px solid #262C3A",
                                    borderRadius: "8px",
                                    fontSize: 12,
                                }}
                                labelStyle={{
                                    color: "#94a3b8", fontWeight: 700, fontSize: 10,
                                    textTransform: "uppercase",
                                }}
                            />
                            {chart.series.map((s) => (
                                <Line
                                    key={s.key}
                                    type="monotone"
                                    dataKey={s.key}
                                    name={s.label}
                                    stroke={s.color}
                                    strokeWidth={2.5}
                                    dot={false}
                                />
                            ))}
                        </LineChart>
                    </ResponsiveContainer>

                    <div className="mt-8 pt-8 border-t border-[#262C3A] text-slate-500 text-xs italic">
                        <p>Source: {detail.source}</p>
                    </div>
                </div>
            </section>

            {/* Detail table */}
            <section className="max-w-6xl mx-auto">
                <div className="bg-[#161A22] border border-[#262C3A] rounded-lg p-8">
                    <div className="mb-6">
                        <h3 className="text-xl font-bold text-white mb-2">{table.title}</h3>
                        {table.subtitle && (
                            <p className="text-sm text-slate-400">{table.subtitle}</p>
                        )}
                    </div>
                    <div className="overflow-x-auto">
                        <table className="w-full text-sm">
                            <thead>
                                <tr className="border-b border-[#262C3A]">
                                    {table.columns.map((c) => (
                                        <th
                                            key={c.key}
                                            className={`py-3 px-4 text-[10px] font-bold text-slate-500 uppercase tracking-widest ${c.numeric ? "text-right" : "text-left"
                                                }`}
                                        >
                                            {c.label}
                                        </th>
                                    ))}
                                </tr>
                            </thead>
                            <tbody>
                                {table.rows.map((row, idx) => (
                                    <tr
                                        key={idx}
                                        className="border-b border-[#262C3A]/50 hover:bg-[#1B2029] transition-colors"
                                    >
                                        {table.columns.map((c) => (
                                            <td
                                                key={c.key}
                                                className={`py-3 px-4 ${c.numeric
                                                    ? "text-right font-mono text-slate-300"
                                                    : "text-left font-semibold text-white"
                                                    }`}
                                            >
                                                {typeof row[c.key] === "number"
                                                    ? (row[c.key] as number).toLocaleString("en-IN")
                                                    : row[c.key] ?? "—"}
                                            </td>
                                        ))}
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>
            </section>
        </>
    );
}

/* ── Metric card ─── */
function MetricCard({ metric }: { metric: SectorDetail["metrics"][number] }) {
    const { label, value, unit, change_pct, trend, sub } = metric;
    const arrow =
        trend === "up" ? "arrow_upward" : trend === "down" ? "arrow_downward" : "remove";
    const tone =
        trend === "up" ? "text-[#20d3ee]" : trend === "down" ? "text-amber-400" : "text-slate-500";

    return (
        <div className="bg-[#161A22] border border-[#262C3A] rounded-md p-6 relative overflow-hidden">
            <div className="absolute left-0 top-0 bottom-0 w-1 bg-[#20d3ee]" />
            <p className="text-xs font-bold text-slate-500 uppercase tracking-widest mb-4">
                {label}
            </p>
            <div className="flex items-baseline gap-2 flex-wrap">
                <span className="text-3xl font-bold text-white tracking-tight">{value}</span>
                {unit && <span className="text-xs text-slate-400 font-medium">{unit}</span>}
                {change_pct !== 0 && (
                    <span className={`${tone} text-xs font-bold flex items-center`}>
                        <span className="material-symbols-outlined text-[14px]">{arrow}</span>
                        {Math.abs(change_pct)}%
                    </span>
                )}
            </div>
            {sub && <p className="text-[10px] text-slate-500 mt-2 italic">{sub}</p>}
        </div>
    );
}

/* ── Loading / error states ─── */
function SectorSkeleton() {
    return (
        <div className="max-w-6xl mx-auto animate-pulse">
            <div className="h-6 w-40 bg-[#1B2029] rounded-full mb-6" />
            <div className="h-12 w-3/4 bg-[#1B2029] rounded mb-4" />
            <div className="h-12 w-1/2 bg-[#1B2029] rounded mb-12" />
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
                {[0, 1, 2, 3].map((i) => (
                    <div key={i} className="h-32 bg-[#161A22] border border-[#262C3A] rounded-md" />
                ))}
            </div>
            <div className="h-[460px] bg-[#161A22] border border-[#262C3A] rounded-lg" />
        </div>
    );
}

function SectorError({ message }: { message: string }) {
    return (
        <div className="max-w-2xl mx-auto mt-16 bg-[#161A22] border border-[#262C3A] rounded-lg p-8 text-center">
            <span className="material-symbols-outlined text-4xl text-amber-400">
                error_outline
            </span>
            <h3 className="mt-4 text-xl font-bold text-white">Sector data unavailable</h3>
            <p className="mt-2 text-sm text-slate-400">{message}</p>
        </div>
    );
}
