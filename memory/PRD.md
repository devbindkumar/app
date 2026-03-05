# OpenRTB 2.5/2.6 Bidder with Campaign Manager - PRD

## Original Problem Statement
Build a Demand-Side Platform (DSP) Bidder that:
1. Receives and parses bid requests in OpenRTB 2.5 and 2.6 formats
2. Integrates with a Campaign Manager with comprehensive targeting
3. Makes real-time bidding decisions matching requests against campaigns
4. Constructs valid OpenRTB bid responses
5. Generates SSP endpoints with API key authentication

## User Personas
- **Ad Tech Professionals**: DSP operators managing programmatic campaigns
- **Campaign Managers**: Setting up targeting and budgets
- **SSP Integration Partners**: Sending bid requests via API

## Core Requirements (Static)
- OpenRTB 2.5 and 2.6 protocol support
- Dual-parse logic for version detection
- Campaign CRUD with comprehensive targeting
- Creative management (banner/video/native)
- SSP endpoint management with API keys
- Real-time bid logging and analytics
- Migration matrix documentation

## Architecture
- **Backend**: FastAPI + MongoDB
- **Frontend**: React + Tailwind + Shadcn
- **Bidding Engine**: Real-time matching with targeting rules
- **Protocol Handler**: Version detection, field migration

## What's Been Implemented (March 5, 2026)
✅ Backend:
- OpenRTB parser with 2.5/2.6 version detection
- Campaign Manager APIs (CRUD, activate/pause)
- Creative Management (banner/video/native)
- SSP Endpoint Management with API key auth
- Bid endpoint POST /api/bid with targeting engine
- Bid logging and statistics
- Migration matrix endpoint

✅ Frontend:
- Dark theme dashboard with charts (Recharts)
- Campaigns list with status management
- Campaign form with 7-tab targeting configuration
- Creatives grid with type badges
- SSP Endpoints with API key reveal/copy
- Bid Logs with real-time monitoring
- Migration Matrix reference page

✅ OpenRTB Features:
- Video placement/plcmt field migration
- Privacy fields (GDPR, CCPA) handling
- Ad pod fields (podid, podseq, slotinpod)
- Structured User Agent parsing
- Rewarded inventory support

## Prioritized Backlog

### P0 - Completed
- [x] Core bidding engine
- [x] Campaign targeting
- [x] API key authentication
- [x] Dashboard analytics

### P1 - Next Phase
- [ ] Win/loss notification endpoints (nurl, burl)
- [ ] Budget pacing algorithms
- [ ] Real-time budget enforcement
- [ ] Campaign scheduling

### P2 - Future
- [ ] Bid shading algorithms
- [ ] Machine learning bid optimization
- [ ] A/B testing framework
- [ ] Advanced reporting exports

## Next Tasks
1. Implement win notification handler for nurl callbacks
2. Add budget pacing to prevent overspend
3. Build campaign performance reports
4. Add frequency capping support
