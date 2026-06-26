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

    public function buildForm(FormBuilderInterface $builder, array $options): void
    {
        $builder
                ->add('email', EmailType::class, [
                    'label' => 'dashboard.user.edit.email',
                    'constraints' => [
                        new NotBlank(message: 'dashboard.user.form.email_required'),
                    ],
                ])
                ->add('firstname', TextType::class, [
                    'label' => 'dashboard.user.edit.prenom',
                    'constraints' => [
                        new NotBlank(message: 'dashboard.user.form.firstname_required'),
                    ],
                ])
                ->add('lastname', TextType::class, [
                    'label' => 'dashboard.user.edit.nom',
                    'constraints' => [
                        new NotBlank(message: 'dashboard.user.form.lastname_required'),
                    ],
                ])
                ->add('roles', ChoiceType::class, [
                    'label' => 'dashboard.user.edit.liste_roles',
                    "multiple" => true,
                    "choices" => array_flip(User::$listRoles)
                ])
        ;
    }

    public function configureOptions(OptionsResolver $resolver): void
    {
        $resolver->setDefaults([
            'data_class' => User::class,
        ]);
    }

}
