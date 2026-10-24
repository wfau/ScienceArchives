<template>
  <div v-if="hasAccess === false" class="m-4 alert alert-danger">
    <h5 class="alert-heading fw-bold">Access Restricted</h5>
    <p class="mb-1">{{ accessDeniedMessage }}</p>
    <p class="fs-7 text-secondary">{{ accessDeniedDetail }}</p>
  </div>

  <div v-else-if="hasAccess === null || loading" class="d-flex flex-column align-items-center justify-content-center py-5">
    <div class="spinner-border text-info" style="width: 3rem; height: 3rem;" role="status">
      <span class="visually-hidden">Loading...</span>
    </div>
    <p class="mt-4 text-info fw-semibold">Synchronizing schemas and components...</p>
  </div>

  <div v-else class="query-workspace">
    <!-- PERSISTENT LEFT PANEL: SCHEMA TREE -->
    <div class="split left p-4" v-if="schemaData && Object.keys(schemaData).length">
      <h5 class="mb-3 d-flex align-items-center gap-2">
        <i class="bi bi-database text-primary"></i> Database Schema
      </h5>
      <div>
        <ul class="tree">
          <li>
            <details open>
              <summary class="fw-semibold">GES</summary>
              <ul>
                <li v-for="(tableSchema, schemaName) in schemaData" :key="schemaName">
                  <details :open="schemaName === currentSchema">
                    <summary class="text-info fw-semibold">{{ schemaName }}</summary>
                    <ul>
                      <li v-for="table of Object.entries({...tableSchema.tables, ...tableSchema.views}).sort()" :key="table[0]">
                        <details>
                          <summary>
                            <span 
                              draggable="true" 
                              @dragstart="handleTreeDragStart($event, table[0])" 
                              :title="table[1].markdown && table[1].markdown[0]?.h"
                              class="draggable-asset text-light-emphasis"
                            >
                              {{ table[0] }}
                              <RouterLink :to="{ name: 'database-schema', query: {schema: schemaName, table: table[0]}}" class="info-badge" title="View schema details">
                                ?
                              </RouterLink>
                            </span>
                          </summary>
                          <ul>
                            <li v-for="col in table[1].columns" :key="col.name">
                              <span 
                                draggable="true" 
                                @dragstart="handleTreeDragStart($event, col.name)" 
                                :title="col.description"
                                :class="(table[1].primary_keys || []).includes(col.name) ? 'text-decoration-underline': ''"
                                class="draggable-asset"
                              >
                                {{ col.name }}
                              </span>
                              <span class="key-icon" v-if="(table[1].primary_keys || []).includes(col.name)" title="Primary Key"></span>
                              <sup class="fst-italic text-warning" title="Foreign Key" v-if="(foreignKeys(table[1]) || []).includes(col.name)">
                                FK
                              </sup>
                              :
                              <span class="fst-italic text-secondary">{{ col.type }}</span>
                            </li>
                          </ul>
                        </details>
                      </li>
                    </ul>
                  </details>
                </li>
              </ul>
            </details>
          </li>
        </ul>
      </div>
    </div>

    <!-- RIGHT PANEL: WORKSPACE CARDS AND TABS -->
    <div class="split right p-4">
      <!-- Tabs Navigation -->
      <ul class="nav nav-tabs mb-4 px-1" role="tablist">
        <li class="nav-item" role="presentation">
          <button 
            class="nav-link" 
            :class="{ active: activeTab === 'generator' }" 
            @click="switchTab('generator')" 
            type="button"
          >
            🪄 SQL Generator
          </button>
        </li>
        <li class="nav-item" role="presentation">
          <button 
            class="nav-link" 
            :class="{ active: activeTab === 'editor' }" 
            @click="switchTab('editor')" 
            type="button"
          >
            Freeform SQL Workspace
          </button>
        </li>
      </ul>

      <div class="tab-content">
        <!-- TAB 1: SQL GENERATION SYSTEM -->
        <div v-show="activeTab === 'generator'" class="tab-pane fade show active">
          <div class="card border mb-4">
            <div class="card-header bg-body-secondary border-bottom py-3 d-flex justify-content-between align-items-center">
              <div>
                <h5 class="mb-0 text-body-emphasis">Generate SQL Code</h5>
                <small class="text-body-secondary">Select a data release and describe your goal.</small>
              </div>
              <span v-if="jobStatus" class="badge" :class="statusBadgeClass">Status: {{ jobStatus }}</span>
            </div>

            <div class="card-body p-4">
              <!-- Processing State Banner -->
              <transition name="fade">
                <div v-if="jobStatus === 'PROCESSING' || jobStatus === 'PENDING'" class="processing-banner text-center mb-4 py-4 rounded">
                  <div class="spinner-glow-wrapper mx-auto">
                    <div class="spinner-border text-info" style="width:3.5rem;height:3.5rem;" role="status"></div>
                  </div>
                  <p class="mt-3 mb-1 text-info fw-semibold">{{ submitButtonText }}</p>
                  <small class="text-body-secondary">Please wait while your SQL query is being compiled...</small>
                </div>
              </transition>

              <form @submit.prevent="submitGeneratorForm">
                <!-- Data Release Step -->
                <div class="mb-4">
                  <label for="releaseSelect" class="form-label fw-bold d-flex align-items-center gap-2">
                    <span class="step-badge">1</span> Active Data Release
                  </label>
                  <select id="releaseSelect" v-model="currentSchema" class="form-select" :disabled="jobStatus === 'PROCESSING' || jobStatus === 'PENDING'">
                    <option v-for="key in schemaKeys" :key="key" :value="key">{{ key }}</option>
                  </select>
                </div>

                <!-- Text Description Target -->
                <div class="mb-4">
                  <label for="promptTextarea" class="form-label fw-bold d-flex align-items-center gap-2">
                    <span class="step-badge">2</span> Describe the SQL instructions<span class="text-danger">*</span>
                  </label>
                  <textarea 
                    id="promptTextarea" 
                    v-model="promptText" 
                    rows="5" 
                    required 
                    class="form-control" 
                    placeholder="e.g. List GES spectrum values where target signal is stronger than matching field elements..."
                    :disabled="jobStatus === 'PROCESSING' || jobStatus === 'PENDING'"
                  ></textarea>
                </div>

                <!-- Optional view hints -->
                <div class="mb-4">
                  <details class="border rounded p-2" :open="selectedViews.length > 0">
                    <summary class="form-label fw-bold d-flex align-items-center gap-2 mb-0">
                      <span class="step-badge">3</span> Prefer Specific Views (optional)
                      <span v-if="selectedViews.length" class="badge text-bg-info">{{ selectedViews.length }}</span>
                    </summary>
                    <div class="mt-2">
                      <small class="text-body-secondary fs-7">
                        Indicate views likely relevant to your request (e.g. <code>RecommendedAstroAnalysis</code>). This is a hint to the AI, not a restriction.
                      </small>
                      <div class="view-options mt-2">
                        <button
                          v-for="viewName in viewNames"
                          :key="viewName"
                          type="button"
                          class="btn btn-sm"
                          :class="selectedViews.includes(viewName) ? 'btn-primary' : 'btn-outline-secondary'"
                          :title="viewDescriptions[viewName] || viewName"
                          @click="toggleView(viewName)"
                        >
                          {{ viewName }}
                        </button>
                      </div>
                      <small v-if="!viewNames.length" class="text-body-secondary fs-7">No views available in this data release.</small>
                    </div>
                  </details>
                </div>

                <!-- Run Compilation -->
                <div class="d-flex justify-content-between align-items-center mt-3">
                  <button v-if="jobStatus === 'PROCESSING' || jobStatus === 'PENDING'" type="button" class="btn btn-outline-danger btn-sm" @click="stopMonitoring">
                    Cancel Compilation
                  </button>
                  <div class="ms-auto d-flex gap-2">
                    <button type="button" class="btn btn-outline-secondary" @click="resetFormState" :disabled="jobStatus === 'PROCESSING' || jobStatus === 'PENDING'">
                      Reset Options
                    </button>
                    <button type="submit" class="btn btn-primary" :disabled="!promptText.trim() || jobStatus === 'PROCESSING' || jobStatus === 'PENDING'">
                      {{ submitButtonText }}
                    </button>
                  </div>
                </div>
              </form>

              <!-- Flow Errors -->
              <div ref="jobErrorRef" v-if="jobErrorMessage" class="mt-4 alert alert-danger" role="alert">
                <h6 class="fw-bold">AI Processing Encountered an Error</h6>
                <p class="mb-0 fs-7">{{ jobErrorMessage }}</p>
              </div>

              <!-- Output Box to Push Target query to Editor -->
              <div ref="sqlResultRef" v-if="queryTextResult" class="mt-4 pt-4 border-top">
                <div class="card border-success">
                  <div class="card-header bg-success-subtle text-success-emphasis border-success py-2 d-flex justify-content-between align-items-center">
                    <span class="fw-bold">Generated SQL Ready</span>
                    <div class="d-flex gap-2">
                      <button type="button" class="btn btn-outline-secondary btn-sm" @click="copyToClipboard">{{ copyButtonText }}</button>
                      <button type="button" class="btn btn-success btn-sm text-white fw-bold d-flex align-items-center gap-1" @click="sendQueryResultToEditor">
                        Review &amp; Edit in Workspace <i class="bi bi-arrow-right-short"></i>
                      </button>
                    </div>
                  </div>
                  <div class="card-body p-0">
                    <pre class="m-0 p-3 bg-body-tertiary border-0 text-success font-monospace overflow-auto" style="max-height: 250px; font-size: 0.9rem;"><code>{{ queryTextResult }}</code></pre>
                  </div>
                </div>
              </div>

            </div>
          </div>
        </div>

        <!-- TAB 2: INTERACTIVE CODE EDITOR WORKSPACE -->
        <div v-show="activeTab === 'editor'" class="tab-pane fade show active">
        <div class="card border mb-4">
            
            <!-- Card Header (Matching AI Tab layout and background styling) -->
            <div class="card-header bg-body-secondary border-bottom py-3 d-flex justify-content-between align-items-center">
            <div>
                <h5 class="mb-0 text-body-emphasis">Freeform SQL Workspace</h5>
                <small class="text-body-secondary">
                Enter or review SQL instructions against the selected data release.
                </small>
            </div>
            <!-- Environment Context Badge -->
                <span class="badge bg-primary text-white font-monospace">
                    Active Data Release: {{ currentSchema || 'None Selected' }}
                </span>
            </div>

            <!-- Card Body -->
            <div class="card-body p-4">
            
            <!-- STEP 1: Release Selector -->
            <div class="mb-4">
                <label for="workspaceReleaseSelect" class="form-label fw-bold d-flex align-items-center gap-2">
                    <span class="step-badge">1</span> Active Data Release
                </label>
                <select id="workspaceReleaseSelect"  v-model="currentSchema" class="form-select">
                    <option v-for="(value, key) in schemaData" :key="key" :value="key">
                        {{ key }}
                    </option>
                </select>
            </div>

            <!-- STEP 2: SQL Editor Section -->
            <div id="div_id_editor" class="mb-4">
                <label class="form-label fw-bold d-flex align-items-center gap-2">
                <span class="step-badge">2</span> SQL Input Code Editor 
                <span class="text-body-secondary fw-normal fs-7">
                    (Supports autosuggest completion, formatting, and tree drag-drop insertion)
                </span>
                </label>
                <div id="editor" ref="editor" class="form-control p-0"></div>
            </div>

            <!-- Run Controls Dashboard -->
            <div class="d-flex justify-content-between align-items-center mt-3 pt-2">
                <small class="text-body-secondary">
                Clicking run executes your queries directly, with outputs linked on the results timeline.
                </small>
                <button 
                class="btn btn-primary px-4 fw-bold" 
                @click="submitQueryRun"
                :disabled="!currentSchema"
                >
                Run Query &amp; Load Results
                </button>
            </div>

            </div>
        </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { useTemplateRef, ref, computed, onMounted, watch, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import router from '@/router/index'

// CodeMirror Dependencies
import { EditorState, Compartment } from '@codemirror/state';
import { indentWithTab, history, defaultKeymap, historyKeymap } from '@codemirror/commands';
import { indentOnInput, indentUnit, bracketMatching, syntaxHighlighting, defaultHighlightStyle } from '@codemirror/language';
import { closeBrackets, autocompletion, closeBracketsKeymap, completionKeymap } from '@codemirror/autocomplete';
import { lineNumbers, highlightActiveLineGutter, highlightSpecialChars, highlightActiveLine, keymap, EditorView } from '@codemirror/view';
import { oneDark } from "@codemirror/theme-one-dark";
import { sql, PostgreSQL, SQLDialect } from "@codemirror/lang-sql";

// Core Actions & API Endpoints
import { getQueryResult } from '@/api/get_result';
import { getQueryTemplate, postQuery } from '@/api/query'
import { getDatabaseSchema, type Schemas, type TableDefinition } from '@/api/schema';

const route = useRoute()

// ── Shared Workspace States ──────────────────────────────────────────────────
const hasAccess = ref<boolean | null>(null);
const accessDeniedMessage = ref("You must have permissions validated to utilize the database system.");
const accessDeniedDetail = ref("");
const schemaData = ref<Schemas>({})
const currentSchema = ref<string>('')
const loading = ref<boolean>(false)
const workspaceDoc = ref<string>('SELECT ')
const csrfToken = ref('')
const activeTab = ref<'generator' | 'editor'>('generator')

// ── Generator States ────────────────────────────────────────────────────────
const promptText = ref<string>('')
const selectedViews = ref<string[]>([])
const queryTextResult = ref<string | null>(null)
const activeTaskId = ref<string | null>(null)
const jobStatus = ref<'PENDING' | 'PROCESSING' | 'SUCCESS' | 'FAILED' | null>(null)
const jobErrorMessage = ref<string | null>(null)
const copySuccess = ref<boolean>(false)
let pollInterval: number | null = null

// Template refs
const editorElement = useTemplateRef('editor')
const editorView = ref<EditorView | null>(null)
const jobErrorRef = ref<HTMLElement | null>(null)
const sqlResultRef = ref<HTMLElement | null>(null)

const editorTheme = new Compartment()
let systemTheme = document.documentElement.getAttribute('data-bs-theme')
if (systemTheme === 'auto') {
  systemTheme = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
}

// ── CodeMirror SQL Definitions Mapping ────────────────────────────────────────
const codeSchema = computed(() => {
  const result: any = {}
  if (currentSchema.value && schemaData.value[currentSchema.value]) {
    const cs = schemaData.value[currentSchema.value]
    for (const tableName of Object.keys(cs.tables).sort()) {
      result[tableName] = Object.keys(cs.tables[tableName].columns)
    }
    for (const viewName of Object.keys(cs.views).sort()) {
      result[viewName] = Object.keys(cs.views[viewName].columns)
    }
  }
  return result
})

const schemaKeys = computed<string[]>(() => Object.keys(schemaData.value))

const viewNames = computed<string[]>(() => {
  const cs = currentSchema.value ? schemaData.value[currentSchema.value] : undefined;
  if (!cs) return [];
  return Object.keys(cs.views || {}).sort();
})

const viewDescriptions = computed<Record<string, string>>(() => {
  const cs = currentSchema.value ? schemaData.value[currentSchema.value] : undefined;
  if (!cs) return {};
  const desc: Record<string, string> = {};
  for (const [name, def] of Object.entries(cs.views || {})) {
    const first = (def.markdown || [])[0];
    const text = first?.h || first?.t || '';
    desc[name] = text.trim();
  }
  return desc;
})

const toggleView = (name: string) => {
  const idx = selectedViews.value.indexOf(name);
  if (idx > -1) selectedViews.value.splice(idx, 1);
  else selectedViews.value.push(name);
}

const foreignKeys = (table: TableDefinition) => {
  const result: string[] = []
  for (const fk of (table.references || [])) {
    result.push(...fk.sourceCol)
  }
  return result
}

// ── Status Displays ──────────────────────────────────────────────────────────
const statusBadgeClass = computed(() => {
  if (jobStatus.value === 'SUCCESS') return 'bg-success text-white';
  if (jobStatus.value === 'PROCESSING') return 'bg-warning text-black';
  if (jobStatus.value === 'FAILED') return 'bg-danger text-white';
  return 'bg-secondary text-white';
});

const submitButtonText = computed(() => {
  if (jobStatus.value === 'PENDING') return 'Enqueuing...';
  if (jobStatus.value === 'PROCESSING') return 'Generating SQL Code...';
  return 'Compile SQL Request';
});

const copyButtonText = computed(() => (copySuccess.value ? 'Copied!' : 'Copy SQL'));

// ── Access check and Initialization ──────────────────────────────────────────
const checkAccess = async (): Promise<void> => {
  try {
    const response = await fetch('/api/v1/queries/generate/');
    if (response.status === 403) {
      const data = await response.json().catch(() => ({}));
      hasAccess.value = false;
      accessDeniedMessage.value = data.error || "Permission error, review dashboard rules.";
      accessDeniedDetail.value = data.detail || '';
      return;
    }
    if (response.ok) {
      hasAccess.value = true;
      return;
    }
    hasAccess.value = false;
  } catch {
    hasAccess.value = false;
  }
};

const loadSchema = async () => {
  loading.value = true
  try {
    const res = await getDatabaseSchema()
    if (res) {
      schemaData.value = res
      if (Object.keys(res).length >= 1) {
        currentSchema.value = Object.keys(res)[0]
      }
    }
  } catch (error) {
    console.error('Failed to parse database references: ', error);
  } finally {
    loading.value = false
  }
}

// ── CodeMirror Editor Instance Manager ───────────────────────────────────────
const buildEditorInstance = () => {
  if (editorView.value) {
    editorView.value.destroy();
  }

  if (!editorElement.value) return;

  const sqlOptions = {
    upperCaseKeywords: true,
    dialect: SQLDialect.define({ ...PostgreSQL.spec, caseInsensitiveIdentifiers: true }),
    schema: codeSchema.value,
  };

  const extensions = [
    lineNumbers(),
    highlightActiveLineGutter(),
    highlightSpecialChars(),
    history(),
    indentUnit.of("    "),
    indentOnInput(),
    bracketMatching(),
    closeBrackets(),
    autocompletion(),
    highlightActiveLine(),
    keymap.of([
      indentWithTab,
      ...closeBracketsKeymap,
      ...defaultKeymap,
      ...historyKeymap,
      ...completionKeymap,
    ]),
    sql(sqlOptions),
    syntaxHighlighting(defaultHighlightStyle, { fallback: true }),
    editorTheme.of(systemTheme === 'dark' ? oneDark : []),
  ];

  editorView.value = new EditorView({
    doc: workspaceDoc.value,
    extensions,
    parent: editorElement.value
  });
};

// Rebuild Editor on theme / query structure schema updates
watch([codeSchema, currentSchema], () => {
  if (activeTab.value === 'editor') {
    buildEditorInstance();
  }
});

// Views differ per data release; drop any selections that no longer apply
watch(currentSchema, () => {
  selectedViews.value = selectedViews.value.filter((v) => viewNames.value.includes(v));
});

// Refresh / Render CodeMirror viewport on visible tab focus
const switchTab = async (tab: 'generator' | 'editor') => {
  activeTab.value = tab;
  if (tab === 'editor') {
    await nextTick();
    buildEditorInstance();
  }
};

// ── Drag & Drop Logic for Left Panel Tree -> Editor text dump ────────────────
const handleTreeDragStart = (e: DragEvent, text: string) => {
  if (!e.dataTransfer) return;
  
  // CodeMirror uses text/plain to drop code snippets directly at the cursor
  e.dataTransfer.setData('text/plain', text);
};

// ── Tab 1: AI Call Pipeline and Watchers ─────────────────────────────────────
const submitGeneratorForm = async (): Promise<void> => {
  if (!promptText.value.trim()) return;

  jobErrorMessage.value = null;
  queryTextResult.value = null;
  jobStatus.value = 'PENDING';

  try {
    const response = await fetch('/api/v1/queries/generate/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        data_release: currentSchema.value,
        tables: [...selectedViews.value],
        description: promptText.value.trim(),
      }),
    });

    if (response.status === 403) {
      hasAccess.value = false;
      return;
    }

    if (!response.ok) throw new Error('Could not submit generator instruction matrix.');

    const data = await response.json();
    activeTaskId.value = data.task_id;
    jobStatus.value = data.status;
    startTaskPolling(data.task_id);
  } catch (err: any) {
    jobErrorMessage.value = err.message || 'Workflow connection error.';
    jobStatus.value = null;
  }
};

