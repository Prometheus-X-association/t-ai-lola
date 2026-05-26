<?php

namespace App\Entity;

use App\Repository\ScenarioAlgorithmRepository;
use Doctrine\ORM\Mapping as ORM;

#[ORM\Entity(repositoryClass: ScenarioAlgorithmRepository::class)]
class ScenarioAlgorithm
{
    #[ORM\Id]
    #[ORM\GeneratedValue]
    #[ORM\Column(type: 'integer')]
    private $id;

    /**
     * @var Dataset
     **/
    #[ORM\ManyToOne(targetEntity: Scenario::class, inversedBy: 'scenarioAlgorithms')]
    public $scenario;

    /**
     * @var Dataset
     **/
    #[ORM\ManyToOne(targetEntity: AlgorithmVersion::class)]
    public $algorithmVersion;

    #[ORM\Column(type: 'json')]
    private $parametres = [];

    #[ORM\Column(type: 'string', length: 255)]
    private $nfVariable;

    public function getId(): ?int
    {
        return $this->id;
    }

    public function getNfVariable(): ?string
    {
        return $this->nfVariable;
    }

    public function setNfVariable(string $nfVariable): self
    {
        $this->nfVariable = $nfVariable;

        return $this;
    }

    public function getParametres(): ?array
    {
        return $this->parametres;
    }

    public function setParametres(array $parametres): self
    {
        $this->parametres = $parametres;

        return $this;
    }

    public function getScenario(): ?Scenario
    {
        return $this->scenario;
    }

    public function setScenario(?Scenario $scenario): self
    {
        $this->scenario = $scenario;

        return $this;
    }

    public function getAlgorithmVersion(): ?AlgorithmVersion
    {
        return $this->algorithmVersion;
    }

    public function setAlgorithmVersion(?AlgorithmVersion $algorithmVersion): self
    {
        $this->algorithmVersion = $algorithmVersion;

        return $this;
    }
}
