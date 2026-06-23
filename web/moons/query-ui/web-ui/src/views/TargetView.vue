<script setup lang="ts">
import {ref, onMounted, computed} from 'vue';
import { useRoute } from 'vue-router'
import Dygraph from 'dygraphs';
import "dygraphs/dist/dygraph.min.css"

import {getCurrentTheme} from '@/components/theme'
const prefTheme = getCurrentTheme()
if (prefTheme == 'dark') {
    import("@/assets/dygraphs.css")
}

import { getSpectrumData, getSpectrumMetaData } from '@/api/get_result';
import { api_url } from '@/api/query';

const route = useRoute()
const resultId:Number = parseInt(route.params.id as string)
const cname = route.query.cname as string
const schema = route.query.schema

const loading = ref(true)
const metadataUrl = `${api_url}/metadata?cname=${encodeURIComponent(cname)}&schema=${schema}`
const metadata = ref<{metadata?:any,files?:string[],thumbnails?:string[],cname?:string}>({})

const graphRefs = ref<any[]>([])
const graphs = ref<any[]>([])
const hasError = ref<boolean[]>([])
const hasFiles = ref(false)

function setGraphRef(el:any, index:number) {
  graphRefs.value[index] = el
}

const fileDownloadLink = computed(() => {
    return ((filename:string) => `${api_url}/results/${resultId}/file?filename=${filename}`)
})

const getThumbnailTag = (thumbnailPath: string): string => {
    if (!thumbnailPath) return ''
    const pathEl = thumbnailPath.split('/')
    if (pathEl.length > 0) {
        const filename = pathEl[pathEl.length - 1]

        // Safe check to avoid runtime errors if cname is undefined or empty
        const prefixLength = cname ? cname.length + 1 : 0

        return filename?.substring(prefixLength)
            .replace('_', '-')
            .replace('.jpeg', '') || ''
    }
    return ''
}

async function loadData() {
    metadata.value = await getSpectrumMetaData(metadataUrl)
    metadata.value.files?.forEach(async (filename, i) => {
        if (!filename || filename === 'NONE') {
            hasError.value.push(true)
            return;
        }
        hasFiles.value = true
        const url = `${api_url}/results/${resultId}/plot?filename=${filename}`
        try {
            const data = await getSpectrumData(url)
            if (data) {
                const header = data.split('\n', 1)[0]
                var colNames:string[] = ['', '']
                if (header) {
                    colNames = header.split(',')
                }
                const el = graphRefs.value[i]
                if (!el) return
                const g = new Dygraph(
                    el,
                    data,
                    {
                        xlabel: colNames[0],
                        ylabel: colNames[1],
                        customBars: true,
                        axisLineColor: prefTheme == 'dark'? 'white' : 'black',
                    }
                );
                graphs.value.push(g)
                hasError.value.push(false)
            }
            else {
                hasError.value.push(true)
            }
        }
        catch (e) {
            hasError.value.push(true)
        }
    })
    loading.value = false
}

