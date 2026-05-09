<?php

namespace App\EventListener;

use App\Entity\AbstractLolaEntity;
use Doctrine\Persistence\Event\LifecycleEventArgs;
use Symfony\Component\Security\Core\Security;
use App\Lolapy\LolapyServiceApi;
use App\Entity\Tag;

class TagCreationListener {

    /**
     * @var LolapyServiceApi
     */
    private $lolapyService;

    public function __construct(LolapyServiceApi $lolapyService)
    {
       $this->lolapyService = $lolapyService;
    }

    public function prePersist(Tag $tag, LifecycleEventArgs $event): void
    {
        // set the status to processing while Lolapy clone the repository and pull the docker image
        $tag->setStatus(Tag::STATUS_PROCESSING);

        // send data to Lolapy, the status will be returned through the frontend API
        $returnAddTag = $this->lolapyService->addScenarioTag($tag->getMetascenario()->getUrlRepository(), $tag->getName(), $tag->getHash());
    }

}
