<script setup lang="ts">
import {ref, reactive, onMounted, watchEffect, computed, onUnmounted} from 'vue';
import { useRoute } from 'vue-router'

import { getQueryResult } from '@/api/get_result';
import TabulatorResult from './TabulatorResult.vue';
import {getPreferredTheme} from './theme'
const prefTheme = getPreferredTheme()
if (prefTheme == 'light') {
    import("tabulator-tables/dist/css/tabulator.min.css")
}
else {
    import("tabulator-tables/dist/css/tabulator_midnight.min.css")
}

const route = useRoute()

const queryStatus = ref()
const resultId:Number = parseInt(route.params.id as string)
const isComplete = computed(() => {
    const st = queryStatus.value?.current_status
    return st && !(st === 'Queued' || st === 'Running')
})
const queryComplete = ref(false)

const highlightClass = computed(() => {
    const st = queryStatus.value?.current_status
    switch (st) {
        case 'Queued': return 'text-bg-warning'
        case 'Running': return 'text-bg-primary'
        case 'Success': return 'text-bg-success'
        case 'Error': return 'text-bg-danger'
        default: return 'text-bg-light'
    }
})

const borderClass = computed(() => {
    const st = queryStatus.value?.current_status
    switch (st) {
        case 'Queued': return 'border-warning'
        case 'Running': return 'border-primary'
        case 'Success': return 'border-success'
        case 'Error': return 'border-danger'
        default: return 'border-secondary'
    }
})

var timer: number;

onMounted(async () => {
    queryStatus.value = await getQueryResult(resultId)
    timer = setInterval(async () => {
        const st = await getQueryResult(resultId)
        queryStatus.value = st
        if (!(st == 'Queued' || st == 'Running')) {
            queryComplete.value = true
        }
    }, 1000);
})
onUnmounted(() => {
    clearInterval(timer)
})
watchEffect(async () => {
    if (queryComplete.value) {
        clearInterval(timer)
    }
})

</script>

<template>

    <div class="m-4 d-flex justify-content-between">
        <nav aria-label="breadcrumb">
            <ol class="breadcrumb">
                <li class="breadcrumb-item"><RouterLink :to="{ name: 'query-list'}">&laquo; Your Queries</RouterLink></li>
            </ol>
        </nav>
        <button class="btn btn-secondary"><RouterLink class="text-decoration-none text-reset" :to="{ name: 'query-form'}">New Query</RouterLink></button>
    </div>
    <div class="d-flex flex-column">
    <div class="m-4 container" :class="{['d-none']: !(queryStatus?.value)}">
        <div class="lead">Query not found</div>
    </div>
    <!-- <div class="m-4 container" :class="{['d-none']: (queryStatus?.value)}">
        <div class="row">
            <div class="col-3">Query</div><div class="col font-monospace border rounded p-2 m-2">{{ queryStatus?.query }}</div>
        </div>
        <div class="row">
            <div class="col-3">Status</div>
            <div class="col">
                <div class="h5">
                    <span id="job-badge" :class="highlightClass" class="badge p-2">
                        <span :class="{['d-none']: isComplete}" class="spinner-border spinner-border-sm pe-2" aria-hidden="true"></span>
                        <span role="status">{{ queryStatus?.current_status || 'Loading...' }}</span>
                    </span>
                </div>
            </div>
        </div>
        <div class="row" v-if="queryStatus?.started">
            <div class="col-3">Start</div><div class="col">{{new Date(queryStatus?.started).toLocaleString() }}</div>
        </div>
        <div class="row" v-if="queryStatus?.completed">
            <div class="col-3">End</div><div class="col">{{ new Date(queryStatus?.completed).toLocaleString() }}</div>
        </div>
        <div class="row" v-if="queryStatus?.results_error">
            <div class="col-3">Error</div>
            <div class="col border rounded p-2 m-2 border-danger"><pre>{{ queryStatus?.results_error }}</pre></div>
        </div>
    </div> -->

    <div class="m-4" :class="{['d-none']: (queryStatus?.value)}">
        <div class="col font-monospace border border-3 rounded p-2 m-2 my-4">{{ queryStatus?.query }}</div>
        <div class="card m-2" :class="borderClass">
            <div class="card-header" :class="highlightClass">
                <div class="d-flex justify-content-between">
                    <div>
                        <span :class="{['d-none']: isComplete}" class="spinner-border spinner-border-sm pe-2" aria-hidden="true"></span>
                        <span v-if="queryStatus?.current_status === 'Success'">Matched {{ queryStatus?.num_rows }} rows</span>
                        <span v-if="queryStatus?.current_status !== 'Success'">{{ queryStatus?.current_status || 'Loading...' }}</span>
                    </div>
                    <div>
                        <div v-if="queryStatus?.started && !isComplete">Started {{new Date(queryStatus?.started).toLocaleString() }}</div>
                        <div v-if="queryStatus?.completed">Completed {{ new Date(queryStatus?.completed).toLocaleString() }}</div>
                    </div>
                </div>
            </div>
            <div class="card-body" v-if="queryStatus?.results_error">
                <div class="mt-2" v-if="queryStatus?.results_error">
                    <pre>{{ queryStatus?.results_error }}</pre>
                </div>
            </div>
        </div>
        <div class="btn-group m-2" role="group" v-if="!queryStatus?.results_error">
        <button type="button" class="btn btn-primary">
            <svg width="1em" height="1em" class="theme-icon-active">
                <use href="#icon-download" />
            </svg>
            FITS
        </button>
        <button type="button" class="btn btn-primary">
            <svg width="1em" height="1em" class="theme-icon-active">
                <use href="#icon-download" />
            </svg>
            VOTable
        </button>
        <button type="button" class="btn btn-primary">
            <svg width="1em" height="1em" class="theme-icon-active">
                <use href="#icon-download" />
            </svg>
            CSV
        </button>
        </div>
    </div>

    <TabulatorResult :result_url="queryStatus?.result_url" :result_id="queryStatus?.id" class="flex-grow-1"/>
  </div>

  <svg xmlns="http://www.w3.org/2000/svg" class="base-svgs" width="1em" height="1em">
      <symbol id="icon-download" fill="currentColor" viewBox="0 0 448 512">
          <!-- Font Awesome Free v7.1.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2025 Fonticons, Inc. -->
          <path d="M256 32c0-17.7-14.3-32-32-32s-32 14.3-32 32l0 210.7-41.4-41.4c-12.5-12.5-32.8-12.5-45.3 0s-12.5 32.8 0 45.3l96 96c12.5 12.5 32.8 12.5 45.3 0l96-96c12.5-12.5 12.5-32.8 0-45.3s-32.8-12.5-45.3 0L256 242.7 256 32zM64 320c-35.3 0-64 28.7-64 64l0 32c0 35.3 28.7 64 64 64l320 0c35.3 0 64-28.7 64-64l0-32c0-35.3-28.7-64-64-64l-46.9 0-56.6 56.6c-31.2 31.2-81.9 31.2-113.1 0L110.9 320 64 320zm304 56a24 24 0 1 1 0 48 24 24 0 1 1 0-48z"/>
      </symbol>
  </svg>


</template>