onMounted(() => {
    loadData()
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

        <div class="row">
            <div class="col-lg-8">
            <div v-if="!metadata.metadata" class="card-header p-2 m-2 rounded">
                {{ metadata.cname }}
            </div>
            <div class="card m-4" v-for="(entries, header) in metadata.metadata">
                <div class="card-header">
                    {{ header }}
                </div>
                <div class="card-body p-0">
                    <div class="table-responsive">
                        <table class="table table-hover table-sm mb-0">
                            <tbody>
                                <tr v-for="(value, key) in entries">
                                    <th>{{key}}</th><td>{{value.value || value}}</td><td>{{ value.unit }}</td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
            </div>
            <div class="col-lg-4 d-flex flex-column justify-content-center align-items-center" v-if="metadata.thumbnails && metadata.thumbnails.length">
                <div class="row g-3 justify-content-center align-items-center w-100">
                    <div
                        v-for="(thumb, index) in metadata.thumbnails.slice(0, 4)"
                        :key="index"
                        :class="{
                            'col-10': metadata.thumbnails.length === 1,
                            'col-6 col-lg-10': metadata.thumbnails.length === 2,
                            'col-lg-6 col-4': metadata.thumbnails.length === 3,
                            'col-6 col-md-3 col-lg-6': metadata.thumbnails.length >= 4,
                        }"
                        class="d-flex flex-column justify-content-center align-items-center"
                    >
                        <img
                            class="img-fluid rounded border thumbnail mb-1"
                            :src="fileDownloadLink(thumb)"
                            :alt="thumb"
                        >
                        <div class="small text-muted text-center text-break">
                            {{ getThumbnailTag(thumb) }}
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <div class="m-4" v-if="hasFiles">
            <h1>Spectrum Plot</h1>
            <div v-if="loading">Loading ...</div>
            <div v-else>
                <div class="small">
                    This graph is interactive.
                    Move the mouse over the series to display individual values.
                    Select regions of the graph to zoom in and
                    double-click on the graph to reset the zoom (zoom out).
                </div>
                <div
                    v-for="(filename, index) in metadata.files"
                    :key="filename ?? index"
                    class="graph-wrapper"
                >
                    <div class="my-4 font-monospace">
                        {{ filename }}
                        <a :href="fileDownloadLink(filename)" class="download" v-if="!hasError[index]">
                            <svg width="1em" height="1em" class="theme-icon-active"><use href="#icon-download"/></svg>
                        </a>
                    </div>
                    <div v-if="!hasError[index]"
                        :ref="el => setGraphRef(el, index)"
                        style="height:60vh;" 
                    >
                    </div>
                    <div class="alert alert-danger" v-else>There was an error plotting this file.</div>
                </div>
            </div>
        </div>
    </main>

    <svg xmlns="http://www.w3.org/2000/svg" class="base-svgs" width="1em" height="1em">
      <symbol id="icon-download" fill="currentColor" viewBox="0 0 448 512">
          <!-- Font Awesome Free v7.1.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2025 Fonticons, Inc. -->
          <path d="M256 32c0-17.7-14.3-32-32-32s-32 14.3-32 32l0 210.7-41.4-41.4c-12.5-12.5-32.8-12.5-45.3 0s-12.5 32.8 0 45.3l96 96c12.5 12.5 32.8 12.5 45.3 0l96-96c12.5-12.5 12.5-32.8 0-45.3s-32.8-12.5-45.3 0L256 242.7 256 32zM64 320c-35.3 0-64 28.7-64 64l0 32c0 35.3 28.7 64 64 64l320 0c35.3 0 64-28.7 64-64l0-32c0-35.3-28.7-64-64-64l-46.9 0-56.6 56.6c-31.2 31.2-81.9 31.2-113.1 0L110.9 320 64 320zm304 56a24 24 0 1 1 0 48 24 24 0 1 1 0-48z"/>
      </symbol>
    </svg>

</template>

<style scoped>
.card {
  font-size: 12px;
  font-family: system-ui, -apple-system, "Segoe UI", Roboto, Arial;
  border-width: 2px;
  border-radius: .5rem;
  border-color: #0b62a4; /* header blue */
  overflow: hidden; /* keep header and table corners together */
}
/* Blue header bar */
.card-header {
  font-size: 14px;
  background-color: #0b62a4; /* header blue */
  color: #ffffff;            /* header text */
  text-align: left;
  vertical-align: middle;
}
/* make horizontal separators darker */
.card .table tbody td {
  border-top: 1px solid #444444; /* dark grey lines between rows */
}

/* remove top border for the first row so it sits flush with the header */
.card .table tbody tr:first-child td {
  border-top: none;
}

.thumbnail {
    object-fit: contain;
    max-height: 200px;
    width: auto;
}
</style>