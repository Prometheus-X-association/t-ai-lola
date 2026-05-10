<?php

namespace App\Controller\Dashboard;

use App\Repository\ApiLogRepository;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\Routing\Attribute\Route;
use Symfony\Component\Security\Http\Attribute\IsGranted;
use App\Controller\LolaController;

#[Route('/dashboard/apilog', name: 'dashboard_apilog_')]
#[IsGranted('ROLE_ADMIN_SISR')]
class ApiLogController extends LolaController {

    #[Route('/', name: 'index', methods: ['GET'])]
    public function index(ApiLogRepository $apiLogRepository): Response
    {
        return $this->render('dashboard/apilog/index.html.twig', [
                    'apilogs' => $apiLogRepository->findAll(),
        ]);
    }

}
