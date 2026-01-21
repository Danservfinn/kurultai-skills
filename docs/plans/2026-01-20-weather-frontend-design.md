# Weather Model Comparison App - Design Document

**Date**: 2026-01-20
**Status**: Approved
**Deployment**: Railway

## Overview

A public, map-first weather application for comparing multi-model forecasts (ECMWF, GFS, HRRR, ICON). Dark, data-rich aesthetic targeting weather enthusiasts who want to see model agreement/disagreement, spread ranges, and confidence levels.

## Tech Stack

- **Framework**: Next.js 14 (App Router)
- **Styling**: Tailwind CSS + shadcn/ui
- **Map**: Mapbox GL JS (or Leaflet as free alternative)
- **Charts**: Recharts
- **Deployment**: Railway (auto-deploy from GitHub)

## Project Structure

```
/app
  /page.tsx              → Main map view
  /api
    /forecast/route.ts   → Proxies Open-Meteo API calls
    /geocode/route.ts    → Location search
/components
  /Map.tsx               → Interactive map (Mapbox/Leaflet)
  /Sidebar.tsx           → Forecast panel container
  /ModelComparison.tsx   → Charts + comparison visualization
  /LocationSearch.tsx    → Search with autocomplete
  /AgreementMeter.tsx    → Model consensus indicator
  /AccumulationChart.tsx → Timeline chart
/lib
  /weather-api.ts        → Open-Meteo client
  /utils.ts              → Unit conversions, helpers
/types
  /weather.ts            → TypeScript interfaces
```

## UI Layout

### Desktop (>1024px)
```
┌─────────────────────────────────────────────────────────────┐
│ [🔍 Search location...]                    [°F/°C] [About]  │
├─────────────────────────────────────────────────┬───────────┤
│                                                 │           │
│              INTERACTIVE MAP                    │  SIDEBAR  │
│              (dark base style)                  │  (380px)  │
│                                                 │           │
│                 📍 clicked point                │           │
│                                                 │           │
└─────────────────────────────────────────────────┴───────────┘
```

### Mobile (<768px)
- Full-screen map with floating search
- Bottom sheet pattern for forecast panel
- Peek state shows summary, swipe up for full details

## Model Comparison Card

The core UI component emphasizing model agreement/disagreement.

```
┌─────────────────────────────────────────┐
│ SNOW FORECAST                    24-48h │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│                                         │
│  Model Agreement: ██████████░░ HIGH     │
│  Range: 4.2" - 6.8"    Best Est: 5.1"   │
│                                         │
├─────────────────────────────────────────┤
│    ECMWF │████████████████░░░░│ 6.2"    │
│      GFS │██████████████░░░░░░│ 5.4"    │
│     HRRR │█████████████░░░░░░░│ 4.9"    │
│     ICON │████████████████░░░░│ 5.8"    │
├─────────────────────────────────────────┤
│  ┌─────────────────────────────────┐    │
│  │    Accumulation Timeline        │    │
│  │  6"─┤      ___......''''        │    │
│  │  3"─┤   _.-'                    │    │
│  │  0"─┼──'───────────────────     │    │
│  │     Sat 6pm   Sun 6am   Sun 6pm │    │
│  └─────────────────────────────────┘    │
├─────────────────────────────────────────┤
│ ❄️ Snow begins: Sat 4pm                 │
│ 🌨️ Heaviest: Sat 10pm - Sun 2am        │
│ ✓ Snow ends: Sun 11am                   │
└─────────────────────────────────────────┘
```

### Key Elements

- **Agreement Meter**: Visual bar (green/yellow/red) showing model consensus
- **Range Display**: Min-max across models with weighted best estimate
- **Horizontal Bar Chart**: Each model as a row for instant visual comparison
- **Accumulation Timeline**: Line chart showing when precipitation falls
- **Timing Summary**: Plain-language start/peak/end times

## API Design

### Endpoint: `GET /api/forecast`

**Request**
```
GET /api/forecast?lat=35.78&lon=-78.64&days=7
```

**Response**
```typescript
interface ForecastResponse {
  location: {
    name: string;
    lat: number;
    lon: number;
    timezone: string;
  };
  generated: string;
  models: {
    ecmwf: ModelForecast;
    gfs: ModelForecast;
    hrrr: ModelForecast | null;  // null outside US
    icon: ModelForecast;
  };
  summary: {
    agreement: 'high' | 'moderate' | 'low';
    snowRange: [number, number];
    bestEstimate: number;
    snowStart: string | null;
    snowPeak: string | null;
    snowEnd: string | null;
  };
  daily: DailyForecast[];
}

interface ModelForecast {
  snowTotal: number;      // inches
  precipTotal: number;    // inches
  hourly: HourlyData[];
  lastUpdated: string;
}
```

### Open-Meteo Integration

Aggregate data from multiple endpoints:
- `api.open-meteo.com/v1/ecmwf` - European model (9km, 15-day)
- `api.open-meteo.com/v1/gfs` - American model (25km, 16-day)
- `api.open-meteo.com/v1/gfs?models=gfs_hrrr` - High-res US (3km, 48h)
- `api.open-meteo.com/v1/forecast?models=icon_seamless` - German model

### Caching Strategy

- Cache responses for 30 min per lat/lon grid (rounded to 0.1°)
- HTTP caching: `Cache-Control: public, max-age=1800`
- Optional: Redis/Upstash for server-side cache

## Mobile Experience

### Bottom Sheet States

1. **Collapsed**: Just drag handle visible
2. **Peek**: Location name + summary (snow total, agreement level)
3. **Expanded**: Full model comparison with charts

### Responsive Breakpoints

- Mobile (<768px): Bottom sheet, stacked charts
- Tablet (768-1024px): Sidebar 320px
- Desktop (>1024px): Sidebar 380px

## Polish & UX

- **Loading**: Skeleton loaders for map and sidebar
- **Animations**: Smooth transitions, chart animations on data load
- **Shareable URLs**: `app.com/?lat=35.78&lon=-78.64`
- **PWA ready**: Installable, offline-capable with cached forecasts
- **Dark mode only**: Consistent data-rich aesthetic

## Accessibility

- Keyboard navigation for map (arrow keys)
- Screen reader labels for all chart data
- High contrast colors for model differentiation
- Focus indicators on interactive elements

## Error Handling

- **API timeout**: Show partial data with available models
- **Invalid coordinates**: 400 with helpful message
- **Rate limited**: 429 with retry-after header
- **No precipitation**: Friendly "clear skies" message

## Future Considerations (Not in MVP)

- User accounts for saved locations
- Push notifications for storm alerts
- Historical forecast accuracy tracking
- Additional data layers (radar, satellite)
