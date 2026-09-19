"use client";

import { useEffect, useId, useRef, type ReactNode } from "react";

interface Props {
    open: boolean;
    onClose: () => void;
    title: string;
    subtitle?: string;
    children: ReactNode;
    /** Tailwind max-width class for the panel. */
    width?: string;
}

/** Accessible dialog: Escape and backdrop close it, focus returns on close. */
export default function Modal({ open, onClose, title, subtitle, children, width = "max-w-lg" }: Props) {
    const titleId = useId();
    const panelRef = useRef<HTMLDivElement>(null);
    // Callers pass a fresh onClose each render; reading it through a ref keeps
    // the effect below from re-running (and re-grabbing focus) on every change.
    const onCloseRef = useRef(onClose);
    useEffect(() => {
        onCloseRef.current = onClose;
    }, [onClose]);

    useEffect(() => {
        if (!open) return;
        const previouslyFocused = document.activeElement as HTMLElement | null;
        panelRef.current?.focus();

        const onKey = (e: KeyboardEvent) => {
            if (e.key === "Escape") onCloseRef.current();
        };
        document.addEventListener("keydown", onKey);
        return () => {
            document.removeEventListener("keydown", onKey);
            previouslyFocused?.focus?.();
        };
    }, [open]);

    if (!open) return null;

    return (
        <div
            className="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm"
            onMouseDown={(e) => {
                if (e.target === e.currentTarget) onClose();
            }}
        >
            <div
                ref={panelRef}
                role="dialog"
                aria-modal="true"
                aria-labelledby={titleId}
                tabIndex={-1}
                className={`w-full ${width} max-h-[85vh] flex flex-col bg-[#161A22] border border-[#262C3A] rounded-lg shadow-2xl outline-none`}
            >
                <div className="flex items-start justify-between gap-4 px-6 py-4 border-b border-[#262C3A]">
                    <div>
                        <h2 id={titleId} className="text-base font-bold text-white">{title}</h2>
                        {subtitle && <p className="text-xs text-slate-400 mt-1">{subtitle}</p>}
                    </div>
                    <button
                        onClick={onClose}
                        aria-label="Close"
                        className="text-slate-400 hover:text-white transition-colors"
                    >
                        <span className="material-symbols-outlined">close</span>
                    </button>
                </div>
                <div className="px-6 py-5 overflow-y-auto">{children}</div>
            </div>
        </div>
    );
}
