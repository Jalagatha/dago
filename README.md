# Food & Parcel Delivery API

A comprehensive REST API for a food delivery and parcel delivery platform built with FastAPI, PostgreSQL, and SQLAlchemy.

## Features

- **Dual-Purpose Platform**: Handles both food delivery and parcel delivery
- **User Authentication**: JWT-based authentication with role-based access control
- **Three User Roles**: Customers, Delivery Drivers, and Administrators
- **Restaurant Management**: Browse restaurants, view menus, and place orders
- **Parcel Delivery**: Send parcels with automated fee calculation based on distance
- **Driver Operations**: Accept orders, update delivery status, manage availability
- **Reviews & Ratings**: Rate restaurants and drivers after delivery
- **Admin Dashboard**: Manage users, restaurants, orders, and reviews

## Tech Stack

- **FastAPI**: Modern Python web framework
- **PostgreSQL**: Relational database
- **SQLAlchemy**: ORM for database operations
- **Alembic**: Database migrations
- **Pydantic**: Data validation and serialization
- **JWT**: Secure authentication
- **Passlib & Bcrypt**: Password hashing

## Project Structure

```
food_delivery_backend/
├── app/
│   ├── core/
│   │   ├── config.py          # Application configuration
│   │   ├── database.py        # Database connection
│   │   └── security.py        # Authentication utilities
│   ├── models/                # SQLAlchemy ORM models
│   │   ├── user.py
│   │   ├── restaurant.py
│   │   ├── food_order.py
│   │   ├── parcel.py
│   │   └── review.py
│   ├── schemas/               # Pydantic schemas
│   │   ├── auth.py
│   │   ├── user.py
│   │   ├── restaurant.py
│   │   ├── food_order.py
│   │   ├── parcel.py
│   │   └── review.py
│   └── routers/               # API endpoints
│       ├── auth.py
│       ├── restaurants.py
│       ├── food_orders.py
│       ├── parcels.py
│       ├── drivers.py
│       └── admin.py
├── alembic/                   # Database migrations
├── main.py                    # Application entry point
├── requirements.txt           # Python dependencies
├── Procfile                   # Deployment command
└── railway.toml               # Railway deployment config
```

## Setup Instructions

### 1. Clone and Navigate to Project

```bash
cd food_delivery_backend
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file (never commit this file):

```env
DATABASE_URL=postgresql://user:password@host:5432/dbname
SECRET_KEY=generate-with-openssl-rand-hex-32
DEBUG=false
CORS_ORIGINS=*
```

> **Note**: Generate a secure SECRET_KEY with: `openssl rand -hex 32`

### 5. Create Database

```bash
# Using psql
psql -U postgres -c "CREATE DATABASE food_delivery_db;"
```

### 6. Run Migrations

```bash
alembic upgrade head
```

### 7. Start the Server

```bash
python main.py
# Or use uvicorn directly:
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- **API**: http://localhost:8000
- **Interactive Docs (Swagger)**: http://localhost:8000/docs
- **Alternative Docs (ReDoc)**: http://localhost:8000/redoc

## API Endpoints

### Authentication

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/auth/register` | Register new user | No |
| POST | `/api/auth/login` | Login and get tokens | No |
| POST | `/api/auth/refresh` | Refresh access token | No |
| GET | `/api/auth/me` | Get current user info | Yes |
| POST | `/api/auth/logout` | Logout user | Yes |

### Restaurants

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/restaurants` | List all restaurants | No |
| GET | `/api/restaurants/{id}` | Get restaurant details | No |
| GET | `/api/restaurants/{id}/menu` | Get restaurant menu | No |
| GET | `/api/menu-items/{id}` | Get menu item details | No |
| GET | `/api/restaurants/{id}/reviews` | Get restaurant reviews | No |

### Food Orders

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/orders/food` | Create food order | Yes (Customer) |
| GET | `/api/orders/food` | List user's orders | Yes (Customer) |
| GET | `/api/orders/food/{id}` | Get order details | Yes |
| PUT | `/api/orders/food/{id}/cancel` | Cancel order | Yes (Customer) |
| POST | `/api/orders/food/{id}/review` | Review restaurant | Yes (Customer) |

### Parcel Deliveries

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/deliveries/parcel` | Create parcel delivery | Yes (Customer) |
| GET | `/api/deliveries/parcel` | List user's parcels | Yes (Customer) |
| GET | `/api/deliveries/parcel/{id}` | Get parcel details | Yes |
| PUT | `/api/deliveries/parcel/{id}/cancel` | Cancel parcel | Yes (Customer) |
| POST | `/api/deliveries/parcel/{id}/review` | Review driver | Yes (Customer) |

