<?php

namespace App\Entity;

use App\Repository\DatasetLogsRepository;
use Doctrine\ORM\Mapping as ORM;
use App\Entity\Dataset;

#[ORM\Entity(repositoryClass: DatasetLogsRepository::class)]
class DatasetLogs {

    const ACTION_START = "START";
    const ACTION_COMPLETE = "COMPLETE";
    const ACTION_ERROR = "ERROR";

    #[ORM\Id]
    #[ORM\GeneratedValue]
    #[ORM\Column(type: 'integer')]
    private $id;

    #[ORM\Column(type: 'string', length: 255)]
    private $token;

    #[ORM\Column(type: 'string', length: 255)]
    private $action;

    #[ORM\Column(type: 'datetime')]
    private $datetime;

    /**
     * @var Dataset
     **/
    #[ORM\ManyToOne(targetEntity: Dataset::class, inversedBy: 'datasetLogs')]
    public $dataset;

    public function __construct(Dataset $dataset, string $action, string $token)
    {
        $this->setDataset($dataset);
        $this->setAction($action);
        $this->setDatetime(new \DateTime());
        $this->setToken($token);
    }

    public function getId(): ?int
    {
        return $this->id;
    }

    public function getAction(): ?string
    {
        return $this->action;
    }

    public function setAction(string $action): self
    {
        $this->action = $action;

        return $this;
    }

    public function getDatetime(): ?\DateTimeInterface
    {
        return $this->datetime;
    }

    public function setDatetime(\DateTimeInterface $datetime): self
    {
        $this->datetime = $datetime;

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

    public function getToken(): ?string
    {
        return $this->token;
    }

    public function setToken(string $token): self
    {
        $this->token = $token;

        return $this;
    }

}
