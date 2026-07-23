<template>
  <div class="container py-4">
    <div class="card shadow-sm">

      <div class="card-header bg-body-secondary border-bottom py-3 d-flex justify-content-between align-items-center">
        <div>
          <h4 class="mb-0 text-body-emphasis">Generate SQL Query Agent</h4>
          <small class="text-body-secondary">
            Select a data release, describe your goal, then optionally refine with tables.
          </small>
        </div>
        <span v-if="jobStatus" class="badge" :class="statusBadgeClass">
          Status: {{ jobStatus }}
        </span>
      </div>

      <div class="card-body p-4">

        <!-- STATE 1 — Permission probe -->
        <div v-if="hasAccess === null" class="text-center py-5">
          <div class="spinner-glow-wrapper mx-auto">
            <div class="spinner-border text-info" style="width:3rem;height:3rem;" role="status">
              <span class="visually-hidden">Verifying access…</span>
            </div>
          </div>
          <p class="mt-4 text-info fw-semibold">Verifying permissions…</p>
        </div>

        <!-- STATE 2 — Permission denied -->
        <div v-else-if="hasAccess === false" class="py-5">
          <div class="row justify-content-center">
            <div class="col-12 col-md-8 col-lg-6">
              <div class="permission-denied-card text-center p-5 rounded">
                <div class="denied-icon-wrapper mx-auto mb-4">
                  <svg xmlns="http://www.w3.org/2000/svg" width="40" height="40"
                       fill="currentColor" viewBox="0 0 16 16" class="text-danger">
                    <path d="M8 1a2 2 0 0 1 2 2v4H6V3a2 2 0 0 1 2-2zm3 6V3a3 3 0 0 0-6 0v4a2 2 0 0 0-2 2v5a2 2 0 0 0 2 2h6a2 2 0 0 0 2-2V9a2 2 0 0 0-2-2z"/>
                  </svg>
                </div>
                <h5 class="text-danger fw-bold mb-2">Access Restricted</h5>
                <p class="text-body-emphasis mb-1 fw-semibold">{{ accessDeniedMessage }}</p>
                <p class="text-body-secondary fs-7 mb-4">{{ accessDeniedDetail }}</p>
                <hr class="mb-4" />
                <p class="text-body-secondary fs-8 mb-0">
                  Contact your administrator if you believe you should have access.
                </p>
              </div>
            </div>
          </div>
        </div>

        <!-- STATE 3 — Access granted -->
        <div v-else>

          <!-- Loading schema -->
          <div v-if="loading && !activeTaskId" class="text-center py-5">
            <div class="spinner-glow-wrapper mx-auto">
              <div class="spinner-border text-info" style="width:3rem;height:3rem;" role="status">
                <span class="visually-hidden">Loading data release…</span>
              </div>
            </div>
            <p class="mt-4 text-info fw-semibold">Reading data release schemas and relations…</p>
          </div>

          <!-- Error -->
          <div v-else-if="errorMessage" class="alert alert-danger" role="alert">
            <h5 class="alert-heading">Data Release Sync Warning</h5>
            <p class="mb-0">{{ errorMessage }}</p>
            <button type="button" @click="loadSchema" class="btn btn-outline-danger btn-sm mt-3">
              Retry Sync
            </button>
          </div>

          <!-- Workspace -->
          <div v-else>

            <!-- Processing Banner -->
            <transition name="fade">
              <div
                v-if="jobStatus === 'PROCESSING' || jobStatus === 'PENDING'"
                class="processing-banner text-center mb-4 py-4 rounded"
              >
                <div class="spinner-glow-wrapper mx-auto">
                  <div class="spinner-border text-info" style="width:3.5rem;height:3.5rem;" role="status">
                    <span class="visually-hidden">{{ submitButtonText }}</span>
                  </div>
                </div>
                <p class="mt-3 mb-1 text-info fw-semibold">{{ submitButtonText }}</p>
                <small class="text-body-secondary">Please wait while your SQL query is being compiled…</small>
              </div>
            </transition>

            <form @submit.prevent="submitForm">

              <!-- STEP 1: Data Release -->
              <div class="mb-4">
                <label for="dataReleaseSelect" class="form-label fw-bold d-flex align-items-center gap-2">
                  <span class="step-badge">1</span> Active Data Release
                </label>
                <select
                  id="dataReleaseSelect"
                  v-model="activeSchemaKey"
                  class="form-select"
                  :disabled="jobStatus === 'PROCESSING' || jobStatus === 'PENDING'"
                >
                  <option v-for="key in schemaKeys" :key="key" :value="key">{{ key }}</option>
                </select>
              </div>

              <!-- STEP 2: Description -->
              <div class="mb-4">
                <label
                  for="promptInput"
                  class="form-label fw-bold w-100 text-center d-flex align-items-center justify-content-center gap-2"
                >
                  <span class="step-badge">2</span>
                  Describe the SQL instructions
                  <span class="text-danger ms-1">*</span>
                </label>
                <div class="row justify-content-center">
                  <div class="col-12 col-xl-10">
                    <textarea
                      id="promptInput"
                      v-model="promptText"
                      rows="7"
                      required
                      class="form-control"
                      :class="{ 'description-waiting': jobStatus === 'PROCESSING' || jobStatus === 'PENDING' }"
                      placeholder="e.g. List GES fields and count of number of spectra for each"
                      :disabled="jobStatus === 'PROCESSING' || jobStatus === 'PENDING'"
                    ></textarea>
                    <div class="form-text text-center mt-1">
                      Include metrics, ordering directions, and filtering boundaries.
                    </div>
                  </div>
                </div>
              </div>

              <!-- STEP 3: Tables -->
              <div class="mb-4">
                <label class="form-label fw-bold d-flex align-items-center gap-2">
                  <span class="step-badge">3</span>
                  Related Tables &amp; Views
                  <span class="text-body-secondary fw-normal fs-7">
                    (Optional – drag &amp; drop or click to select, arrow to expand docs)
                  </span>
                </label>

                <div class="row g-3">

                  <!-- Available Panel -->
                  <div class="col-md-6">
                    <div class="card h-100 border" @dragover.prevent @drop="onDrop($event, 'available')">
                      <div class="card-header bg-body-secondary border-bottom pb-2">
                        <div class="d-flex justify-content-between align-items-center mb-2">
                          <span class="text-uppercase text-body-secondary font-monospace fs-8">
                            Available Data Release Assets
                          </span>
                          <span class="badge text-bg-secondary">{{ filteredAvailable.length }}</span>
                        </div>
                        <div class="input-group input-group-sm">
                          <span class="input-group-text bg-body-secondary border text-body-secondary">
                            <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" fill="currentColor" viewBox="0 0 16 16">
                              <path d="M11.742 10.344a6.5 6.5 0 1 0-1.397 1.398l3.85 3.85a1 1 0 0 0 1.415-1.414l-3.868-3.834zm-5.242 1.406a5.5 5.5 0 1 1 0-11 5.5 5.5 0 0 1 0 11z"/>
                            </svg>
                          </span>
                          <input
                            v-model="searchAvailable"
                            type="search"
                            class="form-control search-input"
                            placeholder="Search tables & views…"
                            :disabled="jobStatus === 'PROCESSING' || jobStatus === 'PENDING'"
                          />
                        </div>
                      </div>

                      <div class="card-body list-column-scroll p-2" style="max-height:380px;overflow-y:auto;">
                        <div class="list-group list-group-flush">
                          <div
                            v-for="item in filteredAvailable"
                            :key="`${item.schema}-${item.name}`"
                            class="list-group-item border p-0 mb-1 rounded overflow-hidden"
                          >
                            <div
                              draggable="true"
                              @dragstart="onDragStart($event, item)"
                              @click.self="toggleSelection(item)"
                              class="p-2 d-flex align-items-center justify-content-between cursor-pointer asset-header-row"
                            >
                              <div class="d-flex align-items-center" @click.self="toggleSelection(item)">
                                <button type="button" class="btn btn-sm text-body-secondary p-0 me-2" @click.stop="toggleExpand(item)">
                                  <span :class="isExpanded(item) ? 'chevron-down' : 'chevron-right'"></span>
                                </button>
                                <i class="bi bi-grip-vertical text-body-secondary me-1 cursor-grab"></i>
                                <code class="text-info cursor-pointer" @click="toggleSelection(item)">{{ item.name }}</code>
                                <span class="badge bg-secondary-subtle text-secondary ms-2 fs-8">{{ item.type }}</span>
                              </div>
                              <span class="badge text-bg-secondary font-monospace">{{ countColumns(item) }} cols</span>
                            </div>

                            <div v-if="isExpanded(item)" class="bg-body-secondary border-top py-2 px-3">
                              <div
                                v-if="item.definition.markdown && item.definition.markdown.length > 0"
                                class="card bg-body-tertiary border p-2 mb-3 table-description-block"
                              >
                                <div v-for="(entry, idx) in item.definition.markdown" :key="idx" class="mb-1 last-mb-0">
                                  <h6 v-if="entry.h" class="text-info fs-8 fw-bold mb-0 lh-sm">{{ entry.h }}</h6>
                                  <p  v-if="entry.t" class="text-body-secondary fs-8 mb-0 lh-sm">{{ entry.t }}</p>
                                </div>
                              </div>
                              <h6 class="fs-8 text-uppercase text-body-secondary py-1 border-bottom mb-2">
                                Column definitions
                              </h6>
                              <ul class="list-unstyled mb-0 font-monospace fs-8">
                                <li
                                  v-for="(col, key) in item.definition.columns"
                                  :key="key"
                                  class="d-flex justify-content-between py-1 border-bottom text-body-secondary"
                                >
                                  <span>
                                    <strong class="text-warning">{{ col.name }}</strong>
                                    <span class="text-body-secondary ms-1">({{ col.type }})</span>
                                  </span>
                                  <span class="text-truncate text-body-secondary text-end ms-2" style="max-width:50%" :title="col.description">
                                    {{ col.description || 'no docs' }}
                                  </span>
                                </li>
                              </ul>
                            </div>
                          </div>

                          <div v-if="filteredAvailable.length === 0" class="text-center py-4 text-body-secondary">
                            <template v-if="searchAvailable">
                              No results for "<em>{{ searchAvailable }}</em>"
                            </template>
                            <template v-else>No resources available in this data release context.</template>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>

                  <!-- Selected Panel -->
                  <div class="col-md-6">
                    <div class="card h-100 border-primary" @dragover.prevent @drop="onDrop($event, 'selected')">
                      <div class="card-header bg-body-secondary border-bottom text-info pb-2">
                        <div class="d-flex justify-content-between align-items-center mb-2">
                          <span class="text-uppercase font-monospace fs-8">Selected Table Context</span>
                          <span class="badge text-bg-primary">{{ selectedKeys.length }}</span>
                        </div>
                        <div class="input-group input-group-sm">
                          <span class="input-group-text bg-body-secondary border text-body-secondary">
                            <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" fill="currentColor" viewBox="0 0 16 16">
                              <path d="M11.742 10.344a6.5 6.5 0 1 0-1.397 1.398l3.85 3.85a1 1 0 0 0 1.415-1.414l-3.868-3.834zm-5.242 1.406a5.5 5.5 0 1 1 0-11 5.5 5.5 0 0 1 0 11z"/>
                            </svg>
                          </span>
                          <input
                            v-model="searchSelected"
                            type="search"
                            class="form-control search-input"
                            placeholder="Filter selected…"
                            :disabled="jobStatus === 'PROCESSING' || jobStatus === 'PENDING'"
                          />
                        </div>
                      </div>

                      <div class="card-body list-column-scroll p-2" style="max-height:380px;overflow-y:auto;">
                        <div class="list-group list-group-flush">
                          <div
                            v-for="item in filteredSelectedObjects"
                            :key="`selected-${item.schema}-${item.name}`"
                            class="list-group-item border border-primary p-0 mb-1 rounded overflow-hidden"
                          >
                            <div
                              draggable="true"
                              @dragstart="onDragStart($event, item)"
                              @click.self="toggleSelection(item)"
                              class="p-2 d-flex align-items-center justify-content-between cursor-pointer asset-header-row selected-asset-row"
                            >
                              <div class="d-flex align-items-center" @click.self="toggleSelection(item)">
                                <button type="button" class="btn btn-sm text-body-secondary p-0 me-2" @click.stop="toggleExpand(item)">
                                  <span :class="isExpanded(item) ? 'chevron-down' : 'chevron-right'"></span>
                                </button>
                                <i class="bi bi-grip-vertical text-body-secondary me-1 cursor-grab"></i>
                                <strong class="font-monospace text-primary cursor-pointer" @click="toggleSelection(item)">
                                  {{ item.schema }}.{{ item.name }}
                                </strong>
                              </div>
                              <span class="text-danger fw-bold fs-5 px-2 cursor-pointer" @click="toggleSelection(item)">&times;</span>
                            </div>

                            <div v-if="isExpanded(item)" class="bg-body-secondary border-top border-primary py-2 px-3">
                              <div
                                v-if="item.definition.markdown && item.definition.markdown.length > 0"
                                class="card bg-body-tertiary border p-2 mb-3 table-description-block"
                              >
                                <div v-for="(entry, idx) in item.definition.markdown" :key="idx" class="mb-1 last-mb-0">
                                  <h6 v-if="entry.h" class="text-info fs-8 fw-bold mb-0 lh-sm">{{ entry.h }}</h6>
                                  <p  v-if="entry.t" class="text-body-secondary fs-8 mb-0 lh-sm">{{ entry.t }}</p>
                                </div>
                              </div>
                              <h6 class="fs-8 text-uppercase text-body-secondary py-1 border-bottom mb-2">
                                Column definitions
                              </h6>
                              <ul class="list-unstyled mb-0 font-monospace fs-8">
                                <li
                                  v-for="(col, key) in item.definition.columns"
                                  :key="key"
                                  class="d-flex justify-content-between py-1 border-bottom text-body-secondary"
                                >
                                  <span>
                                    <strong class="text-warning">{{ col.name }}</strong>
                                    <span class="text-body-secondary ms-1">({{ col.type }})</span>
                                  </span>
                                  <span class="text-truncate text-body-secondary text-end ms-2" style="max-width:50%" :title="col.description">
                                    {{ col.description || 'no docs' }}
                                  </span>
                                </li>
                              </ul>
                            </div>
                          </div>

                          <div v-if="filteredSelectedObjects.length === 0" class="text-center py-4 text-body-secondary">
                            <template v-if="searchSelected && selectedKeys.length > 0">
                              No results for "<em>{{ searchSelected }}</em>"
                            </template>
                            <template v-else>Drag resources here or select them to build your context payload.</template>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>

                </div>
              </div>

              <!-- Controls -->
              <div class="d-flex justify-content-between align-items-center mt-2">
                <div>
                  <button
                    v-if="jobStatus === 'PROCESSING' || jobStatus === 'PENDING'"
                    type="button" class="btn btn-outline-danger btn-sm"
                    @click="stopMonitoring"
                  >Cancel Compilation Monitor</button>
                </div>
                <div class="d-flex gap-2">
                  <button
                    type="button" class="btn btn-outline-secondary"
                    @click="resetFormState"
                    :disabled="jobStatus === 'PROCESSING' || jobStatus === 'PENDING' || (selectedKeys.length === 0 && !promptText)"
                  >Reset Form</button>
                  <button
                    type="submit"
                    class="btn btn-primary px-4 d-flex align-items-center gap-2"
                    :class="{ 'btn-submit-glow': jobStatus === 'PROCESSING' || jobStatus === 'PENDING' }"
                    :disabled="!promptText.trim() || jobStatus === 'PROCESSING' || jobStatus === 'PENDING'"
                  >
                    <span v-if="jobStatus === 'PROCESSING' || jobStatus === 'PENDING'" class="spinner-glow-inline">
                      <span class="spinner-border spinner-border-sm" role="status"></span>
                    </span>
                    <span>{{ submitButtonText }}</span>
                  </button>
                </div>
              </div>
            </form>

            <!-- Job error alert — sits below the form, keeps inputs intact -->
            <div ref="jobErrorRef" v-if="jobErrorMessage" class="mt-4 alert alert-danger d-flex align-items-start gap-3" role="alert">
              <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20"
                  fill="currentColor" class="flex-shrink-0 mt-1" viewBox="0 0 16 16">
                <path d="M8 15A7 7 0 1 1 8 1a7 7 0 0 1 0 14zm0 1A8 8 0 1 0 8 0a8 8 0 0 0 0 16z"/>
                <path d="M7.002 11a1 1 0 1 1 2 0 1 1 0 0 1-2 0zM7.1 4.995a.905.905 0 1 1 1.8 0l-.35 3.507a.552.552 0 0 1-1.1 0L7.1 4.995z"/>
              </svg>
              <div class="flex-grow-1">
                <h6 class="alert-heading fw-bold mb-1">SQL Generation Failed</h6>
                <p class="mb-2 fs-7">{{ jobErrorMessage }}</p>
                <button
                  type="button"
                  class="btn btn-sm btn-danger"
                  @click="resetFormState"
                >
                  Clear &amp; Start Again
                </button>
              </div>
            </div>

            <!-- SQL Output -->
            <div ref="sqlResultRef" v-if="queryTextResult" class="mt-5 pt-4 border-top">
              <div class="row justify-content-center">
                <div class="col-12 col-lg-10">
                  <div class="d-flex justify-content-between align-items-center mb-3">
                    <h5 class="text-success mb-0">
                      <i class="bi bi-file-earmark-code me-2"></i>Generated SQL Query
                    </h5>
                    <button type="button" class="btn btn-outline-secondary btn-sm" @click="copyToClipboard">
                      {{ copyButtonText }}
                    </button>
                  </div>
                  <pre
                    class="bg-body-tertiary p-3 rounded border border-success text-success font-monospace overflow-auto sql-result-block"
                    style="max-height:450px;font-size:0.9rem;"
                  ><code>{{ queryTextResult }}</code></pre>
                </div>
              </div>
            </div>

          </div>
        </div>

      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { ref, computed, watch, onMounted, nextTick } from 'vue';
