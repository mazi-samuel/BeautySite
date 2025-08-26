# Beauty Product Marketplace - API Documentation

## Overview

This document provides documentation for the Beauty Product Marketplace RESTful API. The API allows developers to integrate with the platform for various functionalities including user management, product listings, shopping cart, community features, and advertisements.

## Authentication

Most API endpoints require authentication using JWT (JSON Web Tokens). To authenticate, first obtain a token by logging in, then include it in the Authorization header of subsequent requests.

### Obtain Authentication Token

**POST** `/api/auth/login`

Request body:
```json
{
  "email": "user@example.com",
  "password": "userpassword"
}
```

Response:
```json
{
  "success": true,
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "user": {
      "id": 1,
      "username": "johndoe",
      "email": "user@example.com",
      "user_type": "buyer"
    }
  }
}
```

### Use Authentication Token

Include the token in the Authorization header:
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

## Rate Limiting

All API endpoints are rate-limited to prevent abuse:
- 100 requests per hour for authenticated users
- 10 requests per hour for unauthenticated users

## Response Format

All API responses follow a consistent format:

Success response:
```json
{
  "success": true,
  "message": "Description of the action",
  "data": {}
}
```

Error response:
```json
{
  "success": false,
  "message": "Error description",
  "errors": [
    "Detailed error information"
  ]
}
```

## Endpoints

### User Authentication

#### Register a New User
**POST** `/api/auth/register`

Request body:
```json
{
  "username": "johndoe",
  "email": "user@example.com",
  "phone": "+1234567890",
  "password": "securepassword",
  "user_type": "buyer"
}
```

#### Login
**POST** `/api/auth/login`

Request body:
```json
{
  "email": "user@example.com",
  "password": "securepassword"
}
```

#### Refresh Token
**POST** `/api/auth/refresh`

Request body:
```json
{
  "refresh_token": "refresh_token_here"
}
```

### User Profile

#### Get User Profile
**GET** `/api/users/profile`

#### Update User Profile
**PUT** `/api/users/profile`

Request body:
```json
{
  "display_name": "John Doe",
  "bio": "Beauty enthusiast",
  "date_of_birth": "1990-01-01"
}
```

#### Upload Avatar
**POST** `/api/users/avatar`

Multipart form data with image file.

#### Change Password
**PUT** `/api/users/password`

Request body:
```json
{
  "current_password": "oldpassword",
  "new_password": "newpassword"
}
```

### KYC Verification

#### Submit KYC Documents
**POST** `/api/kyc/submit`

Multipart form data with ID document and selfie.

#### Get KYC Status
**GET** `/api/kyc/status`

### Products

#### Get Product Categories
**GET** `/api/categories`

#### Get Products
**GET** `/api/products`

Query parameters:
- `category_id`: Filter by category
- `search`: Search term
- `min_price`: Minimum price filter
- `max_price`: Maximum price filter
- `sort`: Sort order (price_asc, price_desc, newest, rating)
- `page`: Page number for pagination
- `limit`: Number of items per page

#### Get Product Detail
**GET** `/api/products/{id}`

#### Create Product (Sellers Only)
**POST** `/api/products`

Request body:
```json
{
  "name": "Product Name",
  "description": "Product description",
  "price": 29.99,
  "quantity": 100,
  "category_id": 1,
  "images": ["base64_encoded_image_data"]
}
```

#### Update Product (Sellers Only)
**PUT** `/api/products/{id}`

Request body:
```json
{
  "name": "Updated Product Name",
  "description": "Updated product description",
  "price": 39.99,
  "quantity": 50,
  "category_id": 2
}
```

#### Delete Product (Sellers Only)
**DELETE** `/api/products/{id}`

#### Add Product Review
**POST** `/api/products/{id}/reviews`

Request body:
```json
{
  "rating": 5,
  "comment": "Excellent product!"
}
```

### Shopping Cart

#### Get Cart Items
**GET** `/api/cart`

#### Add Item to Cart
**POST** `/api/cart`

Request body:
```json
{
  "product_id": 1,
  "quantity": 2
}
```

#### Update Cart Item
**PUT** `/api/cart/{id}`

Request body:
```json
{
  "quantity": 3
}
```

