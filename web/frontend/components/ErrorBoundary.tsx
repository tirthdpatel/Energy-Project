"use client";

import React, { Component, type ReactNode } from "react";

interface Props {
    children: ReactNode;
    fallback?: ReactNode;
}

interface State {
    hasError: boolean;
    message: string;
}

/** Global error boundary — catches render errors & shows fallback UI. */
export default class ErrorBoundary extends Component<Props, State> {
    constructor(props: Props) {
        super(props);
        this.state = { hasError: false, message: "" };
    }

    static getDerivedStateFromError(error: Error): State {
        return { hasError: true, message: error.message };
    }

    componentDidCatch(error: Error, info: React.ErrorInfo) {
        console.error("[ErrorBoundary]", error, info.componentStack);
    }

    render() {
        if (this.state.hasError) {
            return (
                this.props.fallback ?? (
                    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/90">
                        <div className="max-w-md rounded-2xl border border-red-500/30 bg-slate-900 p-8 text-center shadow-2xl">
                            <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-red-500/10">
                                <svg
                                    className="h-8 w-8 text-red-400"
                                    fill="none"
                                    viewBox="0 0 24 24"
                                    stroke="currentColor"
                                    strokeWidth={2}
                                >
                                    <path
                                        strokeLinecap="round"
                                        strokeLinejoin="round"
                                        d="M12 9v2m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                                    />
                                </svg>
                            </div>
                            <h2 className="mb-2 text-xl font-bold text-white">
                                Something went wrong
                            </h2>
                            <p className="mb-4 text-sm text-slate-400">
                                {this.state.message ||
                                    "The application encountered an unexpected error."}
                            </p>
                            {process.env.NODE_ENV === "development" && (
                                <p className="mb-6 text-xs text-slate-500">
                                    Make sure the backend is running on{" "}
                                    <code className="text-cyan-400">localhost:8000</code>
                                </p>
                            )}
                            <button
                                onClick={() => this.setState({ hasError: false, message: "" })}
                                className="rounded-lg bg-cyan-600 px-6 py-2.5 text-sm font-medium text-white transition hover:bg-cyan-500"
                            >
                                Try Again
                            </button>
                        </div>
                    </div>
                )
            );
        }
        return this.props.children;
    }
}
