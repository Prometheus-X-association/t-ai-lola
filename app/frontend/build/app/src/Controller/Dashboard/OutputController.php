<?php

namespace App\Controller\Dashboard;

use App\Entity\Output;
use App\Form\OutputType;
use App\Repository\OutputRepository;
use Symfony\Component\HttpFoundation\Request;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\Routing\Attribute\Route;
use Symfony\Component\Security\Http\Attribute\IsGranted;
use App\Controller\LolaController;

#[Route('/dashboard/output', name: 'dashboard_output_')]
#[IsGranted('ROLE_PROFIL_4')]
class OutputController extends LolaController {

    #[Route('/', name: 'index', methods: ['GET'])]
    public function index(OutputRepository $outputRepository): Response
    {
        return $this->render('dashboard/output/index.html.twig', [
                    'outputs' => $outputRepository->findAll(),
        ]);
    }

    #[Route('/new', name: 'new', methods: ['GET', 'POST'])]
    public function new(Request $request): Response
    {
        $output = new Output();
        $form = $this->createForm(OutputType::class, $output);
        $form->handleRequest($request);

        if ($form->isSubmitted() && $form->isValid()) {
            $this->getEm()->persist($output);
            $this->getEm()->flush();

            $this->addFlash("success", "L'indicateur a bien été ajouté");
            return $this->redirectToRoute('dashboard_output_index');
        }

        return $this->render('dashboard/output/new.html.twig', [
                    'output' => $output,
                    'form' => $form->createView(),
        ]);
    }

    #[Route('/{id}/edit', name: 'edit', methods: ['GET', 'POST'])]
    public function edit(Request $request, Output $output): Response
    {
        $form = $this->createForm(OutputType::class, $output);
        $form->handleRequest($request);

        if ($form->isSubmitted() && $form->isValid()) {
            $this->getEm()->flush();

            $this->addFlash("success", "L'indicateur a bien été modifié");
            return $this->redirectToRoute('dashboard_output_index');
        }

        return $this->render('dashboard/output/edit.html.twig', [
                    'output' => $output,
                    'form' => $form->createView(),
        ]);
    }

    #[Route('/{id}', name: 'delete', methods: ['DELETE'])]
    public function delete(Request $request, Output $output): Response
    {
        if ($this->isCsrfTokenValid('delete' . $output->getId(), $request->request->get('_token'))) {
            $this->getEm()->remove($output);
            $this->getEm()->flush();

            $this->addFlash("success", "L'indicateur a bien été supprimée");
        }

        return $this->redirectToRoute('dashboard_output_index');
    }

    #[Route('/toggle_visible/{id}', name: 'toggle_visible', requirements: ['id' => '\d+'])]
    public function toggleVisible(Output $output): Response
    {
        $output->toggleActive();
        $this->getEm()->flush();
        
        return $this->redirectToRoute("dashboard_output_index");
    }      

}
