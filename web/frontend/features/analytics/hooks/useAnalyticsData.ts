import { useState, useEffect, useMemo } from "react";
import type {
    AnalyticsMeta,
    CorrelationResult,
    LiveMarketResponse,
} from "@/types";
import { fetchAnalyticsMeta, fetchCorrelation, fetchLiveMarketPricing } from "@/lib/api";

export function useAnalyticsData() {
    const [meta, setMeta] = useState<AnalyticsMeta | null>(null);
    const [year, setYear] = useState<number>(2026);
    const [selectedStates, setSelectedStates] = useState<Set<string>>(new Set());
    const [data, setData] = useState<CorrelationResult | null>(null);
    const [marketData, setMarketData] = useState<LiveMarketResponse | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        fetchAnalyticsMeta()
            .then((m) => {
                setMeta(m);
                setYear(m.years.max_year);
                setSelectedStates(new Set(m.states));
            })
            .catch((e) => setError(e.message));

        fetchLiveMarketPricing()
            .then(setMarketData)
            .catch(console.error);
    }, []);

    useEffect(() => {
        setTimeout(() => {
            setLoading(true);
            setError(null);
        }, 0);
        fetchCorrelation(year)
            .then((d) => {
                setData(d);
                setLoading(false);
            })
            .catch((e) => {
                setError(e.message);
                setLoading(false);
            });
    }, [year]);

    const filteredData = useMemo(() => {
        if (!data) return [];
        return data.state_data.filter((s) => selectedStates.has(s.state_id));
    }, [data, selectedStates]);

    const scatterDataGDP = useMemo(() => {
        return filteredData.map((s) => ({
            x: s.gdp_billion_inr ?? 0,
            y: (s.total_capacity_mw ?? 0) / 1000,
            name: s.state,
            tier: (s.gdp_billion_inr ?? 0) > 5000 ? "top" : "emerging",
        }));
    }, [filteredData]);

    const scatterDataEmissions = useMemo(() => {
        return filteredData.map((s) => ({
            x: s.renewable_share_percent ?? 0,
            y: s.total_emissions_mt ?? 0,
            name: s.state,
            risk: (s.total_emissions_mt ?? 0) > 0.5 ? "high" : "low",
        }));
    }, [filteredData]);

    const correlationIndex = data?.correlation_energy_gdp ?? 0;
    const energyIntensity = data
        ? (
            filteredData.reduce((a, s) => a + (s.total_capacity_mw ?? 0), 0) /
            filteredData.reduce((a, s) => a + (s.gdp_billion_inr ?? 1), 0)
        ).toFixed(1)
        : "—";
    const emissionsIntensity = data
        ? (
            filteredData.reduce((a, s) => a + (s.total_emissions_mt ?? 0), 0) /
            (filteredData.length || 1)
        ).toFixed(2)
        : "—";
    const renewableShare = data
        ? (
            (filteredData.reduce((a, s) => a + (s.renewable_share_percent ?? 0), 0) /
                (filteredData.length || 1))
        ).toFixed(1)
        : "—";

    return {
        meta,
        year,
        setYear,
        selectedStates,
        setSelectedStates,
        data,
        marketData,
        loading,
        error,
        filteredData,
        scatterDataGDP,
        scatterDataEmissions,
        correlationIndex,
        energyIntensity,
        emissionsIntensity,
        renewableShare
    };
}
