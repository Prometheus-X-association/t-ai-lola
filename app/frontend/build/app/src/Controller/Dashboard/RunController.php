<?php

namespace App\Controller\Dashboard;

use App\Repository\RunRepository;
use Symfony\Component\HttpFoundation\Request;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\Routing\Attribute\Route;
use Doctrine\ORM\EntityManagerInterface;
use Symfony\Component\Security\Http\Attribute\IsGranted;
use App\Controller\LolaController;
use App\Entity\Run;
use App\Entity\RunLogs;
use App\Entity\Scenario;
use App\Lolapy\LolapyServiceApi;
use Symfony\Component\HttpFoundation\ResponseHeaderBag;
use Symfony\Bridge\Doctrine\Attribute\MapEntity;

#[Route('/dashboard/run', name: 'dashboard_run_')]
#[IsGranted('ROLE_PROFIL_2')]
class RunController extends LolaController {

    #[Route('/', name: 'index', methods: ['GET'])]
    public function index(RunRepository $runRepository): Response
    {
        return $this->render('dashboard/run/index.html.twig', [
                    'runs' => $runRepository->findBy(["createdBy" => $this->getUser()])
        ]);
    }

    #[Route('/scenario/{id}', name: 'index_scenario', methods: ['GET'])]
    public function indexScenario(RunRepository $runRepository, Scenario $scenario): Response
    {
        return $this->render('dashboard/run/index.html.twig', [
                    'runs' => $runRepository->findBy(["createdBy" => $this->getUser(), "scenario" => $scenario])
        ]);
    }

    #[Route('/details/{hash}', name: 'details', methods: ['GET'])]
    public function details(#[MapEntity(mapping: ['hash' => 'hash'])] Run $run): Response
    {
        $runLogs = $this->getRunLogsRepository()->findBy(["run" => $run], ["time" => "DESC"]);
        return $this->render('dashboard/run/details.html.twig', [
                    'run' => $run,
                    'runLogs' => $runLogs
        ]);
    }

    #[Route('/results/{hash}', name: 'results', methods: ['GET'])]
    public function results(#[MapEntity(mapping: ['hash' => 'hash'])] Run $run, EntityManagerInterface $em, LolapyServiceApi $lolapyService): Response
    {
        $filename = "run_" . $run->getHash();
        $response = new Response($lolapyService->scenarioGetArchive($run->getHash()));
        
        $disposition = $response->headers->makeDisposition(
                ResponseHeaderBag::DISPOSITION_ATTACHMENT,
                $filename . ".zip"
        );
        $response->headers->set('Content-Disposition', $disposition);
        $response->headers->set('Content-Type', "application/zip");
        return $response;
    }

    /**
     * Get all the run logs to refresh the run log details table
     */
    #[Route('/details/ajax/logs/{hash}', name: 'ajax_run_logs', methods: ['GET'])]
    public function ajaxRunLogs(Request $request, #[MapEntity(mapping: ['hash' => 'hash'])] Run $run): Response
    {

        $runLogs = $this->getRunLogsRepository()->findBy(["run" => $run], ["time" => "DESC"]);
        $tabRunLogs = [];
        foreach ($runLogs as $runLogEntity) {
            /** @var RunLogs $runLogEntity */
            $tabRunLogs[] = [
                'run_status' => $run->getStatus(),
                'run_output' => $run->getHasOutput(),
                'datetime' => $runLogEntity->getTime()?->format('c'),
                'type' => $runLogEntity->getType(),
                'nomProcess' => $runLogEntity->getNomProcess(),
                'event' => $runLogEntity->getEvent(),
                'workdir' => $runLogEntity->getWorkdir(),
                'error' => $runLogEntity->getError(),
                'statistics' => $runLogEntity->getStatistic(),
            ];
        }

        if (empty($tabRunLogs)) {
            $tabRunLogs[] = [
                'run_status' => $run->getStatus(),
                'run_output' => $run->getHasOutput(),
                'datetime' => null,
                'type' => null,
                'nomProcess' => null,
                'event' => null,
                'workdir' => null,
                'error' => null,
                'statistics' => null,
            ];
        }

        return $this->json($tabRunLogs);
    }

}
