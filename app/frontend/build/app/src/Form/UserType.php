<?php

namespace App\Form;

use App\Entity\User;
use Symfony\Component\Form\AbstractType;
use Symfony\Component\Form\Extension\Core\Type\CheckboxType;
use Symfony\Component\Form\Extension\Core\Type\PasswordType;
use Symfony\Component\Form\Extension\Core\Type\TextType;
use Symfony\Component\Form\Extension\Core\Type\EmailType;
use Symfony\Component\Form\FormBuilderInterface;
use Symfony\Component\OptionsResolver\OptionsResolver;
use Symfony\Component\Validator\Constraints\IsTrue;
use Symfony\Component\Validator\Constraints\Length;
use Symfony\Component\Validator\Constraints\NotBlank;
use Symfony\Component\Form\Extension\Core\Type\ChoiceType;

class UserType extends AbstractType {

    public function buildForm(FormBuilderInterface $builder, array $options)
    {
        $builder
                ->add('email', EmailType::class, [
                    'label' => 'Email',
                    'constraints' => [
                        new NotBlank(['message' => 'L\'email est requis.']),
                    ],
                ])
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
                ->add('roles', ChoiceType::class, [
                    "multiple" => true,
                    "choices" => array_flip(User::$listRoles)
                ])
        ;
    }

    public function configureOptions(OptionsResolver $resolver)
    {
        $resolver->setDefaults([
            'data_class' => User::class,
        ]);
    }

}