import { getDatabaseSchema, type Schemas, type TableDefinition } from '@/api/schema';

interface FlattenedAsset {
  schema: string;
  name: string;
  type: 'table' | 'view';
  definition: TableDefinition;
}

// ── Access control ─────────────────────────────────────────────────────────
// null  = probe in flight (show loading)
// false = server returned 403 (show denied wall)
// true  = granted (show form)
const hasAccess            = ref<boolean | null>(null);
const accessDeniedMessage  = ref<string>("You don't have permissions to use this.");
const accessDeniedDetail   = ref<string>('');

// ── Component states ───────────────────────────────────────────────────────
const loading             = ref<boolean>(false);
const errorMessage    = ref<string | null>(null);  // schema/network errors only
const jobErrorMessage = ref<string | null>(null);  // SQL generation failures only
const rawSchemas          = ref<Schemas>({});
const activeSchemaKey     = ref<string>('');
const promptText          = ref<string>('');
const selectedKeys        = ref<string[]>([]);
const expandedTableStates = ref<Record<string, boolean>>({});
const searchAvailable     = ref<string>('');
const searchSelected      = ref<string>('');

// Template refs
const jobErrorRef = ref<HTMLElement | null>(null);
const sqlResultRef = ref<HTMLElement | null>(null);

// ── Celery task states ─────────────────────────────────────────────────────
const queryTextResult = ref<string | null>(null);
const activeTaskId    = ref<string | null>(null);
const jobStatus       = ref<'PENDING' | 'PROCESSING' | 'SUCCESS' | 'FAILED' | null>(null);
const copySuccess     = ref<boolean>(false);
let pollInterval: number | null = null;

