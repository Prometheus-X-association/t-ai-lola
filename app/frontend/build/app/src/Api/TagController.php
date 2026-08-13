<?php

namespace App\Api;

use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\HttpFoundation\Request;
use Symfony\Component\Routing\Attribute\Route;
use Doctrine\ORM\EntityManagerInterface;
use OpenApi\Attributes as OA;
use App\Entity\Tag;

#[Route('/tag')]
class TagController extends AbstractController {

    /**
     * Notify when a tag is successfully added
     */
    #[OA\Parameter(name: 'hash', in: 'path', required: true, description: 'Tag hash.', schema: new OA\Schema(type: 'string'), example: 'T8bdf038817f64473abe0e82aa339981e')]
    #[OA\Response(response: 200, description: 'Tag status updated to AVAILABLE.')]
    #[OA\Tag(name: 'Tag')]
    #[Route('/{hash}/complete', methods: ['GET'])]
    public function complete(Tag $tag, EntityManagerInterface $em): Response
    {
        $tag->setStatus(Tag::STATUS_AVAILABLE);
        $em->flush();
        return new Response(null, Response::HTTP_OK);
    }

    /**
     * Notify when adding the tag fails
     */
    #[OA\RequestBody(
        required: true,
        description: 'Failure details returned by Lolapy when a tag cannot be added.',
        content: new OA\JsonContent(
            required: ['tag', 'error'],
            properties: [
                new OA\Property(property: 'tag', type: 'string', description: 'Tag hash.', example: 'T8bdf038817f64473abe0e82aa339981e'),
                new OA\Property(property: 'error', type: 'string', description: 'Error message.', example: 'Tag archive cannot be extracted.'),
            ],
        ),
    )]
    #[OA\Response(
        response: 200,
        description: 'Tag status updated to ERROR.',
        content: new OA\JsonContent(type: 'string', example: 'true'),
    )]
    #[OA\Response(
        response: 400,
        description: 'Invalid hash or request body.',
        content: new OA\JsonContent(type: 'string', example: 'Bad hash'),
    )]
    #[OA\Tag(name: 'Tag')]
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
