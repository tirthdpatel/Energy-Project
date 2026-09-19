"use client";

import Modal from "@/components/Modal";
import {
    DEFAULT_SETTINGS,
    YEAR_RANGE,
    resetSettings,
    saveSettings,
    useSettings,
} from "@/lib/settings";
import type { View } from "@/lib/navigation";

const VIEW_OPTIONS: { value: View; label: string }[] = [
    { value: "map", label: "Map" },
    { value: "simple", label: "Simple — sector reports" },
    { value: "pro", label: "Pro — analytics" },
    { value: "datasets", label: "Datasets" },
];

const YEARS = Array.from(
    { length: YEAR_RANGE.max - YEAR_RANGE.min + 1 },
    (_, i) => YEAR_RANGE.max - i,
);

const fieldClass =
    "w-full bg-[#0F1115] border border-[#262C3A] rounded px-3 py-2 text-sm text-slate-200 focus:border-[#20d3ee] focus:outline-none";

export default function SettingsDialog({ open, onClose }: { open: boolean; onClose: () => void }) {
    const settings = useSettings();
    const isDefault =
        settings.startView === DEFAULT_SETTINGS.startView &&
        settings.startYear === DEFAULT_SETTINGS.startYear &&
        settings.reduceMotion === DEFAULT_SETTINGS.reduceMotion;

    return (
        <Modal
            open={open}
            onClose={onClose}
            title="Settings"
            subtitle="Saved in this browser. Changes apply immediately."
        >
            <div className="space-y-6">
                <label className="block">
                    <span className="block text-xs font-bold text-slate-400 uppercase tracking-widest mb-2">
                        Start view
                    </span>
                    <select
                        className={fieldClass}
                        value={settings.startView}
                        onChange={(e) => saveSettings({ ...settings, startView: e.target.value as View })}
                    >
                        {VIEW_OPTIONS.map((o) => (
                            <option key={o.value} value={o.value}>{o.label}</option>
                        ))}
                    </select>
                    <span className="block text-[11px] text-slate-500 mt-1.5">
                        The view the atlas opens on next time.
                    </span>
                </label>

                <label className="block">
                    <span className="block text-xs font-bold text-slate-400 uppercase tracking-widest mb-2">
                        Map start year
                    </span>
                    <select
                        className={fieldClass}
                        value={settings.startYear}
                        onChange={(e) => saveSettings({ ...settings, startYear: Number(e.target.value) })}
                    >
                        {YEARS.map((y) => (
                            <option key={y} value={y}>{y}</option>
                        ))}
                    </select>
                    <span className="block text-[11px] text-slate-500 mt-1.5">
                        Where the map&apos;s timeline scrubber starts.
                    </span>
                </label>

                <label className="flex items-start justify-between gap-4 cursor-pointer">
                    <span>
                        <span className="block text-xs font-bold text-slate-400 uppercase tracking-widest mb-1">
                            Reduce motion
                        </span>
                        <span className="block text-[11px] text-slate-500">
                            Switch views instantly instead of sliding between them.
                        </span>
                    </span>
                    <input
                        type="checkbox"
                        className="mt-1 h-4 w-4 accent-[#20d3ee]"
                        checked={settings.reduceMotion}
                        onChange={(e) => saveSettings({ ...settings, reduceMotion: e.target.checked })}
                    />
                </label>

                <div className="pt-4 border-t border-[#262C3A] flex justify-end">
                    <button
                        onClick={resetSettings}
                        disabled={isDefault}
                        className="text-xs font-semibold text-slate-400 hover:text-white disabled:opacity-40 disabled:hover:text-slate-400 transition-colors"
                    >
                        Reset to defaults
                    </button>
                </div>
            </div>
        </Modal>
    );
}
