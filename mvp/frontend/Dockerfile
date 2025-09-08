FROM nginx:alpine

# Copy the HTML file to nginx web root
COPY index.html /usr/share/nginx/html/

# Create nginx config for SPA
RUN echo 'server { \
    listen 3000; \
    server_name localhost; \
    root /usr/share/nginx/html; \
    index index.html; \
    location / { \
        try_files $uri $uri/ /index.html; \
    } \
}' > /etc/nginx/conf.d/default.conf

# Remove default nginx config
RUN rm /etc/nginx/conf.d/default.conf.backup 2>/dev/null || true

EXPOSE 3000

CMD ["nginx", "-g", "daemon off;"]