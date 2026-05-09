<?php

namespace App\Form;

use App\Entity\User;
use Symfony\Component\Form\AbstractType;
use Symfony\Component\Form\FormEvent;
use Symfony\Component\Form\FormEvents;
use Symfony\Component\Form\Extension\Core\Type\CheckboxType;
use Symfony\Component\Form\Extension\Core\Type\PasswordType;
use Symfony\Component\Form\Extension\Core\Type\TextType;
use Symfony\Component\Form\Extension\Core\Type\EmailType;
use Symfony\Component\Form\FormBuilderInterface;
use Symfony\Component\OptionsResolver\OptionsResolver;
use Symfony\Component\Validator\Constraints\IsTrue;
use Symfony\Component\Validator\Constraints\Length;
use Symfony\Component\Validator\Constraints\NotBlank;
use Gregwar\CaptchaBundle\Type\CaptchaType;

class RegistrationFormType extends AbstractType {

    public function buildForm(FormBuilderInterface $builder, array $options)
    {
        $builder
                ->add('firstname', TextType::class, [
                    'label' => 'Prénom',
                    'constraints' => [
                        new NotBlank(['message' => 'Le prénom est requis.']),
                    ],
                ])
                ->add('lastname', TextType::class, [
                    'label' => 'Nom',
                    'constraints' => [
                        new NotBlank(['message' => 'Le nom est requis.']),
                    ],
                ])
                ->add('agreeTerms', CheckboxType::class, [
                    'label' => 'Condition d\'utilisation',
                    'mapped' => false,
                    'constraints' => [
                        new IsTrue([
                            'message' => 'Vous devez accepter les conditions.',
                                ]),
                    ],
                ])
                ->add('plainPassword', PasswordType::class, [
                    'mapped' => false,
                    'label' => 'Mot de passe',
                    'constraints' => [
                        new NotBlank([
                            'message' => 'Veuillez entrer un mot de passe',
                                ]),
                        new Length([
                            'min' => 6,
                            'minMessage' => 'Le mot de passe doit contenir au moins {{ limit }} caractères',
                            'max' => 50,
                                ]),
                    ],
                ])
                // add the login field only if we create a new account (not in edit mode)
                ->addEventListener(
                        FormEvents::PRE_SET_DATA,
                        array($this, 'onPreSetData')
                )
        ;
    }

    public function onPreSetData(FormEvent $event)
    {
        $form = $event->getForm();
        $user = $event->getData();

        // check if the object is "new"
        if (!$user || !$user->getId()) {
            $form->add('captcha', CaptchaType::class, [
                    'label' => 'Captcha'
                ]);
            $form->add('email', EmailType::class, [
                'label' => 'Email',
                'constraints' => [
                    new NotBlank(['message' => 'L\'email est requis.']),
                ],
            ]);
        } else {
            $form->add('email', null, [
                'disabled' => true,
                'label' => 'Email'
                    ]
            );
        }
    }

    public function configureOptions(OptionsResolver $resolver)
    {
        $resolver->setDefaults([
            'data_class' => User::class,
        ]);
    }

}
