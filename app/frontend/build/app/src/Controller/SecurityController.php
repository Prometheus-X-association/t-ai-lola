<?php

namespace App\Controller;

use App\Entity\TermsOfUse;
use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\Routing\Attribute\Route;
use Symfony\Component\Security\Http\Authentication\AuthenticationUtils;
use Symfony\Component\HttpFoundation\Request;
use App\Form\RegistrationFormType;
use App\Security\LoginFormAuthenticator;
use App\Entity\User;
use Doctrine\ORM\EntityManagerInterface;
use Symfony\Component\PasswordHasher\Hasher\UserPasswordHasherInterface;
use Symfony\Component\Security\Http\Authentication\UserAuthenticatorInterface;

class SecurityController extends AbstractController {

    #[Route('/login', name: 'app_login')]
    public function login(AuthenticationUtils $authenticationUtils, EntityManagerInterface $entityManager): Response
    {
        // if ($this->getUser()) {
        //     return $this->redirectToRoute('target_path');
        // }
        // get the login error if there is one
        $error = $authenticationUtils->getLastAuthenticationError();
        // last username entered by the user
        $lastUsername = $authenticationUtils->getLastUsername();

        return $this->render('public/accueil.html.twig', [
                    'last_username' => $lastUsername,
                    'error' => $error,
                    'form' => $this->createForm(RegistrationFormType::class, new User())->createView(),
                    'termsOfUse' => $entityManager->getRepository(TermsOfUse::class)->findOneBy(["active" => true]),
        ]);
    }

    #[Route('/logout', name: 'app_logout')]
    public function logout(): void
    {
        throw new \LogicException('This method can be blank - it will be intercepted by the logout key on your firewall.');
    }

    #[Route('/terms', name: 'app_terms_update')]
    public function termsUpdate(EntityManagerInterface $entityManager): Response
    {
        /** @var User $user */
        $user = $this->getUser();
        $user->setTermsOfUse(true);
        $entityManager->flush();
        
        return $this->redirectToRoute("dashboard_accueil");
    }

    #[Route('/', name: 'homepage')]
    public function register(Request $request, UserPasswordHasherInterface $passwordHasher, UserAuthenticatorInterface $userAuthenticator, LoginFormAuthenticator $authenticator, EntityManagerInterface $entityManager): Response
    {
        $user = new User();
        $form = $this->createForm(RegistrationFormType::class, $user);
        $form->handleRequest($request);

        if ($form->isSubmitted() && $form->isValid()) {
            // encode the plain password
            $user->setPassword(
                    $passwordHasher->hashPassword(
                            $user,
                            $form->get('plainPassword')->getData()
                    )
            );

            $entityManager->persist($user);
            $entityManager->flush();

            // TODO : notification email

            return $userAuthenticator->authenticateUser(
                            $user,
                            $authenticator,
                            $request,
            );
        }

        return $this->render('public/accueil.html.twig', [
                    'form' => $form->createView(),
                    'formHasError' => $form->isSubmitted() && !$form->isValid() ? "1" : "0",
                    'termsOfUse' => $entityManager->getRepository(TermsOfUse::class)->findOneBy(["active" => true]),
        ]);
    }

    #[Route('/account', name: 'account')]
    public function account(Request $request, UserPasswordHasherInterface $passwordHasher, UserAuthenticatorInterface $userAuthenticator, LoginFormAuthenticator $authenticator, EntityManagerInterface $entityManager): Response
    {
        /** @var User $user */
        $user = $this->getUser();
        $form = $this->createForm(RegistrationFormType::class, $user);
        $form->handleRequest($request);

        if ($form->isSubmitted() && $form->isValid()) {
            // encode the plain password
            $plainPassword = $form->get('plainPassword')->getData();
            if (!empty($plainPassword)) {
                $user->setPassword(
                        $passwordHasher->hashPassword(
                                $user,
                                $plainPassword
                        )
                );
            }

            $entityManager->persist($user);
            $entityManager->flush();

            // TODO : notification email

            return $userAuthenticator->authenticateUser(
                            $user,
                            $authenticator,
                            $request,
            );
        }

        return $this->render('public/account.html.twig', [
                    'form' => $form->createView(),
                    'termsOfUse' => $entityManager->getRepository(TermsOfUse::class)->findOneBy(["active" => true]),
        ]);
    }

}
