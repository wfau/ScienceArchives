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
                <div class="my-4 font-monospace">{{ filename }}</div>
            </div>
            <div style="height:60vh;" ref="diagram"></div>
        </div>
    </main>

</template>
