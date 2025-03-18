# Business Lookup Tool - Deployment Guide

This guide provides instructions for deploying the Business Lookup & Logistics Optimization Tool as a permanent interactive website.

## Deployment Options

The application is configured for multiple deployment options:

1. **Heroku Deployment**
2. **Docker Deployment**
3. **Manual Server Deployment**

## Prerequisites

- Git repository with your code
- API keys for Apollo.io, VectorShift, Google Maps, and LinkedIn
- PostgreSQL database (for production)
- Redis (optional, for caching)

## Option 1: Heroku Deployment

### Steps:

1. Create a Heroku account if you don't have one
2. Install the Heroku CLI
3. Login to Heroku:
   ```
   heroku login
   ```
4. Create a new Heroku app:
   ```
   heroku create business-lookup-tool
   ```
5. Add PostgreSQL add-on:
   ```
   heroku addons:create heroku-postgresql:hobby-dev
   ```
6. Add Redis add-on (optional):
   ```
   heroku addons:create heroku-redis:hobby-dev
   ```
7. Set environment variables:
   ```
   heroku config:set SECRET_KEY=your_secret_key
   heroku config:set APOLLO_API_KEY=your_apollo_api_key
   heroku config:set VECTORSHIFT_API_KEY=your_vectorshift_api_key
   heroku config:set GOOGLE_MAPS_API_KEY=your_google_maps_api_key
   heroku config:set LINKEDIN_API_KEY=your_linkedin_api_key
   ```
8. Deploy the application:
   ```
   git push heroku main
   ```
9. Open the application:
   ```
   heroku open
   ```

## Option 2: Docker Deployment

### Steps:

1. Make sure Docker and Docker Compose are installed
2. Create a `.env` file with your environment variables:
   ```
   SECRET_KEY=your_secret_key
   APOLLO_API_KEY=your_apollo_api_key
   VECTORSHIFT_API_KEY=your_vectorshift_api_key
   GOOGLE_MAPS_API_KEY=your_google_maps_api_key
   LINKEDIN_API_KEY=your_linkedin_api_key
   ```
3. Build and start the containers:
   ```
   docker-compose up -d
   ```
4. Access the application at `http://localhost:8080`

### Deploying to a Cloud Provider with Docker:

1. **AWS Elastic Container Service (ECS)**:
   - Create an ECS cluster
   - Create a task definition using the Dockerfile
   - Create a service to run the task
   - Set up an Application Load Balancer

2. **Google Cloud Run**:
   - Build and push the Docker image to Google Container Registry
   - Deploy the image to Cloud Run
   - Set environment variables in the Cloud Run configuration

3. **Azure Container Instances**:
   - Create a container group using the Docker image
   - Configure environment variables
   - Set up networking and DNS

## Option 3: Manual Server Deployment

### Steps:

1. Set up a server (e.g., Ubuntu on AWS EC2, DigitalOcean Droplet)
2. Install dependencies:
   ```
   sudo apt-get update
   sudo apt-get install python3 python3-pip postgresql nginx
   ```
3. Clone the repository:
   ```
   git clone https://github.com/yourusername/business-lookup-tool.git
   cd business-lookup-tool
   ```
4. Create a virtual environment:
   ```
   python3 -m venv venv
   source venv/bin/activate
   ```
5. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
6. Set up environment variables:
   ```
   export SECRET_KEY=your_secret_key
   export APOLLO_API_KEY=your_apollo_api_key
   export VECTORSHIFT_API_KEY=your_vectorshift_api_key
   export GOOGLE_MAPS_API_KEY=your_google_maps_api_key
   export LINKEDIN_API_KEY=your_linkedin_api_key
   export DATABASE_URL=postgresql://username:password@localhost/business_lookup
   ```
7. Set up Nginx as a reverse proxy:
   ```
   sudo nano /etc/nginx/sites-available/business-lookup-tool
   ```
   Add the following configuration:
   ```
   server {
       listen 80;
       server_name your_domain.com;

       location / {
           proxy_pass http://localhost:8080;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```
8. Enable the site:
   ```
   sudo ln -s /etc/nginx/sites-available/business-lookup-tool /etc/nginx/sites-enabled
   sudo nginx -t
   sudo systemctl restart nginx
   ```
9. Set up a systemd service:
   ```
   sudo nano /etc/systemd/system/business-lookup-tool.service
   ```
   Add the following configuration:
   ```
   [Unit]
   Description=Business Lookup Tool
   After=network.target

   [Service]
   User=ubuntu
   WorkingDirectory=/home/ubuntu/business-lookup-tool
   ExecStart=/home/ubuntu/business-lookup-tool/venv/bin/gunicorn --bind 0.0.0.0:8080 src.web_interface:app
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```
10. Start and enable the service:
    ```
    sudo systemctl start business-lookup-tool
    sudo systemctl enable business-lookup-tool
    ```
11. Access the application at your domain or server IP

## SSL Configuration

For production deployments, it's important to secure your application with SSL:

1. **Heroku**: SSL is automatically provided for all Heroku apps
2. **Docker/Cloud**: Use the provider's SSL configuration or a service like Let's Encrypt
3. **Manual Server**: Set up Let's Encrypt with Certbot:
   ```
   sudo apt-get install certbot python3-certbot-nginx
   sudo certbot --nginx -d your_domain.com
   ```

## Database Migrations

If you need to update the database schema:

1. Create a migration script in `src/migrations/`
2. Run the migration script before deploying the new version

## Monitoring and Logging

For production deployments, set up monitoring and logging:

1. **Heroku**: Use Heroku's built-in logging and add-ons like Papertrail
2. **Docker/Cloud**: Use the provider's monitoring services or set up Prometheus and Grafana
3. **Manual Server**: Set up logging with tools like ELK Stack (Elasticsearch, Logstash, Kibana)

## Backup Strategy

Regularly back up your database:

1. **Heroku**: Use Heroku PG Backups
2. **Docker/Cloud**: Set up automated backups with the provider's tools
3. **Manual Server**: Set up cron jobs for PostgreSQL dumps

## Scaling Considerations

As your application grows:

1. **Heroku**: Upgrade to higher dyno tiers
2. **Docker/Cloud**: Increase container resources or set up auto-scaling
3. **Manual Server**: Upgrade server resources or set up load balancing

## Troubleshooting

If you encounter issues during deployment:

1. Check application logs
2. Verify environment variables are set correctly
3. Ensure database connection is working
4. Check for firewall or network issues
5. Verify API keys are valid and have necessary permissions
