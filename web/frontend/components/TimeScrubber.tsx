"use client";

import { useState, useEffect } from "react";

interface Props {
    minYear: number;
    maxYear: number;
    value: number;
    onChange: (year: number) => void;
    playing: boolean;
    setPlaying: (p: boolean) => void;
}

export default function TimeScrubber({ minYear, maxYear, value, onChange, playing, setPlaying }: Props) {
    const [localVal, setLocalVal] = useState(value);

    // Sync local with parent prop
    useEffect(() => {
        setLocalVal(value);
    }, [value]);

    const handlePlayPause = () => {
        setPlaying(!playing);
    };

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const val = parseInt(e.target.value, 10);
        setLocalVal(val);
        onChange(val);
    };

    return (
        <div className="absolute top-20 left-1/2 transform -translate-x-1/2 z-20 
                        bg-slate-900/90 backdrop-blur-md border border-slate-700/50 
                        rounded-2xl px-6 py-3 shadow-[0_8px_30px_rgb(0,0,0,0.4)] flex items-center gap-6 w-[400px]">
            <button
                onClick={handlePlayPause}
                className="w-10 h-10 rounded-full bg-[#20d3ee]/20 hover:bg-[#20d3ee]/40 
                           flex items-center justify-center text-[#20d3ee] transition-colors border border-[#20d3ee]/30 shrink-0"
            >
                <span className="material-symbols-outlined text-[20px]">
                    {playing ? 'pause' : 'play_arrow'}
                </span>
            </button>
            <div className="flex-1 flex flex-col gap-1.5 min-w-0">
                <div className="flex items-center justify-between text-xs font-bold font-mono">
                    <span className="text-slate-400">{minYear}</span>
                    <span className="text-[#20d3ee] text-base drop-shadow-[0_0_8px_rgba(32,211,238,0.8)]">{localVal}</span>
                    <span className="text-slate-400">{maxYear}</span>
                </div>
                <input
                    type="range"
                    min={minYear}
                    max={maxYear}
                    step={1}
                    value={localVal}
                    onChange={handleChange}
                    className="w-full h-1.5 bg-slate-700/80 rounded-lg appearance-none cursor-pointer
                             accent-[#20d3ee] hover:accent-[#38bdf8] focus:outline-none focus:ring-2 focus:ring-[#20d3ee]/50
                             [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:w-4 [&::-webkit-slider-thumb]:h-4
                             [&::-webkit-slider-thumb]:bg-[#20d3ee] [&::-webkit-slider-thumb]:rounded-full [&::-webkit-slider-thumb]:transition-all
                             [&::-webkit-slider-thumb]:shadow-[0_0_10px_rgba(32,211,238,0.6)]"
                />
            </div>
        </div>
    );
}
