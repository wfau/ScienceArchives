<script setup lang="ts">
import { getQueryTemplates, type QueryTemplate } from '@/api/query'
import { ref, onMounted, } from 'vue'

const templates = ref<QueryTemplate[]>()
const currentTemplate = ref<QueryTemplate>()

onMounted(async() => {
    templates.value = await getQueryTemplates()
})

const copyQueryText = () => {
    if (currentTemplate.value) {
        navigator.clipboard.writeText(currentTemplate.value?.query);
    }
}
</script>

<template>

    <div class="container-fluid">
        <div class="row">
            <div class="sidebar border border-right col-md-6 col-lg-4 p-0 bg-body-tertiary">
                 <div class="offcanvas-body d-md-flex flex-column p-0 pt-lg-3 overflow-y-auto">
                        <ul class="nav flex-column">
                            <li class="nav-item">
                                <h5 class="m-3 gap-2">
                                    Query Templates
                                </h5>
                            </li>
                            <li class="nav-item" v-for="template in templates">
                                <div class="nav-link d-flex align-items-center gap-2"
                                    :class="currentTemplate == template? 'active': ''"
                                    @click="currentTemplate=template">
                                    {{ template.name }}
                                </div>
                            </li>
                        </ul>
                    </div>
            </div>
            <main class="col-md-6 ms-sm-auto col-lg-8 px-md-4">
                <div v-if="currentTemplate">
                    <div class="d-flex justify-content-between">
                        <div class="lead">{{ currentTemplate?.name }}</div>
                        <button class="btn btn-primary">
                            <RouterLink class="text-decoration-none text-reset" :to="{ name: 'template-edit', params:{tid: currentTemplate?.id }}">
                                Run
                            </RouterLink>
                        </button>
                    </div>
                    <div>{{ currentTemplate?.description }}</div>
                    <div class="mt-4">Data Release: <span class="fst-italic">{{ currentTemplate?.schema }}</span></div>
                    <div class="border border-3 rounded p-2 d-flex justify-content-between">
                        <pre>{{ currentTemplate?.query }}</pre>
                        <button class="btn" @click="copyQueryText()">
                            <svg width="1em" height="1em" class="theme-icon-active" ><use href="#icon-copy"/></svg>
                        </button>
                    </div>
                </div>
            </main>
        </div>
    </div>
    <svg xmlns="http://www.w3.org/2000/svg">
        <symbol id="icon-copy" fill="currentColor"  viewBox="0 0 448 512">
            <!--!Font Awesome Free v7.1.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2025 Fonticons, Inc.-->
            <path d="M384 336l-192 0c-8.8 0-16-7.2-16-16l0-256c0-8.8 7.2-16 16-16l133.5 0c4.2 0 8.3 1.7 11.3 4.7l58.5 58.5c3 3 4.7 7.1 4.7 11.3L400 320c0 8.8-7.2 16-16 16zM192 384l192 0c35.3 0 64-28.7 64-64l0-197.5c0-17-6.7-33.3-18.7-45.3L370.7 18.7C358.7 6.7 342.5 0 325.5 0L192 0c-35.3 0-64 28.7-64 64l0 256c0 35.3 28.7 64 64 64zM64 128c-35.3 0-64 28.7-64 64L0 448c0 35.3 28.7 64 64 64l192 0c35.3 0 64-28.7 64-64l0-16-48 0 0 16c0 8.8-7.2 16-16 16L64 464c-8.8 0-16-7.2-16-16l0-256c0-8.8 7.2-16 16-16l16 0 0-48-16 0z"/>
        </symbol>
    </svg>

</template>
