<?php

namespace App\Api;

use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\Routing\Annotation\Route;
use OpenApi\Annotations as OA;
use Nelmio\ApiDocBundle\Annotation\Model;
use App\Entity\ApiLog;
use FOS\RestBundle\Controller\Annotations\RequestParam;
use FOS\RestBundle\Controller\AbstractFOSRestController;
use Symfony\Component\HttpFoundation\Request;
use FOS\RestBundle\Controller\Annotations\Post;
use Doctrine\ORM\EntityManagerInterface;
use FOS\RestBundle\Controller\Annotations as Rest;

class LolapiController extends AbstractFOSRestController {

    /**
     * Insert into database a log record from Lolapy
     * @Post("/log")
     * @OA\Response(response=201, description="Serialized ApiLog object"),
     * @OA\Response(response=400, description="Data sent"),
     * @RequestParam(
     *      name="type",
     *      description="Type of the log record",
     *      nullable=true
     * )
     * @RequestParam(
     *      name="message",
     *      description="Message of the log record",
     *      nullable=true
     * )
     * @RequestParam(
     *      name="details",
     *      description="Details (optionnal)",
     *      nullable=false
     * )
     * @OA\Tag(name="Lolapy Logs")
     */
    public function log(Request $request, EntityManagerInterface $em): Response
    {
        $serializer = $this->container->get('serializer');
        $data = json_decode($request->getContent());
        
        if (isset($data->type) && !empty($data->type) && $data->message && !empty($data->message)) {
            $apiLog = new ApiLog();
            $apiLog->setDatetime(new \Datetime());
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
