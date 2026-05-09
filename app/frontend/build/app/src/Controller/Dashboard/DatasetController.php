<?php

namespace App\Controller\Dashboard;

use App\Entity\Dataset;
use App\Entity\Group;
use App\Form\DatasetType;
use App\Repository\DatasetRepository;
use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Component\HttpFoundation\Request;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\HttpFoundation\ResponseHeaderBag;
use Symfony\Component\Routing\Annotation\Route;
use Sensio\Bundle\FrameworkExtraBundle\Configuration\IsGranted;
use App\Controller\LolaController;


/**
 * @Route("/dashboard/dataset", name="dashboard_dataset_")
 * @IsGranted("ROLE_PROFIL_2")
 */
class DatasetController extends LolaController {

    /**
     * Display users's datasets + shared datasets (by group or for everyone)
     * Admin can see every datasets
     * 
     * @Route("/", name="index", methods={"GET"})
     */
    public function index(): Response
    {
        return $this->render('dashboard/dataset/index.html.twig', [
                    'datasets' => $this->getUser()->getDatasets($this->getDatasetRepository()),
        ]);
    }

    /**
     * @Route("/new", name="new", methods={"GET","POST"})
     */
    public function new(Request $request): Response
    {
        $dataset = new Dataset();
        $form = $this->createForm(DatasetType::class, $dataset);
        $form->handleRequest($request);

        if ($form->isSubmitted() && $form->isValid()) {

            $entityManager = $this->getDoctrine()->getManager();
            $entityManager->persist($dataset);
            $entityManager->flush();

            $this->addFlash("success", $this->getTranslator()->trans('dashboard.dataset.controller.flash_dataset_ajoute'));
            return $this->redirectToRoute('dashboard_dataset_index');
        }

        return $this->render('dashboard/dataset/new.html.twig', [
                    'dataset' => $dataset,
                    'form' => $form->createView(),
        ]);
    }

    /**
     * @Route("/{id}/edit", name="edit", methods={"GET","POST"})
     */
    public function edit(Request $request, Dataset $dataset): Response
    {
        $form = $this->createForm(DatasetType::class, $dataset);
        $form->handleRequest($request);

        if ($form->isSubmitted() && $form->isValid()) {
            $this->getDoctrine()->getManager()->flush();

                        
            $this->addFlash("success", $this->getTranslator()->trans('dashboard.dataset.controller.flash_dataset_modifie'));
            return $this->redirectToRoute('dashboard_dataset_index');
        }

        return $this->render('dashboard/dataset/edit.html.twig', [
                    'dataset' => $dataset,
                    'form' => $form->createView(),
        ]);
    }

    /**
     * @Route("/{id}", name="delete", methods={"DELETE"})
     */
    public function delete(Request $request, Dataset $dataset, \App\Lolapy\LolapyServiceApi $lolapyService): Response
    {
        if (!$lolapyService->isLolapyReady()) {
            $this->addFlash("error", $this->getTranslator()->trans('dashboard.dataset.controller.flash_suppression_erreur'));
            return $this->redirectToRoute('dashboard_dataset_index');
        }

        if ($this->isCsrfTokenValid('delete' . $dataset->getId(), $request->request->get('_token'))) {

            // call Lolapy API to delete the dataset
            $lolapyReturn = $lolapyService->deleteDataset($dataset->getHash(), $dataset->getCreatedBy()->getHash());

            // update status to DELETING until Lolapy return the deleting confirmation on the frontend API
            $dataset->setStatus(Dataset::STATUS_DELETING);
            $this->getDoctrine()->getManager()->flush();

            $this->addFlash("success", $this->getTranslator()->trans('dashboard.dataset.controller.flash_suppression_confirmation') . $lolapyReturn);
        }

        return $this->redirectToRoute('dashboard_dataset_index');
    }

    /**
     * @Route("/toggle_share/{hash}", name="toggle_share", 
     *      requirements = {
     *          "id" = "\d+",
     *      })
     */
    public function toggleShare(Dataset $dataset)
    {
        $dataset->toggleShare();
        $this->getEm()->flush();

        return $this->redirectToRoute("dashboard_dataset_index");
    }

    /**
     * @Route("/group_share/add/{hash}/{group}", name="group_share_add", 
     *      requirements = {
     *          "id" = "\d+",
     *      })
     */
    public function groupShareAdd(Dataset $dataset, Group $group)
    {
        // check if current user is the owner of the dataset and is member of the group
        if( $this->getUser()->isAdmin() || ($dataset->createdBy->getId() === $this->getUser()->getId() && $group->hasUser($this->getUser()))) {
            $group->addDataset($dataset);
            $this->getEm()->flush();

//            $this->addFlash("success", "Le dataset " . $dataset->getName() . " a été partagé avec le groupe " . $group->getName());
            $this->addFlash("success", $this->getTranslator()->trans('dashboard.dataset.controller.flash_partage_ajout', [
                'dataset_name' => $dataset->getName(),
                'group_name' => $group->getName()
            ]));
        }
        else {
            $this->addFlash("danger", $this->getTranslator()->trans('dashboard.dataset.controller.flash_partage_erreur'));
        }
        return $this->redirectToRoute("dashboard_dataset_index");
    }

    /**
     * @Route("/group_share/delete/{hash}/{group}", name="group_share_delete", 
     *      requirements = {
     *          "id" = "\d+",
     *      })
     */
    public function groupShareDelete(Dataset $dataset, Group $group)
    {
        // check if current user is the owner of the dataset and is member of the group
        if( $this->getUser()->isAdmin() || ($dataset->createdBy->getId() === $this->getUser()->getId() && $group->hasUser($this->getUser()))) {
            $group->removeDataset($dataset);
            $this->getEm()->flush();

            $this->addFlash("success", $this->getTranslator()->trans('dashboard.dataset.controller.flash_partage_suppression', [
                'dataset_name' => $dataset->getName(),
                'group_name' => $group->getName()
            ]));
        }
        else {
            $this->addFlash("danger", $this->getTranslator()->trans('dashboard.dataset.controller.flash_partage_erreur'));
        }

        return $this->redirectToRoute("dashboard_dataset_index");
    }

    /**
     * Return the file to be sent with the dataset. 
     * It contains the sftp_hash string to identify the user and the dataset id.
     * 
     * @Route("/download/{hash}", name="download")
     */
    public function download(Dataset $dataset)
    {
        $filename = "dataset_" . preg_replace('/[^a-z0-9]+/', '-', strtolower($dataset->getName()));
        $response = new Response(json_encode(["dataset" => $dataset->getHash(), "user" => $this->getUser()->getHash()]));
        $disposition = $response->headers->makeDisposition(
                ResponseHeaderBag::DISPOSITION_ATTACHMENT,
                $filename . ".json"
        );
        $response->headers->set('Content-Disposition', $disposition);
        return $response;
    }

    /**
     * Make a request on Lolapy API to get dataset stats
     * @Route("/ajax/show/{hash}", name="ajax_show", methods={"GET"})
     */
    public function ajaxShow(Request $request, Dataset $dataset, \App\Lolapy\LolapyServiceApi $lolapyService): Response
    {
        if (!$lolapyService->isLolapyReady()) {
            return new \Symfony\Component\HttpFoundation\Response(json_encode(null));
        }

        return new \Symfony\Component\HttpFoundation\Response($lolapyService->getDatasetData($dataset->getHash(), $dataset->getCreatedBy()->getHash()));
    }

}
