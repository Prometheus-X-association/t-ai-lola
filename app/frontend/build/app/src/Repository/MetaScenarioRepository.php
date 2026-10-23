<?php

namespace App\Repository;

use App\Entity\MetaScenario;
use Doctrine\Bundle\DoctrineBundle\Repository\ServiceEntityRepository;
use Doctrine\Persistence\ManagerRegistry;

/**
 * @method MetaScenario|null find($id, $lockMode = null, $lockVersion = null)
 * @method MetaScenario|null findOneBy(array $criteria, array $orderBy = null)
 * @method MetaScenario[]    findAll()
 * @method MetaScenario[]    findBy(array $criteria, array $orderBy = null, $limit = null, $offset = null)
 */
class MetaScenarioRepository extends ServiceEntityRepository
{
    public function __construct(ManagerRegistry $registry)
    {
        parent::__construct($registry, MetaScenario::class);
    }


    /*
    public function findOneBySomeField($value): ?MetaScenario
    {
        return $this->createQueryBuilder('s')
            ->andWhere('s.exampleField = :val')
            ->setParameter('val', $value)
            ->getQuery()
            ->getOneOrNullResult()
        ;
    }
    */
}
