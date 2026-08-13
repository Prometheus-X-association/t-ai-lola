<?php

namespace App\Api;

use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\HttpFoundation\Request;
use Symfony\Component\Routing\Attribute\Route;
use Doctrine\ORM\EntityManagerInterface;
use OpenApi\Attributes as OA;
use App\Entity\AlgorithmVersion;

#[Route('/algorithm')]
class AlgorithmVersionController extends AbstractController {

    /**
     * Notify when a version algorithm is successfully added
     */
    #[OA\Parameter(name: 'hash', in: 'path', required: true, description: 'Algorithm version hash.', schema: new OA\Schema(type: 'string'), example: 'A9f1d4c2b0e34567890123456789abcd')]
    #[OA\Response(response: 200, description: 'Algorithm version status updated to AVAILABLE.')]
    #[OA\Tag(name: 'Algorithm')]
    #[Route('/{hash}/complete', methods: ['GET'])]
    public function complete(AlgorithmVersion $algorithmVersion, EntityManagerInterface $em): Response
    {
        $algorithmVersion->setStatus(AlgorithmVersion::STATUS_AVAILABLE);
        $em->flush();
        return new Response(null, Response::HTTP_OK);
    }

    /**
     * Notify when adding the version algorithm fails
     */
    #[OA\RequestBody(
        required: true,
        description: 'Failure details returned by Lolapy when an algorithm version cannot be added.',
        content: new OA\JsonContent(
            required: ['algorithm_hash', 'error'],
            properties: [
                new OA\Property(property: 'algorithm_hash', type: 'string', description: 'Algorithm version hash.', example: 'A9f1d4c2b0e34567890123456789abcd'),
                new OA\Property(property: 'error', type: 'string', description: 'Error message.', example: 'Unable to copy algorithm archive.'),
            ],
        ),
    )]
    #[OA\Response(
        response: 200,
        description: 'Algorithm version status updated to ERROR.',
        content: new OA\JsonContent(type: 'string', example: 'true'),
    )]
    #[OA\Response(
        response: 400,
        description: 'Invalid hash or request body.',
        content: new OA\JsonContent(type: 'string', example: 'Bad hash'),
    )]
    #[OA\Tag(name: 'Algorithm')]
    #[Route('/error', methods: ['POST'])]
    public function error(Request $request, EntityManagerInterface $em): Response
    {
        $data = json_decode($request->getContent());

        if (isset($data->algorithm_hash) && !empty($data->algorithm_hash) && isset($data->error) && !empty($data->error)) {

            $algorithmVersion = $em->getRepository(AlgorithmVersion::class)->findOneBy(["hash" => $data->algorithm_hash]);

            if ($algorithmVersion) {
                $algorithmVersion->setStatus(AlgorithmVersion::STATUS_ERROR);
                $algorithmVersion->setLog($data->error);
                $em->flush();
                return new Response("true", Response::HTTP_OK);
            } else {
                return new Response("Bad hash", Response::HTTP_BAD_REQUEST);
            }
        } else {
            return new Response("Bad data", Response::HTTP_BAD_REQUEST);
        }
    }

}
