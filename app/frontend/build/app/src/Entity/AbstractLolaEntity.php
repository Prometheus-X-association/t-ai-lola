<?php

namespace App\Entity;

use Doctrine\ORM\Mapping as ORM;

#[ORM\MappedSuperclass]
#[ORM\HasLifecycleCallbacks]
class AbstractLolaEntity implements LoggableInterface {

    /**
     * @var \DateTime
     */
    #[ORM\Column(name: 'created_at', type: 'datetime')]
    public $createdAt;

    /**
     * @var \DateTime
     */
    #[ORM\Column(name: 'updated_at', type: 'datetime', nullable: true)]
    public $updatedAt;
    
    /**
     * @var User
     */
    #[ORM\ManyToOne(targetEntity: User::class)]
    public $createdBy;
    
    /**
     * @var User
     */
    #[ORM\ManyToOne(targetEntity: User::class)]
    public $updatedBy;

    /**
     * Set createdAt
     *
     * @param \DateTime $createdAt
     *
     * @return AbstractLolaEntity
     */
    public function setCreatedAt(\DateTime $createdAt): self
    {
        $this->createdAt = $createdAt;

        return $this;
    }

    /**
     * Get createdAt
     *
     * @return \DateTime
     */
    public function getCreatedAt(): \DateTime
    {
        return $this->createdAt;
    }

    /**
     * Set updatedAt
     *
     * @param \DateTime $updatedAt
     *
     * @return AbstractLolaEntity
     */
    public function setUpdatedAt(\DateTime $updatedAt): self
    {
        $this->updatedAt = $updatedAt;

        return $this;
    }

    /**
     * Get updatedAt
     *
     * @return \DateTime
     */
    public function getUpdatedAt(): ?\DateTime
    {
        return $this->updatedAt;
    }
    
    /**
     * Set email of the authentified user who is creating the entity
     *
     * @param User $createdBy
     *
     * @return AbstractLolaEntity
     */
    public function setCreatedBy(?User $createdBy): self
    {
        $this->createdBy = $createdBy;

        return $this;
    }

    /**
     * Get email of the user who created the entity 
     *
     * @return User
     */
    public function getCreatedBy(): ?User
    {
        return $this->createdBy;
    }

    /**
     * Set email of the authentified user who is updating the entity
     *
     * @param User $updatedAt
     *
     * @return AbstractLolaEntity
     */
    public function setUpdatedBy(?User $updatedBy): self
    {
        $this->updatedBy = $updatedBy;

        return $this;
    }

    /**
     * Get email of the last user who updated the entity
     *
     * @param User $updatedBy
     *
     * @return User
     */
    public function getUpdatedBy(): ?User
    {
        return $this->updatedBy;
    }
}
