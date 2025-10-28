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

const diagram = useTemplateRef('diagram')
onMounted(async () => {
    // const data = await getSpectrumData(resultId, '/files/GES_MW_00_01/gir_00000014-6003143_H548.8.fit')
    // console.log(data)
    if (diagram.value) {
        new Dygraph(
            diagram.value,
            url, 
            {
                customBars: true,
                height: window.innerHeight*0.5
            }
        );
    }
})
</script>

<template>

    <main class="container-fluid">
        <h1>Spectrum Plot</h1>
        <h5 class="mb-4">{{ filename }}</h5>
        <div ref="diagram"></div>
    </main>

</template>
