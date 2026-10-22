<?php

namespace App\Form;

use App\Entity\Dataset;
use Symfony\Component\Form\AbstractType;
use Symfony\Component\Form\Extension\Core\Type\TextareaType;
use Symfony\Component\Form\Extension\Core\Type\TextType;
use Symfony\Component\Form\FormBuilderInterface;
use Symfony\Component\OptionsResolver\OptionsResolver;

class DatasetType extends AbstractType
{
    public function buildForm(FormBuilderInterface $builder, array $options): void
    {
        $builder
            ->add('name', null, [
                'label' => 'dashboard.dataset.form.nom',
            ])
            ->add('description', TextareaType::class, [
                'label' => 'dashboard.dataset.form.description',    
                'required' => false,
            ])
            ->add('contract', TextType::class, [
                'label' => 'dashboard.dataset.form.contract',
                'required' => false,
                'attr' => [
                    'placeholder' => 'https://contract.visionstrust.com/contracts/...',
                ],
            ])
            ->add('purposeId', TextType::class, [
                'label' => 'dashboard.dataset.form.purpose_id',
                'required' => false,
                'attr' => [
                    'placeholder' => 'https://api.visionstrust.com/v1/catalog/serviceofferings/...',
                ],
            ])
            ->add('resourceId', TextType::class, [
                'label' => 'dashboard.dataset.form.resource_id',
                'required' => false,
                'attr' => [
                    'placeholder' => 'https://api.visionstrust.com/v1/catalog/serviceofferings/...',
                ],
            ])
            ->add('resource', TextType::class, [
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
