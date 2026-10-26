<?php

declare(strict_types=1);

namespace DoctrineMigrations;

use Doctrine\DBAL\Schema\Schema;
use Doctrine\Migrations\AbstractMigration;

/**
 * Migration to add upload_type and target_filename to dataset table
 */
final class Version20261026090000 extends AbstractMigration
{
    public function getDescription(): string
    {
        return 'Add upload_type and target_filename to dataset table';
    }

    public function up(Schema $schema): void
    {
        $this->addSql("ALTER TABLE dataset ADD upload_type VARCHAR(30) DEFAULT 'sftp' NOT NULL, ADD target_filename VARCHAR(255) DEFAULT NULL");
        $this->addSql("UPDATE dataset SET upload_type = 'pdc_jwt' WHERE contract IS NOT NULL AND contract != ''");
    }

    public function down(Schema $schema): void
    {
        $this->addSql("ALTER TABLE dataset DROP upload_type, DROP target_filename");
    }
}
