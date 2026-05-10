<?php

namespace App\EventListener;

use App\Entity\AbstractLolaEntity;
use Doctrine\Persistence\Event\LifecycleEventArgs;
use Symfony\Bundle\SecurityBundle\Security;

class LolaEntityListener {

    /**
     * @var Security
     */
    private $security;

    public function __construct(Security $security)
    {
       $this->security = $security;
    }    
    
    public function preUpdate(AbstractLolaEntity $lolaEntity, LifecycleEventArgs $event): void
    {
        $lolaEntity->setUpdatedAt(new \DateTime());
        $lolaEntity->setUpdatedBy($this->security->getUser());
    }

    public function prePersist(AbstractLolaEntity $lolaEntity, LifecycleEventArgs $event): void
    {
        $lolaEntity->setCreatedAt(new \DateTime());
        $lolaEntity->setCreatedBy($this->security->getUser());
    }

}
