# Beauty Product Marketplace

A comprehensive e-commerce platform for buying and selling beauty and cosmetic products with community features and advertising capabilities.

## Features

### Core Functionality
- **User Management**: Registration, login, profile management with avatar-based anonymity
- **KYC Verification**: Document upload and verification system for sellers
- **Product Marketplace**: Product listings with images, categories, and reviews
- **Shopping System**: Cart functionality, checkout process, and order tracking
- **Payment Integration**: Support for Stripe, Paystack, and Flutterwave
- **Community Features**: Chat rooms, private messaging, and age verification for adult content
- **Advertisement System**: Ad placement slots and management interface
- **Admin Panel**: User management, product approval, KYC review, and content moderation

### Technical Features
- Mobile-responsive design
- RESTful API
- JWT authentication
- Database optimization with caching
- Security features (XSS protection, SQL injection prevention)
- Rate limiting
- Comprehensive test suite

## Prerequisites

- Python 3.8+
- PostgreSQL 12+
- Redis 6+
- Docker (for containerized deployment)
- Node.js and npm (for frontend assets)

## Quick Start with Docker

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/beautymarket.git
   cd beautymarket
   ```

2. Update environment variables in `docker-compose.yml`:
   ```bash
   # Change default passwords and secrets
   ```

3. Build and run the containers:
   ```bash
   docker-compose up --build
   ```

4. Run database migrations:
   ```bash
   docker-compose exec web python manage.py migrate
   ```

5. Create a superuser:
   ```bash
   docker-compose exec web python manage.py createsuperuser
   ```

6. Access the application:
   - Web interface: http://localhost:8000
   - Admin panel: http://localhost:8000/admin

## Manual Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/beautymarket.git
   cd beautymarket
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up the database:
   ```bash
   # Create PostgreSQL database
   sudo -u postgres psql
   CREATE DATABASE beautymarket;
   CREATE USER beautymarket_user WITH PASSWORD 'your_secure_password';
   GRANT ALL PRIVILEGES ON DATABASE beautymarket TO beautymarket_user;
   \q
   ```

5. Configure environment variables:
   ```bash
   # Copy and edit the .env file
   cp .env.example .env
   # Edit .env with your settings
   ```

6. Run database migrations:
   ```bash
   python manage.py migrate
   ```

7. Collect static files:
   ```bash
   python manage.py collectstatic
   ```

8. Create a superuser:
   ```bash
   python manage.py createsuperuser
   ```

9. Start the development server:
   ```bash
   python manage.py runserver
   ```

## Production Deployment

For production deployment, follow the detailed instructions in [docs/deployment_guide.md](docs/deployment_guide.md).

Key considerations for production:
- Use a production web server (Nginx + Gunicorn)
- Configure SSL certificates
- Set up database backups
- Implement monitoring and logging
- Configure caching with Redis
- Set up CDN for static assets
- Implement proper security headers

## API Documentation

The API documentation is available at `/api/docs/` when the application is running.

## Testing

Run the test suite:
```bash
python manage.py test
```

For coverage report:
```bash
coverage run --source='.' manage.py test
coverage report
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For support, please open an issue on the GitHub repository or contact the development team.
