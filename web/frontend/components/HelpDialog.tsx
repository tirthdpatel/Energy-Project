"use client";

import Modal from "@/components/Modal";
import type { Navigate } from "@/lib/navigation";

const VIEWS: { icon: string; name: string; body: string }[] = [
    {
        icon: "dashboard",
        name: "Map",
        body: "State-level capacity across India. Click a state for its detail panel; the timeline scrubs 2019–2026.",
    },
    {
        icon: "layers",
        name: "Layers",
        body: "Opens the map's power plant filters — by fuel type, state and minimum capacity.",
    },
    {
        icon: "analytics",
        name: "Pro analytics",
        body: "Energy vs GDP correlation, emissions vs renewables, state efficiency benchmarks and carbon emissions.",
    },
    {
        icon: "description",
        name: "Sector reports",
        body: "Overview, solar, wind, coal & thermal and the national grid, each built from source data.",
    },
    {
        icon: "database",
        name: "Datasets",
        body: "Every dataset behind the atlas, with its source, coverage and snapshot date, openable as raw JSON.",
    },
];

export default function HelpDialog({
    open,
    onClose,
    onNavigate,
}: {
    open: boolean;
    onClose: () => void;
    onNavigate: Navigate;
}) {
    return (
        <Modal open={open} onClose={onClose} title="Help" subtitle="What each part of the atlas does." width="max-w-xl">
            <div className="space-y-6">
                <ul className="space-y-3">
                    {VIEWS.map((v) => (
                        <li key={v.name} className="flex gap-3">
                            <span className="material-symbols-outlined text-[20px] text-[#20d3ee] shrink-0">{v.icon}</span>
                            <div>
                                <p className="text-sm font-semibold text-white">{v.name}</p>
                                <p className="text-xs text-slate-400 leading-relaxed">{v.body}</p>
                            </div>
                        </li>
                    ))}
                </ul>

                <div className="pt-5 border-t border-[#262C3A] space-y-2">
                    <p className="text-xs font-bold text-slate-400 uppercase tracking-widest">Where the data comes from</p>
                    <p className="text-xs text-slate-400 leading-relaxed">
                        Capacity, generation, peak demand and transmission come from the Central Electricity
                        Authority; solar and wind resource from the Global Solar and Wind Atlases; coal output
                        from Coal India. The CEA snapshot is refreshed daily when its API is reachable.
                    </p>
                    <p className="text-xs text-amber-400/90 leading-relaxed">
                        Live generation and market prices are simulated from installed capacity, not live feeds.
                    </p>
                    <button
                        onClick={() => {
                            onClose();
                            onNavigate({ view: "datasets" });
                        }}
                        className="mt-1 text-xs font-semibold text-[#20d3ee] hover:underline"
                    >
                        Browse the datasets →
                    </button>
                </div>
            </div>
        </Modal>
    );
}
