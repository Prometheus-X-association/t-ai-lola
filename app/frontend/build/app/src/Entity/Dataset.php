<?php

namespace App\Entity;

use App\Repository\DatasetRepository;
use Doctrine\Common\Collections\ArrayCollection;
use Doctrine\Common\Collections\Collection;
use Doctrine\ORM\Mapping as ORM;
use App\Entity\AbstractLolaEntity;

// Atenttion: changement of the LOLA data provider logic
// Now, datasets can be different types: "csv", 'json', "xapi", etc.
// The old logic is remained. To use old logic, just set type = "xapi" in ..... 
// TODO

#[ORM\Entity(repositoryClass: DatasetRepository::class)]
class Dataset extends AbstractLolaEntity {

    const STATUS_WAITING = "WAITING";
    const STATUS_PROCESSING = "PROCESSING";
    const STATUS_AVAILABLE = "AVAILABLE";
    const STATUS_ERROR = "ERROR";
    const STATUS_DELETING = "DELETING";

    /**
     * Datasets with PROCESSING state can be deleted after this number of days (if not the delete button is not displayed)
     */
    const DELAY_DELETE_PROCESSING_DAYS = "10";

    #[ORM\Id]
    #[ORM\GeneratedValue]
    #[ORM\Column(type: 'integer')]
    private $id;

    /**
     * This hash is transfered to Lolapy to identify the dataset
     */
    #[ORM\Column(type: 'string', length: 255, unique: true)]
    private $hash;

    #[ORM\Column(type: 'string', length: 255)]
    private $name;

    #[ORM\Column(type: 'text', nullable: true)]
    private $description;

    #[ORM\Column(type: 'text', nullable: true)]
    private $recipe;

    #[ORM\Column(name: 'recipe_link', type: 'string', length: 255, nullable: true)]
    private $recipeLink;

    #[ORM\Column(type: 'boolean')]
    private $isShared;

    #[ORM\Column(type: 'string', length: 255)]
    private $status;

    #[ORM\ManyToMany(targetEntity: Group::class, mappedBy: 'datasets')]
    private $groups;

    #[ORM\OneToMany(targetEntity: DatasetLogs::class, mappedBy: 'dataset')]
    private $datasetLogs;

    #[ORM\Column(type: 'float', nullable: true)]
    private $pourcentageProgress;

    #[ORM\Column(type: 'bigint', nullable: true)]
    private $size;

    /**
     * [NEW] - added november 2025 (because of removing of obligation to use xapi datasets)
     * Path or name of dataset in common storage directory
     * "a23f1c_mydata.csv"
     *
     */
    #[ORM\Column(type: 'string', length: 255, nullable: true)]
    private $storagePath;

    /**
     * type dataset "file" 
     */
    #[ORM\Column(type: 'string', length: 50)]
    private $type = 'file';

    public function __construct()
    {
        $this->isShared = false;
        $this->hash = "D" . sha1(random_bytes(255));
        $this->status = self::STATUS_WAITING;
        $this->groups = new ArrayCollection();
        $this->datasetLogs = new ArrayCollection();
        $this->type = 'file';
    }

    private function formatSize(): string
    {        
        if ($this->size === null) {
            return "N/A";
        }

        $size = (float) $this->size;
        $unit = ['Byte', 'KiB', 'MiB', 'GiB', 'TiB'];

        $i = 0;
        while ($this->size >= 1024 && $i < count($unit) - 1) {
            $this->size /= 1024;
            $i++;
        }
        return round($this->size) . ' ' . $unit[$i];
    }

    public function getLogs()
    {
        $listeLog = array_map(function ($log) {
            return $log->getToken();
        }, $this->getDatasetLogs()->toArray());
        $listeLog = array_flip($listeLog);
        foreach ($listeLog as $key => $log) {
            $formattedLogs[$key] = array_filter($this->getDatasetLogs()->toArray(), function ($log) use ($key) {
                return $log->getToken() === $key;
            });
            foreach ($formattedLogs[$key] as $fl) {
                $formattedLogs[$key][$fl->getAction()] = $fl->getDatetime();
            }
        }
        return $formattedLogs ?? [];
    }

