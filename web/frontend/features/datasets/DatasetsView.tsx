"use client";

import { useEffect, useState } from "react";
import { datasetUrl, fetchDatasets } from "@/lib/api";
import type { DatasetEntry } from "@/types";

export default function DatasetsView() {
    const [datasets, setDatasets] = useState<DatasetEntry[] | null>(null);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        fetchDatasets()
            .then((res) => setDatasets(res.datasets))
            .catch((err: Error) => setError(err.message));
    }, []);

    const scraped = datasets?.filter((d) => d.kind === "scraped") ?? [];
    const simulated = datasets?.filter((d) => d.kind === "simulated") ?? [];
    const snapshots = [...new Set(scraped.map((d) => d.snapshot).filter(Boolean))].sort();
    const totalRecords = scraped.reduce((n, d) => n + (d.records ?? 0), 0);

    return (
        <div className="h-full overflow-y-auto bg-[#0F1115]">
            <div className="max-w-6xl mx-auto p-8 lg:p-12">
                <section className="mb-10">
                    <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-[#20d3ee]/10 border border-[#20d3ee]/20 text-[#20d3ee] text-[10px] font-bold uppercase tracking-wider mb-6">
                        <span className="material-symbols-outlined text-[14px]">database</span>
                        Datasets
                    </div>
                    <h2 className="text-4xl font-black text-white leading-tight tracking-tight">
                        The data behind the atlas.
                    </h2>
                    <p className="mt-4 text-lg text-slate-400 max-w-2xl leading-relaxed">
                        Every source the dashboards read from, where it came from and what period it covers.
                        Open any dataset as raw JSON.
                    </p>
                </section>

                {error && (
                    <div className="bg-[#161A22] border border-[#262C3A] rounded-lg p-6 text-sm text-slate-400">
                        <span className="text-amber-400 font-semibold">Catalogue unavailable.</span> {error}
                    </div>
                )}

                {!error && !datasets && (
                    <div className="space-y-3 animate-pulse">
                        {[0, 1, 2, 3, 4].map((i) => (
                            <div key={i} className="h-14 bg-[#161A22] border border-[#262C3A] rounded" />
                        ))}
                    </div>
                )}

                {datasets && (
                    <>
                        <section className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-10">
                            <Stat label="Sourced datasets" value={String(scraped.length)} />
                            <Stat label="Records" value={totalRecords.toLocaleString("en-IN")} />
                            <Stat
                                label="Snapshot"
                                value={snapshots.length ? snapshots[snapshots.length - 1]! : "—"}
                                sub="Refreshed daily when the source API responds"
                            />
                        </section>

                        <section className="bg-[#161A22] border border-[#262C3A] rounded-lg overflow-hidden mb-10">
                            <div className="overflow-x-auto">
                                <table className="w-full text-sm">
                                    <thead>
                                        <tr className="border-b border-[#262C3A]">
                                            {["Dataset", "Coverage", "Records", ""].map((h, i) => (
                                                <th
                                                    key={h || i}
                                                    className={`py-3 px-5 text-[10px] font-bold text-slate-500 uppercase tracking-widest ${i === 2 ? "text-right" : "text-left"}`}
                                                >
                                                    {h}
                                                </th>
                                            ))}
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {scraped.map((d) => (
                                            <tr key={d.id} className="border-b border-[#262C3A]/50 hover:bg-[#1B2029] transition-colors">
                                                <td className="py-3 px-5">
                                                    <p className="font-semibold text-white">{d.name}</p>
                                                    <p className="text-[11px] text-slate-500">{d.publisher}</p>
                                                </td>
                                                <td className="py-3 px-5 text-slate-300 whitespace-nowrap">
                                                    {d.coverage ? `${d.coverage.from} – ${d.coverage.to}` : "Point-in-time"}
                                                </td>
                                                <td className="py-3 px-5 text-right font-mono text-slate-300">
                                                    {d.available ? (d.records ?? 0).toLocaleString("en-IN") : "—"}
                                                </td>
                                                <td className="py-3 px-5">
                                                    <div className="flex items-center justify-end gap-4 whitespace-nowrap">
                                                        {d.available ? (
                                                            <a
                                                                href={datasetUrl(d.id)}
                                                                target="_blank"
                                                                rel="noopener noreferrer"
                                                                className="text-xs font-semibold text-[#20d3ee] hover:underline"
                                                            >
                                                                Open JSON ↗
                                                            </a>
                                                        ) : (
                                                            <span className="text-xs text-amber-400">Missing</span>
                                                        )}
                                                        {d.source_url && (
                                                            <a
                                                                href={d.source_url}
                                                                target="_blank"
                                                                rel="noopener noreferrer"
                                                                className="text-xs text-slate-400 hover:text-white"
                                                            >
                                                                Source ↗
                                                            </a>
                                                        )}
                                                    </div>
                                                </td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>
                        </section>

                        {simulated.length > 0 && (
                            <section>
                                <h3 className="text-sm font-bold text-white mb-1">Simulated feeds</h3>
                                <p className="text-xs text-slate-500 mb-4">
                                    Used by the map&apos;s live-generation mode and market prices. These are not real-time data.
                                </p>
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                    {simulated.map((d) => (
                                        <div key={d.id} className="bg-[#161A22] border border-amber-500/20 rounded-lg p-5">
                                            <p className="text-sm font-semibold text-white">{d.name}</p>
                                            <p className="text-xs text-slate-400 mt-1 leading-relaxed">{d.note}</p>
                                        </div>
                                    ))}
                                </div>
                            </section>
                        )}
                    </>
                )}
            </div>
        </div>
    );
}

function Stat({ label, value, sub }: { label: string; value: string; sub?: string }) {
    return (
        <div className="bg-[#161A22] border border-[#262C3A] rounded-md p-6 relative overflow-hidden">
            <div className="absolute left-0 top-0 bottom-0 w-1 bg-[#20d3ee]" />
            <p className="text-xs font-bold text-slate-500 uppercase tracking-widest mb-4">{label}</p>
            <p className="text-3xl font-bold text-white tracking-tight">{value}</p>
            {sub && <p className="text-[10px] text-slate-500 mt-2 italic">{sub}</p>}
        </div>
    );
}
