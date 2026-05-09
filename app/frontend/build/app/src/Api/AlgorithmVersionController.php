<?php

namespace App\Api;

use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\HttpFoundation\Request;
use Symfony\Component\Routing\Annotation\Route;
use Doctrine\ORM\EntityManagerInterface;
use OpenApi\Annotations as OA;
use FOS\RestBundle\Controller\Annotations\Post;
use FOS\RestBundle\Controller\Annotations\RequestParam;
use Nelmio\ApiDocBundle\Annotation\Model;
use App\Entity\ApiLog;
use App\Entity\AlgorithmVersion;

/**
 * @route("/algorithm")
 */
class AlgorithmVersionController extends AbstractController {

    /**
     * Notify when a version algorithm is successfully added
     *
     * @Route("/{hash}/complete", methods={"GET"})
     * @OA\Response(
     *     response=200,
     *     description="",
     * )
     * @OA\Parameter(
     *     name="versionAlgorithm hash",
     *     in="query",
     *     description="The hash of the versionAlgorithm",
     *     @OA\Schema(type="string")
     * )
     * @OA\Tag(name="Algorithm")
     */
    public function complete(AlgorithmVersion $algorithmVersion, EntityManagerInterface $em): Response
    {
        $algorithmVersion->setStatus(AlgorithmVersion::STATUS_AVAILABLE);
        $em->flush();
        return new Response(null, Response::HTTP_OK);
    }

    /**
     * Notify when adding the version algorithm fails
     *
     * @Post("/error")
     * @OA\Response(response=200, description=""),
     * @OA\Response(response=400, description="The hash of the algorithm version is invalid"),
     * @RequestParam(
     *      name="algorithm_hash",
     *      description="The hash of the algorithm version",
     * )
     * @RequestParam(
     *      name="error",
     *      description="The error",
     * )
     * @OA\Tag(name="Algorithm")
     */
    public function error(Request $request, EntityManagerInterface $em): Response
    {
        $serializer = $this->container->get('serializer');
        $data = json_decode($request->getContent());

        if (isset($data->algorithm_hash) && !empty($data->algorithm_hash) && $data->error && !empty($data->error)) {

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