watch(activeSchemaKey, () => { searchAvailable.value = ''; });

// Shared scroll helper
const scrollToResult = async (target: typeof jobErrorRef) => {
  await nextTick(); // wait for the element to render
  target.value?.scrollIntoView({ behavior: 'smooth', block: 'start' });
};

// ── Computed ───────────────────────────────────────────────────────────────

const schemaKeys = computed<string[]>(() => Object.keys(rawSchemas.value));

const allLocalDatabaseAssets = computed<FlattenedAsset[]>(() => {
  const list: FlattenedAsset[] = [];
  for (const [schemaName, schemaObj] of Object.entries(rawSchemas.value)) {
    if (!schemaObj) continue;
    if (schemaObj.tables) {
      for (const [tableName, details] of Object.entries(schemaObj.tables))
        list.push({ schema: schemaName, name: tableName, type: 'table', definition: details });
    }
    if (schemaObj.views) {
      for (const [viewName, details] of Object.entries(schemaObj.views))
        list.push({ schema: schemaName, name: viewName, type: 'view', definition: details });
    }
  }
  return list;
});

const filteredAvailable = computed<FlattenedAsset[]>(() => {
  if (!activeSchemaKey.value) return [];
  const term = searchAvailable.value.toLowerCase().trim();
  return allLocalDatabaseAssets.value
    .filter(asset =>
      asset.schema === activeSchemaKey.value &&
      !selectedKeys.value.includes(`${asset.schema}.${asset.name}`) &&
      (term === '' || asset.name.toLowerCase().includes(term))
    )
    .sort((a, b) => a.name.localeCompare(b.name));
});

