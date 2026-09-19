/**
 * Centralized API layer — all fetch logic goes here.
 * No direct fetch calls allowed in components.
 */
import type {
    StateSummary,
    StateDetail,
    GeoJSONFeatureCollection,
    YearsMeta,
    PowerPlantFilterStats,
    AnalyticsMeta,
    CorrelationResult,
    ComparisonResult,
    InsightsResult,
    LiveGenerationResponse,
    LiveMarketResponse,
    SectorSummary,
    SectorDetail,
    DatasetEntry,
} from "@/types";

// API requests are same-origin and handled by the Next.js rewrite in next.config.ts,
// which proxies /api/* to the FastAPI backend (localhost in dev, API_BASE_URL in prod).
const API = "";

/** Shared fetch wrapper with error handling. */
async function apiFetch<T>(path: string): Promise<T> {
    let res: Response;
    try {
        res = await fetch(`${API}${path}`);
    } catch {
        throw new Error(
            `Network error: backend unreachable at ${API}${path}. Is the server running?`
        );
    }
    if (!res.ok) {
        const body = await res.text().catch(() => "");
        throw new Error(`API ${res.status}: ${res.statusText} — ${path} ${body}`);
    }
    return res.json() as Promise<T>;
}

/** GET /api/states → [{id, name, code}] */
export function fetchStates(): Promise<StateSummary[]> {
    return apiFetch<StateSummary[]>("/api/states");
}

/** GET /api/states/{id}?year=&start=&end= → full computed detail */
export function fetchStateDetail(
    stateId: string,
    params?: { year?: number; start?: number; end?: number }
): Promise<StateDetail> {
    const qs = new URLSearchParams();
    if (params?.year !== undefined) qs.set("year", String(params.year));
    if (params?.start !== undefined) qs.set("start", String(params.start));
    if (params?.end !== undefined) qs.set("end", String(params.end));
    const query = qs.toString();
    return apiFetch<StateDetail>(
        `/api/states/${stateId}${query ? `?${query}` : ""}`
    );
}

/** GET /api/states/geojson → FeatureCollection */
export function fetchGeoJSON(): Promise<GeoJSONFeatureCollection> {
    return apiFetch<GeoJSONFeatureCollection>("/api/states/geojson");
}

/** GET /api/meta/years → {min_year, max_year} */
export function fetchYearsMeta(): Promise<YearsMeta> {
    return apiFetch<YearsMeta>("/api/meta/years");
}

/** GET /api/generation/live → LiveGenerationResponse */
export function fetchLiveGeneration(): Promise<LiveGenerationResponse> {
    return apiFetch<LiveGenerationResponse>("/api/generation/live");
}

/** GET /api/power-plants?state=&type=&min_capacity= → GeoJSON FeatureCollection */
export function fetchPowerPlants(filters?: {
    states?: string[];
    types?: string[];
    minCapacity?: number;
}): Promise<GeoJSONFeatureCollection> {
    const qs = new URLSearchParams();
    if (filters?.states?.length) qs.set("state", filters.states.join(","));
    if (filters?.types?.length) qs.set("type", filters.types.join(","));
    if (filters?.minCapacity !== undefined && filters.minCapacity > 0)
        qs.set("min_capacity", String(filters.minCapacity));
    const query = qs.toString();
    return apiFetch<GeoJSONFeatureCollection>(
        `/api/power-plants${query ? `?${query}` : ""}`
    );
}

/** GET /api/power-plants/stats → filter metadata */
export function fetchPowerPlantStats(): Promise<PowerPlantFilterStats> {
    return apiFetch<PowerPlantFilterStats>("/api/power-plants/stats");
}

/* ── Analytics API ─── */

/** GET /api/analytics/meta → available states & year range */
export function fetchAnalyticsMeta(): Promise<AnalyticsMeta> {
    return apiFetch<AnalyticsMeta>("/api/analytics/meta");
}

/** GET /api/analytics/correlation?year= → correlation results */
export function fetchCorrelation(year?: number): Promise<CorrelationResult> {
    const qs = year !== undefined ? `?year=${year}` : "";
    return apiFetch<CorrelationResult>(`/api/analytics/correlation${qs}`);
}

/** GET /api/analytics/compare?states=...&year= → comparison results */
export function fetchComparison(stateIds: string[], year?: number): Promise<ComparisonResult> {
    const qs = new URLSearchParams();
    qs.set("states", stateIds.join(","));
    if (year !== undefined) qs.set("year", String(year));
    return apiFetch<ComparisonResult>(`/api/analytics/compare?${qs.toString()}`);
}

/* ── Insights API ─── */

/** GET /api/insights/state?state_id= → auto-generated insights */
export function fetchInsights(stateId?: string): Promise<InsightsResult> {
    const qs = stateId ? `?state_id=${stateId}` : "";
    return apiFetch<InsightsResult>(`/api/insights/state${qs}`);
}

/* ── Market API ─── */
export function fetchLiveMarketPricing(): Promise<LiveMarketResponse> {
    return apiFetch<LiveMarketResponse>("/api/market/pricing/live");
}


/* ── Emissions API ─── */

/** GET /api/analytics/emissions/state?year= → per-state CO₂ output */
export function fetchStateEmissions<T>(year: number): Promise<{ year: number; data: T[] }> {
    return apiFetch<{ year: number; data: T[] }>(
        `/api/analytics/emissions/state?year=${year}`
    );
}

/** GET /api/analytics/emissions/trend → national CO₂ totals by year */
export function fetchEmissionsTrend<T>(): Promise<{ data: T[] }> {
    return apiFetch<{ data: T[] }>("/api/analytics/emissions/trend");
}

/* ── Sectors API ─── */

/** GET /api/sectors → sidebar sector list */
export function fetchSectors(): Promise<{ sectors: SectorSummary[] }> {
    return apiFetch<{ sectors: SectorSummary[] }>("/api/sectors");
}

/** GET /api/sectors/{id} → metrics, chart and table for one sector */
export function fetchSector(sectorId: string): Promise<SectorDetail> {
    return apiFetch<SectorDetail>(`/api/sectors/${sectorId}`);
}

/* ── Datasets API ─── */

/** GET /api/datasets → catalogue of every dataset the atlas serves */
export function fetchDatasets(): Promise<{ datasets: DatasetEntry[] }> {
    return apiFetch<{ datasets: DatasetEntry[] }>("/api/datasets");
}

/** Same-origin URL of one dataset's raw JSON. */
export function datasetUrl(datasetId: string): string {
    return `${API}/api/datasets/${datasetId}`;
}
