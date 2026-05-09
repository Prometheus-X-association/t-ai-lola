<?php

namespace App\Controller\Dashboard;

use App\Entity\Group;
use App\Form\GroupType;
use App\Repository\GroupRepository;
use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Component\HttpFoundation\Request;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\Routing\Annotation\Route;
use Sensio\Bundle\FrameworkExtraBundle\Configuration\IsGranted;
use App\Controller\LolaController;

/**
 * @Route("/dashboard/group", name="dashboard_group_")
 * @IsGranted("ROLE_ADMIN")
 */
class GroupController extends LolaController {

    /**
     * @Route("/", name="index", methods={"GET"})
     */
    public function index(GroupRepository $groupRepository): Response
    {
        return $this->render('dashboard/group/index.html.twig', [
                    'groups' => $groupRepository->findAll(),
        ]);
    }

    /**
     * @Route("/new", name="new", methods={"GET","POST"})
     */
    public function new(Request $request): Response
    {
        $group = new Group();
        $form = $this->createForm(GroupType::class, $group);
        $form->handleRequest($request);

        if ($form->isSubmitted() && $form->isValid()) {
            $entityManager = $this->getDoctrine()->getManager();
            $entityManager->persist($group);
            $entityManager->flush();

            $this->addFlash("success", "Le groupe a bien été ajouté");
            return $this->redirectToRoute('dashboard_group_index');
        }

        return $this->render('dashboard/group/new.html.twig', [
                    'group' => $group,
                    'form' => $form->createView(),
        ]);
    }

    /**
     * @Route("/{id}/edit", name="edit", methods={"GET","POST"})
     */
    public function edit(Request $request, Group $group): Response
    {
        $form = $this->createForm(GroupType::class, $group);
        $form->handleRequest($request);

        if ($form->isSubmitted() && $form->isValid()) {
            $this->getDoctrine()->getManager()->flush();

            $this->addFlash("success", "Le groupe a bien été modifié");
            return $this->redirectToRoute('dashboard_group_index');
        }

        return $this->render('dashboard/group/edit.html.twig', [
                    'group' => $group,
                    'form' => $form->createView(),
        ]);
    }

    /**
     * @Route("/{id}", name="delete", methods={"DELETE"})
     */
    public function delete(Request $request, Group $group): Response
    {
        if ($this->isCsrfTokenValid('delete' . $group->getId(), $request->request->get('_token'))) {
            $entityManager = $this->getDoctrine()->getManager();
            $entityManager->remove($group);
            $entityManager->flush();

            $this->addFlash("success", "Le groupe a bien été supprimé");
        }

        return $this->redirectToRoute('dashboard_group_index');
    }

}
