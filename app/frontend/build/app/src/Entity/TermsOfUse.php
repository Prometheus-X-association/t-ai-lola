<?php

namespace App\Entity;

use App\Repository\TermsOfUseRepository;
use Doctrine\ORM\Mapping as ORM;
use App\Entity\AbstractLolaEntity;

#[ORM\Entity(repositoryClass: TermsOfUseRepository::class)]
class TermsOfUse extends AbstractLolaEntity {

    #[ORM\Id]
    #[ORM\GeneratedValue]
    #[ORM\Column(type: 'integer')]
    private $id;

    #[ORM\Column(type: 'text', nullable: true)]
    private $description;

    #[ORM\Column(type: 'boolean')]
    private $active;

    public function __construct()
    {
        $this->active = false;
    }
    
    public function getId(): ?int
    {
        return $this->id;
    }

    public function getDescription(): ?string
    {
        return $this->description;
    }

    public function setDescription(string $description): self
    {
        $this->description = $description;

        return $this;
    }

    public function isActive(): ?bool
    {
        return $this->active;
    }

    public function setActive(): self
    {
        $this->active = true;
        return $this;
    }    

    public function setInactive(): self
    {
        $this->active = false;
        return $this;
    }

    public function getActive(): ?bool
    {
        return $this->active;
    }    

}
