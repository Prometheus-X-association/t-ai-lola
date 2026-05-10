<?php

namespace App\DataFixtures;

use Doctrine\Bundle\FixturesBundle\Fixture;
use Doctrine\Persistence\ObjectManager;
use Symfony\Component\PasswordHasher\Hasher\UserPasswordHasherInterface;
use Doctrine\Bundle\FixturesBundle\FixtureGroupInterface;
use App\Entity\User;
use App\Entity\TermsOfUse;

class ProdFixtures extends Fixture implements FixtureGroupInterface {

    private UserPasswordHasherInterface $passwordHasher;

    public function __construct(UserPasswordHasherInterface $passwordHasher)
    {
        $this->passwordHasher = $passwordHasher;
    }

    public static function getGroups(): array
    {
        return ['prod'];
    }

    public function load(ObjectManager $manager): void
    {
        $user = new User();
        $user->setEmail("sisr@lola.fr");
        $user->setRoles(['ROLE_ADMIN_SISR']);
        $user->setFirstname("Usertest");
        $user->setLastname("RoleSisr");
        $user->setCreatedAt(new \DateTime());
        $user->setActive(true);
        $user->setPassword($this->passwordHasher->hashPassword(
                        $user,
                        'azerty'
        ));
        $manager->persist($user);
        $manager->flush();
        
                
        $terms = new TermsOfUse();
        $terms->setCreatedAt(new \DateTime());
        $terms->setCreatedBy($user);
        $terms->setActive();
        $terms->setDescription("Terms of use");
                                
        $manager->persist($terms);
        $manager->flush();
    }

}
