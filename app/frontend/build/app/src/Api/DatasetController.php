<?php

namespace App\Api;

use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\HttpFoundation\Request;
use Symfony\Component\Routing\Attribute\Route;
use OpenApi\Attributes as OA;
use Doctrine\ORM\EntityManagerInterface;
use App\Entity\User;
use App\Entity\Dataset;
use App\Entity\DatasetLogs;

#[Route('/dataset')]
class DatasetController extends AbstractController {

    /**
     * Notify when there is an error during the processing of the dataset
     */
    #[OA\Parameter(name: 'hash', in: 'path', required: true, description: 'Dataset hash.', schema: new OA\Schema(type: 'string'), example: 'D6da92778e1794c59f3025010ca8612290cbf1e42')]
    #[OA\Parameter(name: 'token', in: 'path', required: true, description: 'Processing token sent by Lolapy.', schema: new OA\Schema(type: 'string'), example: 'copy-20260626-001')]
    #[OA\Response(response: 200, description: 'Dataset status updated to ERROR.')]
    #[OA\Tag(name: 'Dataset')]
    #[Route('/{hash}/error/{token}', methods: ['GET'])]
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
     */
    #[OA\Parameter(name: 'hash', in: 'path', required: true, description: 'Dataset hash.', schema: new OA\Schema(type: 'string'), example: 'D6da92778e1794c59f3025010ca8612290cbf1e42')]
    #[OA\Parameter(name: 'token', in: 'path', required: true, description: 'Processing token sent by Lolapy.', schema: new OA\Schema(type: 'string'), example: 'copy-20260626-001')]
    #[OA\RequestBody(
        required: false,
        description: 'Dataset metadata returned by Lolapy after copy/unzip.',
        content: new OA\JsonContent(
            properties: [
                new OA\Property(property: 'size', type: 'integer', description: 'Dataset size in bytes.', example: 1048576),
                new OA\Property(property: 'storagePath', type: 'string', description: 'Path where the dataset is stored.', example: '/data/datasets/maskott'),
            ],
        ),
    )]
    #[OA\Response(response: 200, description: 'Dataset status updated to AVAILABLE.')]
    #[OA\Tag(name: 'Dataset')]
    #[Route('/{hash}/complete/{token}', methods: ['POST'])]
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
     */
    #[OA\Parameter(name: 'hash', in: 'path', required: true, description: 'Dataset hash.', schema: new OA\Schema(type: 'string'), example: 'D6da92778e1794c59f3025010ca8612290cbf1e42')]
    #[OA\Response(response: 200, description: 'Dataset removed from Lola database.')]
    #[OA\Tag(name: 'Dataset')]
    #[Route('/{hash}/delete', methods: ['GET'])]
    public function delete(Dataset $dataset, EntityManagerInterface $em): Response
    {
        $em->remove($dataset);
        $em->flush();
        return new Response(null, Response::HTTP_OK);
    }

    /**
     * Notify when the processing of the dataset is started
     */
    #[OA\Parameter(name: 'hash', in: 'path', required: true, description: 'Dataset hash.', schema: new OA\Schema(type: 'string'), example: 'D6da92778e1794c59f3025010ca8612290cbf1e42')]
    #[OA\Parameter(name: 'token', in: 'path', required: true, description: 'Processing token sent by Lolapy.', schema: new OA\Schema(type: 'string'), example: 'copy-20260626-001')]
    #[OA\Response(response: 200, description: 'Dataset status updated to PROCESSING.')]
    #[OA\Tag(name: 'Dataset')]
    #[Route('/{hash}/start/{token}', methods: ['GET'])]
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
     */
    #[OA\RequestBody(
        required: true,
        description: 'Dataset and user hashes to validate access permissions.',
        content: new OA\JsonContent(
            required: ['dataset', 'user'],
            properties: [
                new OA\Property(property: 'dataset', type: 'string', description: 'Dataset hash.', example: 'D6da92778e1794c59f3025010ca8612290cbf1e42'),
                new OA\Property(property: 'user', type: 'string', description: 'User hash.', example: 'U6f8a4e9a0d5c42f88911d80af2d34211'),
            ],
        ),
    )]
    #[OA\Response(
        response: 200,
        description: 'The dataset and user hash are valid.',
        content: new OA\JsonContent(type: 'string', example: 'true'),
    )]
    #[OA\Response(
        response: 400,
        description: 'The dataset and user hash are invalid.',
        content: new OA\JsonContent(type: 'string', example: 'false'),
    )]
    #[OA\Tag(name: 'Dataset')]
    #[Route('/check', methods: ['POST'])]
    public function check(Request $request, EntityManagerInterface $em): Response
    {
        $data = json_decode($request->getContent());

        if (isset($data->dataset) && !empty($data->dataset) && isset($data->user) && !empty($data->user)) {

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
     */
    #[OA\Parameter(name: 'hash', in: 'path', required: true, description: 'Dataset hash.', schema: new OA\Schema(type: 'string'), example: 'D6da92778e1794c59f3025010ca8612290cbf1e42')]
    #[OA\Parameter(name: 'pourcentage_progress', in: 'path', required: true, description: 'Dataset processing progress percentage.', schema: new OA\Schema(type: 'number', format: 'float', minimum: 0, maximum: 100), example: 42.5)]
    #[OA\Response(response: 200, description: 'Dataset progress percentage updated.')]
    #[OA\Tag(name: 'Dataset')]
    #[Route('/{hash}/progress/{pourcentage_progress}', methods: ['GET'])]
    public function progress(Dataset $dataset, float $pourcentage_progress, EntityManagerInterface $em): Response
    {
        $english_format_number = number_format($pourcentage_progress, 1, '.', '');
        $dataset->setPourcentageProgress($english_format_number);
        $em->persist($dataset);
        $em->flush();
        return new Response(null, Response::HTTP_OK);
    }

}
