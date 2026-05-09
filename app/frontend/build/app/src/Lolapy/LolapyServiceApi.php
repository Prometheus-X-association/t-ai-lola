<?php

namespace App\Lolapy;

use Psr\Log\LoggerInterface;  // Add this import

class LolapyServiceApi {

    /**
     * Logger service
     * 
     * @var LoggerInterface
     */
    private $logger;  // Add this property

    /**
     * Security service for User logged data
     * 
     * @var \Symfony\Component\Security\Core\Security
     */
    private $security;

    /**
     * Url of Lolapy api
     *
     * @var string $url
     */
    private $url;

    /**
     * Port of Lolapy API of the root api
     *
     * @var string $port
     */
    private $port;

    /**
     * Resource url for Lolapy to check if ther API is ready
     *
     * @var string $resourcePing
     */
    private $resourcePing;

    /**
     * Resource url for Lolapy to get dataset stats
     *
     * @var string $resourceDatasetGet
     */
    private $resourceDatasetGet;

    /**
     * Resource url for Lolapy to delete a dataset
     *
     * @var string $resourceDatasetDelete
     */
    private $resourceDatasetDelete;

    /**
     * Resource url for Lolapy to add a tag for a scenario
     *
     * @var string $resourceScenarioTagAdd
     */
    private $resourceScenarioTagAdd;

    /**
     * Resource url for Lolapy to remove a tag for a scenario
     *
     * @var string $resourceScenarioTagRemove
     */
    private $resourceScenarioTagRemove;

    /**
     * Resource url for Lolapy to get the list of the parameters of scenario
     *
     * @var string $resourceScenarioParameters
     */
    private $resourceScenarioParameters;

    /**
     * Resource url for Lolapy to start the execution of a scenario
     *
     * @var string $resourceScenarioExecute
     */
    private $resourceScenarioExecute;

    /**
     * Resource url for Lolapy to prepare the output for the run
     *
     * @var string $resourceScenarioPrepareResults
     */
    private $resourceScenarioPrepareResults;

    /**
     * Resource url for Lolapy to get the archive
     *
     * @var string $resourceScenarioGetArchive
     */
    private $resourceScenarioGetArchive;

    /**
     * Resource url for Lolapy to add a version of the algorithm
     *
     * @var string $resourceAlgorithmAdd
     */
    private $resourceAlgorithmVersionAdd;

    /**
     * Resource url for Lolapy to remove the version of the algorithm
     *
     * @var string $resourceAlgorithmRemove
     */
    private $resourceAlgorithmVersionRemove;

    /**
     * Resource url for Lolapy to return the list of parameters and readme of the algorithm
     *
     * @var string $resourceAlgorithmParameters
     */
    private $resourceAlgorithmVersionParameters;

    /**
     * Resource url for Lolapy to add server usage statistics
     *
     * @var string $resourceServerUsage
     */
    private $resourceServerUsage;

    // Update the constructor to include LoggerInterface
    public function __construct(
        LoggerInterface $logger,  // Add this parameter
        \Symfony\Component\Security\Core\Security $security
    )
    {
        $this->logger = $logger;  // Add this line
        $this->security = $security;

        $this->url = $_ENV["LOLAPY_API_ADRESS"];
        $this->port = $_ENV["LOLAPY_API_PORT"];
        $this->resourcePing = $_ENV["LOLAPY_RESOURCE_PING"];

        $this->resourceDatasetGet = $_ENV["LOLAPY_RESOURCE_DATASET_GET"];
        $this->resourceDatasetDelete = $_ENV["LOLAPY_RESOURCE_DATASET_DELETE"];
        $this->resourceScenarioTagAdd = $_ENV["LOLAPY_RESOURCE_SCENARIO_TAG_ADD"];
        $this->resourceScenarioTagRemove = $_ENV["LOLAPY_RESOURCE_SCENARIO_TAG_REMOVE"];
        $this->resourceScenarioParameters = $_ENV["LOLAPY_RESOURCE_SCENARIO_PARAMETERS"];
        $this->resourceScenarioExecute = $_ENV["LOLAPY_RESOURCE_SCENARIO_EXECUTE"];
        $this->resourceScenarioPrepareResults = $_ENV["LOLAPY_RESOURCE_SCENARIO_PREPARE_RESULTS"];
        $this->resourceScenarioGetArchive = $_ENV["LOLAPY_RESOURCE_SCENARIO_GET_ARCHIVE"];
        $this->resourceAlgorithmVersionAdd = $_ENV["LOLAPY_RESOURCE_ALGORITHM_VERSION_ADD"];
        $this->resourceAlgorithmVersionRemove = $_ENV["LOLAPY_RESOURCE_ALGORITHM_VERSION_REMOVE"];
        $this->resourceAlgorithmVersionParameters = $_ENV["LOLAPY_RESOURCE_ALGORITHM_VERSION_PARAMETERS"];
        $this->resourceServerUsage = $_ENV["LOLAPY_RESOURCE_SERVER_USAGE"];
    }

