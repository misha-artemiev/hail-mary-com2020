# Frontend

A modern React-based frontend for the Food Rescue project.

## Tech Stack

- **React 19** for responsive, modular frontend development for building the UI.
- **React Router** for fast, modern, client-side routing for a single-page application.
- **Vite** as a local webserver (for development) and as a fast, lightweight build system (for production).
- **TailwindCSS** for simply dynamically styling elements with a CSS framework.
- **ESLint** for code linting and formatting.
- **Prettier** for opinionated code formatting.

## Getting started

### Prerequisites

- **Node.js** (version 16 or higher)
- **npm/yarn** package manager

### Installation

1. Clone the repository and enter the frontend directory:

```bash
$ git clone https://github.com/misha-artemiev/hail-mary-com2020.git
$ cd frontend
```

2. Install dependencies:

```bash
$ npm install
```

### Development

Start the development server:

```bash
npm run dev
```

The application will be available at [`http://localhost:5713`](http://localhost:5713) (default Vite port). This uses **Hot Module Reload (HMR)** so saved changes will be instantly visible without the need to reload the page.

### Building for production

Vite can also be used to compile for production:

```bash
npm run build
```

This build can be found under `dev/`. It can be previewed with Vite:

```bash
npm run preview
```

The compiled webpage will be available at [`http://localhost:4713`](http://localhost:4713) (default Vite preview port).

### Code quality

Lint the code with `eslint`:

```bash
npm run lint
```

Format the code (opinionated) with `prettier`:

```bash
npm run format:fix
```

## Project structure

```
/frontend
├ dist/                 # Emitted webpage
├ node_modules/
├ src/
│   ├ assets/           # Static assets (e.g. images, icons)
│   ├ components/       # Reusable UI components
│   ├ pages/            # Page components (used by Router)
│   │   ├ Home.jsx
│   │   ├ Profile.jsx
│   │   └ NotFound.jsx
│   ├ App.jsx           # Loads the React Router
│   ├ main.jsx          # Main entrypoint for root element
│   └ index.css         # Initialises TailwindCSS
├ package.json
├ index.html
└ other config files...
```

## Available scripts

- `npm run dev` - Run the live development server.
- `npm run build` - Compile the project.
- `npm run preview` - Preview the _built_ product.
- `npm run lint` - Run ESLint: find .and fix linting (_e.g._ syntax) issues.
- `npm run format` - Run Prettier: find formatting issues.
- `npm run format:fix` - Run Prettier: find and fix formatting issues.
