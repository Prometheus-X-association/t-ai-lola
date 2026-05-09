<?php

namespace App\Repository;

use App\Entity\RunLogs;
use Doctrine\Bundle\DoctrineBundle\Repository\ServiceEntityRepository;
use Doctrine\Persistence\ManagerRegistry;

/**
 * @method RunLogs|null find($id, $lockMode = null, $lockVersion = null)
 * @method RunLogs|null findOneBy(array $criteria, array $orderBy = null)
 * @method RunLogs[]    findAll()
 * @method RunLogs[]    findBy(array $criteria, array $orderBy = null, $limit = null, $offset = null)
 */
class RunLogsRepository extends ServiceEntityRepository
{
    public function __construct(ManagerRegistry $registry)
    {
        parent::__construct($registry, RunLogs::class);
    }

    // /**
    //  * @return RunLogs[] Returns an array of RunLogs objects
    //  */
    /*
    public function findByExampleField($value)
    {
        return $this->createQueryBuilder('r')
            ->andWhere('r.exampleField = :val')
            ->setParameter('val', $value)
            ->orderBy('r.id', 'ASC')
            ->setMaxResults(10)
            ->getQuery()
            ->getResult()
        ;
    }
    */

    /*
    public function findOneBySomeField($value): ?RunLogs
    {
        return $this->createQueryBuilder('r')
            ->andWhere('r.exampleField = :val')
            ->setParameter('val', $value)
            ->getQuery()
            ->getOneOrNullResult()
        ;
    }
    */
}
