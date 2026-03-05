# OpenRTB 2.5/2.6 Bidder with Campaign Manager - PRD

## Original Problem Statement
Build a Demand-Side Platform (DSP) Bidder that:
1. Receives and parses bid requests in OpenRTB 2.5 and 2.6 formats
2. Integrates with a Campaign Manager with comprehensive targeting
3. Makes real-time bidding decisions matching requests against campaigns
4. Constructs valid OpenRTB bid responses
5. Generates SSP endpoints with API key authentication

## Architecture
- **Backend**: FastAPI + MongoDB
- **Frontend**: React + Tailwind + Shadcn
- **Bidding Engine**: Real-time matching with targeting rules
- **Protocol Handler**: Version detection, field migration

## What's Been Implemented

### Phase 1 - Core MVP
- OpenRTB parser with 2.5/2.6 version detection
- Campaign Manager APIs (CRUD, activate/pause)
- Creative Management (banner/video/native)
- SSP Endpoint Management
- Bid endpoint with targeting engine
- Dark theme dashboard with charts

### Phase 2 - Advanced Bidding
- Win/Billing notification callbacks
- Budget pacing (even distribution)
- Campaign performance reporting
- Bid shading (automatic price optimization)

### Phase 3 - Optimization Features
- Frequency capping (in-memory via MongoDB)
- Supply Path Optimization (SPO)
- ML-based bid prediction (heuristic model)
- Custom report exports (CSV/JSON)

### Phase 4 - Insights & Management
- Campaign Performance Insights with health scores
- ML Model Management page
- Multi-Currency Support (USD, EUR, GBP, CAD, AUD, JPY)

### Phase 5 - Enhanced Campaign Targeting (December 2025)
- **Ad Placements**: In-App, In-Stream, In-Stream Non-Skip, In-Banner, In-Article, In-Feed, Interstitial, Side Banner, Above/Below Fold, Sticky, Floating, Rewarded
- **Geo Targeting**: Countries, Regions, Cities + Lat/Long/Radius targeting
- **Device Targeting**: 
  - Device types: Mobile/Tablet, PC, CTV, Phone, Tablet, Connected Device, Set Top Box
  - Connection types: Ethernet, WiFi, Cellular 2G-5G
  - Mobile carriers by country (USA, GBR, DEU, FRA, IND, BRA, JPN, CAN, AUS)
- **Video Targeting (OpenRTB 2.5/2.6)**:
  - Placements: In-Stream, In-Banner, In-Article, In-Feed, Interstitial
  - PLCMT: In-Stream, Accompanying, Interstitial, No Content
  - Protocols: VAST 1.0-4.2 with wrappers, DAAST
  - MIME Types: MP4, WebM, OGG, FLV, 3GPP, VPAID JS, SWF
  - Pod Positions: First, Last, First or Last, Any
- **SSP ORTB Version**: Choose OpenRTB 2.5 or 2.6 per SSP endpoint
- **Theme Toggle**: Dark/Light mode with localStorage persistence
- **Creative Preview**: Preview banners, video VAST, native ads, audio

### Creative Manager Enhancements
- Multiple creative formats: Raw Banner, Raw Video, VAST URL, VAST XML, JS Tag, Native JSON, Audio VAST
- Creative preview functionality for all types
- Format badges on creative cards

## Key API Endpoints

### Bidding
- `POST /api/bid` - Main bid endpoint (no auth required)

### Campaigns
- `GET/POST /api/campaigns` - List/create campaigns
- `GET/PUT/DELETE /api/campaigns/{id}` - Single campaign ops

### Reference Data
- `GET /api/reference/iab-categories` - IAB content categories
- `GET /api/reference/ad-placements` - Ad placement options
- `GET /api/reference/video-placements` - OpenRTB 2.5 video placements
- `GET /api/reference/video-plcmt` - OpenRTB 2.6 PLCMT types
- `GET /api/reference/video-protocols` - VAST versions
- `GET /api/reference/video-mimes` - Video MIME types
- `GET /api/reference/pod-positions` - Ad pod positions
- `GET /api/reference/device-types` - Device types
- `GET /api/reference/connection-types` - Connection types
- `GET /api/reference/carriers/{country}` - Mobile carriers

### Currency
- `GET /api/currencies` - Supported currencies
- `GET /api/currency/convert` - Convert amount

## Prioritized Backlog

### Completed
- [x] Core bidding engine
- [x] Campaign targeting
- [x] Win notifications
- [x] Budget pacing
- [x] Bid shading
- [x] Frequency capping
- [x] SPO
- [x] ML prediction
- [x] Campaign insights
- [x] Multi-currency
- [x] Enhanced targeting (geo lat/long, device carriers)
- [x] Video targeting with dropdowns
- [x] Ad placements
- [x] SSP ORTB version
- [x] Theme toggle
- [x] Creative preview

### P1 - Upcoming
- [ ] Campaign Comparison Tool
- [ ] Real-time Dashboard (WebSocket)
- [ ] A/B Testing Framework

### P2 - Future
- [ ] Advanced Fraud Detection
- [ ] Viewability Prediction
- [ ] Custom Audience Segments
- [ ] Native/Audio Ad Format Expansion
- [ ] Creative Editor with Live Preview

## Tech Stack
- **Backend**: FastAPI, Motor (async MongoDB), Pydantic
- **Frontend**: React, Tailwind CSS, Shadcn/UI, Recharts, Axios
- **Database**: MongoDB
- **Domain**: Ad-Tech, OpenRTB, Programmatic Advertising
