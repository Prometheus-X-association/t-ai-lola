<?php

namespace App\Repository;

use App\Entity\AlgorithmVersion;
use App\Entity\User;
use Doctrine\Bundle\DoctrineBundle\Repository\ServiceEntityRepository;
use Doctrine\ORM\QueryBuilder;
use Doctrine\ORM\OptimisticLockException;
use Doctrine\ORM\ORMException;
use Doctrine\Persistence\ManagerRegistry;

/**
 * @method AlgorithmVersion|null find($id, $lockMode = null, $lockVersion = null)
 * @method AlgorithmVersion|null findOneBy(array $criteria, array $orderBy = null)
 * @method AlgorithmVersion[]    findAll()
 * @method AlgorithmVersion[]    findBy(array $criteria, array $orderBy = null, $limit = null, $offset = null)
 */
class AlgorithmVersionRepository extends ServiceEntityRepository
{
    public function __construct(ManagerRegistry $registry)
    {
        parent::__construct($registry, AlgorithmVersion::class);
    }

    /**
     * @throws ORMException
     * @throws OptimisticLockException
     */
    public function add(AlgorithmVersion $entity, bool $flush = true): void
    {
        $this->_em->persist($entity);
        if ($flush) {
            $this->_em->flush();
        }
    }

    /**
     * @throws ORMException
     * @throws OptimisticLockException
     */
    public function remove(AlgorithmVersion $entity, bool $flush = true): void
    {
        $this->_em->remove($entity);
        if ($flush) {
            $this->_em->flush();
        }
    }

    /**
     * @return AlgorithmVersion[]
     */
    public function findAvailableForUser(User $user): array
    {
        return $this->createAvailableForUserQueryBuilder($user)
            ->orderBy('algorithm.name', 'ASC')
            ->addOrderBy('algorithmVersion.name', 'ASC')
            ->getQuery()
            ->getResult();
    }

    public function findOneAvailableForUserByHash(string $hash, User $user): ?AlgorithmVersion
    {
        return $this->createAvailableForUserQueryBuilder($user)
            ->andWhere('algorithmVersion.hash = :hash')
            ->setParameter('hash', $hash)
            ->getQuery()
            ->getOneOrNullResult();
    }

    private function createAvailableForUserQueryBuilder(User $user): QueryBuilder
    {
        $queryBuilder = $this->createQueryBuilder('algorithmVersion')
            ->innerJoin('algorithmVersion.algorithm', 'algorithm')
            ->andWhere('algorithmVersion.status = :status')
            ->setParameter('status', AlgorithmVersion::STATUS_AVAILABLE);

        if (!$user->isAdmin()) {
            $queryBuilder
                ->andWhere('algorithm.isPublic = true OR algorithm.createdBy = :user')
                ->setParameter('user', $user);
        }

        return $queryBuilder;
    }

    // /**
    //  * @return AlgorithmVersion[] Returns an array of AlgorithmVersion objects
    //  */
    /*
    public function findByExampleField($value)
    {
        return $this->createQueryBuilder('a')
            ->andWhere('a.exampleField = :val')
            ->setParameter('val', $value)
            ->orderBy('a.id', 'ASC')
            ->setMaxResults(10)
            ->getQuery()
            ->getResult()
        ;
    }
    */

    /*
    public function findOneBySomeField($value): ?AlgorithmVersion
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