const startTaskPolling = (taskId: string) => {
  if (pollInterval) clearInterval(pollInterval);
  pollInterval = window.setInterval(async () => {
    try {
      const response = await fetch(`/api/v1/queries/generate/poll/${taskId}/`);
      if (response.status === 403) {
        hasAccess.value = false;
        stopMonitoring();
        return;
      }
      if (!response.ok) throw new Error('Task tracker polling lost.');
      
      const data = await response.json();
      jobStatus.value = data.status;

      if (data.status === 'SUCCESS') {
        queryTextResult.value = data.sql;
        stopMonitoring();
        await nextTick();
        sqlResultRef.value?.scrollIntoView({ behavior: 'smooth' });
      } else if (data.status === 'FAILED') {
        jobErrorMessage.value = data.error || 'The model generation process encountered errors.';
        stopMonitoring();
        await nextTick();
        jobErrorRef.value?.scrollIntoView({ behavior: 'smooth' });
      }
    } catch (err: any) {
      jobErrorMessage.value = err.message || 'Monitoring stream failed.';
      stopMonitoring();
    }
  }, 2000);
};

const stopMonitoring = () => {
  if (pollInterval) {
    clearInterval(pollInterval);
    pollInterval = null;
  }
  if (jobStatus.value === 'PENDING' || jobStatus.value === 'PROCESSING') {
    jobStatus.value = null;
    activeTaskId.value = null;
  }
};

