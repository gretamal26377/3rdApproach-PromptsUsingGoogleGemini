# Marketplace Application (under development)

## Needs to be updated (GRL)

## Description

This is a multi-vendor e-commerce Marketplace Application built with React, Node.js, Python, MySQL, Docker microservices and other modern technologies. It allows multiple Stores, belonging to an Organisation, to sell their Products/Services through a single Platform

## Features

- **Organisation's Store Management:** Organisations can manage their own Stores, information, Products/Services, and Customer Orders
- **Product/Service Management:** Stores can add, update, and delete Products/Services, including details like name, description, price, and Category
- **User Authentication:** Users log in their profiles
- **User Roles assigned at Organisation level:**
  Admin: All Management Power
  Supervisor: Operational Management
  Staff: Daily Paperwork Management
  Viewer: Just read-only access view, no allow modification at all
- **Shopping Cart:** Customers can add Products/Services to their Cart and proceed to Checkout
- **Order Management:** Customers can view their Order history

- **Admin Panel:** A dedicated admin panel for managing users, stores, products, and orders

- **Search:** Customers & Users can Search for Products/Services, Organisations, Stores and Categories
- **PWA Support:** The Customer Frontend App is a Progressive Web App with offline access and improved performance features

## Technologies Used

- **Frontend:** React
- **Backend:** Python Flask

- **Monorepo:** shared-lib

- **Database:** MySQL
- **Order State Management:** Temporal Workflow Engine
- **UI Components:** Following STYLEGUIDE.md definitions
- **Form Validation:** Zod, React Hook Form
- **Icons:** Lucide React
- **Containerization:** Docker

## Project Structure (GRL: Need update)

```
marketplace/
├── database/
│   ├── init.sql
│   └── docker-compose.yml
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   ├── context/
│   │   ├── pages/
│   │   ├── services/
│   │   ├── App.js
│   │   ├── index.js
│   │   ├── App.css
│   │   └── setupProxy.js
│   ├── Dockerfile
│   ├── package.json
│   └── docker-compose.yml
├── backend/  (Not implemented in detail)
│   ├── ...
├── README.md
└── ...
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

The `database/init.sql` file contains the SQL schema for the application. The `.database/Dockerfile` and `.docker-compose.yml` files are provided for containerising a MySQL database using Docker.

## Frontend Setup

The `frontend` folder contains the React Frontend applications (Customer, Organisation-Admin and Platform-Admin apps). `npm install` installs the necessary dependencies, and `npm start` starts the development server. The `.frontend/Dockerfile` and `.docker-compose.yml` files are provided for containerising the frontend applications using Docker.

## Backend Setup

The `backend` folder contains the Python-Flask Backends applications (Customer, Organisation-Admin and Platform-Admin apps). The `.backend/Dockerfile` and `.docker-compose.yml` files are provided for containerising the backend applications using Docker.

## Docker Setup (GRL: update till here)

Docker is used to containerise the application, making it easier to set up and deploy.

- `frontend/Dockerfile` defines how to build a Docker image for the frontend.
- `frontend/docker-compose.yml` defines how to run the frontend container.
- `database/docker-compose.yml` defines how to run the database container.

To run the entire application using Docker Compose, you would typically have a single `docker-compose.yml` file at the root of the project that defines services for the frontend, backend, and database. Since the backend implementation is not provided, you would need to create that.

## Deployment

The provided Dockerfiles and `docker-compose.yml` files can be used to deploy the application to a container orchestration platform like Kubernetes or a cloud provider like AWS, Azure, or Google Cloud.

## Future Enhancements

- Add unit and integration tests
- Improve the UI/UX
- Add support for multiple languages

## Gral Notes

- "from typing import Optional": (import use) def find(id: int) -> Optional[User]: signals the function may return a User or None
