<?php

namespace App\Entity;

use App\Repository\UserRepository;
use Doctrine\Common\Collections\ArrayCollection;
use Doctrine\Common\Collections\Collection;
use Doctrine\ORM\Mapping as ORM;
use Symfony\Bridge\Doctrine\Validator\Constraints\UniqueEntity;
use Symfony\Component\Security\Core\User\UserInterface;
use App\Entity\AbstractLolaEntity;
use Symfony\Component\Security\Core\User\PasswordAuthenticatedUserInterface;

#[ORM\Entity(repositoryClass: UserRepository::class)]
#[UniqueEntity(fields: ['email'], message: 'Un compte utilisateur existe déjà avec cet email')]
class User extends AbstractLolaEntity implements UserInterface, PasswordAuthenticatedUserInterface
{

    const ROLE_ADMIN = "ROLE_ADMIN";
    const ROLE_ADMIN_SISR = "ROLE_ADMIN_SISR";
    const ROLE_PROFIL_1 = "ROLE_PROFIL_1";
    const ROLE_PROFIL_2 = "ROLE_PROFIL_2";
    const ROLE_PROFIL_3 = "ROLE_PROFIL_3";
    const ROLE_PROFIL_4 = "ROLE_PROFIL_4";
    const ROLE_PROFIL_5 = "ROLE_PROFIL_5";

    public static $listRoles = [
        self::ROLE_ADMIN => "Admin",
        self::ROLE_ADMIN_SISR => "Admin SISR",
        self::ROLE_PROFIL_1 => "Profil 1",
        self::ROLE_PROFIL_2 => "Profil 2",
        self::ROLE_PROFIL_3 => "Profil 3",
        self::ROLE_PROFIL_4 => "Profil 4",
        self::ROLE_PROFIL_5 => "Profil 5"
    ];

    #[ORM\Id]
    #[ORM\GeneratedValue]
    #[ORM\Column(type: 'integer')]
    private $id;

    #[ORM\Column(type: 'string', length: 180, unique: true)]
    private $email;

    #[ORM\Column(type: 'json')]
    private $roles = [self::ROLE_PROFIL_1];

    /**
     * @var string The hashed password
     */
    #[ORM\Column(type: 'string')]
    private $password;

    #[ORM\Column(type: 'boolean')]
    private $active = true;

    #[ORM\Column(type: 'boolean')]
    private $termsOfUse = true;

    #[ORM\Column(type: 'datetime', nullable: true)]
    private $lastLoginAt;

    #[ORM\Column(type: 'string', length: 255)]
    private $firstname;

    #[ORM\Column(type: 'string', length: 255)]
    private $lastname;

    #[ORM\Column(type: 'string', length: 255, unique: true)]
    private $hash;

    #[ORM\Column(type: 'string', length: 255, nullable: true)]
    private $upgradeRequest;

    #[ORM\ManyToMany(targetEntity: Group::class, mappedBy: 'users')]
    private $groups;

    public function __construct()
    {
        $this->createdAt = new \DateTime();
        // user is authenticated after registration
        $this->lastLoginAt = new \DateTime();
        $this->hash = "U" . sha1(random_bytes(255));
        $this->groups = new ArrayCollection();
    }

    public function __toString()
    {
        return $this->firstname . " " . $this->lastname;
    }

    /**
     * Check if the user has permission on the dataset
     * TODO : remove the DatasetRepository and inject it in a service
     * @param \App\Entity\Dataset $dataset
     * @param \App\Repository\DatasetRepository $datasetRepository
     * @return bool
     */
    public function hasPermission(Dataset $dataset, \App\Repository\DatasetRepository $datasetRepository): bool
    {
        $hasDataset = array_filter($this->getDatasets($datasetRepository), function ($ds) use ($dataset) {
            return $ds->getId() === $dataset->getId();
        });

        return count($hasDataset) > 0;
    }