// ── Pass Generated Code visually back and switch View state ──────────────────
const sendQueryResultToEditor = () => {
  if (queryTextResult.value) {
    workspaceDoc.value = queryTextResult.value;
    switchTab('editor');
  }
};

// ── Tab 2: Freeform Workspace Actions ────────────────────────────────────────
const submitQueryRun = () => {
  const query = editorView.value ? editorView.value.state.doc.toString() : workspaceDoc.value;
  if (query && currentSchema.value) {
    postQuery(query, currentSchema.value, csrfToken.value)
      .then((res) => {
        router.push({ name: 'query-result', params: { id: res.id } });
      })
      .catch((err) => console.error('Workspace run error:', err));
  }
};

const copyToClipboard = async () => {
  if (!queryTextResult.value) return;
  try {
    await navigator.clipboard.writeText(queryTextResult.value);
    copySuccess.value = true;
    setTimeout(() => { copySuccess.value = false }, 2000);
  } catch (err) {
    console.error('Failed to write to clipboard:', err);
  }
};

const resetFormState = () => {
  promptText.value = '';
  selectedViews.value = [];
  queryTextResult.value = null;
  activeTaskId.value = null;
  jobStatus.value = null;
  jobErrorMessage.value = null;
};

// ── Retrieve CSRF and Initial Routing hooks ──────────────────────────────────
onMounted(async () => {
  await checkAccess();
  if (hasAccess.value === true) {
    await loadSchema();

    // Load templates/queries via URL routes if present
    if (route.params.id) {
      const qid = parseInt(route.params.id as string);
      const data = await getQueryResult(qid);
      workspaceDoc.value = data.query;
      currentSchema.value = data.schema;
      switchTab('editor'); // automatically open workspace
    } else if (route.params.tid) {
      const tid = parseInt(route.params.tid as string);
      const data = await getQueryTemplate(tid);
      workspaceDoc.value = data.query;
      currentSchema.value = data.schema;
      switchTab('editor'); // automatically open workspace
    }
  }

  fetch('/api/csrf')
    .then(res => res.text())
    .then(text => new DOMParser().parseFromString(text, "text/html"))
    .then(dom => (<HTMLInputElement>dom.querySelector('[name=csrfmiddlewaretoken]'))?.value)
    .then(token => {
      if (token) csrfToken.value = token;
    });
});
</script>

