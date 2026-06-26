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

    public function buildForm(FormBuilderInterface $builder, array $options): void
    {
        $builder
                ->add('firstname', TextType::class, [
                    'label' => 'public.form.firstname',
                    'constraints' => [
                        new NotBlank(message: 'public.form.firstname_required'),
                    ],
                ])
                ->add('lastname', TextType::class, [
                    'label' => 'public.form.lastname',
                    'constraints' => [
                        new NotBlank(message: 'public.form.lastname_required'),
                    ],
                ])
                ->add('agreeTerms', CheckboxType::class, [
                    'label' => 'public.form.agree_terms',
                    'mapped' => false,
                    'constraints' => [
                        new IsTrue(message: 'public.form.agree_terms_required'),
                    ],
                ])
                ->add('plainPassword', PasswordType::class, [
                    'mapped' => false,
                    'label' => 'public.form.password',
                    'constraints' => [
                        new NotBlank(message: 'public.form.password_required'),
                        new Length(
                            min: 6,
                            minMessage: 'public.form.password_min_length',
                            max: 50
                        ),
                    ],
                ])
                ->addEventListener(
                    FormEvents::PRE_SET_DATA,
                    [$this, 'onPreSetData']
                )
        ;
    }

    public function onPreSetData(FormEvent $event): void
    {
        $form = $event->getForm();
        $user = $event->getData();

        // check if the object is "new"
        if (!$user || !$user->getId()) {
            $form->add('captcha', CaptchaType::class, [
                'label' => 'public.form.captcha',
            ]);

            $form->add('email', EmailType::class, [
                'label' => 'public.form.email',
                'constraints' => [
                    new NotBlank(message: 'public.form.email_required'),
                ],
            ]);
        } else {
            $form->add('email', EmailType::class, [
                'disabled' => true,
                'label' => 'public.form.email',
            ]);
        }
    }

    public function configureOptions(OptionsResolver $resolver): void
    {
        $resolver->setDefaults([
            'data_class' => User::class,
        ]);
    }

}
