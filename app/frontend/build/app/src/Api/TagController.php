<?php

namespace App\Api;

use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\HttpFoundation\Request;
use Symfony\Component\Routing\Attribute\Route;
use Doctrine\ORM\EntityManagerInterface;
use OpenApi\Annotations as OA;
use FOS\RestBundle\Controller\Annotations\Post;
use FOS\RestBundle\Controller\Annotations\RequestParam;
use Nelmio\ApiDocBundle\Annotation\Model;
use App\Entity\Tag;

#[Route('/tag')]
class TagController extends AbstractController {

    /**
     * Notify when a tag is successfully added
     *
     * @OA\Response(
     *     response=200,
     *     description="",
     * )
     * @OA\Parameter(
     *     name="tag hash",
     *     in="query",
     *     description="The hash of the tag",
     *     @OA\Schema(type="string")
     * )
     * @OA\Tag(name="Tag")
     */
    #[Route('/{hash}/complete', methods: ['GET'])]
    public function complete(Tag $tag, EntityManagerInterface $em): Response
    {
        $tag->setStatus(Tag::STATUS_AVAILABLE);
        $em->flush();
        return new Response(null, Response::HTTP_OK);
    }

    /**
     * Notify when adding the tag fails
     *
     * @OA\Response(response=200, description=""),
     * @OA\Response(response=400, description="The hash of the tag is invalid"),
     * @RequestParam(
     *      name="tag",
     *      description="The hash of the tag",
     * )
     * @RequestParam(
     *      name="error",
     *      description="The error",
     * )
     * @OA\Tag(name="Tag")
     */
    #[Route('/error', methods: ['POST'])]
    public function error(Request $request, EntityManagerInterface $em): Response
    {
        $data = json_decode($request->getContent());

        if (isset($data->tag) && !empty($data->tag) && $data->error && !empty($data->error)) {

            $tag = $em->getRepository(Tag::class)->findOneBy(["hash" => $data->tag]);

            if ($tag) {
                $tag->setStatus(Tag::STATUS_ERROR);
                $tag->setLog($data->error);
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
