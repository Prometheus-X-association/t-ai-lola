<?php

namespace App\Repository;

use App\Entity\Algorithm;
use Doctrine\Bundle\DoctrineBundle\Repository\ServiceEntityRepository;
use Doctrine\Persistence\ManagerRegistry;

/**
 * @method Algorithm|null find($id, $lockMode = null, $lockVersion = null)
 * @method Algorithm|null findOneBy(array $criteria, array $orderBy = null)
 * @method Algorithm[]    findAll()
 * @method Algorithm[]    findBy(array $criteria, array $orderBy = null, $limit = null, $offset = null)
 */
class AlgorithmRepository extends ServiceEntityRepository
{
    public function __construct(ManagerRegistry $registry)
    {
        parent::__construct($registry, Algorithm::class);
    }


    /*
    public function findOneBySomeField($value): ?Algorithm
    {
        return $this->createQueryBuilder('a')
            ->andWhere('a.exampleField = :val')
            ->setParameter('val', $value)
            ->getQuery()
            ->getOneOrNullResult()
        ;
    }
    */
}
