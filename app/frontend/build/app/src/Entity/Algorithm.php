<?php

namespace App\Entity;

use App\Repository\AlgorithmRepository;
use Doctrine\Common\Collections\ArrayCollection;
use Doctrine\Common\Collections\Collection;
use Doctrine\ORM\Mapping as ORM;
use App\Entity\AbstractLolaEntity;

/**
 * @ORM\Entity(repositoryClass=AlgorithmRepository::class)
 */
class Algorithm extends AbstractLolaEntity {

    /**
     * @ORM\Id
     * @ORM\GeneratedValue
     * @ORM\Column(type="integer")
     */
    private $id;

    /**
     * @ORM\Column(type="string", length=255)
     */
    private $name;

    /**
     * @ORM\Column(name="url_repository", type="string", length=255)
     */
    private $urlRepository;

    /**
     * @ORM\Column(type="text", nullable=true)
     */
    private $description;

    /**
     * @ORM\Column(type="boolean")
     */
    private $isPublic;

    /**
     * @ORM\OneToMany(targetEntity=AlgorithmVersion::class, mappedBy="algorithm")
     */
    private $algorithmVersions;

    public function __construct() {
        $this->isPublic = false;
        $this->algorithmVersions = new ArrayCollection();
    }

    public function __toString() {
        return $this->name;
    }

    /**
     * Toggle the algorithm active / inactive
     */
    public function toggleActive(): void {
        $this->isActive = !$this->isActive;
    }

    /**
     * Toggle the algorithm public / private
     */
    public function togglePublic(): void {
        $this->isPublic = !$this->isPublic;
    }

    public function getId(): ?int {
        return $this->id;
    }

    public function getName(): ?string {
        return $this->name;
    }

    public function setName(string $name): self {
        $this->name = $name;

        return $this;
    }

    public function getDescription(): ?string {
        return $this->description;
    }

    public function setDescription(?string $description): self {
        $this->description = $description;

        return $this;
    }

    public function getIsPublic(): ?bool {
        return $this->isPublic;
    }

    public function setIsPublic(bool $isPublic): self {
        $this->isPublic = $isPublic;

        return $this;
    }

    /**
     * @return Collection<int, AlgorithmVersion>
     */
    public function getAlgorithmVersions(): Collection {
        return $this->algorithmVersions;
    }

    public function addAlgorithmVersion(AlgorithmVersion $algorithmVersion): self {
        if (!$this->algorithmVersions->contains($algorithmVersion)) {
            $this->algorithmVersions[] = $algorithmVersion;
            $algorithmVersion->setAlgorithm($this);
        }

        return $this;
    }

    public function removeAlgorithmVersion(AlgorithmVersion $algorithmVersion): self {
        if ($this->algorithmVersions->removeElement($algorithmVersion)) {
            // set the owning side to null (unless already changed)
            if ($algorithmVersion->getAlgorithm() === $this) {
                $algorithmVersion->setAlgorithm(null);
            }
        }

        return $this;
    }

    public function getUrlRepository(): ?string {
        return $this->urlRepository;
    }

    public function setUrlRepository(string $urlRepository): self {
        $this->urlRepository = $urlRepository;

        return $this;
    }

    public function getUrlRepositoryNoToken(): ?string {
        // Si l'url contient un @ 
        if (strpos( $this->urlRepository, "@" ) !== false) {
            // Et si l'url commence par http ou https, on supprime tout ce qui se trouve entre / et @
            if (strpos( $this->urlRepository, "http:" ) === 0) {
                return "http://" . substr($this->urlRepository, strpos($this->urlRepository, "@") + 1, strlen($this->urlRepository));
            } elseif (strpos( $this->urlRepository, "https:" ) === 0) {
                return "https://" . substr($this->urlRepository, strpos($this->urlRepository, "@") + 1, strlen($this->urlRepository));
            // Sinon on supprime du début jusqu'au @
            } else {
                return substr($this->urlRepository, strpos($this->urlRepository, "@") + 1, strlen($this->urlRepository));
            }
            
        } else {
            return $this->urlRepository;
        }   
    }

}
