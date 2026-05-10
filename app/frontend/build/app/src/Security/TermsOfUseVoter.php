<?php

namespace App\Security;

use Symfony\Component\Security\Core\Authentication\Token\TokenInterface;
use Symfony\Component\Security\Core\Authorization\Voter\Voter;
use Symfony\Component\Security\Core\Authorization\Voter\Vote;

class TermsOfUseVoter extends Voter {

    protected function supports(string $attribute, mixed $subject): bool
    {
        // check with voter only the authorization to access to the dashboard 
        return $attribute === "IS_AUTHENTICATED_FULLY";
    }

    protected function voteOnAttribute(string $attribute, mixed $subject, TokenInterface $token, ?Vote $vote = null): bool
    {
        /* @var $user \App\Entity\User */
        $user = $token->getUser();
        
        if (!$user instanceof \App\Entity\User) {
            return false;
        }
        if( in_array("ROLE_ADMIN_SISR", $user->getRoles()) || in_array("ROLE_ADMIN", $user->getRoles()) ) {
            return true;
        }
        return $user->getTermsOfUse();
    }

}
