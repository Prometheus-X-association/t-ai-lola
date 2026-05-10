<?php

namespace App\DataFixtures;

use Doctrine\Bundle\FixturesBundle\Fixture;
use Doctrine\Persistence\ObjectManager;
use Symfony\Component\PasswordHasher\Hasher\UserPasswordHasherInterface;
use Doctrine\Bundle\FixturesBundle\FixtureGroupInterface;
use App\Entity\User;
use App\Entity\Group;
use App\Entity\Output;
use App\Entity\MetaScenario;
use App\Entity\TermsOfUse;

class DevFixtures extends Fixture implements FixtureGroupInterface {

    private UserPasswordHasherInterface $passwordHasher;

    public function __construct(UserPasswordHasherInterface $passwordHasher)
    {
        $this->passwordHasher = $passwordHasher;
    }

    public static function getGroups(): array
    {
        return ['dev'];
    }

    public function load(ObjectManager $manager): void
    {
        $userSisr = new User();
        $userSisr->setEmail("sisr@lola.fr");
        $userSisr->setRoles(['ROLE_ADMIN_SISR']);
        $userSisr->setFirstname("Usertest");
        $userSisr->setLastname("RoleSisr");
        $userSisr->setCreatedAt(new \DateTime());
        $userSisr->setActive(true);
        $userSisr->setPassword($this->passwordHasher->hashPassword(
                        $userSisr,
                        'azerty'
        ));
        $manager->persist($userSisr);

        $user = new User();
        $user->setEmail("admin@lola.fr");
        $user->setRoles(['ROLE_ADMIN']);
        $user->setFirstname("Usertest");
        $user->setLastname("RoleAdmin");
        $user->setCreatedAt(new \DateTime());
        $user->setActive(true);
        $user->setPassword($this->passwordHasher->hashPassword(
                        $user,
                        'azerty'
        ));
        $manager->persist($user);

        $user1 = new User();
        $user1->setEmail("p1@lola.fr");
        $user1->setRoles(['ROLE_PROFIL_1']);
        $user1->setFirstname("Usertest");
        $user1->setLastname("RoleP1");
        $user1->setCreatedAt(new \DateTime());
        $user1->setActive(true);
        $user1->setPassword($this->passwordHasher->hashPassword(
                        $user1,
                        'azerty'
        ));
        $manager->persist($user1);

        $user2 = new User();
        $user2->setEmail("p2@lola.fr");
        $user2->setRoles(['ROLE_PROFIL_2']);
        $user2->setFirstname("Usertest");
        $user2->setLastname("RoleP2");
        $user2->setCreatedAt(new \DateTime());
        $user2->setActive(true);
        $user2->setPassword($this->passwordHasher->hashPassword(
                        $user2,
                        'azerty'
        ));
        $manager->persist($user2);

        $user3 = new User();
        $user3->setEmail("p3@lola.fr");
        $user3->setRoles(['ROLE_PROFIL_3']);
        $user3->setFirstname("Usertest");
        $user3->setLastname("RoleP3");
        $user3->setCreatedAt(new \DateTime());
        $user3->setActive(true);
        $user3->setPassword($this->passwordHasher->hashPassword(
                        $user3,
                        'azerty'
        ));
        $manager->persist($user3);

        $user4 = new User();
        $user4->setEmail("p4@lola.fr");
        $user4->setRoles(['ROLE_PROFIL_4']);
        $user4->setFirstname("Usertest");
        $user4->setLastname("RoleP4");
        $user4->setCreatedAt(new \DateTime());
        $user4->setActive(true);
        $user4->setPassword($this->passwordHasher->hashPassword(
                        $user4,
                        'azerty'
        ));
        $manager->persist($user4);

        $user5 = new User();
        $user5->setEmail("p5@lola.fr");
        $user5->setRoles(['ROLE_PROFIL_5']);
        $user5->setFirstname("Usertest");
        $user5->setLastname("RoleP5");
        $user5->setCreatedAt(new \DateTime());
        $user5->setActive(true);
        $user5->setPassword($this->passwordHasher->hashPassword(
                        $user5,
                        'azerty'
        ));
        $manager->persist($user5);

        $groupe = new Group();
        $groupe->setName("Groupe utilisateur A");
        $groupe->addUser($user2);
        $groupe->addUser($user3);
        $groupe->addUser($user4);
        $groupe->addUser($user5);
        $manager->persist($groupe);

        $groupe = new Group();
        $groupe->setName("Groupe 2");
        $groupe->addUser($user2);
        $groupe->addUser($user5);
        $manager->persist($groupe);

        $manager->flush();

        $metascenario = new MetaScenario();
        $metascenario->setName("Metascenario A");
        $metascenario->setDescription("Metascenario description A");
        $metascenario->setIsActive(true);
        $metascenario->setIsPublic(true);
        $metascenario->setUrlRepository("https://gitlab.inria.fr");
        $metascenario->setCreatedAt(new \DateTime());
        $metascenario->setCreatedBy($userSisr);

        $manager->persist($metascenario);
        $manager->flush();

        $terms = new TermsOfUse();
        $terms->setCreatedAt(new \DateTime());
        $terms->setCreatedBy($userSisr);
        $terms->setActive();
        $terms->setDescription("Terms of use");

        $manager->persist($terms);
        $manager->flush();

        // ---

        $output = new Output();
        $output->setName("Indicateur A1");
        $output->setIsActive(true);
        $manager->persist($output);

        $output2 = new Output();
        $output2->setName("Indicateur A2");
        $output2->setIsActive(true);
        $manager->persist($output2);

        $output3 = new Output();
        $output3->setName("Indicateur B");
        $output3->setIsActive(true);
        $manager->persist($output3);

        $output4 = new Output();
        $output4->setName("Indicateur CC");
        $output4->setIsActive(false);
        $manager->persist($output4);

        $manager->flush();

    }

}
