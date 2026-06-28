# Marketplace Application (under development)

## Description

This is a Multi-Vendor e-commerce Marketplace Application built with React, Node.js, Python, MySQL, Docker microservices and other modern technologies. It allows multiple Stores, belonging to an Organisation and managed by different User Roles, to sell their Products/Services through a single Platform to Customers who use this Platform, through their Account, to Search, Cart, Checkout and get those Product/Services Delivered. 

## Features

- **Organisation's Store Management:** Organisations can manage their own Stores, information, Products/Services, and Customer Orders

- **Product/Service Management:** Stores can Add, Update, and Enable/Disable Products/Services, including details like Name, Description, Price and Category

- **User Authentication:** Users Log in their Profiles

- **User Roles assigned at Organisation level:**
  Admin: All Management Power
  Supervisor: Operational Management
  Staff: Daily Paperwork Management
  Viewer: Just read-only access view, no allow modification at all

- **Shopping Cart:** Customers can add Products/Services to their Cart and proceed to Checkout

- **Order Management:** Customers can view their Order history

- **Admin Panel:** A dedicated Admin Panel for managing Users, Stores, Products/Services, and Orders

- **Search:** Customers & Users can Search for Products/Services, Organisations, Stores and Categories using the same Search Tool

- **PWA Support:** The Customer Frontend App is a Progressive Web App (PWA) with offline access and improved performance features

## Technologies Used

- **Frontend:** React (for Customer and Admin Apps)
- **Backend:** Python Flask (for Customer and Admin Apps)
- **Monorepo:** Sharing code for Frontend from ./frontend/shared-lib local package and for Backend from ./backend/app/shared folder
- **Database:** MySQL
- **Search Engine:** More info in [SEARCH_ENGINE_SWITCH.md](backend/SEARCH_ENGINE_SWITCH.md)
- **Order State Management:** Temporal Workflow Engine
- **UI Components:** Following STYLEGUIDE.md definitions
- **Form Validation:** Zod, React Hook Form
- **Icons:** Lucide React
- **Containerization:** Docker

## Project Structure

