<?php

namespace App\Controller\Dashboard;

use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\Routing\Attribute\Route;
use Symfony\Component\Security\Http\Attribute\IsGranted;
use App\Controller\LolaController;

#[Route('/dashboard/hash', name: 'dashboard_hash_')]
#[IsGranted('ROLE_ADMIN')]
class HashObjetController extends LolaController {

    #[Route('/', name: 'index', methods: ['GET'])]
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
