# Microservices Project

This project consists of two microservices:
- User Service (Authentication and User Management)
- Order Service (Order Processing)

## Prerequisites

- Python 3.9 or higher
- MongoDB
- Docker and Docker Compose (for Docker deployment)

## Project Structure
```
microservices_project/
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── README.md
├── run_services.py
├── shared/              # Shared utilities and models
├── user_service/        # User management service
└── order_service/       # Order processing service
```

## Running Locally

1. Create and activate a virtual environment:
```bash
python -m venv venv
# On Windows
venv\Scripts\activate
# On Unix or MacOS
source venv/bin/activate
```

2. Install requirements:
```bash
pip install -r requirements.txt
```

3. Start the services:
```bash
python run_services.py
```

The services will be available at:
- User Service: http://localhost:8000
- Order Service: http://localhost:8001
- MongoDB: localhost:27017

## Running with Docker

1. Build and start the services:
```bash
docker-compose up --build
```

Or run in detached mode:
```bash
docker-compose up -d
```

2. Stop the services:
```bash
docker-compose down
```

## API Documentation

Once the services are running, you can access the Swagger documentation at:
- User Service: http://localhost:8000/docs
- Order Service: http://localhost:8001/docs


## Basic Usage

1. Create a user:
```bash
curl -X POST http://localhost:8000/users/ \
-H "Content-Type: application/json" \
-d '{
    "email": "test@example.com",
    "full_name": "Test User",
    "password": "password123"
}'
```

2. Get authentication token:
```bash
curl -X POST http://localhost:8000/token \
-d "username=test@example.com&password=password123"
```

3. Create an order (using the token from step 2):
```bash
curl -X POST http://localhost:8001/orders/ \
-H "Authorization: Bearer YOUR_TOKEN" \
-H "Content-Type: application/json" \
-d '{
    "items": [
        {
            "product_id": "123",
            "quantity": 2,
            "price_per_unit": 29.99
        }
    ],
    "shipping_address": "123 Main St"
}'
```

## License

This project is licensed under the MIT License.
