<?php

namespace App\Entity;

interface LoggableInterface {

    public function setCreatedAt(\DateTime $createdAt): self;

    public function setUpdatedAt(\DateTime $createdAt): self;

    public function getCreatedAt(): \Datetime;

    public function getUpdatedAt(): ?\Datetime;

    public function setCreatedBy(?User $createdBy): self;

    public function setUpdatedBy(?User $createdBy): self;

    public function getCreatedBy(): ?User;

    public function getUpdatedBy(): ?User;
}
