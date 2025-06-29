# Marketplace Application (under development)
## Needs to be updated (GRL) 

## Description

This is a multi-vendor e-commerce marketplace application built with React, Node.js, and other modern technologies. It allows multiple stores to sell their products through a single platform.


## Features

- **Store Management:** Store owners can manage their store information, products, and orders.
- **Product Management:** Store owners can add, update, and delete products, including details like name, description, price, and category.
- **User Authentication:** Users can create accounts, log in, and manage their profiles.
- **User Roles for simplicity assigned by Store:**
    Admin: All Management Power
    Supervisor: Operational Management
    Seller: Daily Paperwork
    Viewver: Just view no modification at all 
- **Shopping Cart:** Users can add products to their cart and proceed to checkout.
- **Order Management:** Users can view their order history.
- **Admin Panel:** A dedicated admin panel for managing users, stores, products, and orders.
- **Search:** Users can search for products and stores.
- **PWA Support:** Progressive Web App features for offline access and improved performance.

## Technologies Used

- **Frontend:** React
- **Backend:** Node.js, Express (GRL: Not sure about Express)
- **Database:** MySQL
- **State Management:** React Context
- **UI Components:** Radix UI
- **Form Validation:** Zod, React Hook Form
- **Icons:** Lucide React
- **Containerization:** Docker

## Project Structure

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

- Node.js and npm installed.
- Docker installed.

### Installation

1.  **Clone the repository:**

    ```bash
    git clone <repository_url>
    cd marketplace
    ```

2.  **Navigate to the `database` folder and start the database:**

    ```bash
    cd database
    docker-compose up -d
    ```

3.  **Navigate to the `frontend` folder and install dependencies and start the frontend:**

    ```bash
    cd ../frontend
    npm install
    npm start
    ```

    The frontend will be accessible at `http://localhost:3000`.

4.  **Set up the backend:**
    - The `backend` folder is outlined in the project structure, but the implementation details are not provided in this code. You would need to set up a Node.js/Express.js backend, create the necessary API endpoints, and connect it to the MySQL database. The `setupProxy.js` in the `frontend` folder is configured to proxy API requests to `http://backend:5000`, so your backend should be running at that address (or you should change the proxy configuration).
    - You'll need to install the necessary dependencies for your backend (e.g., `express`, `mysql2`), define your models, controllers, and routes, and handle database connections.

## Database Setup

The `database/init.sql` file contains the SQL schema for the application. The `database/docker-compose.yml` file sets up a MySQL database using Docker. When you run `docker-compose up -d` in the `database` directory, it will create a containerized MySQL instance with the schema defined in `init.sql`.

## Frontend Setup

The `frontend` folder contains the React application. `npm install` installs the necessary dependencies, and `npm start` starts the development server. The `Dockerfile` and `docker-compose.yml` files are provided for containerizing the frontend application.

## Backend Setup (Conceptual)

The `backend` folder is included in the project structure, but the actual code is not provided. A complete implementation would involve:

1.  Creating a Node.js/Express.js application.
2.  Installing dependencies (e.g., `express`, `mysql2`, `body-parser`, `cors`).
3.  Connecting to the MySQL database using a library like `mysql2`.
4.  Defining API endpoints for:
    - User authentication (login, signup, logout)
    - Store management (create, get, update, delete)
    - Product management (create, get, update, delete)
    - Order management (create, get)
    - User management (get, update, delete) - for admins
5.  Implementing business logic for each endpoint.
6.  Securing the API endpoints.

## Docker Setup

Docker is used to containerize the application, making it easier to set up and deploy.

- `frontend/Dockerfile` defines how to build a Docker image for the frontend.
- `frontend/docker-compose.yml` defines how to run the frontend container.
- `database/docker-compose.yml` defines how to run the database container.

To run the entire application using Docker Compose, you would typically have a single `docker-compose.yml` file at the root of the project that defines services for the frontend, backend, and database. Since the backend implementation is not provided, you would need to create that.

## Deployment

The provided Dockerfiles and `docker-compose.yml` files can be used to deploy the application to a container orchestration platform like Kubernetes or a cloud provider like AWS, Azure, or Google Cloud.

## Future Enhancements

- Implement the backend.
- Add unit and integration tests.
- Implement user roles and permissions.
- Implement payment processing.
- Add more advanced search features.
- Improve the UI/UX.
- Add support for multiple languages.
- Implement a review system.