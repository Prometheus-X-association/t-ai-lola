<?php

namespace App\Controller\Dashboard;

use App\Repository\RunRepository;
use App\Repository\DatasetRepository;
use App\Repository\ScenarioRepository;
use App\Repository\UserRepository;
use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Component\HttpFoundation\Request;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\Routing\Annotation\Route;
use Doctrine\ORM\EntityManagerInterface;
use Sensio\Bundle\FrameworkExtraBundle\Configuration\IsGranted;
use App\Controller\LolaController;

/**
* @Route("/dashboard/hash", name="dashboard_hash_")
* @IsGranted("ROLE_ADMIN")
*/
class HashObjetController extends LolaController {

    /**
     * @Route("/", name="index", methods={"GET"})
     */
    public function index(): Response
    {
        return $this->render('dashboard/hash_objet/index.html.twig', [
                    'runs' => $this->getRunRepository()->findAll(),
                    'scenarios' => $this->getScenarioRepository()->findAll(),
                    'datasets' => $this->getDatasetRepository()->findAll(),
                    'users' => $this->getUserRepository()->findAll(),
                    'tags' => $this->getTagRepository()->findAll(),
                    'algorithmsVersion' => $this->getAlgorithmVersionRepository()->findAll()
                ]);
    }

    
}