```text
pwa-marketplace/
├── backend/
│   ├── app/
│   │   ├── admin/
│   │   │   ├── __init__.py
│   │   │   ├── customer_management.py
│   │   │   ├── customer_routes.py
│   │   │   ├── wsgi.py
│   │   │   └── __pycache__/
│   │   ├── customer/
│   │   │   ├── __init__.py
│   │   │   ├── customer_management.py
│   │   │   ├── customer_routes.py
│   │   │   ├── wsgi.py
│   │   │   └── __pycache__/
│   │   ├── org_admin/
│   │   ├── platform_admin/
│   │   └── shared/
│   │       ├── __init__.py
│   │       ├── auth.py
│   │       ├── auth copy.py
│   │       ├── config.py
│   │       ├── database.py
│   │       ├── management.py
│   │       ├── models.py
│   │       ├── models_old.py
│   │       ├── models_plain_sqlalchemy22flask_sqlalchemy.py
│   │       ├── models_sql2orm_flask_sqlalchemy.py
│   │       ├── models_sql2orm_plain_sqlalchemy2.py
│   │       ├── search/
│   │       ├── search_google/
│   │       ├── search_meili/
│   │       ├── search_old.py
│   │       ├── search_wsgi_old.py
│   │       ├── utils.py
│   │       └── __pycache__/
│   ├── alembic/
│   │   ├── env.py
│   │   ├── README
│   │   ├── script.py.mako
│   │   └── versions/
│   ├── docs/
│   │   ├── ER_DIAGRAM_README.md
│   │   ├── er_diagram.dot
│   │   ├── er_diagram_20251101_013405.dot
│   │   ├── er_diagram_20251101_023759.html
│   │   └── er_diagram_20251101_023759.mmd
│   ├── scripts/
│   │   ├── __init__.py
│   │   └── convert_models_sqlalchemy22flask_sqlalchemy.py
│   ├── tests/
│   ├── .venv-win/
│   ├── alembic.ini
│   ├── Dockerfile
│   ├── Dockerfile-search
│   ├── Dockerfile-worker
│   ├── requirements.txt
│   ├── SEARCH_ENGINE_SWITCH.md
│   └── __init__.py
├── database/
│   ├── docker-entrypoint-initdb.d/
│   ├── secrets/
│   ├── Dockerfile
│   └── init.sql
├── frontend/
│   ├── admin/
│   │   └── node_modules/
│   ├── customer/
│   │   ├── public/
│   │   ├── src/
│   │   │   ├── App.jsx
│   │   │   ├── Routes.jsx
│   │   │   ├── entry-client.old.jsx
│   │   │   ├── entry-server.old.jsx
│   │   │   ├── index.js
│   │   │   ├── main.old.jsx
│   │   │   ├── serviceWorker.js
│   │   │   ├── components/
│   │   │   │   ├── Cart.jsx
│   │   │   │   └── Checkout.jsx
│   │   │   ├── context/
│   │   │   ├── pages/
│   │   │   │   ├── CartPage.jsx
│   │   │   │   ├── CategoryProductServiceStoresPage.jsx
│   │   │   │   ├── HomePage.jsx
│   │   │   │   ├── index.page.jsx
│   │   │   │   ├── ProductServicePage.jsx
│   │   │   │   ├── SignupPage.jsx
│   │   │   ├── StorePage.jsx
│   │   │   ├── StoresPage.jsx
│   │   │   ├── _default.page.client.jsx
│   │   │   └── _default.page.server.jsx
│   │   ├── .env
│   │   ├── package.json
│   │   ├── README.md
│   │   ├── server.js
│   │   ├── vite.config.js
│   │   └── vite.config.old.js
│   ├── org-admin/
│   │   ├── src/
│   │   │   ├── App.css
│   │   │   ├── App.jsx
│   │   │   ├── assets/
│   │   │   ├── components/
│   │   │   ├── index.css
│   │   │   ├── main.jsx
│   │   │   └── Routes.jsx
│   ├── platform-admin/
│   │   ├── src/
│   │   │   ├── App.css
│   │   │   ├── App.jsx
│   │   │   ├── assets/
│   │   │   ├── components/
│   │   │   ├── index.css
│   │   │   ├── main.jsx
│   │   │   └── Routes.jsx
│   ├── shared-lib/
│   │   ├── src/
│   │   │   ├── components/
│   │   │   │   ├── Login.jsx
│   │   │   │   ├── ProductServiceCard.jsx
│   │   │   │   ├── ProductServiceList.jsx
│   │   │   │   ├── ProductServiceListingCard.jsx
│   │   │   │   ├── SearchBar copy 2.jsx
│   │   │   │   ├── SearchBar copy.jsx
│   │   │   │   ├── SearchBar.jsx
│   │   │   │   ├── Signup.jsx
│   │   │   │   ├── StoreCard.jsx
│   │   │   │   ├── StoreList.jsx
│   │   │   │   └── ui/
│   │   │   │       ├── alert.jsx
│   │   │   │       ├── badge.jsx
│   │   │   │       ├── button.jsx
│   │   │   │       ├── card.jsx
│   │   │   │       ├── carousel.jsx
│   │   │   │       ├── checkbox.jsx
│   │   │   │       ├── DarkModeToggle.jsx
│   │   │   │       ├── dialog.jsx
│   │   │   │       ├── dropdown.jsx
│   │   │   │       ├── form.jsx
│   │   │   │       ├── input.jsx
│   │   │   │       ├── label.jsx
│   │   │   │       ├── scroll-area.jsx
│   │   │   │       ├── table.jsx
│   │   │   │       └── toggle-switch.jsx
│   │   │   ├── context/
│   │   │   ├── index.js
│   │   │   ├── lib/
│   │   │   ├── pages/
│   │   │   ├── services/
│   │   │   └── stories/
│   │   └── package.json
│   ├── .npmrc
│   ├── Dockerfile
│   ├── globals.css
│   ├── node_modules/
│   ├── package.json
│   ├── package-lock.json
│   ├── pnpm-lock.yaml
│   ├── pnpm-workspace.yaml
│   ├── postcss.config.js
│   ├── storybook-CI-localhost-simulation.bat
│   ├── tailwind.config.js
│   └── .storybook/
├── docker-compose.yml
├── docker-compose.override.yml
├── README.md
├── STYLEGUIDE.md
├── tmp-db-stack.yml
├── coverage.xml
└── .coverage
```

## Getting Started

### Prerequisites

- Node.js and npm installed
- Docker installed

### Installation

1.  **Clone the repository:**

    ```bash
    git clone <repository_url>
    cd pwa-marketplace
    ```

2.  **Navigate to the `database` folder and start the database:**

    ```bash
    cd database
    docker-compose up -d db
    ```

3.  **Navigate to the `frontend` folder and install dependencies and start the frontend:**

    ```bash
    cd ../frontend
    npm install
    npm start
    ```

    The frontend will be accessible at `http://localhost:3000`.

4.  **Set up the backend:**
    - The `backend` folder is outlined in the project structure.
    - You'll need to install the necessary dependencies for your backend (eg: `mysql2`), define your models, controllers, and routes, and handle database connections

## Database Setup

The `./database/init.sql` file contains the SQL schema for the application. The `./database/Dockerfile` and `./docker-compose.yml` files are provided for containerising a MySQL database using Docker.

## Frontend Setup

The `./frontend` folder contains the React Frontend applications (Customer, Organisation-Admin and Platform-Admin Apps). `npm install` installs the necessary dependencies, and `npm start` starts the development server. The `./frontend/Dockerfile` and `./docker-compose.yml` files are provided for containerising the frontend applications using Docker.

## Backend Setup

The `./backend` folder contains the Python-Flask Backends applications (Customer, Organisation-Admin and Platform-Admin Apps). The `./backend/Dockerfile` and `./docker-compose.yml` files are provided for containerising the backend applications using Docker.

## Deployment using Docker

Docker is used to containerise the application, making it easier to set up and deploy.

- `.docker-compose.yml` defines how to run the whole Platform (Customer/Admins Frontend/Backend Apps)

## Future Enhancements

- Add unit and integration tests
- Improve the UI/UX
- Add support for multiple languages

## Gral Notes
