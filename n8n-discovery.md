**Read-only Discovery erfolgreich.** Die Verbindung antwortet; **39 n8n-MCP-Tools** sind in diesem Prozess geladen. Keine Änderungen oder Ausführungen vorgenommen, keine Credential-Werte gelesen.

| Befund | Ergebnis |
|---|---|
| Autorisierter Endpoint | `https://mvstnz1.app.n8n.cloud/mcp-server/http` |
| n8n-Instanzversion | **Nicht über die geladenen Tools oder angebotenen Ressourcen exponiert; unbekannt.** |
| Sichtbares Projekt | `YS0S0X7u4Oc458ln` — own personal project |
| Team-Projekt-Funktion | `teamProjectsEnabled: true` |
| APIC-Workflows | **Keine gefunden**: Namens-/Beschreibungssuche `APIC` und Tagsuche `apic-portfolio` jeweils `count: 0` |
| APIC-Ordner | Keine gefunden |
| Workflow-Tags | Keine vorhanden |
| Credential-Metadaten | `count: 0` |
| Gateway | Verfügbarkeit von Gateway Credits gemeldet; keine Nutzung ausgelöst |
| Instanzinformations-Tool | Keines vorhanden |
| MCP-Ressourcen | Nur `n8n://workflow-sdk/reference`; keine Resource Templates |

Im sichtbaren Projekt existieren zwei fremde Workflows, beide inaktiv und `availableInMCP: false`:

| ID | Name |
|---|---|
| `foreign-workflow-1` | Unrelated workflow 1 |
| `foreign-workflow-2` | Unrelated workflow 2 |

Die Node-Suche meldet folgende Versionen. Dies sind **Node-Versionen, keine n8n-Instanzversionen**:

```text
n8n-nodes-base.webhook                 2.1
n8n-nodes-base.respondToWebhook        1.5
n8n-nodes-base.httpRequest             4.5
n8n-nodes-base.code                    2
n8n-nodes-base.if                      2.3
n8n-nodes-base.switch                  3.4
n8n-nodes-base.merge                   3.2
n8n-nodes-base.wait                    1.1
n8n-nodes-base.scheduleTrigger         1.4
n8n-nodes-base.executeWorkflow         1.3
n8n-nodes-base.executeWorkflowTrigger  1.2
n8n-nodes-base.errorTrigger            1
```

Die folgenden Eingabeschemas stammen aus den tatsächlich geladenen Tool-Deklarationen. `?` bezeichnet optionale Felder; gemeinsame Typen dienen nur der kompakten Darstellung.

```ts
type ObjectMap = { [key: string]: unknown };
type StringMap = { [key: string]: string };

type ExecutionStatus =
  | "canceled" | "crashed" | "error" | "new"
  | "running" | "success" | "unknown" | "waiting";

type Inputs = {
  mcp__n8n__search_projects: {
    limit?: number; // max 100
    query?: string;
    type?: "personal" | "team";
  };

  mcp__n8n__search_nodes: {
    queries: string[];
    usage?: "workflow" | "agentTool";
  };

  mcp__n8n__get_node_types: {
    nodeIds: {
      mode?: string;
      nodeId: string;
      operation?: string;
      resource?: string;
      version?: string;
    }[];
  };

  mcp__n8n__explore_node_resources: {
    credentialId: string;
    credentialType: string;
    currentNodeParameters?: ObjectMap;
    filter?: string;
    methodName: string;
    methodType: "listSearch" | "loadOptions";
    nodeType: string;
    paginationToken?: string;
    version: number;
  };

  mcp__n8n__search_workflows: {
    folderId?: string;
    includeSubfolders?: boolean;
    limit?: number; // max 200
    projectId?: string;
    query?: string;
    sortBy?:
      | "updatedAt:desc" | "updatedAt:asc"
      | "createdAt:desc" | "createdAt:asc"
      | "name:asc" | "name:desc";
    tags?: string[];
  };

  mcp__n8n__get_workflow_details: {
    detailLevel?: "full" | "execution";
    workflowId: string;
  };

  mcp__n8n__create_workflow_from_code: {
    code: string; // max 300000 characters; validate first
    description?: string; // shortened to 255 characters
    folderId?: string; // requires projectId
    name?: string;
    projectId?: string;
    skillsUsed?: string[];
    versionDescription?: string;
    versionName?: string; // tool guidance: always provide
  };

  mcp__n8n__update_workflow: {
    operations: UpdateOperation[];
    skillsUsed?: string[];
    versionDescription?: string;
    versionName?: string;
    workflowId: string;
  };

  mcp__n8n__publish_workflow: {
    versionId?: string;
    workflowId: string;
  };

  mcp__n8n__unpublish_workflow: {
    workflowId: string;
  };

  mcp__n8n__execute_workflow: {
    executionMode: "manual" | "production";
    inputs?:
      | { chatInput: string }
      | { formData: ObjectMap }
      | {
          webhookData: {
            body?: ObjectMap;
            headers?: StringMap;
            method?:
              | "GET" | "POST" | "PUT" | "DELETE"
              | "PATCH" | "HEAD" | "OPTIONS";
            query?: StringMap;
          };
        };
    triggerNodeName?: string;
    workflowId: string;
  };

  mcp__n8n__test_workflow: {
    pinData: { [nodeName: string]: ObjectMap[] };
    timeout?: number;
    triggerNodeName?: string;
    workflowId: string;
  };

  mcp__n8n__search_workflow_executions: {
    lastId?: string;
    limit?: number; // max 200
    startedAfter?: string;
    startedBefore?: string;
    status?: ExecutionStatus[];
    workflowId?: string;
  };

  mcp__n8n__get_workflow_execution: {
    executionId: string;
    includeData?: boolean; // default false: metadata only
    nodeNames?: string[];
    truncateData?: number;
    workflowId: string;
  };

  mcp__n8n__list_credentials: {
    limit?: number; // max 200
    onlySharedWithMe?: boolean;
    projectId?: string;
    query?: string;
    type?: string;
  };

  mcp__n8n__list_n8n_gateway_services: {};

  mcp__n8n__search_folders: {
    limit?: number; // max 100
    projectId: string;
    query?: string;
  };

  mcp__n8n__list_workflow_tags: {
    limit?: number; // max 500
  };
};
```

