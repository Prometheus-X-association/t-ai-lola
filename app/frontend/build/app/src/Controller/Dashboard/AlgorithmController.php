<?php

namespace App\Controller\Dashboard;

use App\Entity\Algorithm;
use App\Form\AlgorithmType;
use App\Repository\AlgorithmRepository;
use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Component\HttpFoundation\Request;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\Routing\Annotation\Route;
use Sensio\Bundle\FrameworkExtraBundle\Configuration\IsGranted;
use App\Controller\LolaController;
use App\Entity\AlgorithmVersion;

/**
 * @Route("/dashboard/algorithm", name="dashboard_algorithm_")
 * @IsGranted("ROLE_PROFIL_4")
 */
class AlgorithmController extends LolaController {

    /**
     * @Route("/", name="index", methods={"GET"})
     */
    public function index(AlgorithmRepository $algorithmRepository): Response {
        return $this->render('dashboard/algorithm/index.html.twig', [
                    'algorithms' => $algorithmRepository->findBy($this->getUserFilter()),
        ]);
    }

    /**
     * @Route("/new", name="new", methods={"GET","POST"})
     */
    public function new(Request $request): Response {
        $algorithm = new Algorithm();
        $form = $this->createForm(AlgorithmType::class, $algorithm);
        $form->handleRequest($request);

        if ($form->isSubmitted() && $form->isValid()) {
            $entityManager = $this->getDoctrine()->getManager();
            $entityManager->persist($algorithm);
            $entityManager->flush();

            $this->addFlash("success", "L'algorithme a bien été ajouté");
            return $this->redirectToRoute('dashboard_algorithm_index');
        }

        return $this->render('dashboard/algorithm/new.html.twig', [
                    'algorithm' => $algorithm,
                    'form' => $form->createView(),
        ]);
    }

    /**
     * @Route("/{id}/edit", name="edit", methods={"GET","POST"})
     */
    public function edit(Request $request, Algorithm $algorithm): Response {
        $form = $this->createForm(AlgorithmType::class, $algorithm);
        $form->handleRequest($request);

        if ($form->isSubmitted() && $form->isValid()) {
            $this->getDoctrine()->getManager()->flush();

            $this->addFlash("success", "L'algorithme a bien été modifié");
            return $this->redirectToRoute('dashboard_algorithm_index');
        }

        return $this->render('dashboard/algorithm/edit.html.twig', [
                    'algorithm' => $algorithm,
                    'form' => $form->createView(),
        ]);
    }

    /**
     * @Route("/{id}", name="delete", methods={"DELETE"})
     */
    public function delete(Request $request, Algorithm $algorithm): Response {
        if ($this->isCsrfTokenValid('delete' . $algorithm->getId(), $request->request->get('_token'))) {
            $entityManager = $this->getDoctrine()->getManager();
            $entityManager->remove($algorithm);
            $entityManager->flush();

            $this->addFlash("success", "L'algorithme a bien été supprimée");
        }

        return $this->redirectToRoute('dashboard_algorithm_index');
    }

    /**
     * @Route("/toggle_active/{id}", name="toggle_active",
     *      requirements = {
     *          "id" = "\d+",
     *      })
     */
    public function toggleActive(Algorithm $algorithm) {
        $algorithm->toggleActive();
        $this->getEm()->flush();

        return $this->redirectToRoute("dashboard_algorithm_index");
    }

    /**
     * @Route("/toggle_public/{id}", name="toggle_public",
     *      requirements = {
     *          "id" = "\d+",
     *      })
     */
    public function togglePublic(Algorithm $algorithm) {
        $algorithm->togglePublic();
        $this->getEm()->flush();

        return $this->redirectToRoute("dashboard_algorithm_index");
    }

    /**
     * @Route("/version/new", name="version_new", methods={"GET","POST"})
     * @IsGranted("ROLE_PROFIL_4")
     */
    public function versionNew(Request $request): Response {
        $data = $request->request->all();

        if ($data["version_name"] && !empty($data["version_name"])) {
            $algorithmVersion = new AlgorithmVersion();

            $algorithmVersion->setAlgorithm($this->getAlgorithmRepository()->find($data["algorithm_id"]));
            $algorithmVersion->setName($data["version_name"]);

            $this->getEm()->persist($algorithmVersion);
            $this->getEm()->flush();

            $this->addFlash("success", "La version de l'algorithm a bien été ajouté");
        } else {
            $this->addFlash("error", "La version de l'algorithm est requis");
        }
        return $this->redirectToRoute('dashboard_algorithm_index');
    }

    /**
     * Delete a version with status ERROR or PROCESSING
     * @Route("/version/delete/{hash}", name="version_delete", methods={"GET"})
     */
    public function versionDelete(AlgorithmVersion $version, \App\Lolapy\LolapyServiceApi $lolapyService): Response
    {
        if (!$lolapyService->isLolapyReady()) {
            return new \Symfony\Component\HttpFoundation\Response(json_encode(null));
        }

        // delete version on the backend
//        $lolapyService->removeAlgorithmVersion($version->getHash());

        // delete version on the frontend
        $this->getEm()->remove($version);
        $this->getEm()->flush();

        $this->addFlash("success", "La version a été supprimée");
        return $this->redirectToRoute("dashboard_algorithm_index");
    }
    

    /**
     * Make a request on Lolapy API to get the algorithm parameters
     * @Route("/ajax/parameters/{hash}", name="ajax_parameters", methods={"GET"})
     */
    public function ajaxParameters(string $hash, \App\Lolapy\LolapyServiceApi $lolapyService): Response
    {
        if (!$lolapyService->isLolapyReady()) {
            return new \Symfony\Component\HttpFoundation\Response(json_encode(null));
        }

        return new \Symfony\Component\HttpFoundation\Response($lolapyService->getAlgorithmParameters($hash));
    }    

}
