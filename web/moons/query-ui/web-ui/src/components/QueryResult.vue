<script setup lang="ts">
import {ref, reactive, onMounted, watchEffect, computed, onUnmounted} from 'vue';
import { useRoute } from 'vue-router'

import { getQueryResult } from '@/api/get_result';
import TabulatorResult from './TabulatorResult.vue';
import {getCurrentTheme} from './theme'
const prefTheme = getCurrentTheme()
if (prefTheme == 'light') {
    import("tabulator-tables/dist/css/tabulator.min.css")
}
else {
    import("tabulator-tables/dist/css/tabulator_midnight.min.css")
}
import { api_url } from '@/api/query'

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

const downloadFormats = ['FITS', 'VOTable', 'CSV']

</script>

<template>

    <div class="m-4 d-flex justify-content-between">
        <nav aria-label="breadcrumb">
            <ol class="breadcrumb">
                <li class="breadcrumb-item"><RouterLink :to="{ name: 'query-list'}">&laquo; Your Queries</RouterLink></li>
            </ol>
        </nav>
        <div>
            <button class="btn btn-secondary"><RouterLink class="text-decoration-none text-reset" :to="{ name: 'query-form'}">New Query</RouterLink></button>
        </div>
    </div>
    <div class="d-flex flex-column">
    <div class="m-4 container" :class="{['d-none']: !(queryStatus?.value)}">
        <div class="lead">Query not found</div>
    </div>

    <div class="m-4" :class="{['d-none']: (queryStatus?.value)}">
        <div class="d-flex justify-content-end">
            <button class="btn btn-secondary">
                <RouterLink class="text-decoration-none text-reset" :to="{ name: 'query-edit', params:{id: queryStatus?.id }}">
                    Edit
                    <svg width="1em" height="1em" class="theme-icon-active">
                        <use href="#icon-edit" />
                    </svg>
                </RouterLink>
            </button>
        </div>

        <div class="font-monospace border border-3 rounded p-2 m-2 my-4">{{ queryStatus?.query }}</div>
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
        <div class="btn-group m-2" role="group" v-if="!queryStatus?.results_error && queryStatus?.result_url">
            <a v-for="format in downloadFormats" type="button" class="btn btn-primary" :href="`${api_url}/results/${resultId}?format=${format.toLowerCase()}`" >
                <svg width="1em" height="1em" class="theme-icon-active">
                    <use href="#icon-download" />
                </svg>
                {{ format }}
            </a>
        </div>
        <div class="m-2" v-if="!queryStatus?.results_error && !queryStatus?.result_url">
            <div>
                Results were removed. Press "Edit" above to run the query again.
            </div>
        </div>
    </div>

    <TabulatorResult :result_url="queryStatus?.result_url" :result_id="queryStatus?.id" class="flex-grow-1"/>
  </div>

  <svg xmlns="http://www.w3.org/2000/svg" class="base-svgs" width="1em" height="1em">
      <symbol id="icon-download" fill="currentColor" viewBox="0 0 448 512">
          <!-- Font Awesome Free v7.1.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2025 Fonticons, Inc. -->
          <path d="M256 32c0-17.7-14.3-32-32-32s-32 14.3-32 32l0 210.7-41.4-41.4c-12.5-12.5-32.8-12.5-45.3 0s-12.5 32.8 0 45.3l96 96c12.5 12.5 32.8 12.5 45.3 0l96-96c12.5-12.5 12.5-32.8 0-45.3s-32.8-12.5-45.3 0L256 242.7 256 32zM64 320c-35.3 0-64 28.7-64 64l0 32c0 35.3 28.7 64 64 64l320 0c35.3 0 64-28.7 64-64l0-32c0-35.3-28.7-64-64-64l-46.9 0-56.6 56.6c-31.2 31.2-81.9 31.2-113.1 0L110.9 320 64 320zm304 56a24 24 0 1 1 0 48 24 24 0 1 1 0-48z"/>
      </symbol>
      <symbol id="icon-chart-line" fill="currentColor" viewBox="0 0 512 512">
          <!--!Font Awesome Free v7.1.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2025 Fonticons, Inc. -->
          <path d="M64 64c0-17.7-14.3-32-32-32S0 46.3 0 64L0 400c0 44.2 35.8 80 80 80l400 0c17.7 0 32-14.3 32-32s-14.3-32-32-32L80 416c-8.8 0-16-7.2-16-16L64 64zm406.6 86.6c12.5-12.5 12.5-32.8 0-45.3s-32.8-12.5-45.3 0L320 210.7 262.6 153.4c-12.5-12.5-32.8-12.5-45.3 0l-96 96c-12.5 12.5-12.5 32.8 0 45.3s32.8 12.5 45.3 0l73.4-73.4 57.4 57.4c12.5 12.5 32.8 12.5 45.3 0l128-128z"/>
      </symbol>
      <symbol id="icon-edit" fill="currentColor" viewBox="0 0 512 512">
          <!--!Font Awesome Free v7.1.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2025 Fonticons, Inc.-->
          <path d="M441 58.9L453.1 71c9.4 9.4 9.4 24.6 0 33.9L424 134.1 377.9 88 407 58.9c9.4-9.4 24.6-9.4 33.9 0zM209.8 256.2L344 121.9 390.1 168 255.8 302.2c-2.9 2.9-6.5 5-10.4 6.1l-58.5 16.7 16.7-58.5c1.1-3.9 3.2-7.5 6.1-10.4zM373.1 25L175.8 222.2c-8.7 8.7-15 19.4-18.3 31.1l-28.6 100c-2.4 8.4-.1 17.4 6.1 23.6s15.2 8.5 23.6 6.1l100-28.6c11.8-3.4 22.5-9.7 31.1-18.3L487 138.9c28.1-28.1 28.1-73.7 0-101.8L474.9 25C446.8-3.1 401.2-3.1 373.1 25zM88 64C39.4 64 0 103.4 0 152L0 424c0 48.6 39.4 88 88 88l272 0c48.6 0 88-39.4 88-88l0-112c0-13.3-10.7-24-24-24s-24 10.7-24 24l0 112c0 22.1-17.9 40-40 40L88 464c-22.1 0-40-17.9-40-40l0-272c0-22.1 17.9-40 40-40l112 0c13.3 0 24-10.7 24-24s-10.7-24-24-24L88 64z"/>
      </symbol>
    </svg>


</template>
