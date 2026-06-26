<?php

namespace App\Form;

use App\Entity\MetaScenario;
use Symfony\Component\Form\AbstractType;
use Symfony\Component\Form\FormBuilderInterface;
use Symfony\Component\OptionsResolver\OptionsResolver;
use Symfony\Component\Form\Extension\Core\Type\ChoiceType;
use Symfony\Component\Form\Extension\Core\Type\TextType;

class MetaScenarioType extends AbstractType
{
    public function buildForm(FormBuilderInterface $builder, array $options): void
    {
        $builder
            ->add('name', null, [
                'label' => 'dashboard.metascenario.form.nom',
            ])
            ->add('description', \Symfony\Component\Form\Extension\Core\Type\TextareaType::class, [
                'label' => 'dashboard.metascenario.form.description',    
                'required' => false,
            ])
            ->add('urlRepository', TextType::class, [
                'label' => 'dashboard.metascenario.form.repo_git',
                'required' => true,
            ])
            ->add('isPublic', ChoiceType::class, [
                'label' => 'dashboard.metascenario.form.visibility',
                'choices' => [
                    'dashboard.common.yes' => true,
                    'dashboard.common.no' => false,
                ],
                'expanded' => true,
                'multiple' => false,
                'required' => true,
            ])
        ;
    }

    public function configureOptions(OptionsResolver $resolver): void
    {
        $resolver->setDefaults([
            'data_class' => MetaScenario::class,
        ]);
    }
}
