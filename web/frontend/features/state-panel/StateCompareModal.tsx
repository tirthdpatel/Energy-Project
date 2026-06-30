"use client";

import { useEffect, useState } from "react";
import { fetchComparison, fetchAnalyticsMeta } from "@/lib/api";
import type { ComparisonResult, AnalyticsMeta } from "@/types";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from "recharts";

interface Props {
    baseStateId: string;
    baseStateName: string;
    /** The currently selected year on the dashboard — defaults to max year from meta */
    selectedYear?: number;
    onClose: () => void;
}

export default function StateCompareModal({ baseStateId, baseStateName, selectedYear, onClose }: Props) {
    const [meta, setMeta] = useState<AnalyticsMeta | null>(null);
    const [targetStateId, setTargetStateId] = useState<string>("");
    const [data, setData] = useState<ComparisonResult | null>(null);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        fetchAnalyticsMeta().then(m => {
            setMeta(m);
            // Set an initial target state different from the base
            const target = m.states.find(s => s !== baseStateId) ?? m.states[0];
            setTargetStateId(target);
        }).catch(console.error);
    }, [baseStateId]);

    useEffect(() => {
        if (!targetStateId) return;
        // Resolve the year: use the prop if provided, otherwise fall back to the latest year
        const year = selectedYear ?? meta?.years?.max_year ?? 2026;
        setTimeout(() => setLoading(true), 0);
        fetchComparison([baseStateId, targetStateId], year).then(d => {
            setData(d);
            setLoading(false);
        }).catch(e => {
            console.error(e);
            setLoading(false);
        });
    }, [baseStateId, targetStateId, selectedYear, meta]);

    const baseData = data?.state_comparison?.find(s => s.state_id === baseStateId);
    const targetData = data?.state_comparison?.find(s => s.state_id === targetStateId);

    const chartData = data ? [
        {
            metric: "Capacity (GW)",
            [baseStateId]: baseData?.total_capacity_mw ? +(baseData.total_capacity_mw / 1000).toFixed(2) : 0,
            [targetStateId]: targetData?.total_capacity_mw ? +(targetData.total_capacity_mw / 1000).toFixed(2) : 0,
        },
        {
            metric: "RE Share (%)",
            [baseStateId]: baseData?.renewable_share_percent ?? 0,
            [targetStateId]: targetData?.renewable_share_percent ?? 0,
        },
        {
            metric: "Emissions (Mt)",
            [baseStateId]: baseData?.total_emissions_mt ?? 0,
            [targetStateId]: targetData?.total_emissions_mt ?? 0,
        },
        {
            metric: "GDP (B INR)",
            [baseStateId]: baseData?.gdp_billion_inr ?? 0,
            [targetStateId]: targetData?.gdp_billion_inr ?? 0,
        }
    ] : [];

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm">
            <div className="bg-[#161A22] border border-[#262C3A] rounded-xl shadow-2xl w-[700px] flex flex-col overflow-hidden">
                <div className="p-4 border-b border-[#262C3A] flex items-center justify-between bg-[#0F1115]/50">
                    <h2 className="text-sm font-bold text-white uppercase tracking-wider flex items-center gap-2">
                        <span className="material-symbols-outlined text-[#20d3ee]">compare_arrows</span>
                        State Comparison
                        {data?.year && (
                            <span className="text-slate-500 font-normal normal-case text-xs ml-1">({data.year})</span>
                        )}
                    </h2>
                    <button onClick={onClose} className="p-1 text-slate-400 hover:text-white transition-colors" aria-label="Close comparison">
                        <span className="material-symbols-outlined">close</span>
                    </button>
                </div>

                <div className="p-6">
                    <div className="flex items-center gap-4 mb-8">
                        <div className="flex-1 bg-[#0F1115] border border-[#262C3A] p-3 rounded text-center">
                            <span className="text-[10px] text-slate-500 font-bold uppercase tracking-widest block mb-1">Base</span>
                            <span className="text-secondary font-bold text-[#20d3ee]">{baseStateName}</span>
                        </div>
                        <span className="font-bold text-slate-600">VS</span>
                        <div className="flex-1">
                            <select
                                className="w-full bg-[#0F1115] border border-[#262C3A] p-3 rounded text-center font-bold text-white focus:border-[#20d3ee] focus:ring-0 appearance-none cursor-pointer"
                                value={targetStateId}
                                onChange={(e) => setTargetStateId(e.target.value)}
                            >
                                {meta?.states.map(s => (
                                    <option key={s} value={s}>{s}</option>
                                ))}
                            </select>
                        </div>
                    </div>

                    {loading ? (
                        <div className="h-64 flex items-center justify-center">
                            <div className="w-8 h-8 border-4 border-[#20d3ee] border-t-transparent rounded-full animate-spin" />
                        </div>
                    ) : (
                        <div className="h-64">
                            <ResponsiveContainer width="100%" height="100%">
                                <BarChart data={chartData} margin={{ top: 20, right: 30, left: 0, bottom: 5 }}>
                                    <CartesianGrid strokeDasharray="3 3" stroke="#262C3A" vertical={false} />
                                    <XAxis dataKey="metric" tick={{ fill: '#94a3b8', fontSize: 11 }} axisLine={{ stroke: '#262C3A' }} tickLine={false} />
                                    <YAxis tick={{ fill: '#475569', fontSize: 10 }} axisLine={{ stroke: '#262C3A' }} tickLine={false} />
                                    <Tooltip
                                        cursor={{ fill: '#262C3A', opacity: 0.4 }}
                                        contentStyle={{ backgroundColor: '#0F1115', borderColor: '#262C3A', borderRadius: '8px', fontSize: '12px' }}
                                    />
                                    <Legend
                                        wrapperStyle={{ fontSize: '11px', paddingTop: '10px' }}
                                        formatter={(value) => <span className="text-slate-300">{value}</span>}
                                    />
                                    <Bar dataKey={baseStateId} name={baseStateName} fill="#20d3ee" radius={[4, 4, 0, 0]} />
                                    <Bar dataKey={targetStateId} name={targetStateId} fill="#f43f5e" radius={[4, 4, 0, 0]} />
                                </BarChart>
                            </ResponsiveContainer>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
