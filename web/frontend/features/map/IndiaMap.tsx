"use client";

import { useRef, useEffect, useCallback, useState } from "react";
import maplibregl from "maplibre-gl";
import "maplibre-gl/dist/maplibre-gl.css";
import { fetchGeoJSON, fetchPowerPlants, fetchLiveGeneration } from "@/lib/api";
import type { GeoJSONFeatureCollection, PowerPlantFilters, LiveGenerationResponse } from "@/types";
import PowerPlantFilterPanel from "./PowerPlantFilters";
import TimeScrubber from "../../components/TimeScrubber";

/** Free dark vector tile style — no API key required */
const FREE_DARK_STYLE =
    "https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json";

/** Color map for energy type markers */
const TYPE_COLORS: Record<string, string> = {
    coal: "#ef4444",
    solar: "#eab308",
    hydro: "#3b82f6",
    wind: "#22c55e",
    nuclear: "#a855f7",
    gas: "#f97316",
    biomass: "#84cc16",
    other: "#94a3b8",
    unknown: "#64748b",
};

interface Props {
    onStateSelect: (stateId: string, stateName?: string) => void;
    onPlantSelect?: (plant: any) => void;
    selectedStateId: string | null;
    selectedYear: number;
    onYearChange: (year: number) => void;
}

