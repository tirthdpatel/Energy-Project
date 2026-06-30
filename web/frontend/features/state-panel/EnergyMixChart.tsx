"use client";

import {
    PieChart,
    Pie,
    Cell,
    Tooltip,
    Legend,
    ResponsiveContainer,
} from "recharts";
import type { EnergyMixItem } from "@/types";

const SOURCE_COLORS: Record<string, string> = {
    Thermal: "#ef4444",
    Solar: "#f59e0b",
    Wind: "#06b6d4",
    Hydro: "#3b82f6",
    Nuclear: "#8b5cf6",
};

interface Props {
    data: EnergyMixItem[];
}

export default function EnergyMixChart({ data }: Props) {
    return (
        <div className="w-full h-64">
            <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                    <Pie
                        data={data}
                        dataKey="value"
                        nameKey="source"
                        cx="50%"
                        cy="50%"
                        outerRadius={80}
                        innerRadius={40}
                        paddingAngle={2}
                        label={((props: { source: string; value: number }) =>
                            `${props.source} ${props.value}%`
                        ) as (props: object) => string}
                        labelLine={false}
                    >
                        {data.map((entry) => (
                            <Cell
                                key={entry.source}
                                fill={SOURCE_COLORS[entry.source] ?? "#94a3b8"}
                                stroke="transparent"
                            />
                        ))}
                    </Pie>
                    <Tooltip
                        contentStyle={{
                            backgroundColor: "#1e293b",
                            border: "1px solid #334155",
                            borderRadius: "8px",
                            color: "#f1f5f9",
                        }}
                        formatter={((value: number | undefined) => [`${value ?? 0}%`, "Share"]) as any}
                    />
                    <Legend
                        wrapperStyle={{ color: "#cbd5e1", fontSize: "12px" }}
                    />
                </PieChart>
            </ResponsiveContainer>
        </div>
    );
}
