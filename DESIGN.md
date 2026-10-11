---
name: Obsidian Signal
colors:
  surface: '#051424'
  surface-dim: '#051424'
  surface-bright: '#2c3a4c'
  surface-container-lowest: '#010f1f'
  surface-container-low: '#0d1c2d'
  surface-container: '#122131'
  surface-container-high: '#1c2b3c'
  surface-container-highest: '#273647'
  on-surface: '#d4e4fa'
  on-surface-variant: '#c2c6d6'
  inverse-surface: '#d4e4fa'
  inverse-on-surface: '#233143'
  outline: '#8c909f'
  outline-variant: '#424754'
  surface-tint: '#adc6ff'
  primary: '#adc6ff'
  on-primary: '#002e6a'
  primary-container: '#4d8eff'
  on-primary-container: '#00285d'
  inverse-primary: '#005ac2'
  secondary: '#5de6ff'
  on-secondary: '#00363e'
  secondary-container: '#00cbe6'
  on-secondary-container: '#00515d'
  tertiary: '#ffb3b0'
  on-tertiary: '#670211'
  tertiary-container: '#ea6767'
  on-tertiary-container: '#5b000d'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#d8e2ff'
  primary-fixed-dim: '#adc6ff'
  on-primary-fixed: '#001a42'
  on-primary-fixed-variant: '#004395'
  secondary-fixed: '#a2eeff'
  secondary-fixed-dim: '#2fd9f4'
  on-secondary-fixed: '#001f25'
  on-secondary-fixed-variant: '#004e5a'
  tertiary-fixed: '#ffdad8'
  tertiary-fixed-dim: '#ffb3b0'
  on-tertiary-fixed: '#410006'
  on-tertiary-fixed-variant: '#881d24'
  background: '#051424'
  on-background: '#d4e4fa'
  surface-variant: '#273647'
typography:
  display-lg:
    fontFamily: Inter
    fontSize: 36px
    fontWeight: '700'
    lineHeight: 44px
    letterSpacing: -0.025em
  display-lg-mobile:
    fontFamily: Inter
    fontSize: 28px
    fontWeight: '700'
    lineHeight: 36px
    letterSpacing: -0.02em
  headline-xl:
    fontFamily: Inter
    fontSize: 28px
    fontWeight: '600'
    lineHeight: 36px
    letterSpacing: -0.02em
  headline-xl-mobile:
    fontFamily: Inter
    fontSize: 22px
    fontWeight: '600'
    lineHeight: 30px
    letterSpacing: -0.015em
  headline-lg:
    fontFamily: Inter
    fontSize: 20px
    fontWeight: '600'
    lineHeight: 28px
    letterSpacing: -0.015em
  headline-md:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '600'
    lineHeight: 24px
    letterSpacing: -0.01em
  metric-stat:
    fontFamily: Inter
    fontSize: 24px
    fontWeight: '700'
    lineHeight: 32px
    letterSpacing: -0.02em
  body-lg:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
    letterSpacing: 0em
  body-md:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
    letterSpacing: 0em
  body-sm:
    fontFamily: Inter
    fontSize: 13px
    fontWeight: '400'
    lineHeight: 18px
    letterSpacing: 0em
  label-md:
    fontFamily: Inter
    fontSize: 13px
    fontWeight: '500'
    lineHeight: 18px
    letterSpacing: 0.01em
  label-sm:
    fontFamily: Inter
    fontSize: 11px
    fontWeight: '600'
    lineHeight: 16px
    letterSpacing: 0.04em
  data-tabular:
    fontFamily: Inter
    fontSize: 13px
    fontWeight: '500'
    lineHeight: 18px
    letterSpacing: -0.01em
rounded:
  sm: 0.125rem
  DEFAULT: 0.25rem
  md: 0.375rem
  lg: 0.5rem
  xl: 0.75rem
  full: 9999px
spacing:
  gutter: 1rem
  gutter-desktop: 1.5rem
  margin: 1rem
  margin-desktop: 2rem
  space-xs: 0.25rem
  space-sm: 0.5rem
  space-md: 0.75rem
  space-lg: 1.25rem
  space-xl: 2rem
---

## Brand & Style

This design system embodies high-stakes operational intelligence. Built for enterprise risk teams, revenue operators, and executive leadership, it translates machine-learned churn probabilities into clear strategic action. The interface balances technical rigor with visual clarity, preventing cognitive overload in dense data environments while retaining an authoritative, mission-critical tone.

The aesthetic fuses **Corporate/Modern enterprise precision** with **technical glass and low-contrast surface elevation**. High-contrast telemetry signals (predictive indicators, probability alerts, metric deltas) stand out vividly against deep, layered navy foundations. The experience avoids decorative novelties in favor of utilitarian restraint, crisp visual boundaries, low-latency micro-interactions, and instant legibility across complex operational workflows.

