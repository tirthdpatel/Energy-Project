/* ── India Energy Atlas — Type Definitions (v3) ─── */

/** Summary returned by GET /api/states */
export interface StateSummary {
    id: string;
    name: string;
    code: string;
}

/** Capacity breakdown per source */
export interface CapacityBreakdown {
    solar: number;
    wind: number;
    hydro: number;
    nuclear: number;
    bioenergy: number;
}

/** Capacity section in state detail response */
export interface CapacityInfo {
    selected_year: number;
    total_mw: number;
    breakdown: CapacityBreakdown;
}

/** Generation section in state detail response */
export interface GenerationInfo {
    selected_year: number;
    total_gwh: number;
}

/** Single entry in the dynamically computed energy mix */
export interface EnergyMixItem {
    source: string;
    value: number;
}

/** Single data point in the capacity trend */
export interface TrendPoint {
    year: number;
    total_capacity_mw: number;
}

/** Full detail returned by GET /api/states/{id}?year=&start=&end= */
export interface StateDetail {
    id: string;
    name: string;
    code: string;
    capacity: CapacityInfo;
    generation: GenerationInfo;
    mix: EnergyMixItem[];
    trend: TrendPoint[];
}

/** Available year range returned by GET /api/meta/years */
export interface YearsMeta {
    min_year: number;
    max_year: number;
}

/* ── Live Generation types ─── */
export interface LiveStateGeneration {
    state_id: string;
    state_name: string;
    current_generation_mw: number;
    utilization_pct: number;
    mix: Record<string, number>;
}

export interface LiveGenerationResponse {
    timestamp: string;
    national_total_mw: number;
    states: Record<string, LiveStateGeneration>;
}

/* ── Market Pricing types ─── */
export interface MarketPrice {
    state_id: string;
    price_inr_per_mwh: number;
    status: string;
}

export interface LiveMarketResponse {
    timestamp: string;
    prices: MarketPrice[];
}

/* ── GeoJSON types (minimal, no `any`) ─── */

export interface GeoJSONGeometry {
    type: string;
    coordinates: number[][][] | number[][][][];
}

export interface GeoJSONProperties {
    NAME_1: string;
    state_id: string;
    code: string;
    [key: string]: string | number | boolean | null;
}

export interface GeoJSONFeature {
    type: "Feature";
    properties: GeoJSONProperties;
    geometry: GeoJSONGeometry;
}

export interface GeoJSONFeatureCollection {
    type: "FeatureCollection";
    features: GeoJSONFeature[];
}

/* ── Power Plant types ─── */

/** Properties on each power plant GeoJSON feature */
export interface PowerPlantProperties {
    name: string;
    type: string;         // coal, solar, hydro, wind, nuclear, gas, biomass, other
    capacity_mw: number;
    operator: string;
    state: string;
    osm_id: string;
    [key: string]: string | number | boolean | null;
}

/** Filter stats returned by GET /api/power-plants/stats */
export interface PowerPlantFilterStats {
    states: string[];
    types: string[];
    min_capacity: number;
    max_capacity: number;
    total_plants: number;
}

/** Active filters for power plant queries */
export interface PowerPlantFilters {
    states: string[];
    types: string[];
    minCapacity: number;
}

/* ── Analytics types ─── */

/** Metadata for analytics endpoints */
export interface AnalyticsMeta {
    states: string[];
    years: { min_year: number; max_year: number };
}

/** Per-state analytics row returned in correlation & comparison */
export interface StateAnalyticsEntry {
    state_id: string;
    state: string;
    gdp_billion_inr: number;
    total_capacity_mw: number;
    renewable_share_percent: number;
    coal_emissions_mt: number;
    total_emissions_mt: number;
    energy_intensity: number;
    emissions_intensity: number;
}

/** GET /analytics/correlation response */
export interface CorrelationResult {
    year: number;
    correlation_energy_gdp: number | null;
    correlation_renewable_gdp: number | null;
    correlation_emissions_gdp: number | null;
    correlation_coal_emissions_gdp: number | null;
    states_count: number;
    state_data: StateAnalyticsEntry[];
}

/** GET /analytics/compare response */
export interface ComparisonResult {
    year: number;
    states_compared: number;
    correlation_energy_gdp: number | null;
    state_comparison: StateAnalyticsEntry[];
}

/* ── Insight types ─── */

export interface InsightCard {
    icon: string;
    title: string;
    body: string;
    trend: "rising" | "falling" | "stable";
    color: string;
}

export interface InsightTrendPoint {
    year: number;
    gdp_billion_inr: number;
    total_capacity_mw: number;
    renewable_share_percent: number;
    total_emissions_mt: number;
}

export interface InsightsResult {
    state_id: string | null;
    state: string;
    year: number;
    insights: InsightCard[];
    rankings: Record<string, number> | Record<string, { rank: number; state_id: string; state: string; value: number }[]>;
    total_states: number;
    trend_data: InsightTrendPoint[];
}

/* ── Sector dashboards (Simple view) ─── */

export interface SectorSummary {
    id: string;
    label: string;
    icon: string;
}

export interface SectorMetric {
    label: string;
    value: string;
    unit: string;
    change_pct: number;
    trend: "up" | "down" | "flat";
    sub: string;
}

export interface SectorChartSeries {
    key: string;
    label: string;
    color: string;
}

export interface SectorChart {
    title: string;
    subtitle: string;
    unit: string;
    x_key: string;
    series: SectorChartSeries[];
    data: Record<string, string | number>[];
}

export interface SectorTableColumn {
    key: string;
    label: string;
    numeric?: boolean;
}

export interface SectorTable {
    title: string;
    subtitle?: string;
    columns: SectorTableColumn[];
    rows: Record<string, string | number>[];
}

export interface SectorDetail extends SectorSummary {
    headline: string;
    subtitle: string;
    as_of: string;
    metrics: SectorMetric[];
    chart: SectorChart;
    table: SectorTable;
    source: string;
}

/* ── Dataset catalogue ─── */

export interface DatasetEntry {
    id: string;
    name: string;
    publisher: string;
    kind: "scraped" | "simulated";
    source_url?: string;
    snapshot?: string | null;
    records?: number;
    coverage?: { from: string; to: string } | null;
    available?: boolean;
    note?: string;
}
