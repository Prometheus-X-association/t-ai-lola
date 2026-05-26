<?php

namespace App\Entity;

use App\Repository\RunRepository;
use Doctrine\Common\Collections\ArrayCollection;
use Doctrine\Common\Collections\Collection;
use Doctrine\ORM\Mapping as ORM;

#[ORM\Entity(repositoryClass: RunRepository::class)]
class Run extends AbstractLolaEntity {

    const STATUS_WAITING = "WAITING";
    const STATUS_SCHEDULING_TRAX_DB = "SCHEDULING_TRAX_DB";
    const STATUS_WAITING_NEXTFLOW = "WAITING_NEXTFLOW";
    const STATUS_RUNNING_SCENARIO = "RUNNING_SCENARIO";
    const STATUS_COMPLETED = "COMPLETED";
    const STATUS_ERROR = "ERROR";

    #[ORM\Id]
    #[ORM\GeneratedValue]
    #[ORM\Column(type: 'integer')]
    private $id;

    #[ORM\Column(type: 'string', length: 255)]
    private $hash;

    #[ORM\Column(type: 'string', length: 255)]
    private $status;

    #[ORM\Column(type: 'boolean')]
    private $hasOutput;  

    /**
     * @var Scenario
     **/
    #[ORM\ManyToOne(targetEntity: Scenario::class, inversedBy: 'runs')]
    public $scenario;

    #[ORM\OneToMany(targetEntity: RunLogs::class, mappedBy: 'run')]
    public $runLogs;

    public function __construct()
    {
        $this->hash = "R" . sha1(random_bytes(255));
        $this->setStatus(self::STATUS_WAITING);
        $this->runLogs = new ArrayCollection();
        $this->hasOutput = false;
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

    public function getStatus(): ?string
    {
        return $this->status;
    }

    public function setStatus(string $status): self
    {
        $this->status = $status;

        return $this;
    }

    public function getHasOutput(): ?bool
    {
        return $this->hasOutput;
    }

    public function setHasOutput(bool $hasOutput): self
    {
        $this->hasOutput = $hasOutput;

        return $this;
    }

    /**
     * @return Collection|RunLogs[]
     */
    public function getRunLogs(): Collection
    {
        return $this->runLogs;
    }

    public function addRunLog(RunLogs $runLog): self
    {
        if (!$this->runLogs->contains($runLog)) {
            $this->runLogs[] = $runLog;
            $runLog->setRun($this);
        }

        return $this;
    }

    public function removeRunLog(RunLogs $runLog): self
    {
        if ($this->runLogs->removeElement($runLog)) {
            // set the owning side to null (unless already changed)
            if ($runLog->getRun() === $this) {
                $runLog->setRun(null);
            }
        }

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

}