const selectedObjects = computed<FlattenedAsset[]>(() =>
  allLocalDatabaseAssets.value.filter(asset =>
    selectedKeys.value.includes(`${asset.schema}.${asset.name}`)
  )
);

const filteredSelectedObjects = computed<FlattenedAsset[]>(() => {
  const term = searchSelected.value.toLowerCase().trim();
  return selectedObjects.value
    .filter(asset => term === '' || asset.name.toLowerCase().includes(term))
    .sort((a, b) => a.name.localeCompare(b.name));
});

const statusBadgeClass = computed(() => {
  if (jobStatus.value === 'SUCCESS')    return 'bg-success text-white';
  if (jobStatus.value === 'PROCESSING') return 'bg-warning text-black';
  if (jobStatus.value === 'FAILED')     return 'bg-danger text-white';
  return 'bg-secondary text-white';
});

const submitButtonText = computed(() => {
  if (jobStatus.value === 'PENDING')    return 'Enqueuing Job…';
  if (jobStatus.value === 'PROCESSING') return 'Generating SQL Code…';
  return 'Compile SQL Request';
});

const copyButtonText = computed(() => (copySuccess.value ? 'Copied!' : 'Copy SQL'));

// ── Methods ────────────────────────────────────────────────────────────────

/**
 * Probe the submit endpoint with a lightweight GET.
 * The backend's IsProprietaryUser permission class returns a structured
 * 403 JSON body if access is denied, or 200 {"access": true} if granted.
 */
