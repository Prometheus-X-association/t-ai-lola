<?php

namespace App\Entity;

use App\Repository\MetaScenarioRepository;
use Doctrine\Common\Collections\ArrayCollection;
use Doctrine\Common\Collections\Collection;
use Doctrine\ORM\Mapping as ORM;
use App\Entity\AbstractLolaEntity;

/**
 * @ORM\Entity(repositoryClass=MetaScenarioRepository::class)
 * @ORM\HasLifecycleCallbacks()
 */
class MetaScenario extends AbstractLolaEntity {

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
     * @ORM\Column(type="boolean")
     */
    private $isActive;

    /**
     * @ORM\OneToMany(targetEntity=Tag::class, mappedBy="metascenario")
     */
    private $tags;

    /**
     * @ORM\OneToMany(targetEntity=Scenario::class, mappedBy="metascenario")
     */
    private $scenarios;
    

    public function __construct()
    {
        $this->isPublic = false;
        $this->isActive = true;
        $this->tags = new ArrayCollection();
        $this->scenarios = new ArrayCollection();
    }

    /**
     * Toggle the metascenario public / private
     */
    public function togglePublic(): void
    {
        $this->isPublic = !$this->isPublic;
    }

    /**
     * Toggle the metascenario active / inactive
     */
    public function toggleActive(): void
    {
        $this->isActive = !$this->isActive;
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

    public function getIsPublic(): ?bool
    {
        return $this->isPublic;
    }

    public function setIsPublic(bool $isPublic): self
    {
        $this->isPublic = $isPublic;

        return $this;
    }

    public function getUrlRepository(): ?string
    {
        return $this->urlRepository;
    }

    public function getUrlRepositoryNoToken(): ?string {
        // Si il y a un @ dans l'url
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

    public function setUrlRepository(string $urlRepository): self
    {
        $this->urlRepository = $urlRepository;

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
     * @return Collection|Scenario[]
     */
    public function getScenarios(): Collection
    {
        return $this->scenarios;
    }

    public function addScenario(Scenario $scenario): self
    {
        if (!$this->scenarios->contains($scenario)) {
            $this->scenarios[] = $scenario;
            $scenario->setScenario($this);
        }

        return $this;
    }

    public function removeScenario(Scenario $scenario): self
    {
        if ($this->scenarios->removeElement($scenario)) {
            // set the owning side to null (unless already changed)
            if ($scenario->getScenario() === $this) {
                $scenario->setScenario(null);
            }
        }

        return $this;
    }

    /**
     * @return Collection|Tag[]
     */
    public function getTags(): Collection
    {
        return $this->tags;
    }

    public function addTag(Tag $tag): self
    {
        if (!$this->tags->contains($tag)) {
            $this->tags[] = $tag;
            $tag->setTag($this);
        }

        return $this;
    }

    public function removeTag(Tag $tag): self
    {
        if ($this->tags->removeElement($tag)) {
            // set the owning side to null (unless already changed)
            if ($tag->getTag() === $this) {
                $tag->setTag(null);
            }
        }

        return $this;
    }

}
