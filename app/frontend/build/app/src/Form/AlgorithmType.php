<?php

namespace App\Form;

use App\Entity\Algorithm;
use Symfony\Component\Form\AbstractType;
use Symfony\Component\Form\FormBuilderInterface;
use Symfony\Component\OptionsResolver\OptionsResolver;

class AlgorithmType extends AbstractType
{
    public function buildForm(FormBuilderInterface $builder, array $options)
    {
        $builder
            ->add('name')
            ->add('description', \Symfony\Component\Form\Extension\Core\Type\TextareaType::class, [
                'required' => false,
            ])
            ->add('urlRepository', \Symfony\Component\Form\Extension\Core\Type\TextType::class, [
                'required' => true,
            ])
            ->add('isPublic')
        ;
    }

    public function configureOptions(OptionsResolver $resolver)
    {
        $resolver->setDefaults([
            'data_class' => Algorithm::class,
        ]);
    }
}