    // ... rest of your methods stay the same

    /**
     * Return the Lolapy url as described in the parameters in the .env file
     * There is no ending / returned -> the resources names must begin with /
     *
     * @return string
     */
    private function getLolapyUrl(): string
    {
        return $this->url . ":" . $this->port;
    }

    /**
     * Return an array with Lolapy parameters (url, port, fake)
     * @return array
     */
    public function getLolapyParameters(): array
    {
        return [
            'LOLAPY_API_ADRESS' => $this->url,
            'LOLAPY_API_PORT' => $this->port,
            'LOLAPY_API_FAKE' => $_ENV["LOLAPY_API_FAKE"] ? 'false' : 'true',
        ];
    }

    /**
     * Check if the Lolapy API is ready
     *
     * @return bool
     */
    public function isLolapyReady(): bool
    {
        if ($_ENV["LOLAPY_API_FAKE"] === "true") {
            return true;
        }

        if ($this->executeCurlRequestPost($this->resourcePing, [], false)) {
            return true;
        } else {
            return false;
        }
    }

    /**
     * Execute curl request with post json data
     *
     * @param string $ressource
     * @param array $data
     *
     * @return string|json
     */
    private function executeCurlRequestPost(string $resource, array $data = [], bool $post = true)
    {
        $curl = curl_init();
        curl_setopt($curl, CURLOPT_URL, $this->getLolapyUrl() . $resource);
        curl_setopt($curl, CURLOPT_RETURNTRANSFER, true);
        if ($post) {
            curl_setopt($curl, CURLOPT_POST, true);
            curl_setopt($curl, CURLOPT_CUSTOMREQUEST, "POST");
            curl_setopt($curl, CURLOPT_POSTFIELDS, json_encode($data));
            curl_setopt($curl, CURLOPT_HTTPHEADER, ['Content-Type:application/json']);
        }
        $content = curl_exec($curl);
        curl_close($curl);
        return $content;
    }

    /**
     * Get dataset information
     *
     * @param $datasetHash
     * @param $userHash
     *
     * @return string|json
     */
    public function deleteDataset(string $datasetHash, string $userHash)
    {
        if ($_ENV["LOLAPY_API_FAKE"] === "false") {
            return $this->executeCurlRequestPost($this->resourceDatasetDelete, ["dataset" => $datasetHash, "user" => $userHash]);
        } else {
            return false;
        }
    }

