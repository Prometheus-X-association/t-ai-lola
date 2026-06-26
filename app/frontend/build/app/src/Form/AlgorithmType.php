<?php

namespace App\Form;

use App\Entity\Algorithm;
use Symfony\Component\Form\AbstractType;
use Symfony\Component\Form\FormBuilderInterface;
use Symfony\Component\OptionsResolver\OptionsResolver;
use Symfony\Component\Form\Extension\Core\Type\ChoiceType;

class AlgorithmType extends AbstractType
{
    public function buildForm(FormBuilderInterface $builder, array $options): void
    {
        $builder
            ->add('name', null, [
                'label' => 'dashboard.algorithm.form.title',
            ])
            ->add('description', \Symfony\Component\Form\Extension\Core\Type\TextareaType::class, [
                'label' => 'dashboard.algorithm.form.description',    
                'required' => false,
            ])
            ->add('urlRepository', \Symfony\Component\Form\Extension\Core\Type\TextType::class, [
                'label' => 'dashboard.algorithm.form.repository_url',    
                'required' => true,
            ])
            ->add('isPublic', ChoiceType::class, [
                'label' => 'dashboard.algorithm.form.visibility',
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
            'data_class' => Algorithm::class,
        ]);
    }
}
