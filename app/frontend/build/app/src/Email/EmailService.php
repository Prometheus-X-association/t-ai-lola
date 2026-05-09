<?php

namespace App\Email;

use Symfony\Component\Mailer\MailerInterface;
use Symfony\Component\Mime\Email;
use App\Entity\User;

class EmailService {

    /**
     * @var MailerInterface $mailer
     */
    protected $mailer;

    /**
     * @param MailerInterface $mailer
     */
    public function __construct(MailerInterface $mailer)
    {
        $this->mailer = $mailer;
        $this->lolaTeamEmail = $_ENV["LOLA_TEAM_EMAIL"];
    }

    /**
     * Notify to user the account upgrade is accepted
     *
     * @param App\Entity\User $user
     */
    public function upgradeAccepted(User $user): void
    {
        $email = (new Email())
                ->from($this->lolaTeamEmail)
                ->to($user->getEmail())
                ->subject("LOLA : votre demande de mise à jour")
                ->html("<p>La demande de mise à niveau de votre compte LOLA a été acceptée.</p>");

        $this->mailer->send($email);
    }

    /**
     * Notify to user the account upgrade is denied
     *
     * @param App\Entity\User $user
     */
    public function upgradeDenied(User $user): void
    {
        $email = (new Email())
                ->from($this->lolaTeamEmail)
                ->to($user->getEmail())
                ->subject("LOLA : votre demande de mise à jour")
                ->html("<p>La demande de mise à niveau de votre compte LOLA a été refusée.</p>");

        $this->mailer->send($email);
    }

    /**
     * Notify to Lola team the upgrade request of the user
     *
     * @param App\Entity\User $user
     */
    public function upgradeRequest(User $user): void
    {
        $email = (new Email())
                ->from($this->lolaTeamEmail)
                ->to($this->lolaTeamEmail)
                ->subject("LOLA : Demande d'upgrade")
                ->html("<p>Demande d'upgrade vers le profil <strong>" . User::getProfilFromRole($user->getUpgradeRequest()) . "</strong> "
                . "de " . $user->getFirstname() . " " . $user->getLastname() . " (" . $user->getEmail() . ").");

        $this->mailer->send($email);
    }

}