    /**
     * Get all the users's datasets + shared datasets (by group or for everyone)
     * TODO : remove the DatasetRepository and inject it in a service
     * @param \App\Repository\DatasetRepository $datasetRepository
     * @return array<Dataset> Return a list of dataset object
     */
    public function getDatasets(\App\Repository\DatasetRepository $datasetRepository): array
    {
        // get datasets created by the user (this filter does not apply to admin role)
        $userRoleFilter = $this->isAdmin() ? [] : ["createdBy" => $this];
        $userDatasets = $datasetRepository->findBy($userRoleFilter);

        // get public datasets (shared to all)
        $sharedDatasets = $datasetRepository->findBy(["isShared" => true]);

        // get the datasets shared through groups
        $groupSharedDatasets = [];
        foreach ($this->getGroups() as $group) {
            $groupSharedDatasets = array_merge($groupSharedDatasets, $group->getDatasets()->toArray());
        }

        // combine all the datasets (owner, shared and group share) and remove doublon
        $known = [];
        $datasets = array_filter(array_merge($userDatasets, $sharedDatasets, $groupSharedDatasets), function ($val) use (&$known) {
            $unique = !in_array($val->getId(), $known);
            $known[] = $val->getId();
            return $unique;
        });

        return $datasets;
    }

    /**
     * Return true if the user is a Lola admin user
     * @return bool
     */
    public function isAdmin(): bool
    {
        return $this->hasRole('ROLE_ADMIN') || $this->hasRole('ROLE_ADMIN_SISR');
    }

    public function getId(): ?int
    {
        return $this->id;
    }

    public function getEmail(): ?string
    {
        return $this->email;
    }

    public function setEmail(string $email): self
    {
        $this->email = $email;

        return $this;
    }

    /**
     * A visual identifier that represents this user.
     *
     * @see UserInterface
     */
    public function getUsername(): string
    {
        return (string) $this->email;
    }

    /**
     * Check if a profil is an existing profil for Lola's users (must not be an ADMIN profil)
     * 
     * @param string $profil
     * @return bool
     */
    public static function isUserProfil(string $profil): bool
    {
        if (
            substr($profil, 0, 12) === "ROLE_PROFIL_" &&
            key_exists(strtoupper($profil), self::$listRoles)
        ) {
            return true;
        } else {
            return false;
        }
    }

    /**
     * Return the formatted user profil of the current user (no admin or admin-sisr)
     * If more than 1 profil found, the first is returned (it is not normal to have more than 1 profil)
     * 
     * @param bool $formatted if true, return the string of profil, if false return the ROLE_PROFIL_X
     * @return string The profil formatted or the role corresponding
     */
    public function getProfil(bool $formatted = true): string
    {
        $roles = $this->roles;
        foreach ($roles as $role) {
            if (self::isUserProfil(strtoupper($role))) {
                return $formatted ? self::$listRoles[strtoupper($role)] : $role;
            }
        }

        return "Pas de profil Lola";
    }

    /**
     * 
     */
    public static function getProfilFromRole(string $role): ?string
    {
        if (self::isUserProfil(strtoupper($role))) {
            return self::$listRoles[strtoupper($role)];
        }
        return null;
    }

    /**
     * @see UserInterface
     */
    public function getRoles(): array
    {
        $roles = $this->roles;
        // guarantee every user at least has ROLE_USER
        $roles[] = 'ROLE_USER';

        return array_unique($roles);
    }

    /**
     * Return a formatted role string
     * @return string || null
     */
    public function getRole(string $role): ?string
    {
        return key_exists(strtoupper($role), self::$listRoles) ? self::$listRoles[$role] : null;
    }

    /**
     * Return if the user has a role
     * @param string $role
     * @return boolean
     */
    public function hasRole(string $role): bool
    {
        return in_array(strtoupper($role), $this->getRoles(), true);
    }