Vollständige Operationsstruktur für `mcp__n8n__update_workflow`:

```ts
type UpdateOperation = {
  type:
    | "updateNodeParameters"
    | "setNodeParameter"
    | "addNode"
    | "removeNode"
    | "renameNode"
    | "addConnection"
    | "removeConnection"
    | "setNodeCredential"
    | "setNodePosition"
    | "setNodeDisabled"
    | "setNodeSettings"
    | "setWorkflowMetadata"
    | "setWorkflowSettings"
    | "addTags"
    | "removeTags"
    | "setNodeGroups";

  connectionType?: string;
  credentialId?: string;
  credentialKey?: string;
  credentialName?: string;
  description?: string;
  disabled?: boolean;
  name?: string;
  names?: string[];
  newName?: string;

  node?: {
    credentials?: {
      [key: string]: { id?: string; name: string };
    };
    disabled?: boolean;
    id?: string;
    name: string;
    notes?: string;
    parameters?: ObjectMap;
    position?: number[];
    type: string;
    typeVersion: number;
  };

  nodeGroups?: {
    description?: string;
    id?: string;
    name: string;
    nodeNames: string[];
  }[];

  nodeName?: string;
  oldName?: string;
  parameters?: ObjectMap;
  path?: string;
  position?: number[];
  replace?: boolean;

  settings?: {
    alwaysOutputData?: boolean;
    callerIds?: string;
    callerPolicy?:
      | "any" | "none"
      | "workflowsFromAList" | "workflowsFromSameOwner";
    errorWorkflow?: string;
    executeOnce?: boolean;
    executionOrder?: "v0" | "v1";
    executionTimeout?: number;
    maxTries?: number;
    onError?:
      | "stopWorkflow"
      | "continueRegularOutput"
      | "continueErrorOutput";
    retryOnFail?: boolean;
    saveDataErrorExecution?: "DEFAULT" | "all" | "none";
    saveDataSuccessExecution?: "DEFAULT" | "all" | "none";
    saveExecutionProgress?: boolean | "DEFAULT";
    saveManualExecutions?: boolean | "DEFAULT";
    timeSavedPerExecution?: number;
    timezone?: string;
    waitBetweenTries?: number;
  };

  source?: string;
  sourceIndex?: number;
  target?: string;
  targetIndex?: number;
  value?: unknown;
};
```

Die später erforderlichen SDK- und Validierungswerkzeuge sind ebenfalls vorhanden:

```ts
type PreparationInputs = {
  mcp__n8n__get_workflow_sdk_reference: {
    section?:
      | "patterns" | "patterns_detailed" | "expressions"
      | "functions" | "rules" | "import"
      | "guidelines" | "design" | "all";
  };

  mcp__n8n__get_workflow_best_practices: {
    technique:
      | "scheduling" | "chatbot" | "form_input"
      | "scraping_and_research" | "monitoring" | "enrichment"
      | "triage" | "content_generation" | "document_processing"
      | "data_extraction" | "data_analysis" | "data_transformation"
      | "data_persistence" | "notification" | "knowledge_base"
      | "human_in_the_loop" | "web_app" | "list";
  };

  mcp__n8n__validate_workflow: {
    code: string;
  };

  mcp__n8n__validate_node_config: {
    nodes: {
      isToolNode?: boolean;
      name?: string;
      parameters?: ObjectMap;
      subnodes?: unknown;
      type: string;
      typeVersion?: number;
    }[];
  };
};
```

Weitere geladene Tools, außerhalb der angefragten Kernschemas:

```text
mcp__n8n__add_data_table_column
mcp__n8n__add_data_table_rows
mcp__n8n__archive_workflow
mcp__n8n__create_data_table
mcp__n8n__create_folder
mcp__n8n__delete_data_table_column
mcp__n8n__get_data_table_rows
mcp__n8n__get_workflow_history
mcp__n8n__get_workflow_version
mcp__n8n__get_workflow_versions_diff
mcp__n8n__move_workflows_to_folder
mcp__n8n__prepare_workflow_pin_data
mcp__n8n__rename_data_table
mcp__n8n__rename_data_table_column
mcp__n8n__restore_workflow_version
mcp__n8n__search_data_tables
mcp__n8n__update_folder
```

Für die weitere Implementierung gelten diese verifizierten Schnittstelleneigenschaften:

- Erstellung erfolgt über **SDK-Code**; kein separates Create-Tool für rohes Workflow-JSON ist geladen.
- `update_workflow` beschreibt den Operationsbatch als atomar.
- `execute_workflow` verlangt ausdrücklich `manual` oder `production`. Bei Eingabepayload ist `triggerNodeName` erforderlich; Schedule-/Manual-Trigger erhalten kein `inputs`.
- `test_workflow` führt aus und ist **kein rein lesendes Validierungswerkzeug**. Pin-Items benötigen die Form `{"json": {...}}`.
- `list_credentials` liefert ausschließlich Metadaten wie ID, Name, Typ, Projekt und Scopes.
- Schreib-, Publish- und Execution-Tools sind **vorhanden, aber nicht auf Berechtigung oder Funktion getestet**. Es wurden keine Execution-IDs erzeugt.