## Colors

The palette establishes an ordered deep-space canvas that supports extended analysis while maintaining strict WCAG AAA/AA visual compliance for mission-critical alerts.

### Surface Architecture
- **Canvas Base (`#0B1120`):** The default viewport foundation for the workspace.
- **Sidebar & Inset Canvas (`#080D19`):** Recessed ground used for structural navigation, global drawers, and table filters.
- **Card Surface (`#111B2E`):** Standard container surface for operational panels, metrics cards, and data widgets.
- **Elevated Surface (`#17243A`):** Lifted containers, hover states, popovers, contextual tooltips, and flyout menus.
- **Border Structural (`#263449`):** Thin structural dividers and boundaries engineered to maintain grid integrity without adding visual weight.

### Accents & Machine Intelligence Signals
- **Electric Blue (`#3B82F6`):** Primary interactions, focused states, primary action buttons, active navigation, and aggregate metric indicators.
- **Signal Cyan (`#22D3EE`):** Secondary AI telemetry, predictive trajectory projections, model confidence scoring, and interactive chart highlights.

### Risk & Semantic States
- **High Risk / Critical Churn (`#F87171`):** Actionable churn probability ≥70%, revenue loss alerts, system warnings. Pair with subtle red-tinted backdrops (`rgba(248, 113, 113, 0.12)`).
- **Medium Risk / Degrading (`#FBBF24`):** Churn probability 35%–69%, usage velocity drop-offs, pending renewals at risk.
- **Low Risk / Retained (`#34D399`):** Churn probability <35%, expansion accounts, model health optimal.

### Typography & Content Neutrals
- **Primary Content (`#F1F5F9`):** High-contrast display figures, primary labels, headers, and active values.
- **Secondary Content (`#94A3B8`):** Micro-copy, metadata, table headers, breadcrumbs, and inactive axis labels.
- **Muted Content (`#475569`):** Disabled states, structural placeholders, and inactive chart gridlines.

## Typography

The typography scale utilizes **Inter** throughout the entire interface to maintain consistency, vertical rhythm, and clarity across multi-column data views.

- **Tabular Figures:** All numeric variables, financial tickers, churn percentages, and confidence bands must activate tabular figures (`font-variant-numeric: tabular-nums`) to prevent alignment jitter during real-time streaming updates.
- **Label Tracking:** Uppercase metadata micro-labels (`label-sm`) require tracking at `+0.04em` to preserve optical legibility against dark slate backdrops.
- **Hierarchy Separation:** Strict size pairing ensures clear differentiation: primary KPIs leverage `metric-stat` (`24px/32px Bold`), immediately anchored by `body-sm` (`13px/18px Regular`) for semantic context and cohort descriptors.

## Layout & Spacing

This design system uses a strict **8-point base spatial system** with a 4-point micro-scale reserved for dense telemetry rows, tags, and table cells.

### Grid & Canvas Structure
- **Desktop (≥1280px):** 12-column responsive fluid grid with `gutter-desktop` (`1.5rem`) and outer canvas padding `margin-desktop` (`2rem`). Structural sidebar is pinned at `260px` or collapsed at `64px`.
- **Tablet (768px – 1279px):** 8-column layout with `gutter` (`1rem`) and `margin` (`1.5rem`). Complex metrics panels collapse from 4 columns to 2 columns.
- **Mobile (≤767px):** 4-column layout with `gutter` (`1rem`) and `margin` (`1rem`). Sidebars collapse into off-canvas sliding drawers. Analytics tables switch to horizontally scrollable data sheets or vertical attribute card stacks.

### Content Density Hierarchy
- **Dense Data (Tables, Cohort Lists):** Use `space-xs` (`4px`) and `space-sm` (`8px`) internal cell and row gaps to maximize row density on viewports.
- **Container Structure (KPI Cards, Predictive Matrices):** Use `space-lg` (`1.25rem`) padding to create a clear visual frame around high-priority figures.
- **Section Isolation:** Canvas sections and primary metric modules divide along `space-xl` (`2rem`) boundaries.

## Elevation & Depth

This system avoids heavy, blurry drop shadows that produce muddy artifacts on dark backgrounds. Visual hierarchy is established through **calibrated tonal layers**, **thin structural outlines**, and **focused luminescent glows**.