    /**
     * Delete a role to the user
     * @param type $role
     * @return $this
     */
    public function removeRole(string $role): self
    {
        if (false !== $key = array_search($role, $this->roles, true)) {
            unset($this->roles[$key]);
            $this->roles = array_values($this->roles);
        }
        return $this;
    }

    public function addRole(string $role): self
    {
        if (!in_array(strtoupper($role), $this->roles, true)) {
            $this->roles[] = $role;
        }
        return $this;
    }

    /**
     * Set the user as an Admin (add the role ROLE_ADMIN)
     * @param bool $adminSisr
     * @return $this
     */
    public function setAdmin(bool $admin): self
    {
        if (true === $admin) {
            $this->addRole(self::ROLE_ADMIN);
        } else {
            $this->removeRole(self::ROLE_ADMIN);
        }
        return $this;
    }

    /**
     * Set the user as an Sisr Admin (add the role ROLE_ADMIN_SISR)
     * @param bool $adminSisr
     * @return $this
     */
    public function setAdminSisr(bool $adminSisr): self
    {
        if (true === $adminSisr) {
            $this->addRole(self::ROLE_ADMIN_SISR);
        } else {
            $this->removeRole(self::ROLE_ADMIN_SISR);
        }
        return $this;
    }

    public function setRoles(array $roles): self
    {
        $this->roles = $roles;
        return $this;
    }

    /**
     * Toggle the user with ROLE_ADMIN
     */
    public function toggleAdmin()
    {
        $this->hasRole("ROLE_ADMIN") ? $this->setAdmin(false) : $this->setAdmin(true);
    }

    /**
     * Toggle the user with ROLE_ADMIN
     */
    public function toggleAdminSisr()
    {
        $this->hasRole("ROLE_ADMIN_SISR") ? $this->setAdminSisr(false) : $this->setAdminSisr(true);
    }

    /**
     * @see UserInterface
     */
    public function getPassword(): string
    {
        return (string) $this->password;
    }

    public function setPassword(string $password): self
    {
        $this->password = $password;

        return $this;
    }

    /**
     * @see UserInterface
     */
    public function getSalt()
    {
        // not needed when using the "bcrypt" algorithm in security.yaml
    }

    /**
     * @see UserInterface
     */
    public function eraseCredentials(): void
    {
        // If you store any temporary, sensitive data on the user, clear it here
        // $this->plainPassword = null;
    }

    public function getActive(): ?bool
    {
        return $this->active;
    }

    public function isActive(): ?bool
    {
        return $this->getActive();
    }

    public function setActive(bool $active): self
    {
        $this->active = $active;

        return $this;
    }

    public function getLastLoginAt(): ?\DateTimeInterface
    {
        return $this->lastLoginAt;
    }

    public function setLastLoginAt(?\DateTimeInterface $lastLoginAt): self
    {
        $this->lastLoginAt = $lastLoginAt;

        return $this;
    }

    public function getFirstname(): ?string
    {
        return $this->firstname;
    }

    public function setFirstname(string $firstname): self
    {
        $this->firstname = $firstname;

        return $this;
    }

    public function getLastname(): ?string
    {
        return $this->lastname;
    }

    public function setLastname(string $lastname): self
    {
        $this->lastname = $lastname;

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

    public function getUpgradeRequest(): ?string
    {
        return $this->upgradeRequest;
    }

    public function setUpgradeRequest(?string $upgradeRequest): self
    {
        $this->upgradeRequest = $upgradeRequest;

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
            $group->addUser($this);
        }

        return $this;
    }

    public function removeGroup(Group $group): self
    {
        if ($this->groups->removeElement($group)) {
            $group->removeUser($this);
        }

        return $this;
    }

    public function getTermsOfUse(): ?bool
    {
        return $this->termsOfUse;
    }

    public function setTermsOfUse(bool $termsOfUse): self
    {
        $this->termsOfUse = $termsOfUse;

        return $this;
    }

    public function getUserIdentifier(): string
    {
        return (string) $this->getEmail();
    }
}