const checkAccess = async (): Promise<void> => {
  try {
    const response = await fetch('/api/v1/queries/generate/');

    if (response.status === 403) {
      const data = await response.json().catch(() => ({}));
      hasAccess.value           = false;
      accessDeniedMessage.value = data.error   || "You don't have permissions to use this.";
      accessDeniedDetail.value  = data.detail  || '';
      return;
    }

    if (response.ok) {
      hasAccess.value = true;
      return;
    }

    // Any other unexpected status — deny gracefully
    hasAccess.value           = false;
    accessDeniedMessage.value = 'Unable to verify access. Please try again later.';
  } catch {
    hasAccess.value           = false;
    accessDeniedMessage.value = 'Unable to reach the server. Check your connection.';
  }
};

const loadSchema = async (): Promise<void> => {
  loading.value = true;
  errorMessage.value = null;
  try {
    const data: Schemas | undefined = await getDatabaseSchema();
    if (data === undefined) {
      throw new Error('Data release system returned an empty context. Verify network connectivity.');
    }
    rawSchemas.value = data;
    const keys = Object.keys(data);
    if (keys.length > 0) activeSchemaKey.value = keys[0];
  } catch (error: any) {
    errorMessage.value = error.message || 'Unknown data release retrieval error.';
    console.error('Error fetching data release map:', error);
  } finally {
    loading.value = false;
  }
};