<style scoped>
/* Unified Flex Workspace Split */
.query-workspace {
  display: flex;
  height: calc(100vh - 60px);
  width: 100%;
  overflow: hidden;
  background-color: var(--bs-body-bg);
}

.split {
  height: 100%;
  overflow-y: auto;
}

.left {
  width: 25%;
  border-right: 1px solid var(--bs-border-color);
  background: var(--bs-body-tertiary);
}

.right {
  width: 70%;
}

/* Tab System Stylings */
.nav-tabs .nav-link {
  color: var(--bs-body-color);
  font-weight: 500;
  transition: all 0.2s ease-in-out;
}
.nav-tabs .nav-link.active {
  font-weight: 600;
  color: var(--bs-primary);
  border-bottom-color: var(--bs-primary) !important;
}

/* =========================================================================
   THEME ADAPTIVE SQL CODEMIRROR
   ========================================================================= */
#editor {
  height: 50vh;
  width: 100%;
  overflow: hidden;
  border: 1px solid var(--bs-border-color);
  background-color: var(--bs-body-bg);
  color: var(--bs-body-color);
}

/* Targets internal CodeMirror nodes to inherit the background/body color */
:deep(.cm-editor) {
  height: 100%;
  width: 100%;
  background-color: transparent !important;
}

:deep(.cm-scroller) {
  overflow: auto;
  font-family: var(--bs-font-monospace);
}

