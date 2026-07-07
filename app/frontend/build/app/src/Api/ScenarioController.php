<?php

namespace App\Api;

use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\HttpFoundation\Request;
use Symfony\Component\Routing\Attribute\Route;
use Doctrine\ORM\EntityManagerInterface;
use OpenApi\Attributes as OA;
use App\Lolapy\LolapyServiceApi;
use App\Entity\Run;
use App\Entity\RunLogs;

#[Route('/scenario')]
class ScenarioController extends AbstractController {

    /**
     * Notify when Lolapy start the processing of the Trax db
     */
    #[OA\Parameter(name: 'hash', in: 'path', required: true, description: 'Run hash.', schema: new OA\Schema(type: 'string'), example: 'R2f5c54f2d5f745988c2287a70e73213')]
    #[OA\Response(response: 200, description: 'Run status updated to SCHEDULING_TRAX_DB.')]
    #[OA\Tag(name: 'Scenario')]
    #[Route('/start/trax/{hash}', methods: ['GET'])]
    public function startTrax(Run $run, EntityManagerInterface $em): Response
    {
        $run->setStatus(Run::STATUS_SCHEDULING_TRAX_DB);
        $em->flush();
        return new Response(null, Response::HTTP_OK);
    }

    /**
     * Notify when Lolapy finish the processing of the Trax db and wait for Nextflow
     */
    #[OA\Parameter(name: 'hash', in: 'path', required: true, description: 'Run hash.', schema: new OA\Schema(type: 'string'), example: 'R2f5c54f2d5f745988c2287a70e73213')]
    #[OA\Response(response: 200, description: 'Run status updated to WAITING_NEXTFLOW.')]
    #[OA\Tag(name: 'Scenario')]
    #[Route('/complete/trax/{hash}', methods: ['GET'])]
    public function completeTrax(Run $run, EntityManagerInterface $em): Response
    {
        $run->setStatus(Run::STATUS_WAITING_NEXTFLOW);
        $em->flush();
        return new Response(null, Response::HTTP_OK);
    }

    /**
     * Notify when Lolapy start to run the scenario
     */
    #[OA\Parameter(name: 'hash', in: 'path', required: true, description: 'Run hash.', schema: new OA\Schema(type: 'string'), example: 'R2f5c54f2d5f745988c2287a70e73213')]
    #[OA\Response(response: 200, description: 'Run status updated to RUNNING_SCENARIO.')]
    #[OA\Tag(name: 'Scenario')]
    #[Route('/start/nextflow/{hash}', methods: ['GET'])]
    public function startNextflow(Run $run, EntityManagerInterface $em): Response
    {
        $run->setStatus(Run::STATUS_RUNNING_SCENARIO);
        $em->flush();
        return new Response(null, Response::HTTP_OK);
    }

    /**
     * Notify when Lolapy finish to run the scenario and send to Lolapy the last algorithme workdir
     */
    #[OA\Parameter(name: 'hash', in: 'path', required: true, description: 'Run hash.', schema: new OA\Schema(type: 'string'), example: 'R2f5c54f2d5f745988c2287a70e73213')]
    #[OA\Response(response: 200, description: 'Run status updated to COMPLETED and result preparation started when work directories are available.')]
    #[OA\Response(response: 400, description: 'No run logs found for this run.', content: new OA\JsonContent(type: 'string', example: 'No run logs found for the run'))]
    #[OA\Tag(name: 'Scenario')]
    #[Route('/complete/nextflow/{hash}', methods: ['GET'])]
    public function completeNextflow(Run $run, EntityManagerInterface $em, LolapyServiceApi $lolapy): Response
    {
        $run->setStatus(Run::STATUS_COMPLETED);
        $em->flush();

        // get all the workdir of the run to prepare the output zip
        $runLogs = $em->getRepository(RunLogs::class)->findBy(["run" => $run]);

        if ($runLogs) {
            $runLogs = array_filter($runLogs, function ($runLog) {
                return !empty($runLog->getWorkdir());
            });
            $listWorkdir = array_map(function($runLog) {
                return $runLog->getWorkDir();
            }, $runLogs);

            if ($listWorkdir) {
                $lolapy->scenarioPrepareResults(array_values($listWorkdir), $run->getHash(), $run->getScenario()->getTag()->getHash());
            }
            return new Response(null, Response::HTTP_OK);
        } else {
            return new Response(json_encode("No run logs found for the run"), Response::HTTP_BAD_REQUEST);
        }
    }