const countColumns  = (item: FlattenedAsset): number =>
  item.definition.columns ? Object.keys(item.definition.columns).length : 0;

const toggleExpand  = (item: FlattenedAsset) => {
  const key = `${item.schema}.${item.name}`;
  expandedTableStates.value[key] = !expandedTableStates.value[key];
};

const isExpanded    = (item: FlattenedAsset): boolean =>
  !!expandedTableStates.value[`${item.schema}.${item.name}`];

const toggleSelection = (item: FlattenedAsset) => {
  const key = `${item.schema}.${item.name}`;
  const idx = selectedKeys.value.indexOf(key);
  idx > -1 ? selectedKeys.value.splice(idx, 1) : selectedKeys.value.push(key);
};

const onDragStart = (e: DragEvent, item: FlattenedAsset) => {
  if (!e.dataTransfer) return;
  e.dataTransfer.effectAllowed = 'move';
  e.dataTransfer.setData('application/json', JSON.stringify({ schema: item.schema, name: item.name }));
};

const onDrop = (e: DragEvent, targetList: 'available' | 'selected') => {
  if (!e.dataTransfer) return;
  try {
    const rawData = e.dataTransfer.getData('application/json');
    if (!rawData) return;
    const parsed: { schema: string; name: string } = JSON.parse(rawData);
    const key = `${parsed.schema}.${parsed.name}`;
    const keyIndex = selectedKeys.value.indexOf(key);
    if (targetList === 'selected'  && keyIndex === -1) selectedKeys.value.push(key);
    if (targetList === 'available' && keyIndex >  -1) selectedKeys.value.splice(keyIndex, 1);
  } catch (err) {
    console.error('Failed to parse dropped element:', err);
  }
};

