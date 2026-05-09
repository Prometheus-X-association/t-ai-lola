<?php

namespace App\Controller;

use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\Routing\Annotation\Route;
use Symfony\Component\Security\Http\Authentication\AuthenticationUtils;
use Symfony\Component\Security\Core\Encoder\UserPasswordEncoderInterface;
use Symfony\Component\Security\Guard\GuardAuthenticatorHandler;
use Symfony\Component\HttpFoundation\Request;
use App\Form\RegistrationFormType;
use App\Security\LoginFormAuthenticator;
use App\Entity\User;

class SecurityController extends AbstractController {

    /**
     * @Route("/login", name="app_login")
     */
    public function login(AuthenticationUtils $authenticationUtils): Response
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
                    'termsOfUse' => $this->getDoctrine()->getManager()->getRepository(\App\Entity\TermsOfUse::class)->findOneBy(["active" => true]),
        ]);
    }

    /**
     * @Route("/logout", name="app_logout")
     */
    public function logout()
    {
        throw new \LogicException('This method can be blank - it will be intercepted by the logout key on your firewall.');
    }

    /**
     * @Route("/terms", name="app_terms_update")
     */
    public function termsUpdate()
    {
        $this->getUser()->setTermsOfUse(true);
        $this->getDoctrine()->getManager()->flush();
        
        return $this->redirectToRoute("dashboard_accueil");
    }

    /**
     * @Route("/", name="homepage")
     */
    public function register(Request $request, UserPasswordEncoderInterface $passwordEncoder, GuardAuthenticatorHandler $guardHandler, LoginFormAuthenticator $authenticator): Response
    {
        $user = new User();
        $form = $this->createForm(RegistrationFormType::class, $user);
        $form->handleRequest($request);
        $entityManager = $this->getDoctrine()->getManager();

        if ($form->isSubmitted() && $form->isValid()) {
            // encode the plain password
            $user->setPassword(
                    $passwordEncoder->encodePassword(
                            $user,
                            $form->get('plainPassword')->getData()
                    )
            );

            $entityManager->persist($user);
            $entityManager->flush();

            // TODO : notification email

            return $guardHandler->authenticateUserAndHandleSuccess(
                            $user,
                            $request,
                            $authenticator,
                            'main' // firewall name in security.yaml
            );
        }

        return $this->render('public/accueil.html.twig', [
                    'form' => $form->createView(),
                    'formHasError' => $form->isSubmitted() && !$form->isValid() ? "1" : "0",
                    'termsOfUse' => $entityManager->getRepository(\App\Entity\TermsOfUse::class)->findOneBy(["active" => true]),
        ]);
    }

    /**
     * @Route("/account", name="account")
     */
    public function account(Request $request, UserPasswordEncoderInterface $passwordEncoder, GuardAuthenticatorHandler $guardHandler, LoginFormAuthenticator $authenticator): Response
    {
        $user = $this->getUser();
        $form = $this->createForm(RegistrationFormType::class, $user);
        $form->handleRequest($request);
        $entityManager = $this->getDoctrine()->getManager();

        if ($form->isSubmitted() && $form->isValid()) {
            // encode the plain password
            $user->setPassword(
                    $passwordEncoder->encodePassword(
                            $user,
                            $form->get('plainPassword')->getData()
                    )
            );

            $entityManager->persist($user);
            $entityManager->flush();

            // TODO : notification email

            return $guardHandler->authenticateUserAndHandleSuccess(
                            $user,
                            $request,
                            $authenticator,
                            'main' // firewall name in security.yaml
            );
        }

        return $this->render('public/account.html.twig', [
                    'form' => $form->createView(),
                    'termsOfUse' => $entityManager->getRepository(\App\Entity\TermsOfUse::class)->findOneBy(["active" => true]),
        ]);
    }

}
