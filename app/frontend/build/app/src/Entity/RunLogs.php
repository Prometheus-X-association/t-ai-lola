<?php

namespace App\Entity;

use Symfony\Component\Serializer\Attribute\MaxDepth;
use App\Repository\RunLogsRepository;
use Doctrine\ORM\Mapping as ORM;

#[ORM\Entity(repositoryClass: RunLogsRepository::class)]
class RunLogs
{
    const TYPE_PROCESS = "PROCESS";
    const TYPE_WORKFLOW = "WORKFLOW";

    const EVENT_SUBMIT = "SUBMIT";
    const EVENT_RUN = "RUN";
    const EVENT_DONE = "DONE";
    const EVENT_ERROR = "ERROR";

    public static $listTypes = [
        "process" => self::TYPE_PROCESS,
        "workflow" => self::TYPE_WORKFLOW
    ];
    public static $listEvents = [
        "submit" => self::EVENT_SUBMIT,
        "run" => self::EVENT_RUN,
        "done" => self::EVENT_DONE,
        "error" => self::EVENT_ERROR
    ];

    #[ORM\Id]
    #[ORM\GeneratedValue]
    #[ORM\Column(type: 'integer')]
    private $id;

    #[ORM\Column(type: 'string', length: 255)]
    private $type;

    #[ORM\Column(type: 'string', length: 255)]
    private $event;

    #[ORM\Column(type: 'datetime')]
    private $time;

    #[ORM\Column(type: 'string', length: 255, nullable: true)]
    private $workdir;

    #[ORM\Column(type: 'text', nullable: true)]
    private $error;

    #[ORM\Column(type: 'json', nullable: true)]
    private $statistic = [];

    #[ORM\ManyToOne(targetEntity: Run::class, inversedBy: 'runLogs')]
    #[MaxDepth(1)]
    public $run;

    #[ORM\Column(type: 'string', length: 255, nullable: true)]
    private $nomProcess;

    public function getId(): ?int
    {
        return $this->id;
    }

    public function getType(): ?string
    {
        return $this->type;
    }

    public function setType(string $type): self
    {
        $this->type = $type;

        return $this;
    }

    public function getEvent(): ?string
    {
        return $this->event;
    }

    public function setEvent(string $event): self
    {
        $this->event = $event;

        return $this;
    }

    public function getTime(): ?\DateTimeInterface
    {
        return $this->time;
    }

    public function setTime(\DateTimeInterface $time): self
    {
        $this->time = $time;

        return $this;
    }

    public function getWorkdir(): ?string
    {
        return $this->workdir;
    }

    public function setWorkdir(?string $workdir): self
    {
        $this->workdir = $workdir;

        return $this;
    }

    public function getStatistic(): ?array
    {
        return $this->statistic;
    }

    public function setStatistic(?array $statistic): self
    {
        $this->statistic = $statistic;

        return $this;
    }

    public function getRun(): ?Run
    {
        return $this->run;
    }

    public function setRun(?Run $run): self
    {
        $this->run = $run;

        return $this;
    }

    public function getError(): ?string
    {
        return $this->error;
    }

    public function setError(?string $error): self
    {
        $this->error = $error;

        return $this;
    }

    public function getNomProcess(): ?string
    {
        return $this->nomProcess;
    }

    public function setNomProcess(?string $nomProcess): self
    {
        $this->nomProcess = $nomProcess;

        return $this;
    }
}