    /**
     * Get dataset information
     *
     * @param $datasetHash
     * @param $userHash
     *
     * @return string|json
     */
    public function getDatasetData(string $datasetHash, string $userHash)
    {
        if ($_ENV["LOLAPY_API_FAKE"] === "false") {
            return $this->executeCurlRequestPost($this->resourceDatasetGet, ["dataset" => $datasetHash, "user" => $userHash]);
        } else {
            return '{
                    "size_mb": 512,
                    "files": [
                    {"name": "data.csv", "size_bytes": 524288000}
                    ]
            }';
        }
    }

    /**
     * Add a tag for a scenario
     *
     * @param $scenarioUrlRepository
     * @param $tagName
     * @param $tagHash
     *
     * @return string|json
     */
    public function addScenarioTag(string $scenarioUrlRepository, string $tagName, string $tagHash)
    {
        if ($_ENV["LOLAPY_API_FAKE"] === "false") {
            return $this->executeCurlRequestPost($this->resourceScenarioTagAdd, ["scenario_url_repository" => $scenarioUrlRepository, "tag_name" => $tagName, "tag_hash" => $tagHash]);
        } else {
            return false;
        }
    }

    /**
     * Remove a tag for a scenario
     *
     * @param $scenarioUrlRepository
     * @param $tagName
     * @param $tagHash
     *
     * @return string|json
     */
    public function removeScenarioTag(string $tagHash)
    {
        if ($_ENV["LOLAPY_API_FAKE"] === "false") {
            return $this->executeCurlRequestPost($this->resourceScenarioTagRemove, ["tag_hash" => $tagHash]);
        } else {
            return false;
        }
    }

    /**
     * Get the list of parameters for the scenario
     *
     * @param $tagHash
     *
     * @return string|json
     */
    public function getScenarioParameters(string $tagHash)
    {
        if ($_ENV["LOLAPY_API_FAKE"] === "false") {
            return $this->executeCurlRequestPost($this->resourceScenarioParameters, ["tag_hash" => $tagHash]);
        } else {
            return  '{
            "scenario_name": "Template Scenario",
            "description": "Scenario de test et de template",
            "readme": "Readme of the project",
            "output": [
              "unique_actors.json"
            ],
            "docker_images": [
              {
                "harbor_url": "https://lola.lhs.loria.fr:4443/algo_pnoel/uniq_actors:1.0.0",
                "full_name": "uniq_actors:1.0.0"
              }
            ],
            "switchable_algorithms": [
              {
                "name": "Generate model",
                "description": "Algorithm used to generate a model. The algorithm must connect to a trax database to fetch data.\n The algorithm generate a model in output.",
                "template": "templates/user_model.nf.j2",
                "nf_variable": "userModel"
              },
              {
                "name": "Test data",
                "description": "Algorithm to test data on model generated before. The algorithm must take:\n input model\ninput file containing data (see Readme of this scenario)\nGenerate a list of data",
                "template": "templates/user_test.nf.j2",
                "nf_variable": "userTest"
              }
            ],
            "parameters": [
              {
                "name": "max_actors",
                "description": "limite number of element to get at the end. If value -1, there is no limits",
                "type": "int",
                "default": "-1"
              },
              {
                "name": "element",
                "description": "element to fetch in xapi data.",
                "type": "choices",
                "default": "mbox",
                "choices": [
                  "mbox",
                  "name"
                ]
              }
            ]
            }';
        }
    }
    /**
     * Get the list of parameters for the scenario
     *
     * @param $tagHash
     *
     * @return string|json
     */
    public function getAlgorithmParameters(string $versionAlgorithmHash)
    {
        if ($_ENV["LOLAPY_API_FAKE"] === "false") {
            return $this->executeCurlRequestPost($this->resourceAlgorithmVersionParameters, ["algorithm_hash" => $versionAlgorithmHash]);
        } else {
            return '
           {
                "parameters": [
                {
                        "name": "P2",
                        "description": "gregre",
                        "type": "int",
                        "default": "2"
                },
                {
                        "name": "AZE",
                        "description": "aa",
                        "type": "string",
                        "default": "begrq frq grdegre"
                },
                {
                        "name": "RTY",
                        "description": "zz",
                        "type": "string",
                        "default": "azerty"
                },
                {
                        "name": "P3",
                        "description": "33frze",
                        "type": "string",
                        "default": "gfdgfdgfdgfd",
                        "choices": [
                                "string"
                        ]
                }
                ],
                "readme": "## Préparation de lexécution dun scénario coté Backendprocess avec leurs paramètres:"
            }';
        }
    }

    /**
     * Start the execution of a scenario
     *
     * @param $scenario
     * @param $runHash
     *
     * @return string|json
     */
    public function scenarioExecute(\App\Entity\Scenario $scenario, string $runHash)
    {
        $this->logger->info('Starting scenario execution', [
            'scenario_id' => $scenario->getId(),
            'run_hash' => $runHash,
	    'user' => $this->security->getUser()->getHash(),
            'algorithms' => $scenario->getScenarioAlgorithms()->count()

        ]);

        // prepare the data to send to Lolapy
        $dataExecution = [
            "tag_hash" => $scenario->getTag()->getHash(),
            "run_hash" => $runHash,
            "user_hash" => $this->security->getUser()->getHash(),
            "dataset_hash" => $scenario->getDataset()->getHash(),
            "parameters" => $scenario->getParametres()
        ];

        $this->logger->debug('Data execution prepared', ['data' => $dataExecution]);

        $tabAlgorithms = [];
        foreach($scenario->getScenarioAlgorithms() as $scenarioAlgorithm) {
            /*@var $scenarioAlgorithm \App\Entity\ScenarioAlgorithm */
            $tabAlgorithm["algorithm_hash"] = $scenarioAlgorithm->getAlgorithmVersion()->getHash();
            $tabAlgorithm["nf_variable"] = $scenarioAlgorithm->getNfVariable();
            $tabAlgorithm["parameters"] = $scenarioAlgorithm->getParametres();
            $tabAlgorithms[] = $tabAlgorithm;
            
            $this->logger->debug('Algorithm added to execution', [
                'algorithm_hash' => $tabAlgorithm["algorithm_hash"],
                'nf_variable' => $tabAlgorithm["nf_variable"]
            ]);
        }
        $dataExecution["algorithms"] = $tabAlgorithms;

        $this->logger->info('Total algorithms to execute', ['count' => count($tabAlgorithms)]);

        if ($_ENV["LOLAPY_API_FAKE"] === "false") {
            $this->logger->info('Executing real API call to Lolapy');
            $result = $this->executeCurlRequestPost($this->resourceScenarioExecute, $dataExecution);
            $this->logger->info('API call completed', ['result' => $result]);
            # return $result;
        } else {
            $this->logger->warning('FAKE mode - dumping data instead of API call', ['data' => $dataExecution]);
            dump($dataExecution);
            return false;
        }
    }


    /**
     * Start the preparation of the output of a scenario run
     *
     * @param array $workdir
     * @param string $runHash
     *
     * @return string|json
     */
    public function scenarioPrepareResults(array $workdir, string $runHash, string $tagHash)
    {
        if ($_ENV["LOLAPY_API_FAKE"] === "false") {
            return $this->executeCurlRequestPost($this->resourceScenarioPrepareResults, [
                "workdir" => $workdir,
                "run_hash" => $runHash,
                "tag_hash" => $tagHash
            ]);
        } else {
            return false;
        }
    }

    /**
     * Download the output of a scenario run
     *
     * @param $runHash
     *
     * @return string|json
     */
    public function scenarioGetArchive(string $runHash)
    {
        if ($_ENV["LOLAPY_API_FAKE"] === "false") {
            return $this->executeCurlRequestPost($this->resourceScenarioGetArchive, [
                "run_hash" => $runHash
            ]);
        } else {
            return false;
        }
    }


    /**
     * Add a version for an algorithm
     * 
     * @param $algorithmUrlRepository
     * @param $versionName
     * @param $versionHash
     *
     * @return string|json
     */
    public function addAlgorithmVersion(string $algorithmUrlRepository, string $versionName, string $versionHash)
    {
        if ($_ENV["LOLAPY_API_FAKE"] === "false") {
            return $this->executeCurlRequestPost($this->resourceAlgorithmVersionAdd, [
                    "algorithm_url_repository" => $algorithmUrlRepository,
                    "git_version" => $versionName,
                    "algorithm_hash" => $versionHash
                ]
            );
        } else {
            return false;
        }
    }


    // /**
    //  * Add server usage statistics
    //  * @return string|json
    //  */
    // public function addServerUsage()
    // {
    //     if ($_ENV["LOLAPY_API_FAKE"] === "false") {
    //         // Build the URL
    //         $url = "http://" . $this->url . ":" . $this->port . $this->resourceServerUsage;

    //         // Initiate cURL
    //         $curl = curl_init();

    //         // Set cURL options
    //         curl_setopt($curl, CURLOPT_URL, $url);
    //         curl_setopt($curl, CURLOPT_RETURNTRANSFER, true);

    //         // Execute the cURL request
    //         $response = curl_exec($curl);

    //         // Check for errors
    //         if (curl_errno($curl)) {
    //             $error_message = curl_error($curl);
    //             curl_close($curl);
    //             return "Curl error: " . $error_message;
    //         }

    //         // Close the cURL session
    //         curl_close($curl);

    //         // Decode the JSON response
    //         $json = json_decode($response, true);

    //         return $json;
    //     } else {
    //         return false;
    //     }
    // }
}