export default function IndiaMap({ onStateSelect, onPlantSelect, selectedStateId, selectedYear, onYearChange }: Props) {
    const mapContainer = useRef<HTMLDivElement>(null);
    const mapRef = useRef<maplibregl.Map | null>(null);
    const hoveredId = useRef<string | number | null>(null);
    const popupRef = useRef<maplibregl.Popup | null>(null);
    const popupTimeoutRef = useRef<NodeJS.Timeout | null>(null);
    const [mapError, setMapError] = useState<string | null>(null);
    const [mapLoaded, setMapLoaded] = useState(false);

    // Power plant filter state
    const [plantFilters, setPlantFilters] = useState<PowerPlantFilters>({
        states: [],
        types: [],
        minCapacity: 0,
    });
    const [plantCount, setPlantCount] = useState(0);
    const [filtersVisible, setFiltersVisible] = useState(false);

    // View mode state
    const [viewMode, setViewMode] = useState<"capacity" | "live">("capacity");
    const liveDataRef = useRef<LiveGenerationResponse | null>(null);
    const [isPlaying, setIsPlaying] = useState(false);

    // Advanced Map State
    const [is3D, setIs3D] = useState(false);
    const [isSatellite, setIsSatellite] = useState(false);

    const handleClick = useCallback(
        (
            e: maplibregl.MapMouseEvent & {
                features?: maplibregl.MapGeoJSONFeature[];
            }
        ) => {
            const map = mapRef.current;
            if (!map) return;

            let plantFeatures: maplibregl.MapGeoJSONFeature[] = [];
            try {
                const activeLayers = ["power-plants-circle", "power-plants-cluster"].filter(l => map.getLayer(l));
                if (activeLayers.length > 0) {
                    plantFeatures = map.queryRenderedFeatures(e.point, { layers: activeLayers });
                }
            } catch (err) {
                console.warn(err);
            }
            if (plantFeatures.length > 0) return;

            const feature = e.features?.[0];
            if (!feature) return;

            /* Use enriched state_id from backend GeoJSON */
            const stateId = feature.properties?.state_id as string | undefined;
            const name = feature.properties?.NAME_1 as string | undefined;
            if (!stateId || !name) return;

            onStateSelect(stateId, name);

            /* ── Fly-to animation ── */
            // Compute centroid from bounds
            const geom = feature.geometry;
            if (geom && geom.type !== "GeometryCollection" && "coordinates" in geom) {
                const bounds = new maplibregl.LngLatBounds();
                const coords =
                    geom.type === "MultiPolygon"
                        ? (geom.coordinates as number[][][][]).flat(2)
                        : (geom.coordinates as number[][][]).flat();
                coords.forEach((c: number[]) => bounds.extend(c as [number, number]));
                const center = bounds.getCenter();
                map.flyTo({ center, zoom: 6, duration: 1200, essential: true });
            }
        },
        [onStateSelect]
    );

    // ── Load & update power plant markers ──
    const loadPowerPlants = useCallback(
        async (filters: PowerPlantFilters) => {
            const map = mapRef.current;
            if (!map || !map.isStyleLoaded()) return;

            try {
                // Only skip if user is explicitly filtering but nothing is selected.
                // On initial load (filtersVisible=false), we still show all plants.
                const showEmpty =
                    filtersVisible &&
                    filters.types.length === 0 &&
                    filters.states.length === 0 &&
                    filters.minCapacity === 0;

                let data: GeoJSONFeatureCollection;
                if (showEmpty) {
                    // User reset all filters → show nothing
                    data = { type: "FeatureCollection", features: [] };
                } else {
                    data = await fetchPowerPlants({
                        states: filters.states,
                        types: filters.types,
                        minCapacity: filters.minCapacity,
                    });
                }

                setPlantCount(data.features.length);

                const src = map.getSource("power-plants") as maplibregl.GeoJSONSource | undefined;
                if (src) {
                    src.setData(data as unknown as GeoJSON.GeoJSON);
                } else {
                    // First load — add source and layers
                    map.addSource("power-plants", {
                        type: "geojson",
                        data: data as unknown as GeoJSON.FeatureCollection,
                        cluster: true,
                        clusterMaxZoom: 14,
                        clusterRadius: 50,
                    });

                    // Circle layer — color by type, size by capacity
                    map.addLayer({
                        id: "power-plants-circle",
                        type: "circle",
                        source: "power-plants",
                        filter: ["!", ["has", "point_count"]],
                        paint: {
                            "circle-radius": [
                                "interpolate",
                                ["linear"],
                                ["get", "capacity_mw"],
                                0, 3,
                                100, 5,
                                500, 8,
                                1000, 11,
                                5000, 16,
                            ],
                            "circle-color": [
                                "match",
                                ["get", "type"],
                                "coal", TYPE_COLORS.coal,
                                "solar", TYPE_COLORS.solar,
                                "hydro", TYPE_COLORS.hydro,
                                "wind", TYPE_COLORS.wind,
                                "nuclear", TYPE_COLORS.nuclear,
                                "gas", TYPE_COLORS.gas,
                                "biomass", TYPE_COLORS.biomass,
                                TYPE_COLORS.other,
                            ],
                            "circle-opacity": 0.8,
                            "circle-stroke-width": 1,
                            "circle-stroke-color": "#0f172a",
                            "circle-stroke-opacity": 0.6,
                        },
                    });

                    // Glow layer behind circles
                    map.addLayer(
                        {
                            id: "power-plants-glow",
                            type: "circle",
                            source: "power-plants",
                            filter: ["!", ["has", "point_count"]],
                            paint: {
                                "circle-radius": [
                                    "interpolate",
                                    ["linear"],
                                    ["get", "capacity_mw"],
                                    0, 8,
                                    100, 12,
                                    500, 18,
                                    1000, 24,
                                    5000, 35,
                                ],
                                "circle-color": [
                                    "match",
                                    ["get", "type"],
                                    "coal", TYPE_COLORS.coal,
                                    "solar", TYPE_COLORS.solar,
                                    "hydro", TYPE_COLORS.hydro,
                                    "wind", TYPE_COLORS.wind,
                                    "nuclear", TYPE_COLORS.nuclear,
                                    "gas", TYPE_COLORS.gas,
                                    "biomass", TYPE_COLORS.biomass,
                                    TYPE_COLORS.other,
                                ],
                                "circle-opacity": 0.15,
                                "circle-blur": 1,
                            },
                        },
                        "power-plants-circle" // insert below the main circle layer
                    );

                    // Cluster layer
                    map.addLayer({
                        id: "power-plants-cluster",
                        type: "circle",
                        source: "power-plants",
                        filter: ["has", "point_count"],
                        paint: {
                            "circle-color": [
                                "step",
                                ["get", "point_count"],
                                "#3b82f6",
                                10, "#eab308",
                                50, "#ef4444"
                            ],
                            "circle-radius": [
                                "step",
                                ["get", "point_count"],
                                16,
                                10, 22,
                                50, 30
                            ],
                            "circle-stroke-width": 1,
                            "circle-stroke-color": "#0f172a",
                            "circle-opacity": 0.85
                        }
                    });

                    // Cluster count labels
                    map.addLayer({
                        id: "power-plants-cluster-count",
                        type: "symbol",
                        source: "power-plants",
                        filter: ["has", "point_count"],
                        layout: {
                            "text-field": "{point_count_abbreviated}",
                            "text-size": 12
                        },
                        paint: {
                            "text-color": "#ffffff"
                        }
                    });

                    // ── Click cluster to expand ──
                    map.on("click", "power-plants-cluster", async (e) => {
                        const features = map.queryRenderedFeatures(e.point, {
                            layers: ["power-plants-cluster"]
                        });
                        const clusterId = features[0].properties?.cluster_id;
                        const src = map.getSource("power-plants") as maplibregl.GeoJSONSource;
                        try {
                            const zoom = await src.getClusterExpansionZoom(clusterId);
                            map.easeTo({
                                center: (features[0].geometry as GeoJSON.Point).coordinates as [number, number],
                                zoom: zoom
                            });
                        } catch (err) {
                            console.error(err);
                        }
                    });

                    // Cursor interactions for clusters
                    map.on("mouseenter", "power-plants-cluster", () => {
                        map.getCanvas().style.cursor = "pointer";
                    });
                    map.on("mouseleave", "power-plants-cluster", () => {
                        map.getCanvas().style.cursor = "";
                    });

                    // ── Click plant ──
                    map.on("click", "power-plants-circle", (e) => {
                        const feat = e.features?.[0];
                        if (!feat) return;
                        if (onPlantSelect) {
                            onPlantSelect(feat.properties);
                        }
                    });

                    // ── Hover popup ──
                    map.on("mouseenter", "power-plants-circle", (e) => {
                        map.getCanvas().style.cursor = "pointer";
                        if (popupTimeoutRef.current) {
                            clearTimeout(popupTimeoutRef.current);
                            popupTimeoutRef.current = null;
                        }
                        const feat = e.features?.[0];
                        if (!feat) return;
                        const props = feat.properties;
                        const coords = (feat.geometry as GeoJSON.Point).coordinates.slice() as [number, number];

                        // Close any existing popup
                        if (popupRef.current) popupRef.current.remove();

                        const cap =
                            props.capacity_mw > 0
                                ? `${Number(props.capacity_mw).toLocaleString()} MW`
                                : "Unknown";
                        const typeLabel =
                            String(props.type).charAt(0).toUpperCase() +
                            String(props.type).slice(1);
                        const color = TYPE_COLORS[props.type as string] || TYPE_COLORS.other;

                        const html = `
                            <div style="font-family: 'Inter', sans-serif; min-width: 200px;">
                                <div style="font-size: 14px; font-weight: 600; color: #ffffff; margin-bottom: 8px;">
                                    ${props.name}
                                </div>
                                <div style="display: flex; align-items: center; gap: 6px; margin-bottom: 4px;">
                                    <span style="width: 8px; height: 8px; border-radius: 50%; background: ${color}; display: inline-block;"></span>
                                    <span style="font-size: 12px; color: #cbd5e1;">${typeLabel}</span>
                                </div>
                                <div style="font-size: 12px; color: #cbd5e1; margin-bottom: 2px;">
                                    <strong style="color: #e2e8f0;">Capacity:</strong> ${cap}
                                </div>
                                <div style="font-size: 12px; color: #cbd5e1; margin-bottom: 2px;">
                                    <strong style="color: #e2e8f0;">Operator:</strong> ${props.operator}
                                </div>
                                <div style="font-size: 12px; color: #cbd5e1; margin-bottom: 2px;">
                                    <strong style="color: #e2e8f0;">State:</strong> ${props.state}
                                </div>
                                <a href="https://www.openstreetmap.org/${props.osm_id}"
                                   target="_blank" rel="noopener noreferrer"
                                   style="font-size: 11px; color: #38bdf8; text-decoration: none; display: inline-block; margin-top: 4px; font-weight: 500;">
                                   View on OpenStreetMap →
                                </a>
                            </div>
                        `;

                        popupRef.current = new maplibregl.Popup({
                            closeButton: false, // Turn off close button since it's hover-based now
                            closeOnClick: false,
                            maxWidth: "280px",
                            className: "plant-popup",
                        })
                            .setLngLat(coords)
                            .setHTML(html)
                            .addTo(map);

                        const popupElem = popupRef.current.getElement();
                        if (popupElem) {
                            const contentElem = popupElem.querySelector(".maplibregl-popup-content");
                            if (contentElem) {
                                contentElem.addEventListener("mouseenter", () => {
                                    if (popupTimeoutRef.current) {
                                        clearTimeout(popupTimeoutRef.current);
                                        popupTimeoutRef.current = null;
                                    }
                                });
                                contentElem.addEventListener("mouseleave", () => {
                                    popupTimeoutRef.current = setTimeout(() => {
                                        if (popupRef.current) {
                                            popupRef.current.remove();
                                            popupRef.current = null;
                                        }
                                    }, 300);
                                });
                            }
                        }
                    });

                    // Cursor change and popup close on mouseleave
                    map.on("mouseleave", "power-plants-circle", () => {
                        map.getCanvas().style.cursor = "";
                        popupTimeoutRef.current = setTimeout(() => {
                            if (popupRef.current) {
                                popupRef.current.remove();
                                popupRef.current = null;
                            }
                        }, 300);
                    });
                }
            } catch (err) {
                console.error("Failed to load power plants:", err);
            }
        },
        // filtersVisible is read inside the callback; onPlantSelect is called inside it
        [filtersVisible, onPlantSelect]
    );

    // Reload power plants when filters change
    useEffect(() => {
        if (mapLoaded) {
            loadPowerPlants(plantFilters);
        }
    }, [plantFilters, mapLoaded, loadPowerPlants]);

    useEffect(() => {
        if (!mapContainer.current) return;

        const map = new maplibregl.Map({
            container: mapContainer.current,
            style: FREE_DARK_STYLE,
            center: [82.5, 22.5],
            zoom: 4.2,
            minZoom: 3,
            maxZoom: 12,
            attributionControl: false,
        });

        map.addControl(new maplibregl.NavigationControl(), "bottom-left");
        map.addControl(
            new maplibregl.AttributionControl({ compact: true }),
            "bottom-right"
        );

        map.on("load", async () => {
            /* Fetch GeoJSON and Live Generation from our backend API */
            let geojson: GeoJSONFeatureCollection;
            try {
                const [fetchedGeo, fetchedLive] = await Promise.all([
                    fetchGeoJSON(),
                    fetchLiveGeneration().catch((e) => {
                        console.error("Live generation not available yet", e);
                        return null;
                    })
                ]);
                geojson = fetchedGeo;
                if (fetchedLive) liveDataRef.current = fetchedLive;

                // Inject live data into GeoJSON properties for styling
                geojson.features.forEach(f => {
                    const stId = f.properties.state_id as string;
                    if (liveDataRef.current && liveDataRef.current.states[stId]) {
                        f.properties.live_utilization = liveDataRef.current.states[stId].utilization_pct;
                    } else {
                        f.properties.live_utilization = 0;
                    }
                });

            } catch (err) {
                console.error("Failed to load map data:", err);
                setMapError("Failed to load map data. Is the backend running?");
                return;
            }

            map.addSource("india-states", {
                type: "geojson",
                data: geojson as unknown as GeoJSON.FeatureCollection,
                generateId: true,
            });

            // Satellite Raster Source
            map.addSource("satellite-tiles", {
                type: "raster",
                tiles: [
                    "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
                ],
                tileSize: 256
            });

            // Satellite Layer (Bottom)
            map.addLayer({
                id: "satellite-layer",
                type: "raster",
                source: "satellite-tiles",
                layout: {
                    visibility: "none"
                },
                paint: { "raster-opacity": 0.5 }
            });

            // Fill layer (2D)
            map.addLayer({
                id: "states-fill",
                type: "fill",
                source: "india-states",
                layout: { visibility: "visible" },
                paint: {
                    "fill-color": [
                        "case",
                        ["boolean", ["feature-state", "hover"], false],
                        "#22d3ee",
                        "#1e3a5f",
                    ],
                    "fill-opacity": [
                        "interpolate",
                        ["linear"],
                        ["to-number", ["get", selectedYear.toString(), ["get", "historical_capacity"]], 0],
                        0, 0.1,
                        20000, 0.3,
                        50000, 0.6,
                        100000, 0.9
                    ],
                },
            });

            // Fill Extrusion layer (3D)
            map.addLayer({
                id: "states-extrusion",
                type: "fill-extrusion",
                source: "india-states",
                layout: { visibility: "none" },
                paint: {
                    "fill-extrusion-color": [
                        "case",
                        ["boolean", ["feature-state", "hover"], false],
                        "#22d3ee",
                        "#1e3a5f",
                    ],
                    "fill-extrusion-height": [
                        "interpolate",
                        ["linear"],
                        ["to-number", ["get", selectedYear.toString(), ["get", "historical_capacity"]], 0],
                        0, 0,
                        50000, 200000,
                        100000, 600000
                    ],
                    "fill-extrusion-base": 0,
                    "fill-extrusion-opacity": 0.8
                }
            });

            // Border layer
            map.addLayer({
                id: "states-border",
                type: "line",
                source: "india-states",
                paint: {
                    "line-color": "#38bdf8",
                    "line-width": 1,
                    "line-opacity": 0.6,
                },
            });

            // ── Hover highlight via feature-state ──
            const handleHover = (e: any) => {
                if (!e.features || e.features.length === 0) return;
                map.getCanvas().style.cursor = "pointer";

                if (hoveredId.current !== null) {
                    map.setFeatureState(
                        { source: "india-states", id: hoveredId.current },
                        { hover: false }
                    );
                }
                hoveredId.current = e.features[0].id ?? null;
                if (hoveredId.current !== null) {
                    map.setFeatureState(
                        { source: "india-states", id: hoveredId.current },
                        { hover: true }
                    );
                }
            };

            const handleMouseLeave = () => {
                map.getCanvas().style.cursor = "";
                if (hoveredId.current !== null) {
                    map.setFeatureState(
                        { source: "india-states", id: hoveredId.current },
                        { hover: false }
                    );
                    hoveredId.current = null;
                }
            };

            map.on("mousemove", "states-fill", handleHover);
            map.on("mouseleave", "states-fill", handleMouseLeave);
            map.on("mousemove", "states-extrusion", handleHover);
            map.on("mouseleave", "states-extrusion", handleMouseLeave);

            // Click
            map.on("click", "states-fill", handleClick);
            map.on("click", "states-extrusion", handleClick);

            // Mark map as loaded so power plants can be loaded
            setMapLoaded(true);
        });

        mapRef.current = map;

        // MapLibre measures the container once, at construction time. When the map
        // mounts before layout has settled (or while its view is hidden behind the
        // Map/Simple/Pro toggle) it falls back to a 400x300 canvas and never
        // re-measures, leaving the map blank. Observing the container and calling
        // resize() keeps the canvas in sync with its real dimensions.
        const container = mapContainer.current;
        const resizeObserver = new ResizeObserver(() => map.resize());
        resizeObserver.observe(container);

        return () => {
            resizeObserver.disconnect();
            map.remove();
        };
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []);


    // Effect to update map styling when view mode changes
    useEffect(() => {
        if (!mapLoaded || !mapRef.current) return;
        const map = mapRef.current;

        const liveColorScale: any = [
            "interpolate",
            ["linear"],
            ["get", "live_utilization"],
            0, "#0f172a",
            40, "#1e3a8a",
            60, "#3b82f6",
            80, "#22c55e",
            100, "#eab308"
        ];

        const defaultColorScale: any = [
            "case",
            ["boolean", ["feature-state", "hover"], false],
            "#22d3ee",
            "#1e3a5f",
        ];

        const capacityScale: any = [
            "to-number", ["get", selectedYear.toString(), ["get", "historical_capacity"]], 0
        ];

        const capacityOpacity: any = [
            "interpolate",
            ["linear"],
            capacityScale,
            0, 0.15,
            20000, 0.35,
            50000, 0.6,
            100000, 0.9
        ];

        let targetOpacity: any;
        if (selectedStateId) {
            targetOpacity = [
                "case",
                ["==", ["get", "state_id"], selectedStateId],
                viewMode === "live" ? 0.6 : capacityOpacity,
                viewMode === "live" ? 0.15 : 0.1 // fade out others
            ];
        } else {
            targetOpacity = viewMode === "live" ? 0.6 : capacityOpacity;
        }

        if (viewMode === "live") {
            map.setPaintProperty("states-fill", "fill-color", liveColorScale);
            map.setPaintProperty("states-extrusion", "fill-extrusion-color", liveColorScale);

            map.setPaintProperty("states-fill", "fill-opacity", targetOpacity);
            map.setPaintProperty("states-extrusion", "fill-extrusion-height", [
                "interpolate",
                ["linear"],
                ["get", "live_utilization"],
                0, 0,
                50, 200000,
                100, 600000
            ]);
        } else {
            map.setPaintProperty("states-fill", "fill-color", defaultColorScale);
            map.setPaintProperty("states-extrusion", "fill-extrusion-color", defaultColorScale);

            map.setPaintProperty("states-fill", "fill-opacity", targetOpacity);
            map.setPaintProperty("states-extrusion", "fill-extrusion-height", [
                "interpolate",
                ["linear"],
                capacityScale,
                0, 0,
                50000, 200000,
                100000, 600000
            ]);
        }
    }, [viewMode, mapLoaded, selectedYear, selectedStateId]);

    // Handle 3D Extrusion and Satellite visibility
    useEffect(() => {
        if (!mapLoaded || !mapRef.current) return;
        const map = mapRef.current;

        map.setLayoutProperty("satellite-layer", "visibility", isSatellite ? "visible" : "none");

        if (is3D) {
            map.setLayoutProperty("states-fill", "visibility", "none");
            map.setLayoutProperty("states-extrusion", "visibility", "visible");
            map.easeTo({ pitch: 55, bearing: -15, duration: 1000 });
        } else {
            map.setLayoutProperty("states-extrusion", "visibility", "none");
            map.setLayoutProperty("states-fill", "visibility", "visible");
            map.easeTo({ pitch: 0, bearing: 0, duration: 1000 });
        }
    }, [is3D, isSatellite, mapLoaded]);

    // Handle playback 
    useEffect(() => {
        if (!isPlaying) return;
        const iv = setInterval(() => {
            if (selectedYear < 2026) {
                onYearChange(selectedYear + 1);
            } else {
                setIsPlaying(false);
            }
        }, 1000);
        return () => clearInterval(iv);
    }, [isPlaying, selectedYear, onYearChange]);

    if (mapError) {
        return (
            <div className="flex items-center justify-center w-full h-full bg-slate-950">
                <div className="text-center max-w-sm">
                    <div className="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-full bg-amber-500/10">
                        <svg className="h-7 w-7 text-amber-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                            <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v2m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                    </div>
                    <p className="text-lg font-semibold text-white mb-2">Map Unavailable</p>
                    <p className="text-sm text-slate-400">{mapError}</p>
                </div>
            </div>
        );
    }

    return (
        <div className="relative w-full h-full" style={{ minHeight: "100vh" }}>
            <div
                ref={mapContainer}
                className="w-full h-full"
                style={{ minHeight: "100vh" }}
            />

            {/* Power Plant Filter Panel */}
            <PowerPlantFilterPanel
                filters={plantFilters}
                onFiltersChange={setPlantFilters}
                plantCount={plantCount}
                visible={filtersVisible}
                onToggleVisible={() => setFiltersVisible(!filtersVisible)}
            />

            {/* Map Legend */}
            <div className="absolute bottom-6 right-3 z-10
                            bg-slate-900/80 backdrop-blur-md border border-slate-700/50
                            rounded-lg px-3 py-2.5 shadow-lg">
                <div className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider mb-1.5">
                    Energy Type
                </div>
                <div className="space-y-1">
                    {Object.entries(TYPE_COLORS)
                        .filter(([k]) => !["other", "unknown"].includes(k))
                        .map(([type, color]) => (
                            <div key={type} className="flex items-center gap-2">
                                <span
                                    className="w-2.5 h-2.5 rounded-full"
                                    style={{ backgroundColor: color }}
                                />
                                <span className="text-[11px] text-slate-300">
                                    {type.charAt(0).toUpperCase() + type.slice(1)}
                                </span>
                            </div>
                        ))}
                </div>
            </div>

            {/* View Mode Toggle */}
            <div className="absolute top-6 left-1/2 transform -translate-x-1/2 z-10 
                            bg-slate-900/80 backdrop-blur-md border border-slate-700/50 
                            rounded-full p-1 shadow-lg flex items-center">
                <button
                    onClick={() => setViewMode("capacity")}
                    className={`px-4 py-1.5 text-xs font-semibold rounded-full transition-all duration-300 ease-in-out
                        ${viewMode === "capacity"
                            ? "bg-sky-500/20 text-sky-400 shadow-[0_0_10px_rgba(56,189,248,0.3)]"
                            : "text-slate-400 hover:text-slate-200"}`}
                >
                    Installed Capacity
                </button>
                <div className="w-px h-4 bg-slate-700/50 mx-1"></div>
                <button
                    onClick={() => setViewMode("live")}
                    className={`px-4 py-1.5 text-xs font-semibold rounded-full transition-all duration-300 ease-in-out flex items-center gap-1.5
                        ${viewMode === "live"
                            ? "bg-emerald-500/20 text-emerald-400 shadow-[0_0_10px_rgba(52,211,153,0.3)]"
                            : "text-slate-400 hover:text-slate-200"}`}
                >
                    <span className="relative flex h-2 w-2">
                        <span className={`animate-ping absolute inline-flex h-full w-full rounded-full opacity-75 ${viewMode === 'live' ? 'bg-emerald-400' : 'bg-slate-500'}`}></span>
                        <span className={`relative inline-flex rounded-full h-2 w-2 ${viewMode === 'live' ? 'bg-emerald-500' : 'bg-slate-400'}`}></span>
                    </span>
                    Live Generation
                </button>
            </div>

            {/* Float Controls for 3D and Satellite */}
            <div className="absolute top-6 right-6 z-10 flex flex-col gap-2">
                <button
                    onClick={() => setIsSatellite(!isSatellite)}
                    className={`w-10 h-10 rounded-xl bg-slate-900/80 backdrop-blur-md border border-slate-700/50 
                        shadow-lg flex items-center justify-center transition-all duration-300
                        ${isSatellite ? "text-[#20d3ee] shadow-[0_0_15px_rgba(32,211,238,0.2)]" : "text-slate-400 hover:text-slate-200"}`}
                    title="Toggle Satellite View"
                >
                    <span className="material-symbols-outlined text-lg">satellite_alt</span>
                </button>
                <button
                    onClick={() => setIs3D(!is3D)}
                    className={`w-10 h-10 rounded-xl bg-slate-900/80 backdrop-blur-md border border-slate-700/50 
                        shadow-lg flex items-center justify-center transition-all duration-300
                        ${is3D ? "text-[#20d3ee] shadow-[0_0_15px_rgba(32,211,238,0.2)]" : "text-slate-400 hover:text-slate-200"}`}
                    title="Toggle 3D View"
                >
                    <span className="material-symbols-outlined text-lg">3d_rotation</span>
                </button>
            </div>

            {/* Time Scrubber (Only visible in capacity mode) */}
            {viewMode === "capacity" && (
                <TimeScrubber
                    minYear={2019}
                    maxYear={2026}
                    value={selectedYear}
                    onChange={onYearChange}
                    playing={isPlaying}
                    setPlaying={setIsPlaying}
                />
            )}
        </div>
    );
}
