<?php

namespace App\Controller;

use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Component\HttpFoundation\RedirectResponse;
use Symfony\Component\HttpFoundation\Request;
use Symfony\Component\Routing\Attribute\Route;

class LanguageController extends AbstractController {

    private const SUPPORTED_LOCALES = ['en', 'fr'];

    #[Route('/language/{locale}', name: 'app_language_switch', requirements: ['locale' => 'en|fr'])]
    public function switch(string $locale, Request $request): RedirectResponse
    {
        if (!in_array($locale, self::SUPPORTED_LOCALES, true)) {
            $locale = 'en';
        }

        $request->getSession()->set('_locale', $locale);

        $referer = $request->headers->get('referer');
        if ($referer && str_starts_with($referer, $request->getSchemeAndHttpHost())) {
            return new RedirectResponse($referer);
        }

        return $this->redirectToRoute('homepage');
    }
}
