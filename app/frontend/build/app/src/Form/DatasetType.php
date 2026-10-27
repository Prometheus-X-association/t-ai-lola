<?php

namespace App\Form;

use App\Entity\Dataset;
use Symfony\Component\Form\AbstractType;
use Symfony\Component\Form\Extension\Core\Type\ChoiceType;
use Symfony\Component\Form\Extension\Core\Type\TextareaType;
use Symfony\Component\Form\Extension\Core\Type\TextType;
use Symfony\Component\Form\FormBuilderInterface;
use Symfony\Component\OptionsResolver\OptionsResolver;

class DatasetType extends AbstractType
{
    public function buildForm(FormBuilderInterface $builder, array $options): void
    {
        $builder
            ->add('uploadType', ChoiceType::class, [
                'label' => 'dashboard.dataset.form.upload_type',
                'choices' => [
                    'dashboard.dataset.form.upload_type_sftp' => Dataset::UPLOAD_TYPE_SFTP,
                    'dashboard.dataset.form.upload_type_pdc_jwt' => Dataset::UPLOAD_TYPE_PDC_JWT,
                    'dashboard.dataset.form.upload_type_pdc_s3' => Dataset::UPLOAD_TYPE_PDC_S3,
                ],
                'expanded' => false,
                'multiple' => false,
                'attr' => [
                    'class' => 'form-control',
                    'id' => 'dataset_upload_type_select',
                ],
            ])
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
            ->add('targetFilename', TextType::class, [
                'label' => 'dashboard.dataset.form.target_filename',
                'required' => false,
                'attr' => [
                    'placeholder' => 'test.json',
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
