<?php

namespace App\Controller\Dashboard;

use App\Entity\TermsOfUse;
use App\Form\TermsOfUseType;
use App\Repository\TermsOfUseRepository;
use Symfony\Component\HttpFoundation\Request;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\Routing\Attribute\Route;
use Symfony\Component\Security\Http\Attribute\IsGranted;
use App\Controller\LolaController;

#[Route('/dashboard/termsofuse', name: 'dashboard_termsofuse_')]
#[IsGranted('ROLE_ADMIN')]
class TermsOfUseController extends LolaController {

    #[Route('/', name: 'index', methods: ['GET'])]
    public function index(TermsOfUseRepository $termsOfUseRepository): Response
    {
        return $this->render('dashboard/termsofuse/index.html.twig', [
                    'termsOfUses' => $termsOfUseRepository->findAll(),
        ]);
    }

    #[Route('/new', name: 'new', methods: ['GET', 'POST'])]
    public function new(Request $request): Response
    {
        $termsOfUse = new TermsOfUse();
        $form = $this->createForm(TermsOfUseType::class, $termsOfUse);
        $form->handleRequest($request);

        if ($form->isSubmitted() && $form->isValid()) {
            $this->getEm()->persist($termsOfUse);
            $this->getEm()->flush();

            $this->addFlash("success", "La nouvelle charte a bien été ajoutée");
            return $this->redirectToRoute('dashboard_termsofuse_index');
        }

        return $this->render('dashboard/termsofuse/new.html.twig', [
                    'termsOfUse' => $termsOfUse,
                    'form' => $form->createView(),
        ]);
    }

    #[Route('/{id}/edit', name: 'edit', methods: ['GET', 'POST'])]
    public function edit(Request $request, TermsOfUse $termsOfUse): Response
    {
        $form = $this->createForm(TermsOfUseType::class, $termsOfUse);
        $form->handleRequest($request);

        if ($form->isSubmitted() && $form->isValid()) {
            $this->getEm()->flush();

            $this->addFlash("success", "La charte a bien été modifiée");
            return $this->redirectToRoute('dashboard_termsofuse_index');
        }

        return $this->render('dashboard/termsofuse/edit.html.twig', [
                    'termsOfUse' => $termsOfUse,
                    'form' => $form->createView(),
        ]);
    }

    #[Route('/{id}', name: 'delete', methods: ['DELETE'])]
    public function delete(Request $request, TermsOfUse $termsOfUse): Response
    {
        if ($this->isCsrfTokenValid('delete' . $termsOfUse->getId(), $request->request->get('_token'))) {
            $this->getEm()->remove($termsOfUse);
            $this->getEm()->flush();

            $this->addFlash("success", "La charte a bien été supprimée");
        }

        return $this->redirectToRoute('dashboard_termsofuse_index');
    }

    #[Route('/active/{id}', name: 'active', requirements: ['id' => '\d+'])]
    public function active(TermsOfUse $termsOfUse): Response
    {
        // set inactive all termsOfUse
        $this->getTermsOfUseRepository()->updateAllInactive();
        
        // set active the selected termsOfUse
        $termsOfUse->setActive();
        $this->getEm()->flush();
        
        // Reset for all users the agreement of the terms of use
        // Users must agree to the new terms of use before access to dashboard
        $this->getUserRepository()->updateTermsOfUseReset();

        $this->addFlash("success", "La nouvelle charte à bien été prise en compte");
        return $this->redirectToRoute("dashboard_termsofuse_index");
    }

}
