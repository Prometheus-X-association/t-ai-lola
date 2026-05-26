# Stage 1: Builder (Install dependencies)
FROM ubuntu:25.10 AS builder

# Prevent interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Install build dependencies
RUN apt-get update && apt-get upgrade -y && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    unzip \
    git \
    php-cli \
    php-gd \
    php-xml \
    php-mbstring \
    php-curl \
    php-zip \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

# Install Composer
COPY --from=composer:2 /usr/bin/composer /usr/local/bin/composer

# Install Yarn globally
RUN npm install -g yarn && npm cache clean --force

WORKDIR /build

# Copy the application source code
COPY build/app .

# Set Symfony to production mode so cache:clear doesn't look for dev bundles
ENV APP_ENV=prod

# Install Node and PHP dependencies
RUN yarn install && yarn cache clean
RUN composer install --no-dev --optimize-autoloader && composer clearcache


# Stage 2: Production Image (Runtime)
FROM ubuntu:25.10

# Prevent interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Set environment to production to avoid loading dev bundles at runtime
ENV APP_ENV=prod
ENV APP_DEBUG=0

# Install Apache, PHP, and required extensions
RUN apt-get update && apt-get upgrade -y && apt-get install -y --no-install-recommends \
    apache2 \
    libapache2-mod-php \
    php-mysql \
    php-gd \
    php-intl \
    php-cli \
    php-curl \
    php-xml \
    php-mbstring \
    && rm -rf /var/lib/apt/lists/*

# Configure Apache & Enable necessary modules
RUN a2enmod rewrite

# Enhance Apache Security
RUN echo "ServerTokens Prod" >> /etc/apache2/conf-available/security-custom.conf \
    && echo "ServerSignature Off" >> /etc/apache2/conf-available/security-custom.conf \
    && echo "TraceEnable Off" >> /etc/apache2/conf-available/security-custom.conf \
    && a2enconf security-custom

# Copy custom Apache configuration
COPY build/000-default.conf /etc/apache2/sites-enabled/

# Set up the web root directory
WORKDIR /var/www/html

# Copy built application from the builder stage and set ownership
COPY --from=builder --chown=www-data:www-data /build /var/www/html

# Force production environment for Apache/PHP-FPM
RUN echo "APP_ENV=prod" > /var/www/html/.env \
    && echo "APP_DEBUG=0" >> /var/www/html/.env

# Remove default apache index page
RUN rm -f /var/www/html/index.html

# Set proper permissions for web server access
RUN chown -R www-data:www-data /var/www/html \
    && chmod -R 755 /var/www/html

EXPOSE 80 443

# Start Apache in the foreground
CMD ["apache2ctl", "-D", "FOREGROUND"]
