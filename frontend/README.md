# Kiwi Frontend

React-based frontend for the Kiwi portfolio management application
(Assignment 5).

This is a single-page application (SPA) built with Vite + React 19
that consumes the Flask backend API (Assignments 1–4) and uses
AWS Cognito for OIDC authentication.

## Features

- **Authentication**: OIDC Authorization Code flow with AWS Cognito Hosted UI
- **Portfolio Management**: List, create, and delete portfolios
- **Holdings & Trading**: View holdings, execute buy/sell orders against
  Alpha Vantage real-time prices
- **Transaction History**: Per-portfolio transaction log with timestamps
- **Role-Based Authorization (Frontend)**:
  - **Owner**: full access (view, buy/sell, delete)
  - **Manager**: view + buy/sell, no delete
  - **Viewer**: read-only (no buy/sell, no delete)
  - Role badge displayed on every portfolio card and detail page
- **Reactive UI**: lists and tables refresh automatically after mutations
- **Friendly error handling**: backend errors (insufficient funds,
  ticker not found, deletion of non-empty portfolios, permission denied)
  are surfaced to the user with clear messages

## Tech Stack

- **Build Tool**: Vite 8
- **Framework**: React 19
- **Routing**: react-router-dom 7
- **HTTP**: axios (with auth interceptors)
- **JWT**: jwt-decode (for extracting username from ID token)
- **Styling**: Plain CSS with CSS custom properties

## Project Structure
frontend/
├── src/
│   ├── components/
│   │   ├── LoginPage.jsx           # OIDC sign-in entry
│   │   ├── CallbackPage.jsx        # Cognito redirect handler
│   │   ├── ProtectedRoute.jsx      # Auth-guarded route wrapper
│   │   ├── Dashboard.jsx           # Portfolio list page
│   │   ├── PortfolioList.jsx       # Portfolio cards grid
│   │   ├── PortfolioCard.jsx       # Single portfolio card (role-aware)
│   │   ├── CreatePortfolioModal.jsx
│   │   ├── PortfolioDetail.jsx     # Portfolio detail page (role-aware)
│   │   ├── BuyForm.jsx
│   │   ├── SellForm.jsx
│   │   └── TransactionHistory.jsx
│   ├── services/
│   │   ├── authService.js          # OIDC token exchange & storage
│   │   ├── userService.js          # Decode JWT, get current username
│   │   ├── apiClient.js            # axios instance with auth interceptors
│   │   ├── portfolioService.js     # Portfolio API wrappers
│   │   └── tradeService.js         # Trade API wrappers
│   ├── config/
│   │   └── cognito.js              # Cognito config from env vars
│   ├── App.jsx                     # Router setup
│   ├── App.css
│   ├── index.css
│   └── main.jsx
├── .env.example                    # Environment variable template
├── package.json
└── vite.config.js
## Setup

### Prerequisites

- Node.js 20+ and npm
- Backend Flask app running at `http://localhost:5000` (see project root README)
- AWS Cognito User Pool configured with:
  - Hosted UI domain
  - Callback URL `http://localhost:5173/callback`
  - Sign-out URL `http://localhost:5173/`
  - OAuth 2.0 Authorization Code grant
  - Scopes: `openid`, `email`, `profile`

### Installation

```bash
cd frontend
npm install
```

### Environment Variables

```bash
cp .env.example .env.local
```

Edit `.env.local` and fill in your Cognito values. See `.env.example`
for the list of required variables.

### Development

```bash
npm run dev
```

The application will be available at `http://localhost:5173`.

The backend must be running at `http://localhost:5000` for API calls
to succeed.

### Build

```bash
npm run build
npm run preview
```

## Demo / Testing Flow

1. Sign in as the portfolio owner (e.g. `manager_wen`).
2. Create a portfolio, then buy a few shares (e.g. AAPL, TSLA).
3. Use Postman to share the portfolio with another user:
POST http://localhost:5000/portfolios/<id>/access
Authorization: Bearer <owner's token>
Body: { "username": "viewer_wen", "role": "viewer" }

4. Sign out, then sign in as the shared user (`viewer_wen` or `test_wen`)
   to see role-based UI in action:
   - Viewer: read-only, no Buy/Sell, no Delete
   - Manager: Buy/Sell visible, no Delete
   - Owner: full access including Delete (when portfolio has no holdings)

## Backend API Endpoints Consumed

| Method | Path | Purpose |
|---|---|---|
| GET | `/portfolios/user/<username>` | List portfolios accessible to user |
| GET | `/portfolios/<id>` | Get portfolio detail (with `my_role`) |
| POST | `/portfolios/` | Create portfolio |
| DELETE | `/portfolios/<id>` | Delete portfolio (owner only, no holdings) |
| GET | `/portfolios/<id>/transactions` | List transactions |
| POST | `/trade/buy` | Execute buy order (owner/manager only) |
| POST | `/trade/sell` | Execute sell order (owner/manager only) |

All endpoints require a valid Cognito JWT in the `Authorization: Bearer <token>` header.

## Notes

- The frontend never sees the user's password; authentication is fully
  delegated to Cognito's Hosted UI.
- Tokens are stored in `localStorage` and automatically attached to all
  API requests via an axios interceptor.
- On 401/403 from the backend, the user is redirected to the login page.
- The `my_role` field returned by the backend drives all role-based UI
  decisions; the frontend never independently calls the
  `PortfolioSecurity` table.






