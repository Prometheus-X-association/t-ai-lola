FROM php:8.2-apache

#Assume that the context is parent ../trax3 folder
LABEL org.opencontainers.image.authors="azim.roussanaly@loria.com"

# Args
ARG DEBIAN_FRONTEND=noninteractive

# Enable Apache mod_rewrite
RUN a2enmod rewrite

# Install required dependencies
RUN apt-get update && apt-get install -y \
    libcurl4-openssl-dev \
    libxml2-dev \
    libssl-dev \
    libpq-dev \
    libonig-dev \
    libzip-dev \
    zlib1g-dev\
    zip \
    unzip \
    git
RUN rm -rf /var/lib/apt/lists/*

# Install extensions
RUN docker-php-ext-install \
    pdo_mysql \
    pdo_pgsql
RUN docker-php-ext-enable  \
    pdo_mysql \
    pdo_pgsql

#copy trax3 source code & .env.trax
RUN git clone https://github.com/trax-project/trax3-starter-lrs.git /var/www/trax3
#COPY lrs/build/trax3 /var/www/trax3/
COPY .env.trax /var/www/trax3/.env
WORKDIR /var/www/trax3/
RUN chmod -R 775 bootstrap/cache storage
# Install Composer
RUN curl -sS https://getcomposer.org/installer | php -- --install-dir=/usr/local/bin --filename=composer
RUN composer install


# create a virtual host trax3 & disable default site
RUN chown -R www-data:www-data /var/www/trax3
RUN chmod -R 755 /var/www
COPY lrs/build/trax3.conf /etc/apache2/sites-available/trax3.conf
#RUN echo "memory_limit = 1024M" > /usr/local/etc/build/conf.d/memory-limit.ini
RUN echo "php_value memory_limit 1024K" > /var/www/trax3/.htaccess
RUN a2ensite trax3
RUN a2dissite 000-default.conf

RUN php artisan key:generate
#Bug: not working in docker, but okay in local ????
#RUN php artisan database:install --force
#RUN php artisan migrate --force

# Expose port 80
EXPOSE 80

# Start Apache in the foreground
CMD ["apache2-foreground"]