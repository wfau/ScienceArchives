<script setup lang="ts">
import {ref, useTemplateRef, onMounted} from 'vue';
import { useRoute } from 'vue-router'
import Dygraph from 'dygraphs';
import { getSpectrumData } from '@/api/get_result';
import { api_url } from '@/api/query';

const route = useRoute()
const resultId:Number = parseInt(route.params.id as string)
const filename = route.query.file

// const filename = ref('/files/GES_MW_00_01/gir_00000014-6003143_H548.8.fit')
const url = `${api_url}/results/${resultId}/file?filename=${filename}`
const loading = ref(true)
const hasError = ref(true)
const diagram = useTemplateRef('diagram')
onMounted(async () => {
    const data = await getSpectrumData(url)
    if (data) {
        hasError.value = false
        diagram.value && new Dygraph(
            diagram.value,
            data,
            {
                customBars: true,
                height: window.innerHeight*0.5
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
        <h1>Spectrum Plot</h1>
        <div v-if="loading">Loading ...</div>
        <div v-if="hasError">An error occurred when loading the data.</div>
        <div v-if="!hasError">
            <h5 class="mb-4">{{ filename }}</h5>
            <div ref="diagram"></div>
        </div>
    </main>

</template>
