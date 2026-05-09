<?php

namespace App\Api;

use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\HttpFoundation\Request;
use Symfony\Component\Routing\Annotation\Route;
use OpenApi\Annotations as OA;
use FOS\RestBundle\Controller\Annotations\Post;
use FOS\RestBundle\Controller\Annotations\RequestParam;
use Nelmio\ApiDocBundle\Annotation\Model;
use Doctrine\ORM\EntityManagerInterface;
use App\Entity\ApiLog;
use App\Entity\User;
use App\Entity\Dataset;
use App\Entity\DatasetLogs;

/**
 * @route("/dataset")
 */
class DatasetController extends AbstractController {

    /**
     * Notify when there is an error during the processing of the dataset
     *
     * @Route("/{hash}/error/{token}", methods={"GET"})
     * @OA\Response(
     *     response=200,
     *     description="",
     * )
     * @OA\Tag(name="Dataset")
     */
    public function error(Dataset $dataset, string $token, EntityManagerInterface $em): Response
    {
        $dataset->setStatus(Dataset::STATUS_ERROR);
        $datasetLog = new DatasetLogs($dataset, DatasetLogs::ACTION_ERROR, $token);

        $em->persist($datasetLog);
        $em->persist($dataset);
        $em->flush();
        return new Response(null, Response::HTTP_OK);
    }

    /**
     * Notify when the processing of the dataset is complete (copy + unzip)
     *
     * @Route("/{hash}/complete/{token}", methods={"POST"})
     * @OA\Response(
     * response=200,
     * description="",
     * )
     * @RequestParam(
     * name="size",
     * description="size of the dataset en octet: int",
     * )
     * @OA\Tag(name="Dataset")
     */
    public function complete(Request $request, Dataset $dataset, string $token, EntityManagerInterface $em): Response
    {
        $data = json_decode($request->getContent());

        $dataset->setStatus(Dataset::STATUS_AVAILABLE);
        if (isset($data->size)) {
            $dataset->setSize($data->size);
        }

        if (isset($data->storagePath)) {
            $dataset->setStoragePath($data->storagePath);
            $dataset->setType('file');
        }

        $datasetLog = new DatasetLogs($dataset, DatasetLogs::ACTION_COMPLETE, $token);
        $em->persist($datasetLog);
        $em->persist($dataset);
        $em->flush();
        return new Response(null, Response::HTTP_OK);
    }

    /**
     * Notify when the databases of the dataset is deleted
     *
     * @Route("/{hash}/delete", methods={"GET"})
     * @OA\Response(
     *     response=200,
     *     description="",
     * )
     * @OA\Tag(name="Dataset")
     */
    public function delete(Dataset $dataset, EntityManagerInterface $em): Response
    {
        $em->remove($dataset);
        $em->flush();
        return new Response(null, Response::HTTP_OK);
    }

    /**
     * Notify when the processing of the dataset is started
     *
     * @Route("/{hash}/start/{token}", methods={"GET"})
     * @OA\Response(
     *     response=200,
     *     description="",
     * )
     * @OA\Tag(name="Dataset")
     */
    public function start(Dataset $dataset, string $token, EntityManagerInterface $em): Response
    {
        $dataset->setStatus(Dataset::STATUS_PROCESSING);
        $datasetLog = new DatasetLogs($dataset, DatasetLogs::ACTION_START, $token);

        $em->persist($datasetLog);
        $em->persist($dataset);
        $em->flush();
        return new Response(null, Response::HTTP_OK);
    }

    /**
     * Check if the dataset and the user's hash is correct
     * 
     * @Post("/check")
     * @OA\Response(response=200, description="The dataset and hash are correct"),
     * @OA\Response(response=400, description="The dataset and hash are not correct"),
     * @RequestParam(
     *      name="dataset",
     *      description="The id of the dataset",
     *      nullable=true
     * )
     * @RequestParam(
     *      name="user",
     *      description="The hash of the user",
     *      nullable=true
     * )
     * @OA\Tag(name="Dataset")
     */
    public function check(Request $request, EntityManagerInterface $em): Response
    {
        $serializer = $this->container->get('serializer');
        $data = json_decode($request->getContent());

        if (isset($data->dataset) && !empty($data->dataset) && $data->user && !empty($data->user)) {

            $dataset = $em->getRepository(Dataset::class)->findOneBy(["hash" => $data->dataset]);
            $user = $em->getRepository(User::class)->findOneBy(["hash" => $data->user]);

            if ($dataset && $user && $user->hasPermission($dataset, $em->getRepository(Dataset::class))) {
                return new Response("true", Response::HTTP_OK);
            } else {
                return new Response("false", Response::HTTP_BAD_REQUEST);
            }
        } else {
            return new Response("false", Response::HTTP_BAD_REQUEST);
        }
    }

    /**
     * Notify the percentage of the progress bar during the processing of the dataset
     *
     * @Route("/{hash}/progress/{pourcentage_progress}", methods={"GET"})
     * @OA\Response(
     *     response=200,
     *     description="",
     * )

     * @OA\Tag(name="Dataset")
     */
    public function progress(Dataset $dataset, float $pourcentage_progress, EntityManagerInterface $em): Response
    {
        $english_format_number = number_format($pourcentage_progress, 1, '.', '');
        $dataset->setPourcentageProgress($english_format_number);
        $em->persist($dataset);
        $em->flush();
        return new Response(null, Response::HTTP_OK);
    }

}