/* Keeps gutters looking crisp with matching border lines */
:deep(.cm-gutters) {
  background-color: var(--bs-tertiary-bg) !important;
  color: var(--bs-secondary-color) !important;
  border-right: 1px solid var(--bs-border-color) !important;
}

/* Steps and Helpers badges */
.step-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 1.5rem;
  height: 1.5rem;
  border-radius: 50%;
  background: rgba(var(--bs-primary-rgb), 0.15);
  border: 1px solid rgba(var(--bs-primary-rgb), 0.45);
  color: var(--bs-primary);
  font-size: 0.75rem;
  font-weight: 700;
}

.draggable-asset {
  cursor: grab;
  padding: 2px 4px;
  border-radius: 3px;
  display: inline-block;
  transition: background-color 0.15s;
}
.draggable-asset:hover {
  background-color: var(--bs-secondary-bg);
}

.cursor-grab { cursor: grab; }
.fs-7 { font-size: 0.85rem; }
.fs-8 { font-size: 0.74rem; }

/* Optional view selection (Step 3) */
.view-options {
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem;
}

/* Processing Visual Pulses */
@keyframes glow-pulse {
  0%, 100% { box-shadow: 0 0 8px  4px rgba(var(--bs-info-rgb), 0.25); }
  50%       { box-shadow: 0 0 28px 10px rgba(var(--bs-info-rgb), 0.70); }
}
.spinner-glow-wrapper {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  padding: 10px;
  animation: glow-pulse 1.4s ease-in-out infinite;
}
.processing-banner {
  background: rgba(var(--bs-info-rgb), 0.05);
  border: 1px solid rgba(var(--bs-info-rgb), 0.20);
}