    /**
     * Notify when an error occured during the execution of the scenario
     */
    #[OA\Parameter(name: 'hash', in: 'path', required: true, description: 'Run hash.', schema: new OA\Schema(type: 'string'), example: 'R2f5c54f2d5f745988c2287a70e73213')]
    #[OA\Response(response: 200, description: 'Run status updated to ERROR.')]
    #[OA\Tag(name: 'Scenario')]
    #[Route('/error/{hash}', methods: ['GET'])]
    public function error(Run $run, EntityManagerInterface $em): Response
    {
        $run->setStatus(Run::STATUS_ERROR);
        $em->flush();
        return new Response(null, Response::HTTP_OK);
    }

    /**
     * Collect Nextflow logs for processes only during scenario execution and put status in Submit.
     */
    #[OA\Parameter(name: 'hash', in: 'path', required: true, description: 'Run hash.', schema: new OA\Schema(type: 'string'), example: 'R2f5c54f2d5f745988c2287a70e73213')]
    #[OA\RequestBody(
        required: true,
        description: 'Nextflow process submit event.',
        content: new OA\JsonContent(
            required: ['processName', 'eventTime', 'workDir'],
            properties: [
                new OA\Property(property: 'processName', type: 'string', example: 'extract_features'),
                new OA\Property(property: 'eventTime', type: 'string', format: 'date-time', example: '2026-06-26T10:15:28+02:00'),
                new OA\Property(property: 'workDir', type: 'string', example: '/work/ab/cdef1234567890'),
                new OA\Property(property: 'statistics', type: 'object', nullable: true, example: ['cpus' => 2, 'memory' => '4 GB', 'duration' => '12s']),
            ],
        ),
    )]
    #[OA\Response(response: 200, description: 'Process log created or updated with SUBMIT status.')]
    #[OA\Response(response: 400, description: 'Invalid run hash, invalid payload, or workflow already in error.', content: new OA\JsonContent(type: 'string', example: 'Incorrect data'))]
    #[OA\Tag(name: 'Scenario')]
    #[Route('/process/submit/{hash}', methods: ['POST'])]
    public function submitProcess(Request $request, EntityManagerInterface $em, String $hash): Response
    {

        $data = json_decode($request->getContent());
        $type = "WORKFLOW";
        $event = "ERROR";

        if (isset($data->processName) && isset($data->eventTime) && isset($data->workDir)) {
            $run = $em->getRepository(Run::class)->findOneBy(["hash" => $hash]); 
            $runLogs = $em->getRepository(RunLogs::class)->findOneBy(["nomProcess" => $data->processName, "run" => $run]); 
            $workflow = $em->getRepository(RunLogs::class)->findOneBy(["type" => $type, "event" => $event, "run" => $run ]);
            if ($workflow) { 
                return new Response(json_encode("The workflow is in error"), Response::HTTP_BAD_REQUEST);
            } else {
                    // Si l'objet Process existe, ça veut dire qu'il est soit en 'RUN', soit en 'DONE'
                    if($runLogs) { 
                        return new Response(json_encode("Unable to return to submit event"), Response::HTTP_BAD_REQUEST);
                    } else {
                    // S'il n'exite pas, on crée l'objet Process avec les infos envoyés en paramètres de la requête        
                            if ($run) {
                                $nvRunLogs = new RunLogs();
                                $nvRunLogs->setRun($run);
                                $nvRunLogs->setType(RunLogs::TYPE_PROCESS);  
                                $nvRunLogs->setTime(new \Datetime($data->eventTime));
                                $nvRunLogs->setWorkdir($data->workDir ?? null);
                                $nvRunLogs->setStatistic(json_decode(json_encode($data->statistics), true) ?? null);
                                $nvRunLogs->setNomProcess($data->processName);
                                    // Si le scénario est à 'COMPLETED', on fait passer le process directement à 'DONE'
                                    if ($run->getStatus() == "COMPLETED") { 
                                        $nvRunLogs->setEvent(RunLogs::EVENT_DONE);
                                    // Sinon, il est en 'SUBMIT'
                                    } else { 
                                        $nvRunLogs->setEvent(RunLogs::EVENT_SUBMIT);
                                    }
                                $em->persist($nvRunLogs);
                                $em->flush();
                                return new Response(null, Response::HTTP_OK);
                            } else {   
                                return new Response(json_encode("Hash does not exist"), Response::HTTP_BAD_REQUEST);
                            }
                }
            }
        } else {
            return new Response(json_encode("Incorrect data"), Response::HTTP_BAD_REQUEST);
        }
    }


    /**
     * Put status in Run.
     */
    #[OA\Parameter(name: 'hash', in: 'path', required: true, description: 'Run hash.', schema: new OA\Schema(type: 'string'), example: 'R2f5c54f2d5f745988c2287a70e73213')]
    #[OA\RequestBody(
        required: true,
        description: 'Nextflow process run event.',
        content: new OA\JsonContent(
            required: ['processName', 'eventTime', 'workDir'],
            properties: [
                new OA\Property(property: 'processName', type: 'string', example: 'extract_features'),
                new OA\Property(property: 'eventTime', type: 'string', format: 'date-time', example: '2026-06-26T10:16:01+02:00'),
                new OA\Property(property: 'workDir', type: 'string', example: '/work/ab/cdef1234567890'),
                new OA\Property(property: 'statistics', type: 'object', nullable: true, example: ['cpus' => 2, 'memory' => '4 GB', 'duration' => '30s']),
            ],
        ),
    )]
    #[OA\Response(response: 200, description: 'Process log created or updated with RUN status.')]
    #[OA\Response(response: 400, description: 'Invalid run hash, invalid payload, or forbidden status transition.', content: new OA\JsonContent(type: 'string', example: 'Hash does not exist'))]
    #[OA\Tag(name: 'Scenario')]
    #[Route('/process/run/{hash}', methods: ['POST'])]
    public function runProcess(Request $request, EntityManagerInterface $em, String $hash): Response
    {

        $data = json_decode($request->getContent());
        $type = "WORKFLOW";
        $event = "ERROR";
        
        if (isset($data->processName) && isset($data->eventTime) && isset($data->workDir)) {
            $run = $em->getRepository(Run::class)->findOneBy(["hash" => $hash]);
            $runLogs = $em->getRepository(RunLogs::class)->findOneBy(["nomProcess" => $data->processName, "run" => $run]);
            $workflow = $em->getRepository(RunLogs::class)->findOneBy(["type" => $type, "event" => $event, "run" => $run ]);
            if ($workflow) {
                return new Response(json_encode("The workflow is in error"), Response::HTTP_BAD_REQUEST);
            } else {
                    // Si on a un process en 'SUBMIT'
                    if ($run && $runLogs && $runLogs->getEvent() != "DONE") { 
                        // et le scénario n'est pas à 'COMPLETED'
                        if ($run->getStatus() != "COMPLETED") {
                            // le process passe à 'RUN' 
                            $runLogs->setEvent(RunLogs::EVENT_RUN); 
                        } else {
                            // sinon le process passe directement à 'DONE'
                            $runLogs->setEvent(RunLogs::EVENT_DONE); 
                        }
                        $em->persist($runLogs);
                        $em->flush();
                        return new Response(null, Response::HTTP_OK);

                    // Si le process est déjà en 'DONE'
                    } elseif ($run && $runLogs && $runLogs->getEvent() == "DONE") { 
                        return new Response(json_encode("Unable to return to run event !!"), Response::HTTP_BAD_REQUEST);

                    } else {
                            // Si l'objet 'runLogs n'existe pas, on crée l'objet Process avec les infos envoyés en paramètres de la requête
                            if ($run) { 
                                $nvRunLogs = new RunLogs();
                                $nvRunLogs->setRun($run);
                                $nvRunLogs->setType(RunLogs::TYPE_PROCESS);  
                                $nvRunLogs->setTime(new \Datetime($data->eventTime));
                                $nvRunLogs->setWorkdir($data->workDir ?? null);
                                $nvRunLogs->setStatistic(json_decode(json_encode($data->statistics), true) ?? null);
                                $nvRunLogs->setNomProcess($data->processName);
                                    // Si le scénario est à 'COMPLETED', on fait passer le process directement à 'DONE'
                                    if ($run->getStatus() == "COMPLETED") { 
                                        $nvRunLogs->setEvent(RunLogs::EVENT_DONE);
                                    // Sinon, il est en 'RUN'
                                    }else { 
                                        $nvRunLogs->setEvent(RunLogs::EVENT_RUN);
                                    }
                                $em->persist($nvRunLogs);
                                $em->flush();
                                return new Response(null, Response::HTTP_OK);

                            } else {   
                                return new Response(json_encode("Hash does not exist"), Response::HTTP_BAD_REQUEST);
                            }
                } 
            }
        } else {
            return new Response(json_encode("Incorrect data"), Response::HTTP_BAD_REQUEST);
        }
    }

    
   /**
     * Put status in Done.
     */
    #[OA\Parameter(name: 'hash', in: 'path', required: true, description: 'Run hash.', schema: new OA\Schema(type: 'string'), example: 'R2f5c54f2d5f745988c2287a70e73213')]
    #[OA\RequestBody(
        required: true,
        description: 'Nextflow process done event.',
        content: new OA\JsonContent(
            required: ['processName', 'eventTime', 'workDir', 'statistics'],
            properties: [
                new OA\Property(property: 'processName', type: 'string', example: 'extract_features'),
                new OA\Property(property: 'eventTime', type: 'string', format: 'date-time', example: '2026-06-26T10:20:44+02:00'),
                new OA\Property(property: 'workDir', type: 'string', example: '/work/ab/cdef1234567890'),
                new OA\Property(property: 'statistics', type: 'object', example: ['cpus' => 2, 'memory' => '4 GB', 'duration' => '4m16s', 'exit' => 0]),
            ],
        ),
    )]
    #[OA\Response(response: 200, description: 'Process log created or updated with DONE status.')]
    #[OA\Response(response: 400, description: 'Invalid run hash, invalid payload, or workflow already in error.', content: new OA\JsonContent(type: 'string', example: 'Hash or processName does not exist'))]
    #[OA\Tag(name: 'Scenario')]
    #[Route('/process/done/{hash}', methods: ['POST'])]
    public function doneProcess(Request $request, EntityManagerInterface $em, String $hash): Response
    {
        $data = json_decode($request->getContent());
        $type = "WORKFLOW";
        $event = "ERROR";
        
        if (isset($data->processName) && isset($data->eventTime) && isset($data->workDir) && isset($data->statistics)) {
            $run = $em->getRepository(Run::class)->findOneBy(["hash" => $hash]);
            $runLogs = $em->getRepository(RunLogs::class)->findOneBy(["nomProcess" => $data->processName, "run" => $run]);
            $workflow = $em->getRepository(RunLogs::class)->findOneBy(["type" => $type, "event" => $event, "run" => $run ]);
            if ($workflow) {
                return new Response(json_encode("The workflow is in error"), Response::HTTP_BAD_REQUEST);
            } else {
                    // Si le process existe déjà
                    if ($runLogs) {
                        // On passe son statut à 'DONE' 
                        $runLogs->setEvent(RunLogs::EVENT_DONE);
                        // Mettre à jour les statistiques
                        $runLogs->setStatistic(json_decode(json_encode($data->statistics), true) ?? null);
                        $em->persist($runLogs);
                        $em->flush();
                        return new Response(null, Response::HTTP_OK);
                    } else {
                            if ($run) {
                                // Création d'un nouveau objet RunLogs avec un statut en 'DONE'
                                $nv_runLogs = new RunLogs(); 
                                $nv_runLogs->setRun($run);
                                $nv_runLogs->setType(RunLogs::TYPE_PROCESS); 
                                $nv_runLogs->setEvent(RunLogs::EVENT_DONE);
                                $nv_runLogs->setTime(new \Datetime($data->eventTime));
                                $nv_runLogs->setWorkdir($data->workDir ?? null);
                                $nv_runLogs->setStatistic(json_decode(json_encode($data->statistics), true) ?? null);
                                $nv_runLogs->setNomProcess($data->processName);
                                $em->persist($nv_runLogs);
                                $em->flush();
                                return new Response(null, Response::HTTP_OK);
                            } else {
                                return new Response(json_encode("Hash or processName does not exist"), Response::HTTP_BAD_REQUEST);
                            }
                    } 
            }
        } else {
            return new Response(json_encode("Incorrect data"), Response::HTTP_BAD_REQUEST);
        }
    }

    
    /**
     * Put status in Error.
     */
    #[OA\Parameter(name: 'hash', in: 'path', required: true, description: 'Run hash.', schema: new OA\Schema(type: 'string'), example: 'R2f5c54f2d5f745988c2287a70e73213')]
    #[OA\RequestBody(
        required: true,
        description: 'Nextflow process error event.',
        content: new OA\JsonContent(
            required: ['processName', 'eventTime', 'workDir'],
            properties: [
                new OA\Property(property: 'processName', type: 'string', example: 'extract_features'),
                new OA\Property(property: 'eventTime', type: 'string', format: 'date-time', example: '2026-06-26T10:21:05+02:00'),
                new OA\Property(property: 'workDir', type: 'string', example: '/work/ab/cdef1234567890'),
                new OA\Property(property: 'statistics', type: 'object', nullable: true, example: ['exit' => 1, 'message' => 'Process failed']),
            ],
        ),
    )]
    #[OA\Response(response: 200, description: 'Process log updated with ERROR status.')]
    #[OA\Response(response: 400, description: 'Invalid run hash, process name, or request body.', content: new OA\JsonContent(type: 'string', example: 'Incorrect data'))]
    #[OA\Tag(name: 'Scenario')]
    #[Route('/process/error/{hash}', methods: ['POST'])]
    public function errorProcess(Request $request, EntityManagerInterface $em, Run $run): Response
    {

        $data = json_decode($request->getContent());

        if (isset($data->processName) && isset($data->eventTime) && isset($data->workDir)) {
            $runLogs = $em->getRepository(RunLogs::class)->findOneBy(["nomProcess" => $data->processName, "run" => $run]);
            if ($runLogs) {
                $runLogs->setEvent(RunLogs::EVENT_ERROR);
                $em->persist($runLogs);
                $em->flush();
                return new Response(null, Response::HTTP_OK);
            } else {
                return new Response(json_encode("Hash or processName does not exist"), Response::HTTP_BAD_REQUEST);
            }
        } else {
            return new Response(json_encode("Incorrect data"), Response::HTTP_BAD_REQUEST);
        }
    }


    /**
     * Notify when Lolapy end the compression of the results of the run
     */
    #[OA\Parameter(name: 'hash', in: 'path', required: true, description: 'Run hash.', schema: new OA\Schema(type: 'string'), example: 'R2f5c54f2d5f745988c2287a70e73213')]
    #[OA\Response(response: 200, description: 'Run marked as having an output archive.')]
    #[OA\Tag(name: 'Scenario')]
    #[Route('/results/complete/{hash}', methods: ['GET'])]
    public function resultComplete(Run $run, EntityManagerInterface $em): Response
    {
        $run->setHasOutput(true);
        $em->flush();
        return new Response(null, Response::HTTP_OK);
    }

    
    /**
     * Put the status of Workflow in Run
     */
    #[OA\Parameter(name: 'hash', in: 'path', required: true, description: 'Run hash.', schema: new OA\Schema(type: 'string'), example: 'R2f5c54f2d5f745988c2287a70e73213')]
    #[OA\RequestBody(
        required: true,
        description: 'Nextflow workflow run event.',
        content: new OA\JsonContent(
            required: ['eventTime'],
            properties: [
                new OA\Property(property: 'eventTime', type: 'string', format: 'date-time', example: '2026-06-26T10:15:28+02:00'),
            ],
        ),
    )]
    #[OA\Response(response: 200, description: 'Workflow log created with RUN status.')]
    #[OA\Response(response: 400, description: 'Invalid run hash or request body.', content: new OA\JsonContent(type: 'string', example: 'Hash does not exist'))]
    #[OA\Tag(name: 'Scenario')]
    #[Route('/workflow/run/{hash}', methods: ['POST'])]
    public function workflowRun(Request $request, EntityManagerInterface $em, String $hash): Response
    {
        $data = json_decode($request->getContent());
        if (isset($data->eventTime)) {
            $run = $em->getRepository(Run::class)->findOneBy(["hash" => $hash]);
            if ($run) {
                // Création d'un workflow Run
                $runLogs = new RunLogs(); 
                $runLogs->setRun($run);
                $runLogs->setType(RunLogs::TYPE_WORKFLOW);
                $runLogs->setEvent(RunLogs::EVENT_RUN);
                $runLogs->setTime(new \Datetime($data->eventTime));
                $runLogs->setNomProcess('');
                $em->persist($runLogs);
                $em->flush();
                return new Response(null, Response::HTTP_OK);
            } else {
                return new Response(json_encode("Hash does not exist"), Response::HTTP_BAD_REQUEST);
            }
        } else {
            return new Response(json_encode("Incorrect data"), Response::HTTP_BAD_REQUEST);
        }
    }


    /**
     * Put the status of Workflow in Done
     */
    #[OA\Parameter(name: 'hash', in: 'path', required: true, description: 'Run hash.', schema: new OA\Schema(type: 'string'), example: 'R2f5c54f2d5f745988c2287a70e73213')]
    #[OA\RequestBody(
        required: true,
        description: 'Nextflow workflow done event.',
        content: new OA\JsonContent(
            required: ['eventTime'],
            properties: [
                new OA\Property(property: 'eventTime', type: 'string', format: 'date-time', example: '2026-06-26T10:24:12+02:00'),
            ],
        ),
    )]
    #[OA\Response(response: 200, description: 'Workflow log created with DONE status.')]
    #[OA\Response(response: 400, description: 'Invalid run hash or request body.', content: new OA\JsonContent(type: 'string', example: 'Incorrect data'))]
    #[OA\Tag(name: 'Scenario')]
    #[Route('/workflow/done/{hash}', methods: ['POST'])]
    public function workflowDone(Request $request, EntityManagerInterface $em, String $hash): Response
    {
        $data = json_decode($request->getContent());
        if (isset($data->eventTime)) {
            $run = $em->getRepository(Run::class)->findOneBy(["hash" => $hash]);
            if ($run) {
                // Création d'un workflow Run
                $runLogs = new RunLogs(); 
                $runLogs->setRun($run);
                $runLogs->setType(RunLogs::TYPE_WORKFLOW);
                $runLogs->setEvent(RunLogs::EVENT_DONE);
                $runLogs->setTime(new \Datetime($data->eventTime));
                $runLogs->setNomProcess('');
                $em->persist($runLogs);
                $em->flush();
                return new Response(null, Response::HTTP_OK);
            } else {
                return new Response(json_encode("Hash does not exist"), Response::HTTP_BAD_REQUEST);
            }
        } else {
            return new Response(json_encode("Incorrect data"), Response::HTTP_BAD_REQUEST);
        }
    } 

    /**
     * Put the status of Workflow in Error
     */
    #[OA\Parameter(name: 'hash', in: 'path', required: true, description: 'Run hash.', schema: new OA\Schema(type: 'string'), example: 'R2f5c54f2d5f745988c2287a70e73213')]
    #[OA\RequestBody(
        required: true,
        description: 'Nextflow workflow error event.',
        content: new OA\JsonContent(
            required: ['eventTime', 'errorReport'],
            properties: [
                new OA\Property(property: 'eventTime', type: 'string', format: 'date-time', example: '2026-06-26T10:25:01+02:00'),
                new OA\Property(property: 'errorReport', type: 'string', example: 'Nextflow workflow failed during process extract_features.'),
            ],
        ),
    )]
    #[OA\Response(response: 200, description: 'Workflow log created with ERROR status.')]
    #[OA\Response(response: 400, description: 'Invalid run hash or request body.', content: new OA\JsonContent(type: 'string', example: 'Incorrect data'))]
    #[OA\Tag(name: 'Scenario')]
    #[Route('/workflow/error/{hash}', methods: ['POST'])]
    public function workflowError(Request $request, EntityManagerInterface $em, String $hash): Response
    {
        $data = json_decode($request->getContent());

        if (isset($data->eventTime) && isset($data->errorReport)) {
            $run = $em->getRepository(Run::class)->findOneBy(["hash" => $hash]);
            if ($run) {
                // Création d'un workflow Run
                $runLogs = new RunLogs(); 
                $runLogs->setRun($run);
                $runLogs->setType(RunLogs::TYPE_WORKFLOW);
                $runLogs->setEvent(RunLogs::EVENT_ERROR);
                $runLogs->setTime(new \Datetime($data->eventTime));
                $runLogs->setError($data->errorReport);
                $runLogs->setNomProcess('');
                $em->persist($runLogs);
                $em->flush();
                return new Response(null, Response::HTTP_OK);
            } else {
                return new Response(json_encode("Hash does not exist"), Response::HTTP_BAD_REQUEST);
            }
        } else {
            return new Response(json_encode("Incorrect data"), Response::HTTP_BAD_REQUEST);
        }
    } 

    
}
