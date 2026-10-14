<?php

namespace App\Form;

use App\Entity\Dataset;
use Symfony\Component\Form\AbstractType;
use Symfony\Component\Form\FormBuilderInterface;
use Symfony\Component\OptionsResolver\OptionsResolver;
use Symfony\Component\Form\Extension\Core\Type\FileType;

class DatasetType extends AbstractType
{
    public function buildForm(FormBuilderInterface $builder, array $options): void
    {
        $builder
            ->add('name', null, [
                'label' => 'dashboard.dataset.form.nom',
            ])
            ->add('description', \Symfony\Component\Form\Extension\Core\Type\TextareaType::class, [
                'label' => 'dashboard.dataset.form.description',    
                'required' => false,
            ])
            ->add('contract', \Symfony\Component\Form\Extension\Core\Type\TextType::class, [
                'label' => 'dashboard.dataset.form.contract',
                'required' => false,
                'attr' => [
                    'placeholder' => 'https://contract.visionstrust.com/contracts/...',
                ],
            ])
            ->add('purposeId', \Symfony\Component\Form\Extension\Core\Type\TextType::class, [
                'label' => 'dashboard.dataset.form.purpose_id',
                'required' => false,
                'attr' => [
                    'placeholder' => 'https://api.visionstrust.com/v1/catalog/serviceofferings/...',
                ],
            ])
            ->add('resourceId', \Symfony\Component\Form\Extension\Core\Type\TextType::class, [
                'label' => 'dashboard.dataset.form.resource_id',
                'required' => false,
                'attr' => [
                    'placeholder' => 'https://api.visionstrust.com/v1/catalog/serviceofferings/...',
                ],
            ])
            ->add('resource', \Symfony\Component\Form\Extension\Core\Type\TextType::class, [
                'label' => 'dashboard.dataset.form.resource',
                'required' => false,
                'attr' => [
                    'placeholder' => 'path/to/data.json.gz',
                ],
            ])
        ;
    }

    public function configureOptions(OptionsResolver $resolver): void
    {
        $resolver->setDefaults([
            'data_class' => Dataset::class,
        ]);
    }
}