### Surface Hierarchy
1. **Foundation Level (0dp):** Canvas Base (`#0B1120`). Flat, non-interactive ground.
2. **Structural Tier (1dp):** Sidebar & Data Tables (`#080D19`) with border `1px solid #263449`. Provides optical separation from the main working canvas.
3. **Card Level (2dp):** Analytics Cards & Metric Modules (`#111B2E`) with border `1px solid #263449`. Hovering shifts the border to `#3B82F6` at `40% opacity` and activates an ambient rim light: `0 4px 20px -2px rgba(8, 13, 25, 0.7)`.
4. **Floating Tier (3dp):** Popovers, Risk Score Inspector Flyouts, and Filter Menus (`#17243A`). Border `1px solid rgba(59, 130, 246, 0.25)` accompanied by deep drop shadow: `0 12px 32px -4px rgba(0, 0, 0, 0.6)`.

### Signal Glows
Active alerts and primary CTAs use targeted directional rim glows. A primary electric blue active element leverages `box-shadow: 0 0 16px rgba(59, 130, 246, 0.25)`. High-risk flags apply `box-shadow: 0 0 12px rgba(248, 113, 113, 0.2)` to draw immediate attention without breaking grid structure.

## Shapes

The design uses a **Soft (Level 1)** radius language to convey precision and structural discipline. Rounded forms are kept compact to maximize data density and preserve grid alignment.

- **Base Radius (`0.25rem` / `4px`):** Checkboxes, inline badges, risk score tags, table row selections, input boxes, and button controls.
- **Container Radius (`rounded-lg` / `0.5rem` / `8px`):** Analytics metric cards, charts, risk matrices, alert banners, and table wrappers.
- **Overlay Radius (`rounded-xl` / `0.75rem` / `12px`):** Contextual modals, machine-learning inspector panels, and floating settings drawers.

## Components

### Buttons
- **Primary Action:** Solid Electric Blue (`#3B82F6`) fill, text `#F1F5F9`, `label-md` bold. Hover: `#2563EB` with `0 0 12px rgba(59, 130, 246, 0.35)`. Active: `#1D4ED8`. Height: `36px` (`space-md` horizontal padding).
- **Secondary / Ghost:** Transparent background with `1px solid #263449` border, text `#F1F5F9`. Hover: Surface `#17243A`, border `#3B82F6`.
- **Destructive / Risk Intervention:** Dark crimson base (`rgba(248, 113, 113, 0.1)`) with `1px solid #F87171`, text `#F87171`. Hover: fill `#F87171`, text `#080D19`.

### Chips & Risk Badges
- **Status Indicator Badges:** Height `22px`, `label-sm`, padding `2px 8px`, corner radius `4px`.
  - *High Risk:* Background `rgba(248, 113, 113, 0.12)`, text `#F87171`, border `1px solid rgba(248, 113, 113, 0.3)`. Includes a pulse indicator (`6px` dot).
  - *Medium Risk:* Background `rgba(251, 191, 36, 0.12)`, text `#FBBF24`, border `1px solid rgba(251, 191, 36, 0.3)`.
  - *Low Risk / Safe:* Background `rgba(52, 211, 153, 0.12)`, text `#34D399`, border `1px solid rgba(52, 211, 153, 0.3)`.
- **Filter Tags:** Background `#111B2E`, border `1px solid #263449`, text `#94A3B8`. Active filter toggles text to `#22D3EE` with border `rgba(34, 211, 238, 0.5)`.

### Lists & Churn Telemetry Tables
- **Table Headers:** Background `#080D19`, height `36px`, `label-sm` uppercase, text `#94A3B8`, border-bottom `1px solid #263449`.
- **Data Rows:** Background `#111B2E`, height `44px` (dense: `36px`), border-bottom `1px solid #1E293B`, text `#F1F5F9`.
- **Row Interaction:** Hover invokes surface `#17243A` with smooth 120ms ease. Checked/active row gains a `2px` left border in `#3B82F6`.
- **Numeric Cells:** Right-aligned, set in `data-tabular` using monospace numeric figures.

### Checkboxes & Form Controls
- **Checkboxes:** Size `16px x 16px`, corner radius `3px`, border `1px solid #263449`, background `#080D19`. Checked: background `#3B82F6`, border `#3B82F6`, check icon white.
- **Input Fields:** Height `36px`, background `#080D19`, border `1px solid #263449`, typography `body-md`, text `#F1F5F9`, placeholder `#475569`. Focus: border `#3B82F6`, outline `none`, subtle shadow `0 0 0 1px #3B82F6`.

### Cards & Analytical Widgets
- **KPI Container:** Surface `#111B2E`, border `1px solid #263449`, radius `8px`, padding `space-lg`. Includes card top bar for metric title (`label-md`, text `#94A3B8`) and model confidence tag. Primary figure uses `metric-stat` (`#F1F5F9`), paired with a trend vector indicator (e.g., `+14.2% Churn Velocity` in `#F87171`).
- **Interactive Chart Panels:** Inner plot canvas background `#0B1120`, gridlines dotted `#1E293B`, crosshair cursor line `#22D3EE`. Floating hover tooltip set to surface `#17243A` with border `1px solid #263449`.