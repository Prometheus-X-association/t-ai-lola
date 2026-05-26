<?php

namespace App\EventListener;

use App\Entity\AbstractLolaEntity;
use Doctrine\Persistence\Event\LifecycleEventArgs;
use Symfony\Component\Security\Core\Security;
use App\Lolapy\LolapyServiceApi;
use App\Entity\AlgorithmVersion;

class AlgorithmVersionCreationListener {

    /**
     * @var LolapyServiceApi
     */
    private $lolapyService;

    public function __construct(LolapyServiceApi $lolapyService) {
        $this->lolapyService = $lolapyService;
    }

    public function prePersist(AlgorithmVersion $algorithmVersion, LifecycleEventArgs $event): void {
        error_log('### AlgorithmVersionCreationListener CALLED ###');
        // set the status to processing while Lolapy clone the repository and pull the docker image
        $algorithmVersion->setStatus(AlgorithmVersion::STATUS_PROCESSING);

        // send data to Lolapy, the status will be returned through the frontend API
        $returnAddAlgorithmVersion = $this->lolapyService->addAlgorithmVersion(
                $algorithmVersion->getAlgorithm()->getUrlRepository(),
                $algorithmVersion->getName(),
                $algorithmVersion->getHash());
        
        
        error_log('### addAlgorithmVersion return: ' . print_r($returnAddAlgorithmVersion, true));

    }

}
