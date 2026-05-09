<?php

namespace App\Security;

use App\Entity\User;
use App\Exception\AccountDeletedException;
use Symfony\Component\Security\Core\Exception\AccountExpiredException;
use Symfony\Component\Security\Core\Exception\CustomUserMessageAuthenticationException;
use Symfony\Component\Security\Core\User\UserCheckerInterface;
use Symfony\Component\Security\Core\User\UserInterface;
use Doctrine\ORM\EntityManagerInterface;

class UserChecker implements UserCheckerInterface {

    private $userManager;

    public function __construct(EntityManagerInterface $userManager)
    {
        $this->userManager = $userManager;
    }

    public function checkPreAuth(UserInterface $user)
    {
        if (!$user instanceof User) {
            return;
        }
        
        if (!$user->isActive()) {
            throw new CustomUserMessageAuthenticationException("Votre compte est inactif.");
        }
    }

    public function checkPostAuth(UserInterface $user)
    {
        if (!$user instanceof User) {
            return;
        }
        $user->setLastLoginAt(new \DateTime());
        $this->userManager->persist($user);
        $this->userManager->flush();
    }

}
