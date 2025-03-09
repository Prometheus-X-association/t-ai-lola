FROM php:7.4-apache

EXPOSE 80 443
WORKDIR  /var/www/html

RUN apt-get update && apt-get install -y \
  vim nano git unzip npm \
  libonig-dev libcurl4-openssl-dev && \
  docker-php-ext-install pdo pdo_mysql mbstring curl tokenizer ctype json bcmath exif && \
  curl -sS https://getcomposer.org/installer -o composer-setup.php && \
  php composer-setup.php --install-dir=/usr/local/bin --filename=composer && \
  a2enmod rewrite

## Fix the version of composer to 1.10 because trax/lrs raises errors with composer 2
RUN chmod -R a=rwx /var/www/html/traxlrs/storage
RUN chmod -R a=rwx /var/www/html/traxlrs/bootstrap/cache
COPY 000-default.conf /etc/apache2/sites-enabled/
COPY phpmyadmin-misc.ini /usr/local/etc/php/conf.d/
