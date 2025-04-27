server {
    listen 80;
    server_name your_domain.com;

    location / {
        proxy_pass http://localhost:8080;  # Adjust to your application's port
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}