# CineGraph Frontend

The CineGraph frontend is built with **Next.js (App Router)**, **React**, **TypeScript**, and **Tailwind CSS**.

## Design Philosophy

- **Zero Direct Database Connections**: The browser interacts exclusively with the FastAPI backend (`http://127.0.0.1:8000`), preserving security and ensuring clean decoupling.
- **Type Safety**: Strictly typed with TypeScript.
- **Modern UI**: Clean dark-mode aesthetic designed for movie discovery and analytical visualizations.

## Prerequisites

- Node.js LTS (tested on Node v25 / v20+ LTS)
- npm (v10+)

## Getting Started

### 1. Install Dependencies
```bash
npm install
```

### 2. Configure Environment (Optional)
If connecting to an alternate backend port or host, specify:
```bash
# In .env.local
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
```

### 3. Run Development Server
```bash
npm run dev
```
Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

### 4. Production Build & Start
```bash
npm run build
npm run start
```
