<?php

namespace App\Controller\Dashboard;

use App\Repository\ScenarioRepository;
use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Component\HttpFoundation\Request;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\Routing\Annotation\Route;
use Doctrine\ORM\EntityManagerInterface;
use Sensio\Bundle\FrameworkExtraBundle\Configuration\IsGranted;
use App\Controller\LolaController;
use App\Entity\Scenario;
use App\Entity\ScenarioAlgorithm;
use App\Entity\Run;
use App\Entity\AlgorithmVersion;
use Psr\Log\LoggerInterface;

/**
 * @Route("/dashboard/scenario", name="dashboard_scenario_")
 * @IsGranted("ROLE_PROFIL_2")
 */
class ScenarioController extends LolaController {

    /**
     * @Route("/", name="index", methods={"GET"})
     */
    public function index(): Response
    {
        return $this->render('dashboard/scenario/index.html.twig', [
                    'scenarios' => $this->getScenarioRepository()->findBy($this->getUserFilter())
        ]);
    }

    /**
     * @Route("/toggle_active/{id}", name="toggle_active",
     *      requirements = {
     *          "id" = "\d+",
     *      })
     * @IsGranted("ROLE_PROFIL_4")
     */
    public function toggleActive(Scenario $scenario)
    {
        $scenario->toggleActive();
        $this->getEm()->flush();

        return $this->redirectToRoute("dashboard_scenario_index");
    }

    /**
     * Execute the scenario
     * @Route("/execute/{id}", name="execute", methods={"POST"})
     */
    public function execute(Request $request, Scenario $scenario, \App\Lolapy\LolapyServiceApi $lolapyService): Response
    {
	error_log('DEBUG: ScenarioController::execute called with scenario ID: ' . $scenario->getId());
        if ($this->isCsrfTokenValid('execute' . $scenario->getId(), $request->request->get('_token'))) {
            $run = new Run();
            $run->setScenario($scenario);
            $this->getEm()->persist($run);
            $this->getEm()->flush();

            // lance l'execution du scénar$io sur Lolapy
            $resultExecute = $lolapyService->scenarioExecute($scenario, $run->getHash());

            return $this->redirectToRoute("dashboard_run_details", ['hash' => $run->getHash()]);
        }
        return $this->redirectToRoute("dashboard_accueil");
    }

    /**
     * Edit the scenario - step 1 (tag and dataset)
     * @Route("/prepare/{id}", name="edit_prepare", methods={"GET"})
     */
    public function prepare(Scenario $scenario)
    {
        $this->getSession()->set("edit_scenario", ["metascenario" => $scenario->getMetascenario()]);
        return $this->render('dashboard/scenario/edit_prepare.html.twig', [
                    'metaScenario' => $scenario->getMetascenario(),
                    'tags' => $scenario->getMetascenario()->getTags(),
                    'datasets' => $this->getUser()->getDatasets($this->getDatasetRepository()),
                    'tagHash' => $scenario->getTag()->getHash(),
                    'datasetHash' => $scenario->getDataset()->getHash(),
                    'scenario' => $scenario
        ]);
    }

    /**
     * Edit the scenario - step 2 (parameters)
     * @Route("/prepare/parameter", name="edit_prepare_parameter", methods={"POST"})
     */
    public function prepareParameter(Request $request)
    {
        $data = $request->request->all();
        $tag = $this->getTagRepository()->findOneBy(["hash" => $data["hidden_tag_hash"]]);
        $dataset = $this->getDatasetRepository()->findOneBy(["hash" => $data["hidden_dataset_hash"]]);
        $scenario = $this->getScenarioRepository()->find($data["hidden_scenario_id"]);

        // check if the tag and dataset exist and if user has permission to view the dataset
        if (!$tag || !$dataset || !$this->getUser()->hasPermission($dataset, $this->getDatasetRepository())) {
            $this->addFlash("danger", "Une erreur est survenue lors de la préparation du scénario");
            $this->redirectToRoute("dashboard_metascenario_index");
        }

        $dataSession = $this->getSession()->get("edit_scenario");
        $dataSession["tag"] = $tag;
        $dataSession["dataset"] = $dataset;
        $dataSession["scenario"] = $scenario;
        $this->getSession()->set("edit_scenario", $dataSession);

        return $this->render('dashboard/scenario/edit_prepare_parameter.html.twig', [
                    'metascenario' => $dataSession["metascenario"],
                    'tag' => $dataSession["tag"],
                    'dataset' => $dataSession["dataset"],
                    'scenario' => $scenario,
                ]);
               
    }

