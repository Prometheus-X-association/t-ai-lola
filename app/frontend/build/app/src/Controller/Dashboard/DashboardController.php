<?php

namespace App\Controller\Dashboard;

use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\Mailer\Exception\TransportException;
use Symfony\Component\Routing\Attribute\Route;
use Symfony\Component\HttpFoundation\Request;
use App\Entity\User;
use App\Controller\LolaController;
use App\Email\EmailService;
use App\Lolapy\LolapyServiceApi;

#[Route('/dashboard', name: 'dashboard_')]
class DashboardController extends LolaController
{

    #[Route('/', name: 'accueil')]
    public function index(LolapyServiceApi $lolapyService): Response
    {
        // if user has only profil_1, redirect after authentification to the upgrade page
        if ($this->getUser()->hasRole(User::ROLE_PROFIL_1)) {
            return $this->render('dashboard/upgrade.html.twig');
        } else {
            if (!$lolapyService->isLolapyReady()) {
                return $this->render('dashboard/accueil.html.twig', [
                    'datasets' => $this->getDatasetRepository()->findBy($this->getUserFilter()),
                    'algorithms' => $this->getAlgorithmRepository()->findBy($this->getUserFilter()),
                    'metascenarios' => $this->getMetaScenarioRepository()->findBy($this->getUserFilter()),
                    'runs' => $this->getRunRepository()->findBy($this->getUserFilter()),
                ]);
            } else {
                $lolapyReturn = $lolapyService->addServerUsage();
                return $this->render('dashboard/accueil.html.twig', [
                    'datasets' => $this->getDatasetRepository()->findBy($this->getUserFilter()),
                    'algorithms' => $this->getAlgorithmRepository()->findBy($this->getUserFilter()),
                    'metascenarios' => $this->getMetaScenarioRepository()->findBy($this->getUserFilter()),
                    'runs' => $this->getRunRepository()->findBy($this->getUserFilter()),
                    'statistics' => $lolapyReturn
                ]);
            }
            
        }
    }

    #[Route('/upgrade', name: 'upgrade')]
    public function upgrade(): Response
    {
        return $this->render('dashboard/upgrade.html.twig');
    }

    #[Route('/user/upgrade/{profil}', name: 'user_upgrade')]
    public function userUpgrade(Request $request, EmailService $mailer): Response
    {
        $userProfil = strtoupper($request->get("profil"));
        if (User::isUserProfil($userProfil)) {
            $this->getUser()->setUpgradeRequest(strtoupper($userProfil));
            $this->getEm()->flush();
            $this->addFlash('success', 'Votre demande à bien été prise en compte.');

            try {
                $mailer->upgradeRequest($this->getUser());
            } catch (TransportException) {
                $this->addFlash('warning', "L'envoi de la notification par email à échoué.");
            }
        } else {
            $this->addFlash('error', 'Une erreur est survenue lors de la prise en compte de votre demande.');
        }
        return $this->render('dashboard/upgrade.html.twig');
    }
}
