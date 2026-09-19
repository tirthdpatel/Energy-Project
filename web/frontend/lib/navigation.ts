/**
 * Navigation model shared by the shell, the icon rail and the Pro sidebar.
 *
 * Every nav control resolves to a Destination, so each one can land somewhere
 * specific — a view, and where relevant a tab, a section or an open panel —
 * instead of several controls all pointing at the same top-level view.
 */

export type View = "map" | "simple" | "pro" | "datasets";

export type ProTab = "overview" | "emissions";

/** A section inside the Pro overview that a link can scroll to. */
export type ProSection = "benchmarks";

export interface Destination {
    view: View;
    /** Pro view: which tab to show. */
    proTab?: ProTab;
    /** Pro view: a section to scroll into view. */
    section?: ProSection;
    /** Map view: open (true) or close (false) the layers panel. */
    layers?: boolean;
}

export type Navigate = (to: Destination) => void;