    /**
     * Prepare the execution of the scenario - switchable algorithm
     * @Route("/prepare/algorithm", name="edit_prepare_algorithm", methods={"POST"})
    */
    public function prepareAlgorithm(Request $request)
    {
        $parameters = $request->request->all();
        $dataSession = $this->getSession()->get("edit_scenario");
        $dataSession["parameters"] = serialize($parameters);
        $this->getSession()->set("edit_scenario", $dataSession);
        $scenario = $this->getScenarioRepository()->find($dataSession["scenario"]->getId());
        $scenarioAlgorithms = $this->getScenarioAlgorithmRepository()->findBy(['scenario' => $scenario->getId()]);
        $algorithmVersions = $this->getAlgorithmVersionRepository()->findBy(["status" => \App\Entity\AlgorithmVersion::STATUS_AVAILABLE]); 
        $tableauAlgosScenario = [];
        // Insertion des algos interchangeables dans un tableau
        foreach ($scenarioAlgorithms as $algorithm) {
            $tableauAlgosScenario[] = [
                "hash" => $algorithm->getAlgorithmVersion()->getHash(), 
                "nameAlgo" => $algorithm->getAlgorithmVersion()->getAlgorithm()->getName(),
                "nameAlgoVersion" => $algorithm->getAlgorithmVersion()->getName(), 
                "nfVariable" => $algorithm->getNfVariable(),
                "parameters" => $algorithm->getParametres()
            ];
        }
        $tableauVersionAlgos = [];
        // Insertion des versions des algos interchangeables dans un tableau 
        foreach ($algorithmVersions as $version) {
            $tableauVersionAlgos[] = [
                "hash" => $version->getHash(), 
                "nameAlgo" => $version->getAlgorithm()->getName(), 
                "nameAlgoVersion" => $version->getName()
            ];
        }

        return $this->render('dashboard/scenario/edit_prepare_algorithm.html.twig', [
                    'tag' => $dataSession["tag"],
                    'dataset' => $dataSession["dataset"],
                    'metascenario' => $dataSession["metascenario"],
                    'scenario' => $scenario,
                    'tableauAlgosScenario' => $tableauAlgosScenario,
                    'tableauVersionAlgos' => $tableauVersionAlgos
        ]);        
    }

    /**
     * Update the scenario
     * @param string $datasetHash
     * @param string $tagHash
     * @param type $data
     * @param Scenario $scenario
     */
    private function update(string $datasetHash, string $tagHash, $data, Scenario $scenario)
    {
        $scenario->setDataset($this->getDatasetRepository()->findOneBy(["hash" => $datasetHash]));
        $scenario->setTag($this->getTagRepository()->findOneBy(["hash" => $tagHash]));
        $scenario->setParametres($data);

        $this->getEm()->persist($scenario);
        $this->getEm()->flush();

        $this->addFlash("success", "Le scénario a bien été modifié");
    }

    /**
     * Create a new scenario
     * @param string $datasetHash
     * @param string $tagHash
     * @param type $data
     * @param string $metascenarioId
     */
    private function create(string $datasetHash, string $tagHash, $data, string $metascenarioId): Scenario
    {
        $scenario = new Scenario();
        $scenario->setDataset($this->getDatasetRepository()->findOneBy(["hash" => $datasetHash]));
        $scenario->setTag($this->getTagRepository()->findOneBy(["hash" => $tagHash]));
        $scenario->setMetascenario($this->getMetaScenarioRepository()->find($metascenarioId));
        $scenario->setParametres($data);

        $this->getEm()->persist($scenario);
        $this->getEm()->flush();

        $this->addFlash("success", "Le scénario a bien été créé");

        return $scenario;
    }

