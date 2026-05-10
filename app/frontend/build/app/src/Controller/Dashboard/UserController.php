<?php

namespace App\Controller\Dashboard;

use App\Controller\LolaController;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\Mailer\Exception\TransportException;
use Symfony\Component\Routing\Attribute\Route;
use Symfony\Component\Security\Http\Attribute\IsGranted;
use Symfony\Component\HttpFoundation\Request;
use App\Form\UserType;
use App\Entity\User;
use App\Email\EmailService;

#[Route('/dashboard/user', name: 'dashboard_user_')]
#[IsGranted('ROLE_ADMIN')]
class UserController extends LolaController {

    #[Route('/', name: 'index')]
    public function index(): Response
    {
        return $this->render('dashboard/user/index.html.twig', [
                    "listUsers" => $this->getUserRepository()->findAll()
        ]);
    }

    #[Route('/edit/{id}', name: 'edit', methods: ['GET', 'POST'])]
    public function edit(Request $request, User $user): Response
    {
        $form = $this->createForm(UserType::class, $user);
        $form->handleRequest($request);

        if ($form->isSubmitted() && $form->isValid()) {
            $this->getEm()->flush();

            $this->addFlash("success", "L'utilisateur a bien été modifié");
            return $this->redirectToRoute('dashboard_user_index');
        }

        return $this->render('dashboard/user/edit.html.twig', [
                    'user' => $user,
                    'form' => $form->createView(),
        ]);
    }

    #[Route('/upgrade/validation/{user}', name: 'upgrade_validation')]
    public function upgradeValidation(User $user, EmailService $mailer): Response
    {
        if (User::isUserProfil($user->getUpgradeRequest())) {
            $user->removeRole($user->getProfil(false));
            $user->addRole($user->getUpgradeRequest());
            $user->setUpgradeRequest(null);
            $this->getEm()->flush();
            $this->addFlash('success', 'La mise à jour du compte à bien été effectuée. L\'utilisateur a été notifié par email.');

            try {
                $mailer->upgradeAccepted($user);
            } catch (TransportException) {
                $this->addFlash('warning', "L'envoi de la notification par email a échoué.");
            }
        } else {
            $this->addFlash('error', 'Une erreur est survenue lors de la mise à jour du compte.');
        }
        return $this->redirectToRoute('dashboard_user_index');
    }

    #[Route('/upgrade/deny/{user}', name: 'upgrade_deny')]
    public function upgradeDeny(User $user, EmailService $mailer): Response
    {
        if (User::isUserProfil($user->getUpgradeRequest())) {
            $user->setUpgradeRequest(null);
            $this->getEm()->flush();
            $this->addFlash('success', 'La demande de mise à niveau à bien été refusée. L\'utilisateur a été notifié par email.');

            try {
                $mailer->upgradeDenied($user);
            } catch (TransportException) {
                $this->addFlash('warning', "L'envoi de la notification par email a échoué.");
            }

        } else {
            $this->addFlash('error', 'Une erreur est survenue lors de la mise à jour du compte.');
        }
        return $this->redirectToRoute('dashboard_user_index');
    }

    #[Route('/enable/{id}', name: 'enable', requirements: ['id' => '\d+'])]
    public function enable(User $user): Response
    {
        $user->setActive(true);
        $this->getEm()->flush();

        return $this->redirectToRoute("dashboard_user_index");
    }

    #[Route('/disable/{id}', name: 'disable', requirements: ['id' => '\d+'])]
    public function disable(User $user): Response
    {
        $user->setActive(false);
        $this->getEm()->flush();

        return $this->redirectToRoute("dashboard_user_index");
    }

    #[Route('/toggle_admin/{id}', name: 'toggle_admin', requirements: ['id' => '\d+'])]
    public function toggleAdmin(User $user): Response
    {
        $user->toggleAdmin();
        $this->getEm()->flush();

        return $this->redirectToRoute("dashboard_user_index");
    }

    #[Route('/toggle_admin_sisr/{id}', name: 'toggle_admin_sisr', requirements: ['id' => '\d+'])]
    public function toggleAdminSisr(User $user): Response
    {
        $user->toggleAdminSisr();
        $this->getEm()->flush();

        return $this->redirectToRoute("dashboard_user_index");
    }

}