#### Remove Item from Cart
**DELETE** `/api/cart/{id}`

#### Clear Cart
**DELETE** `/api/cart`

### Orders

#### Get Orders
**GET** `/api/orders`

Query parameters:
- `status`: Filter by order status
- `page`: Page number for pagination

#### Get Order Detail
**GET** `/api/orders/{id}`

#### Create Order (Checkout)
**POST** `/api/orders`

Request body:
```json
{
  "delivery_address": "123 Main St, City, State 12345",
  "payment_method": "stripe",
  "payment_token": "payment_token_here"
}
```

### Community

#### Get Chat Rooms
**GET** `/api/community/rooms`

Query parameters:
- `adult_content`: Filter for adult content rooms (requires age verification)
- `search`: Search term

#### Create Chat Room
**POST** `/api/community/rooms`

Request body:
```json
{
  "name": "Skincare Discussion",
  "description": "Discuss skincare routines and products",
  "is_private": false,
  "is_adult_content": false
}
```

#### Get Room Posts
**GET** `/api/community/rooms/{id}/posts`

Query parameters:
- `page`: Page number for pagination

#### Create Room Post
**POST** `/api/community/rooms/{id}/posts`

Request body:
```json
{
  "title": "New Skincare Product Review",
  "content": "I recently tried this new product and here's my review...",
  "media": "base64_encoded_image_data"
}
```

#### Get Post Comments
**GET** `/api/community/posts/{id}/comments`

#### Add Comment to Post
**POST** `/api/community/posts/{id}/comments`

Request body:
```json
{
  "content": "Great review! Thanks for sharing.",
  "media": "base64_encoded_image_data"
}
```

#### Get Private Messages
**GET** `/api/community/messages`

#### Send Private Message
**POST** `/api/community/messages`

Request body:
```json
{
  "recipient_id": 2,
  "content": "Hi, I'm interested in your product.",
  "media": "base64_encoded_image_data"
}
```

#### Verify Age for Adult Content
**POST** `/api/community/age-verification`

Request body:
```json
{
  "date_of_birth": "1990-01-01"
}
```

### Advertisements

#### Get Active Ads
**GET** `/api/ads`

Query parameters:
- `slot`: Filter by advertisement slot

### Admin Endpoints

#### Get Users (Admin Only)
**GET** `/api/admin/users`

Query parameters:
- `user_type`: Filter by user type
- `is_active`: Filter by active status
- `kyc_status`: Filter by KYC status

#### Update User Status (Admin Only)
**PUT** `/api/admin/users/{id}/status`

Request body:
```json
{
  "is_active": true
}
```

#### Get Pending KYC Submissions (Admin Only)
**GET** `/api/admin/kyc/pending`

#### Review KYC Submission (Admin Only)
**PUT** `/api/admin/kyc/{id}/review`

Request body:
```json
{
  "status": "verified",
  "rejection_reason": ""
}
```

#### Get Pending Products (Admin Only)
**GET** `/api/admin/products/pending`

#### Review Product (Admin Only)
**PUT** `/api/admin/products/{id}/review`

Request body:
```json
{
  "status": "approved",
  "rejection_reason": ""
}
```

#### Get Reported Community Content (Admin Only)
**GET** `/api/admin/community/reports`

#### Moderate Community Content (Admin Only)
**PUT** `/api/admin/community/reports/{id}/moderate`

Request body:
```json
{
  "action": "remove",
  "notes": "Inappropriate content"
}
```

#### Manage Advertisements (Admin Only)
**GET** `/api/admin/ads`
**POST** `/api/admin/ads`
**PUT** `/api/admin/ads/{id}`
**DELETE** `/api/admin/ads/{id}`

#### Get Analytics (Admin Only)
**GET** `/api/admin/analytics`

Query parameters:
- `period`: Time period (day, week, month, year)

## Error Codes

- 200: Success
- 201: Created
- 400: Bad Request (validation errors)
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 429: Too Many Requests
- 500: Internal Server Error

## Rate Limiting Headers

All responses include rate limiting headers:
- `X-RateLimit-Limit`: Request limit per hour
- `X-RateLimit-Remaining`: Requests remaining in current window
- `X-RateLimit-Reset`: Time when rate limit resets (Unix timestamp)