// ── Celery task management ─────────────────────────────────────────────────

const handlePermissionError = () => {
  hasAccess.value           = false;
  accessDeniedMessage.value = "You don't have permissions to use this.";
  accessDeniedDetail.value  = 'Your session may have changed. Please refresh the page.';
};

const submitForm = async (): Promise<void> => {
  if (!promptText.value.trim()) return;

  loading.value         = true;
  errorMessage.value    = null;
  jobErrorMessage.value = null; // ← clear previous job error on new submit
  queryTextResult.value = null;
  jobStatus.value       = 'PENDING';

  try {
    const response = await fetch('/api/v1/queries/generate/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        data_release: activeSchemaKey.value,
        tables:       [...selectedKeys.value],
        description:  promptText.value.trim(),
      }),
    });

    if (response.status === 403) {
      handlePermissionError();
      loading.value   = false;
      jobStatus.value = null;
      return;
    }

    if (!response.ok) {
      // ↓ was errorMessage — now jobErrorMessage
      throw new Error('Failed to submit the SQL generation request.');
    }

    const data = await response.json();
    activeTaskId.value = data.task_id;
    jobStatus.value    = data.status;
    startMonitoringJob(data.task_id);
  } catch (err: any) {
    loading.value         = false;
    jobErrorMessage.value = err.message || 'Workflow failed to initialise.'; // ← was errorMessage
    jobStatus.value       = null;
  }
};

const startMonitoringJob = (taskId: string): void => {
  if (pollInterval) clearInterval(pollInterval);

  pollInterval = window.setInterval(async () => {
    try {
      const response = await fetch(`/api/v1/queries/generate/poll/${taskId}/`);

      if (response.status === 403) {
        handlePermissionError();
        stopMonitoring();
        return;
      }

      if (!response.ok) throw new Error('Lost connection with the task tracker.');

      const data = await response.json();
      jobStatus.value = data.status;

      if (data.status === 'SUCCESS') {
        queryTextResult.value = data.sql;
        stopMonitoring();
        scrollToResult(sqlResultRef); // ← scroll to SQL output
      } else if (data.status === 'FAILED') {
        jobErrorMessage.value = data.error || 'The SQL generation task failed on the server.';
        stopMonitoring();
        scrollToResult(jobErrorRef); // ← scroll to error
      }
    } catch (err: any) {
      jobErrorMessage.value = err.message || 'Lost connection while monitoring the job.';
      stopMonitoring();
      scrollToResult(jobErrorRef); // ← scroll to error
    }
  }, 2000);
};

const stopMonitoring = (): void => {
  if (pollInterval) { clearInterval(pollInterval); pollInterval = null; }
  loading.value = false;
  if (jobStatus.value === 'PENDING' || jobStatus.value === 'PROCESSING') {
    jobStatus.value = null;
    activeTaskId.value = null;
  }
};

const copyToClipboard = async (): Promise<void> => {
  if (!queryTextResult.value) return;
  try {
    await navigator.clipboard.writeText(queryTextResult.value);
    copySuccess.value = true;
    setTimeout(() => { copySuccess.value = false; }, 2000);
  } catch (err) {
    console.error('Failed to copy text:', err);
  }
};

const resetFormState = (): void => {
  selectedKeys.value        = [];
  promptText.value          = '';
  expandedTableStates.value = {};
  queryTextResult.value     = null;
  activeTaskId.value        = null;
  jobStatus.value           = null;
  searchAvailable.value     = '';
  searchSelected.value      = '';
  jobErrorMessage.value     = null;
};

// ── Lifecycle ──────────────────────────────────────────────────────────────

onMounted(async () => {
  // Always check permission first — only load schema when confirmed.
  await checkAccess();
  if (hasAccess.value === true) {
    await loadSchema();
  }
});
</script>

<style scoped>
.cursor-pointer  { cursor: pointer; }
.cursor-grab     { cursor: grab; }
.cursor-grab:active { cursor: grabbing; }

