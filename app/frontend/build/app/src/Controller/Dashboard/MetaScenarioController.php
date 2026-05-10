<?php

namespace App\Controller\Dashboard;

use App\Entity\AlgorithmVersion;
use App\Entity\MetaScenario;
use App\Entity\Tag;
use App\Form\MetaScenarioType;
use App\Repository\MetaScenarioRepository;
use Symfony\Component\HttpFoundation\Request;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\Routing\Attribute\Route;
use Symfony\Component\Security\Http\Attribute\IsGranted;
use App\Controller\LolaController;
use App\Lolapy\LolapyServiceApi;

#[Route('/dashboard/metascenario', name: 'dashboard_metascenario_')]
#[IsGranted('ROLE_PROFIL_2')]
class MetaScenarioController extends LolaController {

    #[Route('/', name: 'index', methods: ['GET'])]
    public function index(MetaScenarioRepository $metaScenarioRepository): Response
    {
        $userMetaScenario = $metaScenarioRepository->findBy($this->getUserFilter());
        $sharedMetaScenario = $metaScenarioRepository->findBy(["isPublic" => true]);
        $known = [];
        $metaScenarios = array_filter(array_merge($userMetaScenario, $sharedMetaScenario), function ($val) use (&$known) {
            $unique = !in_array($val->getId(), $known);
            $known[] = $val->getId();
            return $unique;
        });

        return $this->render('dashboard/metascenario/index.html.twig', [
                    'metaScenarios' => $metaScenarios,
                    'userDatasets' => $this->getUser()->getDatasets($this->getDatasetRepository())
        ]);
    }

    #[Route('/new', name: 'new', methods: ['GET', 'POST'])]
    #[IsGranted('ROLE_PROFIL_4')]
    public function new(Request $request): Response
    {
        $metaScenario = new MetaScenario();
        $form = $this->createForm(MetaScenarioType::class, $metaScenario);
        $form->handleRequest($request);

        if ($form->isSubmitted() && $form->isValid()) {
            $this->getEm()->persist($metaScenario);
            $this->getEm()->flush();

            $this->addFlash("success", "Le méta-scénario a bien été ajouté");
            return $this->redirectToRoute('dashboard_metascenario_index');
        }

        return $this->render('dashboard/metascenario/new.html.twig', [
                    'metaScenario' => $metaScenario,
                    'form' => $form->createView(),
        ]);
    }

    #[Route('/tag/new', name: 'tag_new', methods: ['GET', 'POST'])]
    #[IsGranted('ROLE_PROFIL_4')]
    public function tagNew(Request $request): Response
    {
        $data = $request->request->all();

        if (!empty($data["tag_name"])) {
            $tag = new Tag();

            // TODO : controle que l'utilisateur à des droits sur le metascenario
            $metaScenario = $this->getMetaScenarioRepository()->find($data["meta_scenario_id"]);
            $tag->setMetascenario($metaScenario);
            $tag->setName($data["tag_name"]);
            $tag->setVersion($data["tag_version"]);
//            $tag->setVariant($data["tag_variant"]);
            $tag->setVariant("");

            $this->getEm()->persist($tag);
            $this->getEm()->flush();

            $this->addFlash("success", "Le tag a bien été ajouté");
        } else {
            $this->addFlash("error", "Le nom du tag est requis");
        }
        return $this->redirectToRoute('dashboard_metascenario_index');
    }

    #[Route('/{id}/edit', name: 'edit', methods: ['GET', 'POST'])]
    #[IsGranted('ROLE_PROFIL_4')]
    public function edit(Request $request, MetaScenario $metaScenario): Response
    {
        $form = $this->createForm(MetaScenarioType::class, $metaScenario);
        $form->handleRequest($request);

        if ($form->isSubmitted() && $form->isValid()) {
            $this->getEm()->flush();

            $this->addFlash("success", "Le méta-scénario a bien été modifié");
            return $this->redirectToRoute('dashboard_metascenario_index');
        }

        return $this->render('dashboard/metascenario/edit.html.twig', [
                    'metaScenario' => $metaScenario,
                    'form' => $form->createView(),
        ]);
    }

    #[Route('/toggle_public/{id}', name: 'toggle_public', requirements: ['id' => '\d+'])]
    #[IsGranted('ROLE_PROFIL_4')]
    public function togglePublic(MetaScenario $metaScenario): Response
    {
        $metaScenario->togglePublic();
        $this->getEm()->flush();

        return $this->redirectToRoute("dashboard_metascenario_index");
    }

