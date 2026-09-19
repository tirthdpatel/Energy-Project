/**
 * User preferences, persisted in localStorage.
 *
 * Read through useSyncExternalStore so the server render and first client
 * render both use the defaults (no hydration mismatch), after which stored
 * values take over.
 */
import { useSyncExternalStore } from "react";
import type { View } from "@/lib/navigation";

export interface Settings {
    /** View shown when the app opens. */
    startView: View;
    /** Year the map timeline starts on. */
    startYear: number;
    /** Skip view-transition animations. */
    reduceMotion: boolean;
}

export const YEAR_RANGE = { min: 2019, max: 2026 } as const;

export const DEFAULT_SETTINGS: Settings = {
    startView: "map",
    startYear: YEAR_RANGE.max,
    reduceMotion: false,
};

const KEY = "india-energy-atlas.settings.v1";
const VIEWS: View[] = ["map", "simple", "pro", "datasets"];

let cache: Settings | null = null;
const listeners = new Set<() => void>();

function sanitize(raw: unknown): Settings {
    const s = (raw && typeof raw === "object" ? raw : {}) as Partial<Settings>;
    const year = Number(s.startYear);
    return {
        startView: VIEWS.includes(s.startView as View) ? (s.startView as View) : DEFAULT_SETTINGS.startView,
        startYear:
            Number.isInteger(year) && year >= YEAR_RANGE.min && year <= YEAR_RANGE.max
                ? year
                : DEFAULT_SETTINGS.startYear,
        reduceMotion: typeof s.reduceMotion === "boolean" ? s.reduceMotion : DEFAULT_SETTINGS.reduceMotion,
    };
}

function read(): Settings {
    try {
        const raw = window.localStorage.getItem(KEY);
        return raw ? sanitize(JSON.parse(raw)) : DEFAULT_SETTINGS;
    } catch {
        // Private mode or blocked storage: fall back to defaults.
        return DEFAULT_SETTINGS;
    }
}

function getSnapshot(): Settings {
    if (cache === null) cache = read();
    return cache;
}

function getServerSnapshot(): Settings {
    return DEFAULT_SETTINGS;
}

function subscribe(listener: () => void): () => void {
    listeners.add(listener);
    return () => listeners.delete(listener);
}

export function saveSettings(next: Settings): void {
    cache = sanitize(next);
    try {
        window.localStorage.setItem(KEY, JSON.stringify(cache));
    } catch {
        /* storage unavailable — keep the in-memory value for this session */
    }
    listeners.forEach((l) => l());
}

export function resetSettings(): void {
    saveSettings(DEFAULT_SETTINGS);
}

export function useSettings(): Settings {
    return useSyncExternalStore(subscribe, getSnapshot, getServerSnapshot);
}
