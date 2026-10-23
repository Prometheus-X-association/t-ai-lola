<?php

namespace App\Repository;

use App\Entity\DatasetLogs;
use Doctrine\Bundle\DoctrineBundle\Repository\ServiceEntityRepository;
use Doctrine\Persistence\ManagerRegistry;

/**
 * @method DatasetLogs|null find($id, $lockMode = null, $lockVersion = null)
 * @method DatasetLogs|null findOneBy(array $criteria, array $orderBy = null)
 * @method DatasetLogs[]    findAll()
 * @method DatasetLogs[]    findBy(array $criteria, array $orderBy = null, $limit = null, $offset = null)
 */
class DatasetLogsRepository extends ServiceEntityRepository
{
    public function __construct(ManagerRegistry $registry)
    {
        parent::__construct($registry, DatasetLogs::class);
    }


    /*
    public function findOneBySomeField($value): ?DatasetLogs
    {
        return $this->createQueryBuilder('d')
            ->andWhere('d.exampleField = :val')
            ->setParameter('val', $value)
            ->getQuery()
            ->getOneOrNullResult()
        ;
    }
    */
}