.fs-7 { font-size: 0.85rem; }
.fs-8 { font-size: 0.74rem; }

/* Step badge — uses Bootstrap CSS vars so it adapts to the theme */
.step-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 1.5rem;
  height: 1.5rem;
  flex-shrink: 0;
  border-radius: 50%;
  background: rgba(var(--bs-primary-rgb), 0.15);
  border: 1px solid rgba(var(--bs-primary-rgb), 0.45);
  color: var(--bs-primary);
  font-size: 0.72rem;
  font-weight: 700;
}

/* Scrollbar */
.list-column-scroll::-webkit-scrollbar { width: 6px; }
.list-column-scroll::-webkit-scrollbar-thumb {
  background-color: rgba(var(--bs-emphasis-color-rgb), 0.15);
  border-radius: 4px;
}

/* Row hovers */
.asset-header-row:hover    { background-color: rgba(var(--bs-emphasis-color-rgb), 0.05) !important; }
.selected-asset-row:hover  { background-color: rgba(var(--bs-primary-rgb), 0.08) !important; }

/* Table description left-border accent */
.table-description-block              { border-left: 3px solid var(--bs-info) !important; }
.table-description-block div          { margin-bottom: 4px !important; }
.table-description-block h6           { margin-bottom: 2px !important; }
.table-description-block p,
.table-description-block h6           { line-height: 1.25 !important; }
.last-mb-0:last-child                 { margin-bottom: 0 !important; }

/* Chevrons */
.chevron-right::before {
  content: "▶";
  display: inline-block;
  font-size: 0.65rem;
  transition: transform 0.15s ease;
}
.chevron-down::before {
  content: "▼";
  display: inline-block;
  font-size: 0.65rem;
}

/* Search focus glow */
.search-input:focus {
  border-color: rgba(var(--bs-info-rgb), 0.5) !important;
  box-shadow: 0 0 0 0.2rem rgba(var(--bs-info-rgb), 0.15);
}

/* Spinner glow — large */
@keyframes glow-pulse {
  0%, 100% { box-shadow: 0 0 8px  4px rgba(var(--bs-info-rgb), 0.30); }
  50%       { box-shadow: 0 0 28px 10px rgba(var(--bs-info-rgb), 0.90); }
}
.spinner-glow-wrapper {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  padding: 10px;
  animation: glow-pulse 1.4s ease-in-out infinite;
}

/* Spinner glow — inline button */
@keyframes inline-glow {
  0%, 100% { filter: drop-shadow(0 0 3px rgba(var(--bs-info-rgb), 0.5)); }
  50%       { filter: drop-shadow(0 0 9px rgba(var(--bs-info-rgb), 1.0)); }
}
.spinner-glow-inline {
  display: inline-flex;
  align-items: center;
  animation: inline-glow 1.4s ease-in-out infinite;
}

/* Submit button glow */
@keyframes btn-glow {
  0%, 100% { box-shadow: 0 0 6px  2px rgba(var(--bs-primary-rgb), 0.40); }
  50%       { box-shadow: 0 0 18px 6px rgba(var(--bs-primary-rgb), 0.85); }
}
.btn-submit-glow { animation: btn-glow 1.4s ease-in-out infinite; }

/* Processing banner */
.processing-banner {
  background: rgba(var(--bs-info-rgb), 0.05);
  border: 1px solid rgba(var(--bs-info-rgb), 0.22);
}

/* Description textarea — job running */
.description-waiting {
  border-color: rgba(var(--bs-info-rgb), 0.5) !important;
  box-shadow: 0 0 0 0.2rem rgba(var(--bs-info-rgb), 0.10);
}

/* SQL output block */
.sql-result-block { box-shadow: 0 0 16px rgba(var(--bs-success-rgb), 0.25); }

/* Permission denied card */
.permission-denied-card {
  background: rgba(var(--bs-danger-rgb), 0.05);
  border: 1px solid rgba(var(--bs-danger-rgb), 0.25);
}
.denied-icon-wrapper {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 5rem;
  height: 5rem;
  border-radius: 50%;
  background: rgba(var(--bs-danger-rgb), 0.10);
  border: 1px solid rgba(var(--bs-danger-rgb), 0.30);
}

/* Fade transition */
.fade-enter-active, .fade-leave-active { transition: opacity 0.3s ease; }
.fade-enter-from,   .fade-leave-to     { opacity: 0; }
</style>