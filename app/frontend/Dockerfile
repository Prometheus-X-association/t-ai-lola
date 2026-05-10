FROM php:8.4-apache

EXPOSE 80 443
WORKDIR  /var/www/html

RUN apt-get update && apt-get install -y --no-install-recommends \
  unzip npm zlib1g-dev libpng-dev libfreetype6-dev libjpeg-dev libicu-dev \
  && docker-php-ext-configure gd --with-freetype --with-jpeg \
  && docker-php-ext-install -j$(nproc) pdo pdo_mysql gd intl \
  && curl -sS https://getcomposer.org/installer -o composer-setup.php \
  && php composer-setup.php --install-dir=/usr/local/bin --filename=composer \
  && rm composer-setup.php \
  && npm install --global yarn \
  && npm cache clean --force \
  && rm -rf /var/lib/apt/lists/*

#APACHE
RUN a2enmod rewrite
COPY build/000-default.conf /etc/apache2/sites-enabled/

COPY build/app .

RUN yarn install && yarn cache clean
RUN composer install && composer clearcache
