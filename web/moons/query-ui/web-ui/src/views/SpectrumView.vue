<script setup lang="ts">
import {ref, useTemplateRef, onMounted} from 'vue';
import { useRoute } from 'vue-router'
import Dygraph from 'dygraphs';
import "dygraphs/dist/dygraph.min.css"

import {getCurrentTheme} from '@/components/theme'
const prefTheme = getCurrentTheme()
if (prefTheme == 'dark') {
    import("@/assets/dygraphs.css")
}

import { getSpectrumData } from '@/api/get_result';
import { api_url } from '@/api/query';

const route = useRoute()
const resultId:Number = parseInt(route.params.id as string)
const filename = route.query.file

// const filename = ref('/files/GES_MW_00_01/gir_00000014-6003143_H548.8.fit')
const url = `${api_url}/results/${resultId}/plot?filename=${filename}`
const loading = ref(true)
const hasError = ref(true)
const diagram = useTemplateRef('diagram')
const downloadUrl = `${api_url}/results/${resultId}/file?filename=${filename}`

onMounted(async () => {
    const data = await getSpectrumData(url)
    if (data) {
        const header = data.split('\n', 1)[0]
        var colNames:string[] = ['', '']
        if (header) {
            colNames = header.split(',')
        }
        hasError.value = false
        diagram.value && new Dygraph(
            diagram.value,
            data,
            {
                xlabel: colNames[0],
                ylabel: colNames[1],
                customBars: true,
                axisLineColor: prefTheme == 'dark'? 'white' : 'black',
            }
        );
        loading.value = false;
    }
    else {
        hasError.value = true
    }
    loading.value = false
})
</script>

<template>

    <main class="container-fluid">

        <div class="m-4">
            <nav aria-label="breadcrumb">
                <ol class="breadcrumb">
                    <li class="breadcrumb-item"><RouterLink :to="{ name: 'query-result', params: {id: route.params.id}}">&laquo; Query Results</RouterLink></li>
                </ol>
            </nav>
        </div>

        <div class="m-4">
            <h1>Spectrum Plot</h1>
            <div v-if="loading">Loading ...</div>
            <div v-if="!loading && hasError">An error occurred when loading the data.</div>
            <div v-if="!loading && !hasError">
                <div class="small">
                    This graph is interactive.
                    Move the mouse over the series to display individual values.
                    Select regions of the graph to zoom in and
                    double-click on the graph to reset the zoom (zoom out).
                </div>
                <div class="my-4 font-monospace">
                    {{ filename }}
                    <a :href="downloadUrl" class="download">
                        <svg width="1em" height="1em" class="theme-icon-active"><use href="#icon-download"/></svg>
                    </a>
                </div>
            </div>
            <div style="height:60vh;" ref="diagram"></div>
        </div>
    </main>

    <svg xmlns="http://www.w3.org/2000/svg" class="base-svgs" width="1em" height="1em">
      <symbol id="icon-download" fill="currentColor" viewBox="0 0 448 512">
          <!-- Font Awesome Free v7.1.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2025 Fonticons, Inc. -->
          <path d="M256 32c0-17.7-14.3-32-32-32s-32 14.3-32 32l0 210.7-41.4-41.4c-12.5-12.5-32.8-12.5-45.3 0s-12.5 32.8 0 45.3l96 96c12.5 12.5 32.8 12.5 45.3 0l96-96c12.5-12.5 12.5-32.8 0-45.3s-32.8-12.5-45.3 0L256 242.7 256 32zM64 320c-35.3 0-64 28.7-64 64l0 32c0 35.3 28.7 64 64 64l320 0c35.3 0 64-28.7 64-64l0-32c0-35.3-28.7-64-64-64l-46.9 0-56.6 56.6c-31.2 31.2-81.9 31.2-113.1 0L110.9 320 64 320zm304 56a24 24 0 1 1 0 48 24 24 0 1 1 0-48z"/>
      </symbol>
    </svg>

</template>