    #[Route('/toggle_active/{id}', name: 'toggle_active', requirements: ['id' => '\d+'])]
    #[IsGranted('ROLE_PROFIL_4')]
    public function toggleActive(MetaScenario $metaScenario): Response
    {
        $metaScenario->toggleActive();
        $this->getEm()->flush();

        return $this->redirectToRoute("dashboard_metascenario_index");
    }

    /**
     * Make a request on Lolapy API to get the metascenario parameters
     */
    #[Route('/ajax/parameters/{hash}', name: 'ajax_parameters', methods: ['GET'])]
    public function ajaxParameters(Request $request, Tag $tag, LolapyServiceApi $lolapyService): Response
    {
        if (!$lolapyService->isLolapyReady()) {
            return new Response(json_encode(null));
        }

        return new Response($lolapyService->getScenarioParameters($tag->getHash()));
    }

    /**
     * Delete a tag with status ERROR or PROCESSING
     */
    #[Route('/tag/delete/{hash}', name: 'tag_delete', methods: ['GET'])]
    public function tagDelete(Tag $tag, LolapyServiceApi $lolapyService): Response
    {
        if (!$lolapyService->isLolapyReady()) {
            return new Response(json_encode(null));
        }

        // delete tag on the backend
        $lolapyService->removeScenarioTag($tag->getHash());

        // delete tag on the frontend
        $this->getEm()->remove($tag);
        $this->getEm()->flush();

        $this->addFlash("success", "Le tag a été supprimé");
        return $this->redirectToRoute("dashboard_metascenario_index");
    }

    /**
     * Prepare the execution of the scenario
     */
    #[Route('/prepare/{id}', name: 'prepare', methods: ['GET'])]
    public function prepare(MetaScenario $metaScenario): Response
    {
        $this->getSession()?->set("create_scenario", ["metascenario" => $metaScenario]);
        return $this->render('dashboard/metascenario/prepare.html.twig', [
                    'metaScenario' => $metaScenario,
                    'tags' => $metaScenario->getTags(),
                    'datasets' => $this->getUser()->getDatasets($this->getDatasetRepository())
        ]);
    }

    /**
     * Prepare the execution of the scenario - scenario parameters
     */
    #[Route('/prepare/parameter', name: 'prepare_parameter', methods: ['POST'])]
    public function prepareParameter(Request $request): Response
    {
        $data = $request->request->all();
        $tag = $this->getTagRepository()->findOneBy(["hash" => $data["hidden_tag_hash"]]);
        $dataset = $this->getDatasetRepository()->findOneBy(["hash" => $data["hidden_dataset_hash"]]);

        // check if the tag and dataset exist and if user has permission to view the dataset
        if (!$tag || !$dataset || !$this->getUser()->hasPermission($dataset, $this->getDatasetRepository())) {
            $this->addFlash("danger", "Une erreur est survenue lors de la préparation du scénario");
            $this->redirectToRoute("dashboard_metascenario_index");
        }

        $dataSession = $this->getSession()?->get('create_scenario', []);
        $dataSession["tag"] = $tag;
        $dataSession["dataset"] = $dataset;
        $this->getSession()?->set('create_scenario', $dataSession);

        return $this->render('dashboard/metascenario/prepare_parameter.html.twig', [
                    'tag' => $dataSession["tag"],
                    'dataset' => $dataSession["dataset"],
                    'metascenario' => $dataSession["metascenario"]
        ]);
    }

    /**
     * Prepare the execution of the scenario - switchable algorithm
     */
    #[Route('/prepare/algorithm', name: 'prepare_algorithm', methods: ['POST'])]
    public function prepareAlgorithm(Request $request): Response
    {
        $parameters = $request->request->all();
        $dataSession = $this->getSession()?->get('create_scenario', []);
        $dataSession["parameters"] = serialize($parameters);
        $this->getSession()?->set('create_scenario', $dataSession);
        
        return $this->render('dashboard/metascenario/prepare_algorithm.html.twig', [
                    'tag' => $dataSession["tag"],
                    'dataset' => $dataSession["dataset"],
                    'metascenario' => $dataSession["metascenario"],
                    'algorithmVersions' => $this->getAlgorithmVersionRepository()->findBy(["status" => AlgorithmVersion::STATUS_AVAILABLE])
        ]);        
    }

}
