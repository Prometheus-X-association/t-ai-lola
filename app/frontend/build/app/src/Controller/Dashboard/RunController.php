<?php

namespace App\Controller\Dashboard;

use App\Repository\RunRepository;
use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Component\HttpFoundation\Request;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\Routing\Annotation\Route;
use Doctrine\ORM\EntityManagerInterface;
use Sensio\Bundle\FrameworkExtraBundle\Configuration\IsGranted;
use App\Controller\LolaController;
use App\Entity\Run;
use App\Entity\RunLogs;
use App\Entity\Scenario;

/**
 * @Route("/dashboard/run", name="dashboard_run_")
 * @IsGranted("ROLE_PROFIL_2")
 */
class RunController extends LolaController {

    /**
     * @Route("/", name="index", methods={"GET"})
     */
    public function index(RunRepository $runRepository): Response
    {
        return $this->render('dashboard/run/index.html.twig', [
                    'runs' => $runRepository->findBy(["createdBy" => $this->getUser()])
        ]);
    }

    /**
     * @Route("/{id}", name="index_scenario", methods={"GET"})
     */
    public function indexScenario(RunRepository $runRepository, Scenario $scenario): Response
    {
        return $this->render('dashboard/run/index.html.twig', [
                    'runs' => $runRepository->findBy(["createdBy" => $this->getUser(), "scenario" => $scenario])
        ]);
    }

    /**
     * @Route("/details/{hash}", name="details", methods={"GET"})
     */
    public function details(Run $run): Response
    {
        $runLogs = $this->getRunLogsRepository()->findBy(["run" => $run], ["time" => "DESC"]);
        return $this->render('dashboard/run/details.html.twig', [
                    'run' => $run,
                    'runLogs' => $runLogs
        ]);
    }

    /**
     * @Route("/results/{hash}", name="results", methods={"GET"})
     */
    public function results(Run $run, EntityManagerInterface $em, \App\Lolapy\LolapyServiceApi $lolapyService): Response
    {
        $filename = "run_" . $run->getHash();
        $response = new Response($lolapyService->scenarioGetArchive($run->getHash()));
        
        $disposition = $response->headers->makeDisposition(
                \Symfony\Component\HttpFoundation\ResponseHeaderBag::DISPOSITION_ATTACHMENT,
                $filename . ".zip"
        );
        $response->headers->set('Content-Disposition', $disposition);
        $response->headers->set('Content-Type', "application/zip");
        return $response;
    }

    /**
     * Get all the run logs to refresh the run log details table
     * @Route("/details/ajax/logs/{hash}", name="ajax_run_logs", methods={"GET"})
     */
    public function ajaxRunLogs(Request $request, Run $run): Response
    {
        // TODO : à reprendre, problème de circular références
        $serializer = $this->container->get('serializer');

        $runLogs = $this->getRunLogsRepository()->findBy(["run" => $run], ["time" => "DESC"]);
        $tabRunLogs = [];
        foreach ($runLogs as $runLogs) {
            /* @var RunLogs $runLog */
            $tabRunLog['run_status'] = $run->getStatus();
            $tabRunLog['run_output'] = $run->getHasOutput();
            $tabRunLog['datetime'] = $runLogs->getTime();
            $tabRunLog['type'] = $runLogs->getType();
            $tabRunLog['nomProcess'] = $runLogs->getNomProcess();
            $tabRunLog['event'] = $runLogs->getEvent();
            $tabRunLog['workdir'] = $runLogs->getWorkdir();
            $tabRunLog['error'] = $runLogs->getError();
            $tabRunLog['statistics'] = $runLogs->getStatistic();
            $tabRunLogs[] = $tabRunLog;
        }

        return new \Symfony\Component\HttpFoundation\Response(json_encode($tabRunLogs));
    }

}