    /**
     * dispatch to creation or updating method
     * @Route("/scenario/manage", name="scenario_manage", methods={"POST"})
     */
    public function manage(Request $request,): Response
    {
         $this->logger->info('ScenarioController::manage called');
        
        $data = $request->request->all();
         $this->logger->debug('Request data received', ['data_keys' => array_keys($data)]);
        
        if (isset($data["create_button_no_algo"])) { 
             $this->logger->info('Creating scenario without algorithms');
            unset($data["create_button_no_algo"]);
            $dataSession = $this->getSession()->get("create_scenario"); 
            $dataSession["parameters"] = serialize($data);
            $this->getSession()->set("create_scenario", $dataSession);
            
             $this->logger->debug('Session data prepared', [
                'dataset_hash' => $dataSession["dataset"]->getHash(),
                'tag_hash' => $dataSession["tag"]->getHash(),
                'metascenario_id' => $dataSession["metascenario"]->getId()
            ]);
            
            // create the scenario object
            $scenario = $this->create(
                    $dataSession["dataset"]->getHash(),
                    $dataSession["tag"]->getHash(),
                    unserialize($dataSession["parameters"]),
                    $dataSession["metascenario"]->getId()
            );
            
             $this->logger->info('Scenario created without algorithms', ['scenario_id' => $scenario->getId()]);

        } elseif (isset($data["create_button_with_algo_after_edit"])) { 
             $this->logger->info('Creating scenario with algorithms after edit');
            
            $dataScenario = $this->getSession()->get("edit_scenario");
            unset($data["create_button_with_algo_after_edit"]);
                    
            // create the scenario object
            $scenario = $this->create(
                    $dataScenario["dataset"]->getHash(),
                    $dataScenario["tag"]->getHash(),
                    unserialize($dataScenario["parameters"]),
                    $dataScenario["metascenario"]->getId()
            );
            
             $this->logger->info('Scenario created', ['scenario_id' => $scenario->getId()]);

            // handle the algorithms parameters
            $tabParameters = [];
            foreach ($data as $param => $value) {
                list($algorithmHash, $nfVariable, $parameterName) = explode(":", $param);
                $tabParameters[$algorithmHash][$nfVariable][$parameterName] = $value;
            }
            
             $this->logger->debug('Processing algorithms', ['algorithm_count' => count($tabParameters)]);
            
            foreach ($tabParameters as $algorithmHash => $dataParams) {
                foreach ($dataParams as $nfVariable => $params) {
                    // if there is no parameters for algorithm, only selected_algorithm parameters is passed
                    unset($params["selected_algorithm"]);

                     $this->logger->debug('Creating ScenarioAlgorithm', [
                        'algorithm_hash' => $algorithmHash,
                        'nf_variable' => $nfVariable,
                        'param_count' => count($params)
                    ]);

                    $scenarioAlgorithm = new ScenarioAlgorithm();
                    $scenarioAlgorithm->setScenario($scenario);
                    $scenarioAlgorithm->setAlgorithmVersion($this->getAlgorithmVersionRepository()->findOneBy(["hash" => $algorithmHash]));
                    $scenarioAlgorithm->setNfVariable($nfVariable);
                    $scenarioAlgorithm->setParametres($params);

                    $this->getEm()->persist($scenarioAlgorithm);
                    $this->getEm()->flush();
                    
                     $this->logger->info('ScenarioAlgorithm created', [
                        'scenario_algorithm_id' => $scenarioAlgorithm->getId(),
                        'nf_variable' => $nfVariable
                    ]);
                }
            }
            
             $this->logger->info('Scenario with algorithms created successfully', ['scenario_id' => $scenario->getId()]);
            
        } elseif (isset($data["create_button_with_algo"])) { 
             $this->logger->info('Creating scenario with algorithms');
            
            $dataScenario = $this->getSession()->get("create_scenario");
            unset($data["create_button_with_algo"]);
            
            // create the scenario object
            $scenario = $this->create(
                    $dataScenario["dataset"]->getHash(),
                    $dataScenario["tag"]->getHash(),
                    unserialize($dataScenario["parameters"]),
                    $dataScenario["metascenario"]->getId()
            );
            
             $this->logger->info('Scenario created', ['scenario_id' => $scenario->getId()]);
             $this->logger->debug('Algorithm data received', ['data' => $data]); 
            // handle the algorithms parameters
            $tabParameters = [];
            foreach ($data as $param => $value) {                
                list($algorithmHash, $nfVariable, $parameterName) = explode(":", $param);
                $tabParameters[$algorithmHash][$nfVariable][$parameterName] = $value;               
            }
            
             $this->logger->debug('Processing algorithms', ['algorithm_count' => count($tabParameters)]);
            
            foreach ($tabParameters as $algorithmHash => $dataParams) {
                foreach ($dataParams as $nfVariable => $params) {
                    // if there is no parameters for algorithm, only selected_algorithm parameters is passed
                    unset($params["selected_algorithm"]);

                     $this->logger->debug('Creating ScenarioAlgorithm', [
                        'algorithm_hash' => $algorithmHash,
                        'nf_variable' => $nfVariable,
                        'param_count' => count($params)
                    ]);

                    $scenarioAlgorithm = new ScenarioAlgorithm();
                    $scenarioAlgorithm->setScenario($scenario);
                    $scenarioAlgorithm->setAlgorithmVersion($this->getAlgorithmVersionRepository()->findOneBy(["hash" => $algorithmHash]));
                    $scenarioAlgorithm->setNfVariable($nfVariable);
                    $scenarioAlgorithm->setParametres($params);

                    $this->getEm()->persist($scenarioAlgorithm);
                    $this->getEm()->flush();
                    
                     $this->logger->info('ScenarioAlgorithm created', [
                        'scenario_algorithm_id' => $scenarioAlgorithm->getId(),
                        'nf_variable' => $nfVariable
                    ]);
                }
            }
            
             $this->logger->info('Scenario with algorithms created successfully', ['scenario_id' => $scenario->getId()]);

        } elseif (isset($data["update_button"])) {
             $this->logger->info('Updating existing scenario');
            
            $dataScenario = $this->getSession()->get("edit_scenario"); 
            unset($data["update_button"]);

            // update the scenario object
            $scenario = $this->getScenarioRepository()->find($dataScenario["scenario"]->getId());
            
             $this->logger->debug('Scenario found for update', ['scenario_id' => $scenario->getId()]);
            
            $this->update(
                $dataScenario["dataset"]->getHash(),
                $dataScenario["tag"]->getHash(),
                unserialize($dataScenario["parameters"]),
                $scenario);
            
             $this->logger->info('Scenario updated', ['scenario_id' => $scenario->getId()]);
            
            // handle the algorithms parameters
            $tabParameters = [];
            foreach ($data as $param => $value) {                
                list($algorithmHash, $nfVariable, $parameterName) = explode(":", $param);
                $tabParameters[$algorithmHash][$nfVariable][$parameterName] = $value;               
            }
            
             $this->logger->debug('Processing algorithm updates', ['algorithm_count' => count($tabParameters)]);
            
            foreach ($tabParameters as $algorithmHash => $dataParams) {
                foreach ($dataParams as $nfVariable => $params) {
                    // if there is no parameters for algorithm, only selected_algorithm parameters is passed
                    unset($params["selected_algorithm"]);
                    $scenarioAlgorithm = $this->getScenarioAlgorithmRepository()->findBy(['scenario' => $dataScenario["scenario"]->getId()]);
                    
                     $this->logger->debug('Found existing ScenarioAlgorithms', ['count' => count($scenarioAlgorithm)]);
                    
                    foreach ($scenarioAlgorithm as $valeur) {
                        if ($valeur->getNfVariable() === $nfVariable) {
                             $this->logger->debug('Updating ScenarioAlgorithm', [
                                'scenario_algorithm_id' => $valeur->getId(),
                                'old_algorithm_hash' => $valeur->getAlgorithmVersion()->getHash(),
                                'new_algorithm_hash' => $algorithmHash,
                                'nf_variable' => $nfVariable
                            ]);
                            
                            $valeur->setAlgorithmVersion($this->getAlgorithmVersionRepository()->findOneBy(["hash" => $algorithmHash]));
                            $valeur->setNfVariable($nfVariable);
                            $valeur->setParametres($params);
                            $this->getEm()->flush();
                            
                             $this->logger->info('ScenarioAlgorithm updated successfully', [
                                'scenario_algorithm_id' => $valeur->getId()
                            ]);
                        } 
                    }  
                }   
            }
            
             $this->logger->info('Scenario update completed', ['scenario_id' => $scenario->getId()]);
        } else {
             $this->logger->warning('Unknown action in manage method', ['data_keys' => array_keys($data)]);
        }

         $this->logger->info('Redirecting to scenario index');
        return $this->redirectToRoute("dashboard_scenario_index");
    }

}   

//        $tagHash = $data["tag_hash"];
//        $datasetHash = $data["dataset_hash"];
//        $metascenarioId = $data["metascenario_id"];
//        unset($data["tag_hash"]);
//        unset($data["dataset_hash"]);
//        unset($data["metascenario_id"]);
//
//        // in update context we have the scenario id
//        if(isset($data["scenario_id"])) {
//            $scenario = $this->getScenarioRepository()->find($data["scenario_id"]);
//            unset($data["scenario_id"]);
//        }
//
//        if (isset($data["update_button"])) {
//            unset($data["update_button"]);
//            $this->update($datasetHash, $tagHash, $data, $scenario);
//        }
//        elseif ($data["create_button"]) {
//            unset($data["create_button"]);
//            $this->create($datasetHash, $tagHash, $data, $metascenarioId);
//        }
//
//        return $this->redirectToRoute("dashboard_scenario_index");
     

