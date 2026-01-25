<div align="center">
<img width="1200" height="475" alt="GHBanner" src="https://github.com/user-attachments/assets/0aa67016-6eaf-458a-adb2-6e31a0763ed6" />
</div>

# Flash UI - PROJECT_elements Integration

Rapid UI generation using Gemini with OKLCH design token intelligence.

## Run Locally

**Prerequisites:** Node.js, Doppler CLI

### Default (Doppler)

```bash
# One-time setup
doppler setup --project ai-tools --config dev

# Install and run
npm install
npm run dev
```

### Fallback (Local .env)

```bash
# Set GEMINI_API_KEY in .env.local
npm install
npm run dev:local
```

## Commands

| Command | Description |
|---------|-------------|
| `npm run dev` | Development with Doppler secrets |
| `npm run dev:local` | Development with .env.local |
| `npm run build` | Production build with Doppler |
| `npm run build:local` | Production build with .env.local |
| `npm run preview` | Preview production build |

## Features

- **Copycat Mode** - Pixel-perfect replication from images
- **OKLCH Color System** - Full design token integration
- **Semantic Presets** - Tier, Family, Ring, Role colors
- **Three-Phase Pipeline** - Analysis → Synthesis → Generation
