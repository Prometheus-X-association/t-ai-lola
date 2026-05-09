<?php

namespace App\Controller;

use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Bundle\FrameworkBundle\Controller\Controller;
use Symfony\Contracts\Translation\TranslatorInterface;
use Symfony\Component\HttpFoundation\Session\SessionInterface;
use Psr\Log\LoggerInterface;

class LolaController extends AbstractController {

    /**
     * @var Symfony\Contracts\Translation\TranslatorInterface 
     */
    private $translator;
    protected $logger;

    /**
     * @var SessionInterface $session
     */
    private $session;
    
    public function __construct(TranslatorInterface $translator, SessionInterface $session, LoggerInterface $logger) {
        $this->translator = $translator;
        $this->session = $session;
        $this->logger = $logger;
    }

    /**
     * @return \Doctrine\ORM\EntityManager
     */
    protected function getEm(): \Doctrine\ORM\EntityManager
    {
        return $this->getDoctrine()->getManager();
    }

    /**
     * @return SessionInterface
     */
    protected function getSession(): SessionInterface
    {
        return $this->session;
    }
    
    /**
     * @return TranslatorInterface
     */
    protected function getTranslator(): TranslatorInterface
    {
        return $this->translator;
    }

    /**
     * @return \App\Repository\UserRepository
     */
    protected function getUserRepository(): \App\Repository\UserRepository
    {
        return $this->getEm()->getRepository(\App\Entity\User::class);
    }

    /**
     * @return \App\Repository\GroupRepository
     */
    protected function getGroupRepository(): \App\Repository\GroupRepository
    {
        return $this->getEm()->getRepository(\App\Entity\Group::class);
    }

    /**
     * @return \App\Repository\DatasetRepository
     */
    protected function getDatasetRepository(): \App\Repository\DatasetRepository
    {
        return $this->getEm()->getRepository(\App\Entity\Dataset::class);
    }

    /**
     * @return \App\Repository\MetaScenarioRepository
     */
    protected function getMetaScenarioRepository(): \App\Repository\MetaScenarioRepository
    {
        return $this->getEm()->getRepository(\App\Entity\MetaScenario::class);
    }

    /**
     * @return \App\Repository\ScenarioRepository
     */
    protected function getScenarioRepository(): \App\Repository\ScenarioRepository
    {
        return $this->getEm()->getRepository(\App\Entity\Scenario::class);
    }

    /**
     * @return \App\Repository\TagRepository
     */
    protected function getTagRepository(): \App\Repository\TagRepository
    {
        return $this->getEm()->getRepository(\App\Entity\Tag::class);
    }

    /**
     * @return \App\Repository\RunRepository
     */
    protected function getRunRepository(): \App\Repository\RunRepository
    {
        return $this->getEm()->getRepository(\App\Entity\Run::class);
    }

    /**
     * @return \App\Repository\RunLogsRepository
     */
    protected function getRunLogsRepository(): \App\Repository\RunLogsRepository
    {
        return $this->getEm()->getRepository(\App\Entity\RunLogs::class);
    }

    /**
     * @return \App\Repository\TermsOfUseRepository
     */
    protected function getTermsOfUseRepository(): \App\Repository\TermsOfUseRepository
    {
        return $this->getEm()->getRepository(\App\Entity\TermsOfUse::class);
    }

    /**
     * @return \App\Repository\AlgorithmRepository
     */
    protected function getAlgorithmRepository(): \App\Repository\AlgorithmRepository
    {
        return $this->getEm()->getRepository(\App\Entity\Algorithm::class);
    }

    /**
     * @return \App\Repository\ScenarioAlgorithmRepository
    */
    protected function getScenarioAlgorithmRepository(): \App\Repository\ScenarioAlgorithmRepository
    {
        return $this->getEm()->getRepository(\App\Entity\ScenarioAlgorithm::class);
    }

    /**
     * @return \App\Repository\AlgorithmVersionRepository
     */
    protected function getAlgorithmVersionRepository(): \App\Repository\AlgorithmVersionRepository
    {
        return $this->getEm()->getRepository(\App\Entity\AlgorithmVersion::class);
    }

    /**
     * @return \App\Entity\User
     */
    protected function getUser(): \App\Entity\User
    {
        return parent::getUser();
    }

    /**
     * Return a basic filter for AbstractLolaEntity objects based on the createdBy field
     * There is no filter for admin user (admin and admin-sisr)
     * @return array
     */
    protected function getUserFilter(): array
    {
        return $this->getUser()->isAdmin() ? [] : ["createdBy" => $this->getUser()];
    }

}