/* Left panel directory look */
ul.tree, ul.tree ul {
  list-style-type: none;
  padding-left: 15px;
  margin: 0;
}
ul.tree li {
  margin: 5px 0;
}
summary {
  cursor: pointer;
  outline: none;
  user-select: none;
}
summary::-webkit-details-marker {
  color: var(--bs-primary);
}
.info-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 14px;
  height: 14px;
  font-size: 9px;
  background-color: var(--bs-secondary);
  color: white;
  border-radius: 50%;
  text-decoration: none;
  vertical-align: middle;
  margin-left: 2px;
}
/* Grab Hands & Interaction Cues */
.asset-row-interactive,
.asset-row-selected-interactive {
  cursor: grab; /* Webkit / Mozilla native "Open Hand Window" */
  user-select: none; /* Prevents text highlighted selects on double-click */
  transition: all 0.15s ease;
}

.asset-row-interactive:active,
.asset-row-selected-interactive:active {
  cursor: grabbing; /* Clenched hand grip cue when drag/mousedown is active */
}

/* Row Hovers */
.asset-row-interactive:hover {
  background-color: var(--bs-secondary-bg);
  border-color: var(--bs-primary-border-subtle);
}

.asset-row-selected-interactive {
  background-color: rgba(var(--bs-primary-rgb), 0.04);
}
.asset-row-selected-interactive:hover {
  background-color: rgba(var(--bs-danger-rgb), 0.06);
  border-color: var(--bs-danger-border-subtle) !important;
}

/* Revert pointer for buttons inside the rows */
.asset-row-interactive button,
.asset-row-selected-interactive button {
  cursor: pointer;
}

/* =========================================================================
   COMPACT DATABASE SCHEMA TREE VIEW
   ========================================================================= */
ul.tree, ul.tree ul {
    list-style-type: none;
    padding-left: 12px; /* Snug indent for nested datasets */
    margin: 0;
}

ul.tree li {
    margin: 2px 0;       /* Replaced loose 5px spacing with a tight 1px gap */
    line-height: 1.2;    /* Tighter text wrapping on schema names */
    font-size: 0.85rem;  /* Keeps column data precise and neat */
}

ul.tree summary {
    cursor: pointer;
    outline: none;
    user-select: none;
    padding: 1px 0;      /* Minimal hit target spacing */
}

ul.tree summary::-webkit-details-marker {
    color: var(--bs-primary);
}

/* Draggable tree nodes styling */
.draggable-asset {
    cursor: grab;
    padding: 0px 2px;
    border-radius: 3px;
    display: inline-block;
    transition: background-color 0.1s ease;
}
.draggable-asset:hover {
    background-color: var(--bs-secondary-bg);
}
</style>
