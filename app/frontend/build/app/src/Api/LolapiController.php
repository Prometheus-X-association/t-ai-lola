<?php

namespace App\Api;

use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\Routing\Attribute\Route;
use OpenApi\Attributes as OA;
use App\Entity\ApiLog;
use FOS\RestBundle\Controller\AbstractFOSRestController;
use Symfony\Component\HttpFoundation\Request;
use Doctrine\ORM\EntityManagerInterface;

#[Route('/lolapi')]
class LolapiController extends AbstractFOSRestController {

    /**
     * Insert into database a log record from Lolapy
     */
    #[OA\RequestBody(
        required: true,
        description: 'Log payload sent by Lolapy.',
        content: new OA\JsonContent(
            required: ['type', 'message'],
            properties: [
                new OA\Property(property: 'type', type: 'string', description: 'Log type.', example: 'INFO'),
                new OA\Property(property: 'message', type: 'string', description: 'Log message.', example: 'Dataset import started.'),
                new OA\Property(property: 'details', type: 'string', nullable: true, description: 'Optional log details.', example: 'dataset=D6da92778e1794c59f3025010ca8612290cbf1e42'),
            ],
        ),
    )]
    #[OA\Response(
        response: 201,
        description: 'Serialized ApiLog object.',
        content: new OA\JsonContent(
            properties: [
                new OA\Property(property: 'id', type: 'integer', example: 42),
                new OA\Property(property: 'datetime', type: 'string', format: 'date-time', example: '2026-06-26T10:15:28+02:00'),
                new OA\Property(property: 'type', type: 'string', example: 'INFO'),
                new OA\Property(property: 'message', type: 'string', example: 'Dataset import started.'),
                new OA\Property(property: 'details', type: 'string', nullable: true, example: 'dataset=D6da92778e1794c59f3025010ca8612290cbf1e42'),
            ],
        ),
    )]
    #[OA\Response(
        response: 400,
        description: 'Missing type or message. The submitted payload is returned in the response body.',
        content: new OA\JsonContent(type: 'object', example: ['details' => 'missing type/message']),
    )]
    #[OA\Tag(name: 'Lolapy Logs')]
    #[Route('/log', methods: ['POST'])]
    public function log(Request $request, EntityManagerInterface $em): Response
    {
        $serializer = $this->container->get('serializer');
        $data = json_decode($request->getContent());
        
        if (isset($data->type) && !empty($data->type) && isset($data->message) && !empty($data->message)) {
            $apiLog = new ApiLog();
            $apiLog->setDatetime(new \DateTime());
            $apiLog->setType($data->type);
            $apiLog->setMessage($data->message);
            (!isset($data->details)) ?: $apiLog->setDetails($data->details);
            $em->persist($apiLog);
            $em->flush();

            return new Response($serializer->serialize($apiLog, 'json'), Response::HTTP_CREATED);
        } else {
            return new Response($request->getContent(), Response::HTTP_BAD_REQUEST);
        }
    }

}