    /**
     * Toggle the dataset share / not share
     */
    public function toggleShare(): void
    {
        $this->isShared = !$this->isShared;
    }

    /**
     * Test if a dataset can be deleted
     */
    public function isDeletable()
    {
        if (in_array($this->status, [static::STATUS_AVAILABLE, static::STATUS_ERROR, static::STATUS_WAITING])) {
            return true;
        } elseif ($this->status === static::STATUS_PROCESSING) {
            $now = new \DateTime();
            $diff = $now->diff($this->getCreatedAt());
            if ($diff->days > static::DELAY_DELETE_PROCESSING_DAYS) {
                return true;
            } else {
                return false;
            }
        }
    }

    /**
     * Toggle the dataset shared / not shared
     */
    public function toggleShared(): void
    {
        $this->isShared = !$this->isShared;
    }

    public function getId(): ?int
    {
        return $this->id;
    }

    public function getName(): ?string
    {
        return $this->name;
    }

    public function setName(string $name): self
    {
        $this->name = $name;

        return $this;
    }

    public function getDescription(): ?string
    {
        return $this->description;
    }

    public function setDescription(?string $description): self
    {
        $this->description = $description;

        return $this;
    }

    public function getIsShared(): ?bool
    {
        return $this->isShared;
    }

    public function setIsShared(bool $isShared): self
    {
        $this->isShared = $isShared;

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

    public function getHash(): ?string
    {
        return $this->hash;
    }

    public function setHash(string $hash): self
    {
        $this->hash = $hash;

        return $this;
    }

    /**
     * @return Collection|Group[]
     */
    public function getGroups(): Collection
    {
        return $this->groups;
    }

    public function addGroup(Group $group): self
    {
        if (!$this->groups->contains($group)) {
            $this->groups[] = $group;
            $group->addDataset($this);
        }

        return $this;
    }

    public function removeGroup(Group $group): self
    {
        if ($this->groups->removeElement($group)) {
            $group->removeDataset($this);
        }

        return $this;
    }

    /**
     * @return Collection|datasetLogs[]
     */
    public function getDatasetLogs(): Collection
    {
        return $this->datasetLogs;
    }

    public function addDatasetLog(datasetLogs $datasetLog): self
    {
        if (!$this->datasetLogs->contains($datasetLog)) {
            $this->datasetLogs[] = $datasetLog;
            $datasetLog->setDataset($this);
        }

        return $this;
    }

    public function removeDatasetLog(datasetLogs $datasetLog): self
    {
        if ($this->datasetLogs->removeElement($datasetLog)) {
            // set the owning side to null (unless already changed)
            if ($datasetLog->getDataset() === $this) {
                $datasetLog->setDataset(null);
            }
        }

        return $this;
    }

    // [OLD] - removed november 2025 (because of removing of obligation to use xapi datasets)

    
    // public function getRecipe(): ?string
    // {
    //     return $this->recipe;
    // }

    // public function setRecipe(?string $recipe): self
    // {
    //     $this->recipe = $recipe;

    //     return $this;
    // }

    // public function getRecipeLink(): ?string
    // {
    //     return $this->recipeLink;
    // }

    // public function setRecipeLink(?string $recipeLink): self
    // {
    //     $this->recipeLink = $recipeLink;

    //     return $this;
    // }

    public function getPourcentageProgress(): ?float
    {
        return $this->pourcentageProgress;
    }

    public function setPourcentageProgress(?float $pourcentageProgress): self
    {
        $this->pourcentageProgress = $pourcentageProgress;

        return $this;
    }

    public function getSize(): string
    {
        return $this->formatSize();
    }

    public function setSize($size): self
    {
        $this->size = (int) $size;

        return $this;
    }

    public function getStoragePath(): ?string
    {
        return $this->storagePath;
    }

    public function setStoragePath(?string $storagePath): self
    {
        $this->storagePath = $storagePath;

        return $this;
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

}
