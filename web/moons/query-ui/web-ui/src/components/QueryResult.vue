<script setup lang="ts">
import {ref, reactive, onMounted, useTemplateRef, computed, onUnmounted} from 'vue';
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
    return st ? !(st === 'Queued' || st === 'Running') : true
})
const statusFound = computed(() => queryStatus.value != null)

const highlightClass = computed(() => {
    const st = queryStatus.value?.current_status
    switch (st) {
        case 'Queued': return 'text-bg-warning'
        case 'Running': return 'text-bg-primary'
        case 'Success': return 'text-bg-success'
        case 'Error': return 'text-bg-danger'
        default: return 'text-bg-secondary'
    }
})

var timer: number;

onMounted(async () => {
    queryStatus.value = await getQueryResult(resultId)
    timer = setInterval(async () => {
        queryStatus.value = await getQueryResult(resultId)
    }, 1000);
})
onUnmounted(() => {
    clearInterval(timer)
})

</script>

<template>

    <div class="m-2">
    <nav aria-label="breadcrumb">
    <ol class="breadcrumb">
        <li class="breadcrumb-item"><RouterLink :to="{ name: 'query-list'}">&laquo; Your Queries</RouterLink></li>
    </ol>
    </nav>
    </div>    
    <div class="d-flex flex-column">
    <div class="m-4 container" :class="{['d-none']: !(queryStatus?.value)}">
        <div class="lead">Query not found</div>
    </div>
    <div class="m-4 container" :class="{['d-none']: (queryStatus?.value)}">
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
    </div>

    <TabulatorResult :result_url="queryStatus?.result_url" class="flex-grow-1"/>
    </div>

</template>
