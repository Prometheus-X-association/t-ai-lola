<?php

namespace App\Entity;

use App\Repository\ScenarioRepository;
use Doctrine\Common\Collections\ArrayCollection;
use Doctrine\Common\Collections\Collection;
use Doctrine\ORM\Mapping as ORM;
use App\Entity\AbstractLolaEntity;

#[ORM\Entity(repositoryClass: ScenarioRepository::class)]
class Scenario extends AbstractLolaEntity {

    #[ORM\Id]
    #[ORM\GeneratedValue]
    #[ORM\Column(type: 'integer')]
    private $id;


    #[ORM\Column(type: 'string', length: 255)]
    private $hash;

    #[ORM\Column(type: 'json')]
    private $parametres = [];

    /**
     * @var Tag
     **/
    #[ORM\ManyToOne(targetEntity: Tag::class)]
    public $tag;

    #[ORM\Column(type: 'boolean')]
    private $isActive;    

    /**
     * @var Dataset
     **/
    #[ORM\ManyToOne(targetEntity: Dataset::class)]
    public $dataset;

    /**
     * @var MetaScenario
     **/
    #[ORM\ManyToOne(targetEntity: MetaScenario::class, inversedBy: 'scenarios')]
    public $metascenario;

    #[ORM\OneToMany(targetEntity: ScenarioAlgorithm::class, mappedBy: 'scenario')]
    private $scenarioAlgorithms;    

    #[ORM\OneToMany(targetEntity: Run::class, mappedBy: 'scenario')]
    public $runs;

    public function __construct()
    {
        $this->hash = "S" . sha1(random_bytes(255));
        $this->isActive = true;
        $this->runs = new ArrayCollection();
        $this->scenarioAlgorithms = new ArrayCollection();
    }

    /**
     * Toggle the scenario active / inactive
     */
    public function toggleActive(): void
    {
        $this->isActive = !$this->isActive;
    }    
    
    public function getId(): ?int
    {
        return $this->id;
    }

    public function getHash(): ?string
    {
        return $this->hash;
    }

    public function setHash(string $hash): self
    {
        $this->hash = $hash;

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

    public function getDataset(): ?Dataset
    {
        return $this->dataset;
    }

    public function setDataset(?Dataset $dataset): self
    {
        $this->dataset = $dataset;

        return $this;
    }

    public function getTag(): ?Tag
    {
        return $this->tag;
    }

    public function setTag(?Tag $tag): self
    {
        $this->tag = $tag;

        return $this;
    }

    /**
     * @return Collection|Run[]
     */
    public function getRuns(): Collection
    {
        return $this->runs;
    }

    public function addRun(Run $run): self
    {
        if (!$this->runs->contains($run)) {
            $this->runs[] = $run;
            $run->setScenario($this);
        }

        return $this;
    }

    public function removeRun(Run $run): self
    {
        if ($this->runs->removeElement($run)) {
            // set the owning side to null (unless already changed)
            if ($run->getScenario() === $this) {
                $run->setScenario(null);
            }
        }

        return $this;
    }

    public function getMetascenario(): ?MetaScenario
    {
        return $this->metascenario;
    }

    public function setMetascenario(?MetaScenario $metascenario): self
    {
        $this->metascenario = $metascenario;

        return $this;
    }

    public function getIsActive(): ?bool
    {
        return $this->isActive;
    }

    public function setIsActive(bool $isActive): self
    {
        $this->isActive = $isActive;

        return $this;
    }

    /**
     * @return Collection<int, scenarioAlgorithm>
     */
    public function getScenarioAlgorithms(): Collection
    {
        return $this->scenarioAlgorithms;
    }

    public function addScenarioAlgorithm(scenarioAlgorithm $scenarioAlgorithm): self
    {
        if (!$this->scenarioAlgorithms->contains($scenarioAlgorithm)) {
            $this->scenarioAlgorithms[] = $scenarioAlgorithm;
            $scenarioAlgorithm->setScenario($this);
        }

        return $this;
    }

    public function removeScenarioAlgorithm(scenarioAlgorithm $scenarioAlgorithm): self
    {
        if ($this->scenarioAlgorithms->removeElement($scenarioAlgorithm)) {
            // set the owning side to null (unless already changed)
            if ($scenarioAlgorithm->getScenario() === $this) {
                $scenarioAlgorithm->setScenario(null);
            }
        }

        return $this;
    }

}

