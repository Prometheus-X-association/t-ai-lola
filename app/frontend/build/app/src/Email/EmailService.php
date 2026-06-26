<?php

namespace App\Email;

use Symfony\Component\Mailer\MailerInterface;
use Symfony\Component\Mime\Email;
use Symfony\Contracts\Translation\TranslatorInterface;
use App\Entity\User;

class EmailService {

    /**
     * @var MailerInterface $mailer
     */
    protected $mailer;

    /**
     * @var TranslatorInterface $translator
     */
    protected $translator;

    /**
     * @var string $lolaTeamEmail
     */
    protected $lolaTeamEmail;

    /**
     * @param MailerInterface $mailer
     * @param TranslatorInterface $translator
     */
    public function __construct(MailerInterface $mailer, TranslatorInterface $translator)
    {
        $this->mailer = $mailer;
        $this->translator = $translator;
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
                ->subject($this->translator->trans('email.upgrade_accepted.subject'))
                ->html($this->translator->trans('email.upgrade_accepted.html'));

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
                ->subject($this->translator->trans('email.upgrade_denied.subject'))
                ->html($this->translator->trans('email.upgrade_denied.html'));

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
            ->subject($this->translator->trans('email.upgrade_request.subject'))
            ->html($this->translator->trans('email.upgrade_request.html', [
                'profile' => htmlspecialchars(User::getProfilFromRole($user->getUpgradeRequest()), ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8'),
                'firstname' => htmlspecialchars((string) $user->getFirstname(), ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8'),
                'lastname' => htmlspecialchars((string) $user->getLastname(), ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8'),
                'email' => htmlspecialchars((string) $user->getEmail(), ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8'),
            ]));

        $this->mailer->send($email);
    }

}
