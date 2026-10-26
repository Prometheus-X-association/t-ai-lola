<?php

namespace App\Repository;

use App\Entity\TermsOfUse;
use Doctrine\Bundle\DoctrineBundle\Repository\ServiceEntityRepository;
use Doctrine\Persistence\ManagerRegistry;

/**
 * @method TermsOfUse|null find($id, $lockMode = null, $lockVersion = null)
 * @method TermsOfUse|null findOneBy(array $criteria, array $orderBy = null)
 * @method TermsOfUse[]    findAll()
 * @method TermsOfUse[]    findBy(array $criteria, array $orderBy = null, $limit = null, $offset = null)
 */
class TermsOfUseRepository extends ServiceEntityRepository
{
    public function __construct(ManagerRegistry $registry)
    {
        parent::__construct($registry, TermsOfUse::class);
    }

    /**
     * Set all terms of use to inactive
     * Used before a change of terms of use, only one can be active
     */
    public function updateAllInactive(): void
    {
        $qb = $this->createQueryBuilder('t')
                ->update(TermsOfUse::class, 't')
                ->set('t.active', '0')
                ->getQuery()
                ->execute();
    }


    /*
    public function findOneBySomeField($value): ?TermsOfUse
    {
        return $this->createQueryBuilder('t')
            ->andWhere('t.exampleField = :val')
            ->setParameter('val', $value)
            ->getQuery()
            ->getOneOrNullResult()
        ;
    }
    */
}