### Driver Operations

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/driver/available-orders` | Get available food orders | Yes (Driver) |
| GET | `/api/driver/available-parcels` | Get available parcels | Yes (Driver) |
| POST | `/api/driver/accept/food/{id}` | Accept food order | Yes (Driver) |
| POST | `/api/driver/accept/parcel/{id}` | Accept parcel | Yes (Driver) |
| PUT | `/api/driver/orders/{id}/status` | Update order status | Yes (Driver) |
| PUT | `/api/driver/parcels/{id}/status` | Update parcel status | Yes (Driver) |
| GET | `/api/driver/current-deliveries` | Get active deliveries | Yes (Driver) |
| PUT | `/api/driver/availability` | Toggle availability | Yes (Driver) |
| PUT | `/api/driver/location` | Update location | Yes (Driver) |

### Admin Operations

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/admin/users` | List all users | Yes (Admin) |
| PUT | `/api/admin/users/{id}` | Update user | Yes (Admin) |
| DELETE | `/api/admin/users/{id}` | Delete user | Yes (Admin) |
| POST | `/api/admin/restaurants` | Create restaurant | Yes (Admin) |
| PUT | `/api/admin/restaurants/{id}` | Update restaurant | Yes (Admin) |
| DELETE | `/api/admin/restaurants/{id}` | Delete restaurant | Yes (Admin) |
| POST | `/api/admin/restaurants/{id}/categories` | Create menu category | Yes (Admin) |
| POST | `/api/admin/restaurants/{id}/menu-items` | Create menu item | Yes (Admin) |
| GET | `/api/admin/orders` | List all orders | Yes (Admin) |
| GET | `/api/admin/parcels` | List all parcels | Yes (Admin) |
| GET | `/api/admin/reviews` | List all reviews | Yes (Admin) |
| DELETE | `/api/admin/reviews/{id}` | Delete review | Yes (Admin) |

## Usage Examples

### 1. Register a Customer

```bash
curl -X POST "http://localhost:8000/api/auth/register" \\
  -H "Content-Type: application/json" \\
  -d '{
    "email": "customer@example.com",
    "password": "securepassword",
    "phone_number": "+1234567890",
    "role": "customer",
    "full_name": "John Doe"
  }'
```

### 2. Login

```bash
curl -X POST "http://localhost:8000/api/auth/login" \\
  -H "Content-Type: application/json" \\
  -d '{
    "email": "customer@example.com",
    "password": "securepassword"
  }'
```

Response:
```json
{
  "access_token": "eyJhbGc...",
  "refresh_token": "eyJhbGc...",
  "token_type": "bearer"
}
```

### 3. List Restaurants

```bash
curl -X GET "http://localhost:8000/api/restaurants"
```

### 4. Create Food Order (with auth token)

```bash
curl -X POST "http://localhost:8000/api/orders/food" \\
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \\
  -H "Content-Type: application/json" \\
  -d '{
    "restaurant_id": "uuid-here",
    "delivery_address": "123 Main St, City",
    "delivery_latitude": 40.7128,
    "delivery_longitude": -74.0060,
    "items": [
      {
        "menu_item_id": "uuid-here",
        "quantity": 2,
        "special_instructions": "Extra spicy"
      }
    ]
  }'
```

### 5. Create Parcel Delivery

```bash
curl -X POST "http://localhost:8000/api/deliveries/parcel" \\
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \\
  -H "Content-Type: application/json" \\
  -d '{
    "recipient_name": "Jane Smith",
    "recipient_phone": "+0987654321",
    "pickup_address": "456 Oak Ave",
    "pickup_latitude": 40.7128,
    "pickup_longitude": -74.0060,
    "delivery_address": "789 Elm St",
    "delivery_latitude": 40.7589,
    "delivery_longitude": -73.9851,
    "parcel_description": "Documents",
    "parcel_size": "small",
    "weight_kg": 0.5
  }'
```

## Database Schema

### Key Tables

- **users**: User accounts with authentication
- **user_profiles**: User profile information
- **driver_profiles**: Driver-specific data (vehicle, ratings)
- **restaurants**: Restaurant information
- **menu_categories**: Menu organization
- **menu_items**: Food items with pricing
- **food_orders**: Customer food orders
- **order_items**: Items within each order
- **parcel_deliveries**: Parcel delivery requests
- **reviews**: Reviews for restaurants and drivers

## Development

### Running Tests

```bash
pytest
```

### Creating New Migration

```bash
alembic revision --autogenerate -m "Description of changes"
alembic upgrade head
```

### Checking Migration Status

```bash
alembic current
alembic history
```

## Security Notes

1. **Change the SECRET_KEY**: Generate a secure key with `openssl rand -hex 32`
2. **Update Database Credentials**: Use strong passwords in production
3. **Enable HTTPS**: Use a reverse proxy (nginx) with SSL in production
4. **Rate Limiting**: Consider adding rate limiting for production
5. **CORS**: Update CORS_ORIGINS in .env for production (don't use "*")

## License

This project is for educational and commercial use.

## Support

For issues or questions, please create an issue in the repository.
